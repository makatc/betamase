# 🌐 Usando PostgreSQL 17 en Aiven con Betamase

> PostgreSQL 17 en Aiven es totalmente compatible. Mejor aún, Aiven es managed, así que no hay que mantener el servidor.

---

## ✅ Compatibilidad

| Aspecto | Status |
|--------|--------|
| PostgreSQL 17 | ✅ Compatible (mejor que 14+) |
| Aiven cloud | ✅ Funciona perfectamente |
| RLS (Row-Level Security) | ✅ Totalmente soportado |
| Auditoría | ✅ Sin problemas |
| Alertas Predictivas | ✅ Sin problemas |
| FastAPI connection | ✅ Funciona remotamente |
| Metabase connection | ✅ Funciona remotamente |

---

## 🔧 Configuración Necesaria (MUY SIMPLE)

### 1. Obtener Service URI de Aiven

En tu dashboard de Aiven:
1. Ir a tu servicio PostgreSQL 17
2. Click "Connection details"
3. Buscar **"Service URI"** (algo como `postgresql://user:pass@host:port/dbname`)
4. Copiar el URI completo (⚠️ Cambiar `?sslmode=require` al final)

Ejemplo:
```
postgresql://avnadmin:tu_contraseña@xxx-123.aivencloud.com:12345/defaultdb?sslmode=require
```

### 2. Configurar Variable de Entorno (¡Solo 1!)

**Para FastAPI (Middleware AI)**:

```bash
# En Terminal 3 — UNA SOLA VARIABLE
export DATABASE_URL="postgresql://avnadmin:tu_contraseña@xxx-123.aivencloud.com:12345/defaultdb?sslmode=require"

# Ejecutar el middleware
cd automation/ai/api && uvicorn main:app --port 8001 --reload
```

**Eso es todo.** El middleware automáticamente parseará el SERVICE URI.

### Alternativa: Variables Individuales (si prefieres)

Si no quieres usar el SERVICE URI, puedes seguir usando variables individuales:

```bash
export POSTGRES_DW_HOST="xxx-123.aivencloud.com"
export POSTGRES_DW_PORT="12345"
export POSTGRES_DW_NAME="defaultdb"
export POSTGRES_DW_USER="avnadmin"
export POSTGRES_DW_PASSWORD="tu_contraseña"

cd automation/ai/api && uvicorn main:app --port 8001 --reload
```

**El código soporta AMBAS formas.** Elige la que prefieras.

**Para Metabase**:

En Metabase, cuando agregues la BD:
```
Host: xxx-123.aivencloud.com
Port: 12345
Database: defaultdb
Username: avnadmin
Password: tu_contraseña
SSL Mode: require
```

### 3. Cómo Funciona Internamente

El archivo `automation/ai/api/models/schema_embeddings.py` automáticamente:

```python
# Detecta si tienes SERVICE URI (Aiven)
if os.getenv("DATABASE_URL") or os.getenv("POSTGRES_SERVICE_URI"):
    # Parsea el URI automáticamente
    parsed = urlparse(service_uri)
    DB_HOST = parsed.hostname
    DB_PORT = parsed.port
    # ... etc
else:
    # Fallback a variables individuales (local)
    DB_HOST = os.getenv("POSTGRES_DW_HOST", "localhost")
    # ... etc
```

**No hay que hacer nada.** Solo exporta `DATABASE_URL` y listo.

---

## 🚀 Ejecución con Aiven (Super Simple)

### Terminal 1 — Backend Metabase (sin cambios)
```bash
export LW_FEATURE_AI_SQL_GENERATION=true
export LW_FEATURE_AI_CHAT_WIDGET=true
export LW_FEATURE_AI_INSIGHTS=true

eval "$(mise activate bash)"
clojure -M:dev:drivers:drivers-dev:ee:ee-dev:dev-start --hot
```

### Terminal 2 — Frontend (sin cambios)
```bash
bun run build-hot
```

### Terminal 3 — FastAPI Middleware (Con Aiven SERVICE URI)
```bash
# UNA SOLA VARIABLE: El Service URI completo de Aiven
export DATABASE_URL="postgresql://avnadmin:tu_contraseña@xxx-123.aivencloud.com:12345/defaultdb?sslmode=require"

# AI API key
export GEMINI_API_KEY="AIza..."

# Ejecutar
cd /home/makatc/PROYECTOS/betamase/automation/ai/api
uvicorn main:app --host 0.0.0.0 --port 8001 --reload

# FastAPI automáticamente parsea el SERVICE URI y se conecta a Aiven ✅
```

**Eso es todo.** Una línea para la BD, una para API key. Fin.

---

## 📋 Verificación de Conexión

### Opción 1: Desde la CLI (Rápido)

```bash
# Copiar el SERVICE URI de Aiven y probarlo directamente
psql "postgresql://avnadmin:tu_contraseña@xxx-123.aivencloud.com:12345/defaultdb?sslmode=require" \
     -c "SELECT version();"

# Debería mostrar:
# PostgreSQL 17.x on ...
```

### Opción 2: Desde Python (Verificar con el middleware)

```bash
# Verificar que el middleware puede conectarse a Aiven
cd /home/makatc/PROYECTOS/betamase/automation/ai/api

export DATABASE_URL="postgresql://avnadmin:tu_contraseña@xxx-123.aivencloud.com:12345/defaultdb?sslmode=require"

python3 << 'EOF'
import os
from models.schema_embeddings import get_database_schema

schema = get_database_schema()
print("✅ Conexión exitosa!")
print(schema)  # Debería mostrar el schema de tu BD en Aiven
EOF
```

Si ves el schema de tu BD → ✅ Funcionando perfecto

### Desde Metabase

1. Abrir http://localhost:3000
2. Admin Panel → Databases → Add Database
3. PostgreSQL con credenciales de Aiven
4. Click "Save"
5. Si conecta correctamente, verás tus tablas

---

## 🔒 Seguridad con Aiven

### SSL/TLS (Recomendado)

Aiven requiere SSL. En `schema_embeddings.py` ya está soportado:

```python
conn = psycopg2.connect(
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASS if DB_PASS else None,
    sslmode='require'  # Automático con Aiven
)
```

Si psycopg2 da error de SSL, instala:
```bash
pip install psycopg2-binary
```

### Firewall

Aiven tiene firewall. Asegúrate de:
- ✅ Tu IP está en whitelist (si usas desde fuera)
- ✅ O acceso público configurado en Aiven
- ✅ O VPN configurada

---

## 📊 RLS en Aiven

Los scripts RLS funcionan igual en Aiven:

```bash
# Desde tu máquina local
psql -h tu-host-aiven.aivencloud.com \
     -p 12345 \
     -U avnadmin \
     -d defaultdb \
     < database/rls/01_create_roles.sql

# Luego los demás scripts
psql -h tu-host-aiven.aivencloud.com ... < database/rls/02_create_policies.sql
# ... etc
```

O usar el script automatizado (actualizado):

```bash
# Script version para Aiven
POSTGRES_DW_HOST="tu-host.aivencloud.com" \
POSTGRES_DW_PORT="12345" \
POSTGRES_DW_NAME="defaultdb" \
POSTGRES_DW_USER="avnadmin" \
POSTGRES_DW_PASSWORD="contraseña" \
bash scripts/setup-rls.sh
```

---

## ⚡ Ventajas de Usar Aiven

✅ **Managed Database**
- No hay que mantener el servidor
- Backups automáticos
- High availability incluido

✅ **PostgreSQL 17**
- Más rápido que versiones anteriores
- Mejor soporte para RLS
- Mejor performance en queries

✅ **Escalabilidad**
- Puedes aumentar RAM/CPU fácilmente
- Connection pooling si lo necesitas

✅ **Seguridad**
- SSL/TLS obligatorio
- Firewall configurado
- Cifrado en tránsito y reposo

---

## ⚠️ Consideraciones

### 1. Costos
- Aiven cobra por el servicio PostgreSQL
- Generalmente ~$20-50/mes para desarrollo
- Más caro que local pero menos mantenimiento

### 2. Latencia
- Si tu máquina está lejos del servidor Aiven, habrá latencia
- Para desarrollo local, puede notar pequeñas demoras
- En producción es aceptable

### 3. Límites de Conexiones
- Aiven limita el número de conexiones
- FastAPI + Metabase pueden usar varias
- Si ves errores "too many connections", aumenta en Aiven

### 4. Backups
- Aiven hace backups automáticos
- Pero tienes que hacer punto de restauración si necesitas

---

## 🔧 Troubleshooting

### Error: "connection refused"
```
Causa: Firewall de Aiven bloquea tu IP
Solución: Agregar tu IP en Aiven dashboard → Firewall
```

### Error: "SSL certificate verify failed"
```
Causa: psycopg2 no confía en certificado de Aiven
Solución:
  pip install psycopg2-binary --upgrade
  O usar sslmode='allow' en dev (no recomendado para prod)
```

### Error: "too many connections"
```
Causa: Metabase + FastAPI + otros = muchas conexiones
Solución:
  - Aumentar max_connections en Aiven
  - O usar connection pooling (PgBouncer)
```

### Lentitud en FastAPI
```
Causa: Latencia de red remota
Solución:
  - Cachear el schema_embeddings (no relectura cada vez)
  - O desplegar FastAPI más cerca del servidor BD
```

---

## 📝 Checklist para Aiven

- [ ] Obtener credenciales de Aiven
- [ ] Probar conexión desde CLI: `psql -h ... -c "SELECT 1;"`
- [ ] Configurar variables de entorno
- [ ] Ejecutar FastAPI con vars de Aiven
- [ ] Conectar BD en Metabase
- [ ] Verificar que puedes ver las tablas
- [ ] Ejecutar scripts RLS si necesitas
- [ ] Probar queries desde Metabase

---

## 🚀 Script Quick Start con Aiven (Service URI)

```bash
#!/bin/bash
# Guardar como /tmp/start-with-aiven.sh

# PASO 1: Pegar aquí el SERVICE URI de Aiven
AIVEN_SERVICE_URI="postgresql://avnadmin:tu_contraseña@xxx-123.aivencloud.com:12345/defaultdb?sslmode=require"

echo "Verificando conexión a Aiven con SERVICE URI..."
psql "$AIVEN_SERVICE_URI" -c "SELECT version();"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Conexión a Aiven OK"
    echo ""
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║           ABRE 3 TERMINALES Y COPIA ESTOS COMANDOS             ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo ""

    # Terminal 1: Backend
    echo "Terminal 1 — Backend Metabase:"
    echo "─────────────────────────────"
    echo "export LW_FEATURE_AI_SQL_GENERATION=true"
    echo "export LW_FEATURE_AI_CHAT_WIDGET=true"
    echo "export LW_FEATURE_AI_INSIGHTS=true"
    echo "eval \"\$(mise activate bash)\""
    echo "clojure -M:dev:drivers:drivers-dev:ee:ee-dev:dev-start --hot"
    echo ""

    # Terminal 2: Frontend
    echo "Terminal 2 — Frontend React:"
    echo "────────────────────────────"
    echo "cd /home/makatc/PROYECTOS/betamase"
    echo "bun run build-hot"
    echo ""

    # Terminal 3: FastAPI
    echo "Terminal 3 — FastAPI con Aiven:"
    echo "───────────────────────────────"
    echo "export DATABASE_URL=\"$AIVEN_SERVICE_URI\""
    echo "export GEMINI_API_KEY=\"AIza...\""
    echo "cd /home/makatc/PROYECTOS/betamase/automation/ai/api"
    echo "uvicorn main:app --host 0.0.0.0 --port 8001 --reload"
    echo ""
    echo "✅ Metabase en: http://localhost:3000"
    echo "✅ AI en: http://localhost:8001"
else
    echo "❌ No se puede conectar a Aiven"
    echo "Verifica que el SERVICE URI es correcto:"
    echo "  $AIVEN_SERVICE_URI"
    echo ""
    echo "Desde tu dashboard de Aiven:"
    echo "  1. Ir a tu servicio PostgreSQL"
    echo "  2. Connection details → Service URI"
    echo "  3. Copiar URI y reemplazarlo arriba"
fi
```

**Uso**:
```bash
# Editar el script y poner tu SERVICE URI
nano /tmp/start-with-aiven.sh
# Reemplazar: postgresql://avnadmin:tu_contraseña@xxx.aivencloud.com:12345/defaultdb...

# Ejecutar
bash /tmp/start-with-aiven.sh
```

---

## 📞 Si Necesitas Ayuda

1. Compartir detalles de Aiven (host, puerto, BD name)
2. Decirme qué error ves cuando intentas conectar
3. Te ayudo a ajustar `schema_embeddings.py` si es necesario

---

**Conclusión**: PostgreSQL 17 en Aiven funciona perfecto con Betamase. Solo necesitas exportar las credenciales de Aiven como variables de entorno. ✅
