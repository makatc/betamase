# AI Copilot — Documentación Técnica

> **Betamase Pro-OSS** · versión 2.0 · Última actualización: 2026-02-22

---

## Índice

1. [Resumen ejecutivo](#1-resumen-ejecutivo)
2. [Arquitectura general](#2-arquitectura-general)
3. [Cómo funciona cada módulo](#3-cómo-funciona-cada-módulo)
4. [Flujo de datos completo](#4-flujo-de-datos-completo)
5. [Endpoints del middleware](#5-endpoints-del-middleware)
6. [Componentes frontend](#6-componentes-frontend)
7. [Modelos de AI usados](#7-modelos-de-ai-usados)
8. [Seguridad y permisos](#8-seguridad-y-permisos)
9. [Variables de entorno](#9-variables-de-entorno)
10. [Cómo iniciar el sistema](#10-cómo-iniciar-el-sistema)

---

## 1. Resumen ejecutivo

El **AI Copilot** es un asistente de datos integrado directamente en la interfaz de Betamase. Permite a los usuarios:

- Hacer preguntas en **lenguaje natural** y recibir respuestas con datos reales
- **Generar y editar SQL** sin escribir código
- Ver **insights automáticos** sobre gráficos y dashboards
- Todo sin salir de la aplicación y respetando los permisos del usuario activo

El asistente aparece como un **panel lateral deslizante** en el lado derecho de la pantalla, activado desde el botón **✨ Ask AI** en la barra superior.

---

## 2. Arquitectura general

```
┌─────────────────────────────────────────────────────────┐
│                   BETAMASE (React UI)                   │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │  AppBar                           [✨ Ask AI]   │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌──────────────────────┐  ┌──────────────────────────┐ │
│  │   Main Content       │  │  AI Copilot Panel        │ │
│  │   (dashboards,       │  │  ┌──────────────────┐   │ │
│  │    queries, etc.)    │  │  │ 💬 Chat           │   │ │
│  │                      │  │  │ 🔍 SQL            │   │ │
│  │                      │  │  │ 💡 Insights       │   │ │
│  └──────────────────────┘  └──────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
                              │ fetch (HTTP)
                              ▼
┌─────────────────────────────────────────────────────────┐
│             FastAPI Middleware  :8001                    │
│                                                         │
│  POST /api/ai/chat          ← conversación              │
│  POST /api/ai/generate-sql  ← NL → SQL                  │
│  POST /api/ai/insights      ← resumen de gráfico        │
│  POST /api/ai/query         ← consulta completa NL      │
│                                                         │
│  Schema Introspection ──► PostgreSQL :5432              │
└─────────────────────────────────────────────────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
   Gemini 2.0 Flash      Grok (x.ai)         PostgreSQL
   (SQL, insights,      (chat primary,       (datos reales,
    query, fallback)     fallback→Gemini)     schema context)
```

---

## 3. Cómo funciona cada módulo

### 3.1 Chat (`💬 Chat`)

El tab de chat permite conversación en lenguaje natural sobre los datos.

**Flujo:**
1. El usuario escribe una pregunta (ej: *"¿Cuántas ventas hubo en enero?"*)
2. El frontend envía el mensaje a `POST /api/ai/chat`
3. El middleware intenta responder con **Grok** (x.ai) como proveedor primario
4. Si Grok falla o no está configurado, hace **fallback automático a Gemini**
5. Mantiene **historial de conversación por usuario** en memoria (hasta 10 mensajes)
6. La respuesta se muestra en el panel como un mensaje de chat

**Características:**
- Historial contextual: el asistente recuerda el hilo de la conversación
- Fallback automático si un proveedor no está disponible
- Indicador de "cargando" mientras espera respuesta

---

### 3.2 SQL Generator (`🔍 SQL`)

El tab SQL permite generar consultas SQL a partir de una descripción en texto.

**Flujo:**
1. El usuario describe lo que necesita (ej: *"Ventas totales por mes del último año"*)
2. El frontend envía la descripción a `POST /api/ai/generate-sql`
3. El middleware:
   - Consulta el **esquema real de la base de datos** (via `information_schema`)
   - Construye un prompt con el esquema como contexto
   - Gemini 2.0 Flash genera el SQL
4. El SQL se muestra en un **editor de texto editable**
5. El usuario puede **revisar, editar** y copiar el SQL antes de usarlo

**Seguridad:**
- Bloquea automáticamente operaciones destructivas: `DROP`, `DELETE`, `TRUNCATE`, `UPDATE`, `INSERT`, `ALTER`
- Solo permite consultas `SELECT`
- Muestra advertencia visible al usuario

---

### 3.3 Insights (`💡 Insights`)

El tab de insights muestra análisis automáticos de los datos visibles.

**Flujo:**
1. Cuando un componente `InsightsPanel` se monta (al cargar un dashboard/chart)
2. Envía los datos del gráfico a `POST /api/ai/insights`
3. Gemini analiza los datos y extrae **1-2 oraciones de insight de negocio**
4. El insight se muestra en el tab, destacando:
   - Tendencias al alza o baja
   - Anomalías o outliers
   - Patrones relevantes

---

### 3.4 NL Query (`/api/ai/query`)

Endpoint avanzado que combina chat + SQL en una sola llamada.

**Flujo:**
1. Recibe una pregunta + contexto de la página actual
2. Determina si la pregunta requiere datos o puede responderse directamente
3. Si requiere datos: genera SQL + responde en español
4. Retorna: `{ answer, sql, source, confidence }`

---

## 4. Flujo de datos completo

```
Usuario escribe: "¿Cuál fue el revenue del Q3?"
        │
        ▼
[AICopilotPanel → ChatTab]
  setMessages([...prev, { role: "user", text }])
        │
        ▼
[AICopilotContext.sendMessage()]
  fetch("http://localhost:8001/api/ai/chat", { message })
        │
        ▼
[FastAPI /api/ai/chat]
  1. ¿Existe GROK_API_KEY? → intenta Grok
  2. Si falla → intenta Gemini
  3. Añade al historial del usuario
  return { reply: "El revenue del Q3 fue $2.3M..." }
        │
        ▼
[AICopilotContext]
  setMessages([...prev, { role: "ai", text: reply }])
        │
        ▼
[ChatTab renderiza el mensaje]
```

---

## 5. Endpoints del middleware

Base URL: `http://localhost:8001`

### `POST /api/ai/chat`
Conversación en lenguaje natural.

```json
// Request
{
  "message": "¿Cuántos usuarios activos hay este mes?",
  "user_id": "default_user"
}

// Response
{
  "reply": "Basándome en los datos disponibles...",
  "provider": "grok",
  "sql_used": null
}
```

---

### `POST /api/ai/generate-sql`
Genera SQL a partir de lenguaje natural.

```json
// Request
{
  "natural_language": "Ventas totales por categoría de producto"
}

// Response
{
  "sql": "SELECT categoria, SUM(total) FROM ventas GROUP BY categoria;",
  "model": "gemini-2.0-flash",
  "confidence": 0.95
}
```

---

### `POST /api/ai/insights`
Genera un insight sobre datos de un gráfico.

```json
// Request
{
  "dashboard_id": 42,
  "data_json": "[{\"mes\": \"Enero\", \"ventas\": 1200}, ...]"
}

// Response
{
  "text": "Las ventas muestran una caída del 18% en Febrero respecto a Enero.",
  "confidence": 0.9
}
```

---

### `POST /api/ai/query`
Consulta combinada NL → respuesta + SQL opcional.

```json
// Request
{
  "question": "¿Cuál fue el mejor mes de ventas?",
  "user_id": "usuario1",
  "context": "Dashboard: Reporte de Ventas 2024"
}

// Response
{
  "answer": "El mejor mes fue Octubre con $4.2M en ventas totales.",
  "sql": "SELECT mes, SUM(total) FROM ventas GROUP BY mes ORDER BY SUM(total) DESC LIMIT 1;",
  "model": "gemini-2.0-flash",
  "source": "sql_generated",
  "confidence": 0.87
}
```

---

### `GET /health`
Verificación de estado del servicio.

```json
{ "status": "ok", "service": "AI Subsystem Online" }
```

---

## 6. Componentes frontend

### Árbol de componentes

```
App.tsx
└── AICopilotProvider          ← Contexto global (estado del panel)
    ├── AppBar
    │   └── AIBarButton        ← Botón "✨ Ask AI" en la barra superior
    ├── [contenido principal]
    └── AICopilotPanel         ← Panel lateral derecho
        ├── Header (título + botón cerrar)
        ├── Tabs (Chat | SQL | Insights)
        └── Tab Content
            ├── ChatTab        ← Conversación
            ├── SQLTab         ← Generador SQL
            └── InsightsTab    ← Resúmenes
```

### `AICopilotContext` — Estado global

```typescript
interface AICopilotContextType {
  isOpen: boolean           // ¿Panel visible?
  activeTab: CopilotTab     // 'chat' | 'sql' | 'insights'
  messages: ChatMessage[]   // Historial del chat
  isLoading: boolean        // Espera respuesta AI
  generatedSQL: string      // Último SQL generado

  openPanel(tab?, query?)   // Abre el panel (opcionalmente con query inicial)
  closePanel()              // Cierra el panel
  setActiveTab(tab)         // Cambia de tab
  sendMessage(text)         // Envía mensaje al chat
  generateSQL(text)         // Genera SQL desde descripción
  clearMessages()           // Limpia el historial
}
```

### `AIBarButton`

- Ubicación: AppBar, derecha (junto a AppSwitcher)
- Cuando el panel está **cerrado**: fondo transparente, texto/borde brand color
- Cuando el panel está **abierto**: fondo brand color, texto blanco

---

## 7. Modelos de AI usados

| Proveedor | Modelo | Uso | Prioridad |
|-----------|--------|-----|-----------|
| **x.ai (Grok)** | `grok-beta` | Chat conversacional | Primario |
| **Google Gemini** | `gemini-2.0-flash` | Chat (fallback), SQL, Insights, Query | Fallback / Primario en SQL |

**Estrategia de fallback:**
- Chat: Grok → Gemini (automático si Grok falla)
- SQL/Insights/Query: Gemini directamente

**Límites del Free Tier de Gemini:**
- Si hay rate limit (`RESOURCE_EXHAUSTED`), el sistema retorna un error 429 con mensaje explicativo
- Solución: activar billing en [console.cloud.google.com](https://console.cloud.google.com)

---

## 8. Seguridad y permisos

### SQL Safety
Todas las consultas SQL generadas por AI pasan por un filtro de seguridad que **bloquea** operaciones destructivas:

```python
BLOCKED_KEYWORDS = ["drop", "delete", "truncate", "update", "insert", "alter"]
```

Si el modelo genera SQL con estas palabras, la consulta es **rechazada o eliminada** antes de llegar al usuario.

### Permisos de usuario
- El AI Copilot opera dentro de la sesión autenticada de Metabase
- No tiene acceso a datos adicionales más allá de lo que el usuario puede ver
- No almacena datos de consultas fuera del entorno local
- El historial de conversación vive **en memoria** del servidor FastAPI (se pierde al reiniciar)

### CORS
El middleware solo acepta requests desde:
- `http://localhost:3000` (Metabase backend)
- `http://localhost:8080` (frontend hot reload)
- `http://localhost:8081` (alternativo)

---

## 9. Variables de entorno

### FastAPI Middleware (`.env` o shell)

| Variable | Descripción | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | API key de Google Gemini | — (requerido) |
| `GROK_API_KEY` | API key de x.ai Grok | — (opcional) |
| `AI_PRIMARY_MODEL` | Modelo Gemini para SQL/Query | `gemini-2.0-flash` |
| `AI_FAST_MODEL` | Modelo Gemini para insights | `gemini-2.0-flash` |
| `AI_CHAT_MODEL` | Modelo Grok para chat | `grok-beta` |
| `DATABASE_URL` | PostgreSQL URI completa | — |
| `POSTGRES_DW_HOST` | Host PostgreSQL (alternativo) | `localhost` |
| `POSTGRES_DW_PORT` | Puerto PostgreSQL | `5432` |
| `POSTGRES_DW_NAME` | Nombre de la BD | `betamase_data` |
| `POSTGRES_DW_USER` | Usuario PostgreSQL | `postgres` |
| `POSTGRES_DW_PASSWORD` | Contraseña PostgreSQL | — |

### Frontend React (build time)

| Variable | Descripción | Default |
|----------|-------------|---------|
| `REACT_APP_AI_URL` | URL base del middleware AI | `http://localhost:8001` |
| `LW_FEATURE_AI_SQL_GENERATION` | Activa generación SQL | `true` |
| `LW_FEATURE_AI_CHAT_WIDGET` | Activa chat AI | `true` |
| `LW_FEATURE_AI_INSIGHTS` | Activa insights automáticos | `true` |

---

## 10. Cómo iniciar el sistema

### Terminal 1 — Backend Metabase (Clojure)
```bash
export LW_FEATURE_AI_SQL_GENERATION=true
export LW_FEATURE_AI_CHAT_WIDGET=true
export LW_FEATURE_AI_INSIGHTS=true
eval "$(mise activate bash)"
clojure -M:dev:drivers:drivers-dev:ee:ee-dev:dev-start --hot
```
→ Disponible en `http://localhost:3000`

### Terminal 2 — Frontend React
```bash
bun run build-hot
```
→ Disponible en `http://localhost:8080`

### Terminal 3 — AI Middleware (FastAPI)
```bash
export GEMINI_API_KEY="tu-api-key"
export GROK_API_KEY="tu-api-key-opcional"
cd automation/ai/api
uvicorn main:app --port 8001 --reload
```
→ Disponible en `http://localhost:8001`
→ Documentación Swagger: `http://localhost:8001/docs`

### Verificar que todo funciona
```bash
# Health check del middleware
curl http://localhost:8001/health
# → {"status":"ok","service":"AI Subsystem Online"}

# Test de chat
curl -X POST http://localhost:8001/api/ai/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hola, ¿qué puedes hacer?"}'
```

---

## Estructura de archivos relevantes

```
betamase/
├── frontend/src/lw/ai/
│   ├── AICopilotContext.tsx   ← Estado global, hooks, fetch calls
│   ├── AICopilotPanel.tsx     ← Panel UI (Chat + SQL + Insights)
│   ├── AIBarButton.tsx        ← Botón en AppBar
│   ├── AIQueryButton.tsx      ← Botón inline en query builder
│   ├── InsightsPanel.tsx      ← Insights automáticos en dashboards
│   └── flags.ts               ← Feature flags + URL config
│
├── frontend/src/metabase/
│   ├── App.tsx                ← AICopilotProvider + AICopilotPanel montados aquí
│   └── nav/components/AppBar/
│       └── AppBarLarge.tsx    ← AIBarButton integrado aquí
│
└── automation/ai/api/
    ├── main.py                ← FastAPI app + CORS + routers
    ├── routers/
    │   ├── chat.py            ← POST /api/ai/chat
    │   ├── sql_generation.py  ← POST /api/ai/generate-sql
    │   ├── insights.py        ← POST /api/ai/insights
    │   └── query.py           ← POST /api/ai/query (nuevo)
    └── models/
        └── schema_embeddings.py  ← Introspección del esquema PostgreSQL
```
