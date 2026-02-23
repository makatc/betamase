# ✅ Resumen de Cambios — 2026-02-22

## 🎯 Objetivo
Fijar los problemas críticos del stack local para que los botones AI aparezcan y funcionen en la UI de Metabase.

---

## ✅ Cambios Realizados

### 1. Frontend React — URLs de API

#### Problema
Los componentes React usaban URLs **relativas** que apuntaban a `http://localhost:3000` (Metabase), pero el middleware AI corre en `http://localhost:8001`. Metabase no sabía cómo proxear esas llamadas.

#### Solución

**Archivo**: `frontend/src/lw/flags.ts`
- ✅ Agregado export `getAIMiddlewareURL()`
- ✅ Lee variable de entorno `REACT_APP_AI_URL` (fallback: `http://localhost:8001`)
- ✅ Centraliza la configuración de URL en un sólo lugar

**Archivo**: `frontend/src/lw/ai/ChatWidget.tsx`
- ✅ Import: `import { isFeatureEnabled, getAIMiddlewareURL } from '../flags'`
- ✅ Cambio en fetch (línea 20-21):
  ```typescript
  // Antes:
  fetch('/api/ai/chat', ...)

  // Después:
  const aiUrl = getAIMiddlewareURL();
  fetch(`${aiUrl}/api/ai/chat`, ...)
  ```
- ✅ Agregado error logging: `console.error('Chat API error:', e)`

**Archivo**: `frontend/src/lw/ai/AIQueryButton.tsx`
- ✅ Import actualizado
- ✅ Cambio en fetch (línea 14-17):
  ```typescript
  // Antes:
  fetch('/api/ai/generate-sql', ...)

  // Después:
  const aiUrl = getAIMiddlewareURL();
  fetch(`${aiUrl}/api/ai/generate-sql`, ...)
  ```
- ✅ Agregado error logging

**Archivo**: `frontend/src/lw/ai/InsightsPanel.tsx`
- ✅ Import actualizado
- ✅ Cambio en fetch (línea 11-13):
  ```typescript
  // Antes:
  fetch('/api/ai/insights', ...)

  // Después:
  const aiUrl = getAIMiddlewareURL();
  fetch(`${aiUrl}/api/ai/insights`, ...)
  ```
- ✅ Agregado error logging

### 2. FastAPI — Dependencias Python

#### Problema
El archivo `chat.py` importa `from langchain_openai import ChatOpenAI` pero esta librería **no estaba en requirements.txt**.

#### Solución

**Archivo**: `automation/ai/requirements.txt`
- ✅ Agregado `langchain-openai==0.0.5`

**Archivo**: `automation/ai/api/requirements.txt` (NUEVO)
- ✅ Creado archivo local en `automation/ai/api/` con todas las dependencias
- ✅ Permite correr `pip install -r automation/ai/api/requirements.txt` desde la carpeta del middleware

Dependencias actuales:
```
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.4.2
google-generativeai==0.3.0
langchain==0.0.335
langchain-openai==0.0.5          ← AGREGADO
chromadb==0.4.15
psycopg2-binary==2.9.9
```

### 3. FastAPI — PostgreSQL Connection (Development)

#### Problema
El script `schema_embeddings.py` asumía variables de entorno Docker (host: `metabase-db`, BD: `metabaseappdb`). En desarrollo local no funcionaría.

#### Solución

**Archivo**: `automation/ai/api/models/schema_embeddings.py`

Líneas 4-8 — Cambio en env vars:
```python
# Antes:
DB_HOST = os.getenv("POSTGRES_DW_HOST", "metabase-db")
DB_NAME = os.getenv("POSTGRES_DW_NAME", "metabaseappdb")
DB_USER = os.getenv("POSTGRES_DW_USER_ADMIN", "metabase_user")
DB_PASS = os.getenv("POSTGRES_DW_PASSWORD", "metabase_password")

# Después (development-friendly):
DB_HOST = os.getenv("POSTGRES_DW_HOST", "localhost")
DB_PORT = int(os.getenv("POSTGRES_DW_PORT", "5432"))
DB_NAME = os.getenv("POSTGRES_DW_NAME", "betamase_data")
DB_USER = os.getenv("POSTGRES_DW_USER", "postgres")
DB_PASS = os.getenv("POSTGRES_DW_PASSWORD", "")
```

Línea 17-23 — Cambio en conexión psycopg2:
```python
# Antes:
conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)

# Después (soporta password vacía):
conn = psycopg2.connect(
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASS if DB_PASS else None
)
```

### 4. FastAPI — Main Entry Point

**Archivo**: `automation/ai/api/main.py`

Línea 19 — Actualizado comentario con puerto correcto:
```python
# Antes:
# uvicorn main:app --host 0.0.0.0 --port 8000

# Después:
# uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

---

## 📊 Cambios por Archivo

| Archivo | Cambios | Estado |
|---------|---------|--------|
| `frontend/src/lw/flags.ts` | ✅ Agregada `getAIMiddlewareURL()` | Completado |
| `frontend/src/lw/ai/ChatWidget.tsx` | ✅ URLs apuntan a `:8001` | Completado |
| `frontend/src/lw/ai/AIQueryButton.tsx` | ✅ URLs apuntan a `:8001` | Completado |
| `frontend/src/lw/ai/InsightsPanel.tsx` | ✅ URLs apuntan a `:8001` | Completado |
| `automation/ai/requirements.txt` | ✅ `+langchain-openai` | Completado |
| `automation/ai/api/requirements.txt` | ✅ NUEVO archivo | Completado |
| `automation/ai/api/models/schema_embeddings.py` | ✅ Conexión local | Completado |
| `automation/ai/api/main.py` | ✅ Comentario actualizado | Completado |
| `PROGRESS.md` | ✅ Estado actualizado | Completado |
| `GETTING_STARTED.md` | ✅ NUEVO archivo | Completado |

---

## 🚀 Próximos Pasos

### Para el Usuario
1. Seguir la guía en `GETTING_STARTED.md` para levantar el stack
2. Verificar que los botones AI aparecen en Metabase
3. Probar: Chat, Ask AI (SQL generation), Insights

### Para el Próximo Agente (si hay tareas pendientes)
1. **RLS en PostgreSQL** — Ejecutar scripts en `database/rls/`
2. **CORS en FastAPI** — Agregar middleware si hay errores de cross-origin
3. **Tests** — Crear tests para routers FastAPI
4. **DOCKER** — Cuando el usuario lo indique (ver `DOCKER_ABANDONMENT.md`)

---

## ✅ Validación

Para verificar que todo está correcto:

```bash
# 1. Verificar cambios en React
grep -n "getAIMiddlewareURL" frontend/src/lw/ai/*.tsx
# Debería mostrar 3 archivos con la función

# 2. Verificar requirements.txt
grep langchain-openai automation/ai/requirements.txt
# Debería mostrar: langchain-openai==0.0.5

# 3. Verificar schema_embeddings
grep "localhost" automation/ai/api/models/schema_embeddings.py
# Debería mostrar: DB_HOST = os.getenv("POSTGRES_DW_HOST", "localhost")

# 4. Verificar puerto correcto en main.py
grep "8001" automation/ai/api/main.py
# Debería mostrar: --port 8001
```

---

**Todos los cambios están en la rama `custom`**
**Listos para ejecución inmediata**
