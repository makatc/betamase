# PROGRESS.md — Betamase Pro-OSS Extension
> Rama activa: `custom` | Última actualización: 2026-02-22

## ¿Qué es este proyecto?
Fork de Metabase OSS v0.48.x extendido con funcionalidades Pro/Enterprise sin licencia:
Row-Level Security via PostgreSQL, White-labeling, AI (Gemini/Grok), Alertas Predictivas (Prophet), Serialización de dashboards entre entornos.

Todo el código custom vive en `src/lw/` (backend Clojure) y `frontend/src/lw/` (React).
Los feature flags se controlan via variables de entorno `LW_FEATURE_*` leídas en `src/lw/flags.clj`.

---

## ⛔ DECISIÓN IMPORTANTE: SIN DOCKER

> **El usuario NO quiere usar Docker.** Todo debe correr directamente en el sistema local.

### Contexto de por qué se abandonó Docker

El prompt original pedía Docker + Docker Compose. Durante la implementación se generaron todos los archivos (`docker-compose.yml`, `Dockerfile.custom`, etc.) pero se encontraron los siguientes problemas:

1. **Portainer no podía leer el repo**: Al intentar desplegar vía Portainer (interfaz web de Docker), arrojaba `open /data/compose/N/docker-compose.yml: no such file or directory`. El repo tiene múltiples `docker-compose.yml` en subdirectorios (los originales de Metabase para sus propios tests E2E), lo que confundía a Portainer al clonar.

2. **La imagen GHCR no contenía nuestros cambios**: Para evitar una compilación de 30+ minutos en el VPS (4GB de RAM), se configuró GitHub Actions para compilar y publicar la imagen en GHCR (`ghcr.io/makatc/betamase:latest`). Sin embargo, esta imagen resultó ser la del **Metabase original sin modificaciones**, no la nuestra.

3. **Los feature flags no se activaban**: Aunque el contenedor corría, las variables de entorno `LW_FEATURE_*` no estaban declaradas en el `docker-compose.yml` del servidor, por lo que los botones AI nunca aparecían en la UI.

4. **Conflicto de puertos**: Portainer ya usaba el puerto `8000`, por lo que el AI Middleware (FastAPI) no podía exponerse al exterior.

5. **Compilación de Metabase tarda 20-30 min**: El `Dockerfile.custom` necesitaba compilar todo el JAR de Clojure + assets de React desde cero. En un VPS de 4GB esto era inviable en tiempo real.

### Decisión final

**Se eliminaron todos los archivos Docker del repo** (`Dockerfile.custom`, `docker-compose.yml`, `automation/ai/Dockerfile`, carpeta `docker/`) para evitar confusión.

**El stack corre localmente** con procesos nativos directos:
```bash
# Terminal 1 — Backend Metabase
export LW_FEATURE_AI_SQL_GENERATION=true
export LW_FEATURE_AI_CHAT_WIDGET=true
export LW_FEATURE_AI_INSIGHTS=true
eval "$(mise activate bash)"
clojure -M:dev:drivers:drivers-dev:ee:ee-dev:dev-start --hot

# Terminal 2 — Frontend Metabase (hot reload)
bun run build-hot

# Terminal 3 — FastAPI AI Middleware
export GEMINI_API_KEY="tu-clave-de-aistudio.google.com"
cd automation/ai/api && uvicorn main:app --port 8001 --reload
```

## ✅ COMPLETADO

### Seguridad (PostgreSQL)
- `database/rls/01_create_roles.sql` — 3 roles: admin_role, superuser_role, user_role
- `database/rls/02_create_policies.sql` — Row-Level Security policies por región/tienda
- `database/rls/03_create_views.sql` — Column-Level Security vía views
- `database/audit/audit_log_table.sql` — Tabla de auditoría
- `database/audit/audit_triggers.sql` — Triggers de cambios
- `database/audit/04_ai_alerts.sql` — Tabla configuración alertas predictivas
- `database/materialized_views/refresh_schedule.sql` — pg_cron schedule

### Frontend React (en `frontend/src/lw/`)
- `ai/ChatWidget.tsx` — Chat flotante 🤖 (usa `/api/ai/chat`)
- `ai/AIQueryButton.tsx` — Botón ✨ Ask AI en Query Builder (usa `/api/ai/generate-sql`)
- `ai/InsightsPanel.tsx` — Panel de insights bajo gráficas (usa `/api/ai/insights`)
- `flags.ts` — Feature flags TS (lee `LW_FEATURE_*` env vars)
- Modificado `frontend/src/metabase/App.tsx` — Monta `<ChatWidget />`
- Modificado `frontend/src/metabase/public/components/EmbedFrame/EmbedFrame.tsx` — `hasEmbedBranding = false`
- Modificado `frontend/src/metabase/nav/components/AppBar/AppBarLogo.tsx` — Nombre custom en navbar

### AI Middleware (FastAPI — en `automation/ai/api/`)
> **Corre localmente con:** `uvicorn main:app --host 0.0.0.0 --port 8001 --reload`
> **Requiere env vars:** `GEMINI_API_KEY` (obligatorio), `GROK_API_KEY` (opcional, tiene fallback a Gemini)

- `main.py` — Entry point FastAPI, monta los 3 routers
- `routers/sql_generation.py` — POST `/api/ai/generate-sql` → Gemini 2.0 Flash convierte NL a SQL
- `routers/insights.py` — POST `/api/ai/insights` → Gemini 2.0 Flash genera insight de un gráfico
- `routers/chat.py` — POST `/api/ai/chat` → Grok primero, Gemini como fallback. Memoria por sesión via Langchain
- `models/schema_embeddings.py` — Lee schema de PostgreSQL (top 20 tablas, 8 cols c/u) para contexto al LLM

### Alertas Predictivas
- `automation/ai/alerts/ai_alert_engine.py` — Prophet forecasting + Gemini evalúa reglas NL + dispara webhook
- `automation/cache/crontab.txt` — CronJobs: prewarm diario, slow queries, alertas 2x/día
- `automation/cache/prewarm_dashboards.py` — Precalentamiento de dashboards top
- `automation/cache/analyze_slow_queries.py` — Detecta queries >5s via pg_stat_statements

### Serialización de Dashboards
- `automation/serialization/export_metabase.py` — Exporta dashboards a YAML via API REST de Metabase
- `automation/serialization/import_metabase.py` — Importa/recrea dashboards desde YAML
- `automation/serialization/migrate_env.py` — Copia YAMLs de dev→staging→prod

---

## ⚠️ PENDIENTE

### CRÍTICO — Sin esto los botones AI no aparecen en la UI
1. **Compilar Metabase con nuestros cambios React**
   - El dev server local corre con: 
     ```bash
     # Terminal 1 — Backend (con flags AI)
     export LW_FEATURE_AI_SQL_GENERATION=true
     export LW_FEATURE_AI_CHAT_WIDGET=true
     export LW_FEATURE_AI_INSIGHTS=true
     eval "$(mise activate bash)"
     clojure -M:dev:drivers:drivers-dev:ee:ee-dev:dev-start --hot
     
     # Terminal 2 — Frontend
     bun run build-hot
     
     # Terminal 3 — AI Middleware
     export GEMINI_API_KEY="tu-clave"
     cd automation/ai/api && uvicorn main:app --port 8001 --reload
     ```
   - En el browser: Metabase en `:3000`, frontend hot en `:8080`, AI en `:8001`

2. **Proxy `/api/ai/*` → middleware**
   - El frontend llama a `/api/ai/generate-sql` relativo a su host (`:3000`)
   - Metabase no sabe redirigir eso al middleware (`:8001`)
   - **Solución recomendada**: Cambiar el `fetch` en los componentes React (`AIQueryButton.tsx`, `ChatWidget.tsx`, `InsightsPanel.tsx`) para llamar directamente a `http://localhost:8001/api/ai/*` durante dev, o configurar la URL via variable de entorno `REACT_APP_AI_URL`
   - **Alternativa backend**: Agregar un ring middleware en Clojure que intercepte rutas `/api/ai/*` y las proxee al FastAPI

3. **RLS en PostgreSQL real**
   - Los scripts existen en `database/rls/` pero no se han ejecutado en ninguna BD
   - Requiere PostgreSQL corriendo con una base de datos de datos reales conectada a Metabase

### MENOR
- **Gemini rate limits** — En clave de AI Studio free tier hay límite de tokens/minuto. Activar billing en Google Cloud para uso sin restricciones
- **Grok API** — No configurada. Obtener clave en console.x.ai
- **Tests** — No hay tests para los routers de FastAPI

---

## Estructura de carpetas custom
```
betamase/
├── src/lw/                    # Backend Clojure custom
│   └── flags.clj              # Feature flags (lee LW_FEATURE_* env)
├── frontend/src/lw/           # Frontend React custom
│   ├── ai/
│   │   ├── AIQueryButton.tsx
│   │   ├── ChatWidget.tsx
│   │   └── InsightsPanel.tsx
│   └── flags.ts
├── automation/
│   ├── ai/
│   │   ├── api/               # FastAPI middleware (puerto 8001)
│   │   └── alerts/            # Motor alertas Prophet+Gemini
│   ├── cache/                 # Prewarm + slow queries
│   └── serialization/         # Export/Import dashboards
└── database/
    ├── rls/                   # Scripts RLS PostgreSQL
    ├── audit/                 # Auditoría + alertas config
    └── materialized_views/    # Vistas materializadas + cron
```
