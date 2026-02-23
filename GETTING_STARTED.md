# 🚀 Betamase Pro-OSS — Guía de Inicio Rápido

**Estado**: ✅ Listo para desarrollo local | **Fecha**: 2026-02-22

## Prerequisitos

```bash
# Verificar que tienes instalado:
- Node.js (v18+) con Bun
- Java 11+ (para Clojure)
- PostgreSQL 14+
- Python 3.10+
- Mise (gestor de versiones)

# Verificar instalaciones
bun --version
java -version
psql --version
python --version
mise --version
```

---

## Setup Inicial (Una sola vez)

### 1. Instalar dependencias del proyecto

```bash
cd /home/makatc/PROYECTOS/betamase

# Dependencias Node
bun install

# Dependencias Python (FastAPI middleware)
pip install -r automation/ai/api/requirements.txt
```

### 2. Configurar PostgreSQL

```bash
# Iniciar PostgreSQL (si no está corriendo)
sudo systemctl start postgresql

# Crear bases de datos
createdb metabase           # BD para metabase (aplicación)
createdb betamase_data      # BD para datos reales (para testing RLS)

# Verificar
psql -l | grep -E "metabase|betamase"
```

### 3. Obtener API Keys

**Gemini (Obligatorio)**:
1. Ir a https://aistudio.google.com
2. Click "Get API Key"
3. Copiar la key
4. Guardar en variable de entorno: `export GEMINI_API_KEY="AIza..."`

**Grok (Opcional)**:
- Ir a https://console.x.ai
- Crear API key (fallback a Gemini si no lo configuras)

---

## Ejecución: 3 Terminales Paralelas

Abre **3 terminales diferentes** en `/home/makatc/PROYECTOS/betamase` y corre cada comando:

### 📍 Terminal 1 — Backend Metabase

```bash
export LW_FEATURE_AI_SQL_GENERATION=true
export LW_FEATURE_AI_CHAT_WIDGET=true
export LW_FEATURE_AI_INSIGHTS=true

eval "$(mise activate bash)"
clojure -M:dev:drivers:drivers-dev:ee:ee-dev:dev-start --hot
```

**Esperar hasta ver**:
```
✓ Metabase is starting
✓ App DB is up
✓ Adding metabase.com analytics to nREPL
```

**Acceso**: http://localhost:3000

---

### 📍 Terminal 2 — Frontend React (Hot Reload)

```bash
cd /home/makatc/PROYECTOS/betamase
bun run build-hot
```

**Esperar hasta ver**:
```
✓ Watching files...
✓ rspack compiled...
```

Los cambios en `frontend/src/lw/` se compilan en <2 segundos.

---

### 📍 Terminal 3 — FastAPI AI Middleware

```bash
export GEMINI_API_KEY="AIza..."  # Tu key de aistudio.google.com
# export GROK_API_KEY="xai-..."    # Opcional

cd /home/makatc/PROYECTOS/betamase/automation/ai/api
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

**Esperar hasta ver**:
```
✓ Uvicorn running on http://0.0.0.0:8001
✓ Application startup complete
```

**Verificar salud del servicio**:
```bash
curl http://localhost:8001/health
# Respuesta: {"status":"ok","service":"AI Subsystem Online"}
```

---

## URLs Disponibles

| Servicio | URL | Puerto |
|----------|-----|--------|
| **Metabase** | http://localhost:3000 | 3000 |
| **AI Middleware** | http://localhost:8001 | 8001 |
| **PostgreSQL** | localhost:5432 | 5432 |

---

## Verificación: ¿Funcionan los botones AI?

### 1. Abrir Metabase

```
http://localhost:3000
```

Login: `admin@metabase.com` / `metabase` (default)

### 2. Crear una Query

- Click "New" → "Question"
- Click el botón azul **"✨ Ask AI"**

Si aparece el botón → ✅ Frontend está correctamente compilado

### 3. Probar generación de SQL

- Escribir: "Muéstrame las primeras 10 filas"
- Click "Generar Query"

Si funciona → ✅ Middleware AI está respondiendo correctamente

### 4. Probar Chat

- Buscar el ícono **🤖** en la esquina inferior derecha
- Hacer una pregunta: "¿Cuántas tablas hay en la BD?"

Si responde → ✅ Chat conversacional está activo

---

## Troubleshooting

### ❌ Los botones AI no aparecen

**Causa**: Feature flags no activos

```bash
# Verificar variables de entorno en Terminal 1
echo $LW_FEATURE_AI_CHAT_WIDGET
echo $LW_FEATURE_AI_SQL_GENERATION
echo $LW_FEATURE_AI_INSIGHTS

# Si están vacías, agregalos:
export LW_FEATURE_AI_CHAT_WIDGET=true
export LW_FEATURE_AI_SQL_GENERATION=true
export LW_FEATURE_AI_INSIGHTS=true

# Reiniciar Backend (Ctrl+C en Terminal 1 y volver a correr)
```

### ❌ Error: "GEMINI_API_KEY not configured on server"

```bash
# Verificar variable en Terminal 3
echo $GEMINI_API_KEY

# Si está vacía:
export GEMINI_API_KEY="AIza..."
# Reiniciar middleware (Ctrl+C y volver a correr)
```

### ❌ Error: "Cannot connect to PostgreSQL"

```bash
# Verificar que PostgreSQL está corriendo
sudo systemctl status postgresql

# Si no está corriendo:
sudo systemctl start postgresql

# Verificar que existen las BDs
psql -l | grep betamase

# Si no existen, crearlas:
createdb betamase_data
```

### ❌ Error CORS: "Access to XMLHttpRequest blocked"

**Causa**: El middleware no está configurado para CORS

**Solución**: Agregar middleware CORS en `automation/ai/api/main.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Dev: permitir todo. Prod: especificar origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Próximos Pasos

### 1. Ejecutar Scripts RLS (Row-Level Security)

```bash
psql -U postgres -d betamase_data

\i /home/makatc/PROYECTOS/betamase/database/rls/01_create_roles.sql
\i /home/makatc/PROYECTOS/betamase/database/rls/02_create_policies.sql
\i /home/makatc/PROYECTOS/betamase/database/rls/03_create_views.sql
\i /home/makatc/PROYECTOS/betamase/database/audit/audit_log_table.sql
\i /home/makatc/PROYECTOS/betamase/database/audit/audit_triggers.sql
\i /home/makatc/PROYECTOS/betamase/database/audit/04_ai_alerts.sql
```

### 2. Conectar Base de Datos en Metabase

1. Ir a Metabase → Admin Panel → Databases
2. Click "Add database"
3. PostgreSQL:
   - Host: localhost
   - Port: 5432
   - Database: betamase_data
   - User: postgres
   - Password: (dejar vacío si no lo configuraste)

### 3. Crear Queries y Dashboards

- Usar "Ask AI" para generar queries
- Ver insights automáticos debajo de gráficas
- Chat 🤖 para análisis conversacional

---

## Desarrollo

### Modificar Componentes React

Los cambios en `frontend/src/lw/ai/*.tsx` se compilan automáticamente en Terminal 2.

```bash
# Ejemplo: Agregar funcionalidad a ChatWidget
nano frontend/src/lw/ai/ChatWidget.tsx
# Los cambios aparecen en ~1 segundo en http://localhost:3000
```

### Modificar FastAPI Routers

Los cambios en `automation/ai/api/routers/*.py` se recargan automáticamente en Terminal 3.

```bash
# Ejemplo: Cambiar el modelo de Gemini a otro
nano automation/ai/api/routers/sql_generation.py
# Los cambios aparecen inmediatamente
```

### Modificar Backend Clojure

Los cambios en `src/lw/flags.clj` se recargan en el REPL de Terminal 1 (con `--hot`).

```bash
# Ejemplo: Agregar un nuevo feature flag
nano src/lw/flags.clj
# Usar (require '[lw.flags] :reload) en el REPL para recargar
```

---

## Parar los Servicios

```bash
# En cada terminal:
Ctrl+C
```

PostgreSQL continuará corriendo. Para pararlo:

```bash
sudo systemctl stop postgresql
```

---

## Stack Technologies

- **Backend**: Metabase OSS v0.48.x (Clojure)
- **Frontend**: React 18 + TypeScript
- **AI**: Gemini 2.0 Flash + Grok
- **Database**: PostgreSQL 14+
- **Python**: FastAPI + Langchain
- **Build**: Rspack + Bun + Clojure CLI

---

**¿Necesitas ayuda?** Revisa `PROGRESS.md` y `DOCKER_ABANDONMENT.md` para más contexto.
