# PROMPT.md — Objetivo Original del Proyecto

## Prompt Original del Usuario

> Quiero extender Metabase Open Source (v0.48.x) para replicar las funcionalidades de la versión Pro/Enterprise **sin pagar la licencia** (~$20k/año).
> 
> El proyecto debe correr **100% local** usando el código fuente de Metabase en un fork de GitHub, con modificaciones propias en una rama separada (`custom`) para poder recibir actualizaciones del upstream sin conflictos.

---

## Objetivos Específicos

### 1. Row-Level Security (RLS) — Seguridad de Datos
- Implementar RLS **en PostgreSQL nativo**, no en la capa de aplicación
- Crear 3 niveles de acceso: `admin_role`, `superuser_role`, `user_role`
- Cada rol de Postgres se conecta a Metabase como una "Database Connection" separada
- Los usuarios solo ven los datos de sus tiendas/regiones permitidas
- También implementar Column-Level Security (CLS) via vistas de PostgreSQL para ocultar campos sensibles (PII, tarjetas de crédito, etc.)

### 2. Multi-Entorno (Dev → Staging → Prod)
- Configurar 3 entornos separados
- Serializar dashboards y preguntas de Metabase para poder migrarlos entre entornos via Git
- Scripts para export/import de configuraciones vía la API REST de Metabase

### 3. White-Labeling / Personalización de Marca
- Eliminar el logo y texto "Powered by Metabase" de los embeds y dashboards públicos
- Personalizar el nombre/logo en la barra de navegación
- Controlar features via **Feature Flags** leídos de variables de entorno (`LW_FEATURE_*`)
- Todo el código custom aislado en `src/lw/` (Clojure) y `frontend/src/lw/` (React)

### 4. Integración de Inteligencia Artificial
- **Generación de SQL desde lenguaje natural**: El usuario escribe "Muéstrame ventas por región" y Gemini genera el SQL
- **Insights automáticos**: Analizar el JSON de un gráfico y generar una frase de insight (ej: "Caída del 15% los fines de semana")
- **Chat conversacional**: Widget de chat flotante en Metabase que usa Grok-xAI con memoria de conversación

#### Modelos AI seleccionados:
- `gemini-2.0-flash` (Google) → Generación SQL + Insights (rápido y barato)
- `grok-beta` (xAI) → Chat conversacional (contexto masivo)
- Langchain para manejo de memoria de conversación

### 5. Caché Inteligente (replica Pro Feature)
- Detectar queries lentas (>5s) via `pg_stat_statements`
- Crear Vistas Materializadas automáticamente para esas queries
- Pre-calentar (prewarm) dashboards top cada madrugada antes que entren los usuarios

### 6. Alertas Predictivas con IA
- Motor de series de tiempo con **Facebook Prophet**
- El usuario define reglas en lenguaje natural: *"Avisarme si las ventas caen más de 10%"*
- Gemini evalúa si la predicción de Prophet cumple la condición NL
- Si se cumple → dispara webhook a Slack/Discord

### 7. Auditoría
- Tabla `audit_log` en PostgreSQL
- Triggers que capturan INSERT/UPDATE en las tablas de configuración de Metabase

---

## Stack Tecnológico

| Componente | Tecnología |
|---|---|
| BI Core | Metabase OSS v0.48.x (fork en rama `custom`) |
| Backend BI | Clojure (código original Metabase) |
| Frontend BI | React/TypeScript (código original Metabase) |
| AI Middleware | Python + FastAPI (puerto 8001) |
| Base de Datos | PostgreSQL 15 |
| AI Providers | Google Gemini API + xAI Grok |
| ML / Series Tiempo | Facebook Prophet + Pandas |
| Orquestación AI | Langchain + langchain-openai |
| Runtime Local | mise (Node 22, Java 21, Python 3.12, Bun, Clojure CLI) |

---

## Restricciones

- **Sin Docker** — Todo corre directamente en el sistema local
- **Sin licencias de pago** — Solo herramientas OSS o APIs con tier gratuito/de pago por uso
- **Sin tocar la rama `master`** — Todos los cambios en rama `custom`, para poder hacer `git rebase master` cuando Metabase saque parches
- El código custom nunca mezcla con el upstream: usa `src/lw/` y `frontend/src/lw/` como namespaces propios

---

## Estado del Proyecto
Ver `PROGRESS.md` para el estado actual de implementación.
