# Extensión de Metabase Open Source v0.48.x con Funcionalidades Pro/Enterprise

## Contexto del Proyecto

Necesito extender Metabase Open Source v0.48.x para replicar funcionalidades que solo están disponibles en las versiones Pro y Enterprise (que cuestan $500-$20,000 anuales). El objetivo es implementar estas capacidades sobre la versión gratuita usando técnicas de ingeniería de software, automatización y modificación de código fuente.

## Stack Tecnológico
```yaml
Infraestructura:
  - Metabase OSS: v0.48.x (fork personalizado)
  - Database: PostgreSQL 14+
  - Containerization: Docker + Docker Compose
  - Proxy: Nginx (reverse proxy)

Automatización:
  - Python 3.11+
  - Bash scripts
  - Cron jobs
  - Git (versionado)

AI Integration:
  - Google Gemini API (gemini-1.5-pro para SQL, gemini-1.5-flash para insights)
  - Grok API (xAI) para chatbot conversacional
  - Langchain (orquestación)
  - ChromaDB (vector embeddings)
  - FastAPI (middleware AI)

Branding:
  - Primary Color: #0F766E (Teal clínico)
  - Secondary Color: #2563EB (Azul confianza)
  - Background: #F8FAFC (Gris claro)
  - Text: #0F172A (Slate oscuro)
  - Sidebar: #0B1220 (Azul/negro profundo)
```

## Requisitos de Seguridad (RLS - Row Level Security)

Implementar 3 niveles de acceso a datos:
1. **Admin**: Acceso total a todos los datos
2. **Super Users**: Lectura + escritura limitada en regiones específicas
3. **Users**: Solo lectura filtrada por región/departamento

Utilizar PostgreSQL Row-Level Security (RLS) nativo con políticas (CREATE POLICY) en lugar de implementarlo en la capa de aplicación. Crear 3 roles de base de datos y 3 conexiones separadas en Metabase mapeadas a cada grupo de usuarios.

## Entornos Requeridos

Crear 3 ambientes completamente separados:
- **Dev**: Desarrollo y testing (http://localhost:3000)
- **Staging**: Pre-producción (https://staging.metabase.tudominio.com)
- **Prod**: Producción (https://metabase.tudominio.com)

Cada ambiente debe tener su propia instancia de Metabase y base de datos PostgreSQL. Usar Nginx como reverse proxy con routing por subdominios.

## Funcionalidades a Implementar

### 1. Row & Column Level Security (RLS)
**Prioridad: CRÍTICA**

- Configurar PostgreSQL con políticas RLS para filtrar filas automáticamente según el usuario conectado
- Crear vistas SQL que proyecten solo columnas no confidenciales (Column-Level Security)
- Configurar 3 roles PostgreSQL: `admin_role`, `superuser_role`, `user_role`
- En Metabase OSS, crear 3 conexiones a la misma base de datos usando credenciales diferentes
- Mapear grupos de Metabase a las conexiones correspondientes
- Documentar el proceso en `docs/RLS_SETUP.md`

### 2. Serialización de Dashboards (Environment Management)
**Prioridad: CRÍTICA**

Metabase Pro tiene serialización nativa (export/import de dashboards a YAML). Replicar esto:

- Crear script Python `export_metabase.py` que use la API REST de Metabase (`/api/card`, `/api/dashboard`, `/api/collection`) para extraer todos los dashboards, preguntas y colecciones a archivos JSON/YAML
- Crear script Python `import_metabase.py` que reconstruya los dashboards en otra instancia, con lógica de remapeo de IDs (los IDs de bases de datos y colecciones difieren entre entornos)
- Estructura Git:
```
  dashboards/
  ├── dev/
  ├── staging/
  └── prod/
```
- Script `migrate_env.py` para migrar cambios: Dev → Staging → Prod
- Integrar con Git para versionado y rollback

### 3. Caché Avanzado y Pre-warming
**Prioridad: ALTA**

Metabase Pro tiene caché adaptativo y pre-calentamiento. Replicar con PostgreSQL + automatización:

- Crear script `analyze_slow_queries.py` que identifique queries que tardan >5 segundos
- Para queries lentas, generar automáticamente Vistas Materializadas en PostgreSQL
- Configurar `pg_cron` (extensión PostgreSQL) para refrescar vistas materializadas cada noche
- Crear script `prewarm_dashboards.py` que haga requests HTTP a URLs de dashboards críticos a las 5:00 AM (antes de que lleguen usuarios), forzando a Metabase a cachear resultados
- Configurar cron job para ejecutar pre-warming diariamente

### 4. White-labeling (Personalización de Marca)
**Prioridad: ALTA**

Metabase Pro permite personalizar logo, colores y eliminar "Powered by Metabase". Hacer fork del código:

- Fork del repositorio oficial de Metabase v0.48.x en GitHub
- Modificar archivos frontend (React):
  - `frontend/src/metabase/nav/components/AppBar.jsx` → Cambiar logo
  - `frontend/src/metabase/css/core/colors.css` → Variables de color
  - `resources/frontend_client/app/assets/img/logo.svg` → Reemplazar logo
  - `frontend/src/metabase/public/components/widgets/EmbedFrame.jsx` → Eliminar footer "Powered by Metabase"
- Modificar backend (Clojure):
  - `src/metabase/email/messages.clj` → Templates de emails personalizados
  - `resources/email/` → HTML templates con branding
- Crear `Dockerfile.custom` para build del fork
- Script `build_custom.sh` para compilar y generar imagen Docker personalizada
- Documentar proceso de merge de actualizaciones de seguridad desde upstream en `docs/FORK_MAINTENANCE.md`

### 5. Sistema de Auditoría (Audit Logs)
**Prioridad: MEDIA**

Metabase Enterprise tiene logs de auditoría. Implementar con triggers PostgreSQL:

- Crear tabla `audit_log` en la base de datos de aplicación de Metabase
- Implementar triggers PostgreSQL que registren:
  - Login/logout de usuarios
  - Cambios en permisos
  - Ejecución de queries (guardar SQL, usuario, timestamp)
  - Modificaciones de dashboards
- Crear dashboard en el propio Metabase que muestre:
  - Métricas de uso por grupo
  - Queries ejecutadas por usuario
  - Accesos fallidos
  - Timeline de actividad
- Script `generate_compliance_report.py` para exportar logs a CSV mensualmente
- Política de retención: 90 días

### 6. Integración de AI - SQL Generation
**Prioridad: ALTA**

Metabase Enterprise tiene "Metabot" (IA para SQL). Crear versión propia con Gemini/Grok:

**Backend (FastAPI):**
- API middleware en `/automation/ai/api/main.py`
- Endpoint `POST /api/ai/generate-sql`:
  - Input: Pregunta en lenguaje natural ("Muéstrame ventas del último trimestre por región")
  - Proceso:
    1. Usar Gemini-1.5-Pro para generar SQL
    2. Introspección del schema PostgreSQL (leer `information_schema`)
    3. Crear embeddings vectoriales de schemas con ChromaDB para context retrieval
    4. Validar SQL generado (prevenir SQL injection, verificar sintaxis)
  - Output: SQL query validado
- Integración con Langchain para orquestar llamadas a LLMs

**Frontend (Fork de Metabase):**
- Nuevo componente React: `frontend/src/metabase/ai/AIQueryButton.jsx`
- Botón "Ask AI" en el Query Builder de Metabase
- Al hacer click, abre modal con input de texto
- Envía request a `/api/ai/generate-sql`
- Inserta SQL generado en el editor

### 7. Integración de AI - Insights Automáticos
**Prioridad: MEDIA**

Análisis automático de datos en dashboards:

- Endpoint `POST /api/ai/insights`:
  - Input: Dashboard ID + datos del gráfico (JSON)
  - Proceso con Gemini-1.5-Flash (modelo rápido):
    - Detección de tendencias (subida/bajada)
    - Identificación de anomalías (outliers)
    - Generación de narrativas ("Las ventas cayeron 15% en marzo debido a...")
  - Output: Texto explicativo + nivel de confianza
- Tabla `ai_insights` para cachear insights generados
- Componente React `InsightsPanel.jsx` que muestra insights bajo cada gráfico

### 8. Integración de AI - Chatbot Conversacional
**Prioridad: MEDIA**

Chat interactivo con datos:

- Endpoint `POST /api/ai/chat`:
  - Input: Mensaje del usuario
  - Modelo: Grok (xAI) por su largo context window (128k tokens)
  - Funcionalidad:
    - "¿Cuál fue el producto más vendido este mes?" → Genera SQL, ejecuta, devuelve tabla
    - Mantiene memoria conversacional (seguimiento de contexto)
    - Puede generar gráficos on-the-fly
  - Integración con Langchain Memory para context retention
- Componente React `ChatWidget.jsx` en el sidebar de Metabase
- Streaming de respuestas (Server-Sent Events)
- Rate limiting: 100 requests/hora por usuario

### 9. Integración de AI - Alertas Inteligentes
**Prioridad: BAJA**

Alertas predictivas y contextuales:

- Script `ai_alert_engine.py` ejecutado cada 15 minutos (cron)
- Funcionalidad:
  - Detección de anomalías con Prophet (modelo time-series ligero)
  - Predicciones: "Stock de producto X bajará en 3 días"
  - NLP para configurar alertas: "Avisarme si las ventas caen más de 10%"
- Tabla `ai_alerts` con configuración de alertas
- Webhooks a Slack/Email cuando se dispara alerta
- Panel de configuración en Metabase (modificación fork)

## Estructura de Archivos Final
```
metabase-pro-oss/
├── docker/
│   ├── docker-compose.yml              # Orquestación base
│   ├── docker-compose.dev.yml          # Override Dev
│   ├── docker-compose.staging.yml      # Override Staging
│   ├── docker-compose.prod.yml         # Override Prod
│   └── nginx/
│       ├── nginx.conf                  # Reverse proxy config
│       └── ssl/                        # Certificados Let's Encrypt
│
├── metabase-fork/                      # Fork de Metabase v0.48.x
│   ├── frontend/src/metabase/
│   │   ├── ai/                         # Componentes AI (nuevos)
│   │   │   ├── AIQueryButton.jsx
│   │   │   ├── ChatWidget.jsx
│   │   │   └── InsightsPanel.jsx
│   │   ├── nav/components/AppBar.jsx   # Logo modificado
│   │   └── css/core/colors.css         # Colores personalizados
│   ├── src/metabase/email/             # Templates email
│   ├── Dockerfile.custom
│   └── build_custom.sh
│
├── database/
│   ├── rls/
│   │   ├── 01_create_roles.sql         # Admin, SuperUser, User
│   │   ├── 02_create_policies.sql      # RLS policies
│   │   └── 03_create_views.sql         # Column filtering
│   ├── materialized_views/
│   │   └── refresh_schedule.sql        # pg_cron jobs
│   └── audit/
│       ├── audit_log_table.sql
│       └── audit_triggers.sql
│
├── automation/
│   ├── serialization/
│   │   ├── export_metabase.py
│   │   ├── import_metabase.py
│   │   ├── migrate_env.py
│   │   └── requirements.txt
│   ├── cache/
│   │   ├── analyze_slow_queries.py
│   │   ├── prewarm_dashboards.py
│   │   └── crontab.txt
│   ├── ai/
│   │   ├── api/
│   │   │   ├── main.py                 # FastAPI app
│   │   │   ├── routers/
│   │   │   │   ├── sql_generation.py
│   │   │   │   ├── insights.py
│   │   │   │   └── chat.py
│   │   │   └── models/
│   │   │       ├── schema_embeddings.py
│   │   │       └── query_validator.py
│   │   ├── alerts/
│   │   │   └── ai_alert_engine.py
│   │   └── requirements.txt
│   └── audit/
│       └── generate_compliance_report.py
│
├── dashboards/                         # Git versionado
│   ├── dev/
│   ├── staging/
│   └── prod/
│
├── docs/
│   ├── ARCHITECTURE.md
│   ├── RLS_SETUP.md
│   ├── AI_INTEGRATION.md
│   ├── FORK_MAINTENANCE.md
│   └── DEPLOYMENT.md
│
├── .env.example                        # Template de variables
├── .gitignore
└── README.md
```

## Variables de Entorno Requeridas
```bash
# PostgreSQL
POSTGRES_METABASE_PASSWORD=<strong_password>
POSTGRES_DW_PASSWORD=<strong_password>
POSTGRES_DW_USER_ADMIN=admin_role
POSTGRES_DW_USER_SUPERUSER=superuser_role
POSTGRES_DW_USER_USER=user_role

# Metabase
MB_SITE_URL_DEV=http://localhost:3000
MB_SITE_URL_STAGING=https://staging.metabase.tudominio.com
MB_SITE_URL_PROD=https://metabase.tudominio.com

# AI APIs
GEMINI_API_KEY=AIza...
GROK_API_KEY=xai-...
AI_PRIMARY_MODEL=gemini-1.5-pro
AI_FAST_MODEL=gemini-1.5-flash
AI_CHAT_MODEL=grok-beta

# Branding
BRAND_PRIMARY_COLOR=#0F766E
BRAND_SECONDARY_COLOR=#2563EB
BRAND_BACKGROUND_COLOR=#F8FAFC
BRAND_TEXT_COLOR=#0F172A
BRAND_SIDEBAR_COLOR=#0B1220
```

## Restricciones y Consideraciones

1. **Licencia**: Metabase OSS está bajo AGPL v3. Si expones el fork modificado públicamente, debes publicar el código fuente.

2. **Mantenimiento**: El fork requiere merge manual de security patches del repositorio oficial de Metabase. Documentar proceso en `FORK_MAINTENANCE.md`.

3. **Seguridad**:
   - Validar TODA entrada de usuario antes de ejecutar SQL (prevenir injection)
   - Rate limiting en endpoints AI (100 req/hora por usuario)
   - Nunca exponer API keys en frontend

4. **Performance**:
   - Vistas materializadas solo para queries >5s de ejecución
   - Caché de embeddings vectoriales
   - Pre-warming solo de dashboards críticos (top 10 más usados)

5. **Costos AI**:
   - Gemini-1.5-Flash para tareas rápidas (más barato)
   - Gemini-1.5-Pro solo para SQL generation complejo
   - Cachear insights generados para evitar regeneración

## Entregables Esperados

Al finalizar, el sistema debe:

1. ✅ Levantar 3 entornos independientes (Dev/Staging/Prod) con `docker-compose up`
2. ✅ Segregar datos por grupo de usuarios usando RLS nativo de PostgreSQL
3. ✅ Permitir migrar dashboards entre entornos con comandos Git + scripts Python
4. ✅ Mostrar interfaz con branding personalizado (colores, logo, sin "Powered by Metabase")
5. ✅ Registrar todas las acciones de usuarios en tabla de auditoría
6. ✅ Generar SQL desde lenguaje natural con botón "Ask AI"
7. ✅ Mostrar insights automáticos bajo gráficos en dashboards
8. ✅ Permitir chat conversacional con datos empresariales
9. ✅ Precalentar caché de dashboards críticos automáticamente
10. ✅ Incluir documentación completa en `/docs`

## Criterios de Éxito

- Sistema funcional end-to-end sin necesidad de licencia Pro/Enterprise
- Costo total: $0 en licencias + costos de API AI (estimado $50-100/mes)
- Tiempo de respuesta de dashboards <2s (con caché)
- 100% de segregación de datos verificada con testing
- Fork mantenible con proceso documentado de merge de updates

## Prioridad de Implementación

**Fase 1 (Crítico - 4 semanas):**
- RLS con PostgreSQL
- Multi-entorno (Dev/Staging/Prod)
- Serialización de dashboards

**Fase 2 (Alto - 3 semanas):**
- Fork y white-labeling
- Caché y pre-warming
- Auditoría

**Fase 3 (Medio - 4 semanas):**
- AI SQL Generation
- AI Insights
- AI Chatbot

**Fase 4 (Opcional - 2 semanas):**
- AI Alertas predictivas
- Optimizaciones finales

---

**INSTRUCCIÓN PARA ANTIGRAVITY**: Implementa este sistema completo siguiendo las especificaciones técnicas. Prioriza las funcionalidades de Fase 1 y Fase 2. Genera código funcional, dockerfiles, scripts y documentación. El sistema debe estar listo para deployment en producción.
