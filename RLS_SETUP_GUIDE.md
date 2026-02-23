# 🔐 Row-Level Security (RLS) — Guía de Configuración

> **Nota**: Este proceso requiere que PostgreSQL esté corriendo y que tengas acceso con usuario `postgres`.

---

## 📋 Requisitos

```bash
# Verificar que PostgreSQL está corriendo
psql --version

# Verificar que puedes conectarte
psql -U postgres -c "SELECT version();"
```

Si ves errores, instala PostgreSQL primero:
```bash
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# macOS
brew install postgresql

# Luego inicia el servicio
sudo systemctl start postgresql  # Linux
brew services start postgresql    # macOS
```

---

## 🔧 Ejecución de Scripts RLS (En Orden)

### Paso 1: Crear la Base de Datos

```bash
# Crear BD para datos reales (si no existe)
psql -U postgres -c "CREATE DATABASE betamase_data;"

# Verificar que fue creada
psql -U postgres -l | grep betamase_data
```

### Paso 2: Crear los Roles de Seguridad

```bash
psql -U postgres -d betamase_data < /home/makatc/PROYECTOS/betamase/database/rls/01_create_roles.sql
```

**Output esperado**:
```
CREATE ROLE
CREATE ROLE
CREATE ROLE
GRANT
GRANT
GRANT
GRANT
ALTER DEFAULT PRIVILEGES
```

**¿Qué hace?**
- Crea 3 roles: `admin_role`, `superuser_role`, `user_role`
- Otorga permisos básicos de SELECT en todas las tablas

### Paso 3: Crear Políticas de Seguridad

```bash
psql -U postgres -d betamase_data < /home/makatc/PROYECTOS/betamase/database/rls/02_create_policies.sql
```

**Output esperado**:
```
ALTER TABLE
ALTER TABLE
CREATE POLICY
CREATE POLICY
CREATE POLICY
```

**¿Qué hace?**
- Habilita RLS en tablas `ventas` y `clientes`
- **Admin**: Puede ver TODAS las filas
- **SuperUser**: Solo ve datos de su región (via `app.current_region`)
- **User**: Solo ve sus propias ventas (via `app.current_user_id`)

### Paso 4: Crear Vistas de Seguridad (Column-Level)

```bash
psql -U postgres -d betamase_data < /home/makatc/PROYECTOS/betamase/database/rls/03_create_views.sql
```

**¿Qué hace?**
- Crea vistas SQL que ocultan columnas sensibles (ej: salarios, info privada)

### Paso 5: Crear Tabla de Auditoría

```bash
psql -U postgres -d betamase_data < /home/makatc/PROYECTOS/betamase/database/audit/audit_log_table.sql
```

**Output esperado**:
```
CREATE TABLE
CREATE INDEX
CREATE INDEX
CREATE INDEX
```

**¿Qué hace?**
- Crea tabla `audit_log` para registrar TODAS las acciones
- 3 índices para búsquedas rápidas

### Paso 6: Crear Triggers de Auditoría

```bash
psql -U postgres -d betamase_data < /home/makatc/PROYECTOS/betamase/database/audit/audit_triggers.sql
```

**¿Qué hace?**
- Triggers que registran automáticamente cambios en tablas monitoreadas

### Paso 7: Configurar Alertas Predictivas

```bash
psql -U postgres -d betamase_data < /home/makatc/PROYECTOS/betamase/database/audit/04_ai_alerts.sql
```

**¿Qué hace?**
- Tabla `ai_alerts` para guardar reglas de alertas
- Tabla `alert_notifications` para historial de alertas disparadas

---

## ✅ Script Automatizado (All-in-One)

Si prefieres ejecutar TODO de una vez:

```bash
#!/bin/bash
# Guardar como /tmp/setup_rls.sh y ejecutar: bash /tmp/setup_rls.sh

DB_NAME="betamase_data"
REPO_PATH="/home/makatc/PROYECTOS/betamase"

echo "🔐 Configurando RLS en PostgreSQL..."

# Crear BD
psql -U postgres -c "CREATE DATABASE $DB_NAME;" 2>/dev/null || true

# Ejecutar scripts en orden
echo "1️⃣  Creando roles..."
psql -U postgres -d $DB_NAME < $REPO_PATH/database/rls/01_create_roles.sql

echo "2️⃣  Creando políticas..."
psql -U postgres -d $DB_NAME < $REPO_PATH/database/rls/02_create_policies.sql

echo "3️⃣  Creando vistas..."
psql -U postgres -d $DB_NAME < $REPO_PATH/database/rls/03_create_views.sql

echo "4️⃣  Creando tabla de auditoría..."
psql -U postgres -d $DB_NAME < $REPO_PATH/database/audit/audit_log_table.sql

echo "5️⃣  Creando triggers..."
psql -U postgres -d $DB_NAME < $REPO_PATH/database/audit/audit_triggers.sql

echo "6️⃣  Configurando alertas..."
psql -U postgres -d $DB_NAME < $REPO_PATH/database/audit/04_ai_alerts.sql

echo "✅ RLS configurado exitosamente!"
echo ""
echo "Próximo paso: Conectar esta BD en Metabase"
echo "  1. Abrir http://localhost:3000"
echo "  2. Admin Panel → Databases → Add Database"
echo "  3. PostgreSQL con host: localhost, database: $DB_NAME"
```

---

## 🔍 Verificación de RLS

Después de ejecutar los scripts, verifica que todo esté correcto:

```bash
# Verificar que los roles existen
psql -U postgres -d betamase_data -c "\du" | grep -E "admin_role|superuser_role|user_role"

# Verificar que RLS está habilitado en tablas
psql -U postgres -d betamase_data -c "SELECT tablename FROM pg_tables WHERE schemaname='public';"

# Verificar que audit_log existe
psql -U postgres -d betamase_data -c "\dt audit_log"

# Verificar que ai_alerts existe
psql -U postgres -d betamase_data -c "\dt ai_alerts"
```

---

## 📊 Entendiendo RLS

### Row-Level Security (RLS)
- **Filtra filas** automáticamente según el usuario
- Ejemplo: User con role `user_role` ve SOLO sus propias ventas
- Implementado en la BD, NO en la aplicación (más seguro)

### Column-Level Security
- **Oculta columnas** en vistas SQL
- Ejemplo: Vista `ventas_public` sin columna `salary`

### Auditoría
- Tabla `audit_log` registra TODAS las acciones
- Quién hizo qué, cuándo, en qué tabla

### Alertas Predictivas
- Tabla `ai_alerts` para configurar reglas
- Ej: "Alertarme si las ventas caen >20%"

---

## ⚙️ Configuración en Metabase

Una vez que los scripts se hayan ejecutado:

### 1. Conectar la BD en Metabase

```
http://localhost:3000
→ Admin Panel (engranaje)
→ Settings → Databases
→ Add Database
```

Usar estos valores:
```
Database Type: PostgreSQL
Host: localhost
Port: 5432
Database Name: betamase_data
Username: postgres
Password: (dejar vacío o tu contraseña)
```

Click "Save"

### 2. Crear Conexiones por Rol (Opcional)

Para aprovechar RLS, puedes crear 3 conexiones diferentes:

**Conexión 1 — Admin**:
- Database: `betamase_data`
- Username: `admin_role` (o usuario conectado como admin_role)

**Conexión 2 — SuperUser**:
- Database: `betamase_data`
- Username: `superuser_role`

**Conexión 3 — User**:
- Database: `betamase_data`
- Username: `user_role`

Luego mapear cada Metabase Group a su correspondiente conexión.

### 3. Probar RLS

Crear una query simple:
```sql
SELECT * FROM ventas LIMIT 5;
```

Si conconectas como `user_role`, verás SOLO las filas que el usuario tiene permiso de ver (según las políticas RLS).

---

## 🚨 Troubleshooting

### Error: "permission denied for schema public"

```sql
-- Otorgar permisos al usuario específico
GRANT USAGE ON SCHEMA public TO postgres;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO postgres;
```

### Error: "table ventas does not exist"

Los scripts asumen que existen tablas `ventas` y `clientes`. Si no existen, crea ejemplos:

```bash
psql -U postgres -d betamase_data << 'EOF'

CREATE TABLE ventas (
    id SERIAL PRIMARY KEY,
    vendedor_id INT,
    region_id INT,
    amount DECIMAL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE clientes (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    region_id INT,
    email VARCHAR(255)
);

INSERT INTO ventas (vendedor_id, region_id, amount) VALUES
    (1, 1, 1000.00),
    (2, 2, 2000.00),
    (1, 1, 500.00);

EOF
```

### Error: "role 'user_role' already exists"

Los scripts son idempotentes pero si ves este error, intenta:

```bash
psql -U postgres -d betamase_data -c "DROP ROLE IF EXISTS admin_role, superuser_role, user_role;"
```

Luego vuelve a correr los scripts.

---

## 📝 Próximos Pasos

1. ✅ **RLS en PostgreSQL** (Este paso)
2. ⏳ **Conectar BD en Metabase**
3. ⏳ **Crear queries/dashboards** usando datos con RLS
4. ⏳ **Probar que RLS filtra correctamente**

---

**¿Necesitas ayuda?** Revisa los scripts en `database/rls/` y `database/audit/`.
