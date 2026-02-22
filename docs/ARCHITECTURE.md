# Arquitectura Extendida: Metabase OSS Pro-Features

## Resumen

Esta solución expande las capacidades de **Metabase OSS (v0.48.x)** mediante un middleware basado en APIs de Inteligencia Artificial (Gemini/Grok), una gestión robusta de PostgreSQL para seguridad (RLS y CLS), y un wrapper con Docker y Python para suplir carencias de serialización y caching que normalmente existen en la versión Enterprise de $20k/año.

## Componentes

### 1. Nivel de Acceso de Datos (Data Sandboxing)

Se abandonó el enfoque de filtrar en la capa de aplicación (Metabase) para usar **PostgreSQL Row-Level Security**.

- Múltiples cuentas de PostgreSQL configuradas en Metabase.
- Cada cuenta se vincula a un "Grupo" en Metabase (Admin, SuperUser, User).
- PostgreSQL filtra la data devolviendo solo las tiendas/regiones permitidas para el usuario de BD.

### 2. Infraestructura Multi-Entorno y CD

- Scripts de Serialización en `/automation/serialization`: Extraen Dashboards y Questions de Metabase DEV vía API y los guardan en `/dashboards/{env}/*.yaml`.
- Estos archivos se versionan en Git provocando despliegues inmutables.
- Metabase PROD simplemente se recarga importando estos archivos pre-verificados desde la rama de GitHub (`migrate_env.py`).

### 3. Caché y Materialización (Fase 2)

- Replicando la heurística PRO de cache caching.
- Queries con un tiempo `T > 5s` capturadas por Python.
- Creación automatizada de `MVIEWs` en Postgres vía script de Python.
- Precalentamiento de dashboards ejecutando peticiones fantasma a la API cada madrugada.

### 4. Inteligencia Artificial Múltiple (AI Layer)

- Orquestado usando **FastAPI**.
- _Generación SQL_: **Gemini 1.5 Pro**. Realiza RAG contra los esquemas (`information_schema`).
- _Insights Categóricos_: **Gemini 1.5 Flash**. Devuelve narrativas de "Baja o Alza" extraídas del JSON emitido por una chart de Metabase.
- _Conversación Contextual_: **Grok**. Integrado en el sidebar de Metabase mediante una inyección en el fork frontend React. Soporte masivo de tokens.

### 5. Auditoría

- Logs almacenados temporalmente en bases de datos a través de `audit_triggers.sql`.
- Exportaciones en CSV mensuales a storage (S3/local).

## Decisiones Técnicas

- Se usó Nginx en lugar de Traefik por simplicidad para redireccionar el microservicio FastAPI en `/api/ai/` y el core de Metabase en `/`.
- `lw/flags.clj` y `lw/flags.ts` controlan si la UI de IA y la personalización de marca están activa.
