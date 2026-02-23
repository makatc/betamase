# 📚 RLS Scripts Explicados

Esta guía describe exactamente qué hace cada script SQL y por qué es importante.

---

## 1️⃣ `database/rls/01_create_roles.sql`

**¿Qué hace?**
- Crea 3 roles (roles = usuarios especiales en PostgreSQL)
- Cada role tiene permisos diferentes

**Roles creados:**

```sql
CREATE ROLE admin_role        -- Acceso total a TODOS los datos
CREATE ROLE superuser_role    -- Acceso amplio (por región/departamento)
CREATE ROLE user_role         -- Acceso restrictivo (solo sus propios datos)
```

**Permisos otorgados:**
- Todos los roles pueden: `SELECT` (leer) de todas las tablas en schema `public`
- Admin también puede: `INSERT`, `UPDATE`, `DELETE`

**Conexión en Metabase:**
- Cada Metabase Group se conecta con un role diferente
- El frontend Metabase ejecuta queries como el rol del usuario

**Ejemplo de flujo:**
```
User "Juan" (Group: Users)
  → Conecta como role: user_role
  → Ejecuta: SELECT * FROM ventas
  → PostgreSQL filtra automáticamente (solo filas where vendedor_id = juan_id)
  → Juan ve 3 filas, Pedro ve otras 3 filas
```

---

## 2️⃣ `database/rls/02_create_policies.sql`

**¿Qué hace?**
- Crea las POLÍTICAS de seguridad Row-Level
- Define qué filas puede ver cada rol

**Requisitos:**
- Las tablas `ventas` y `clientes` deben existir
- Si no existen, los comandos son ignorados (no hay error)

**Políticas creadas:**

### Política 1: Admin (Ver todo)
```sql
CREATE POLICY admin_all_ventas ON ventas
    FOR ALL
    TO admin_role
    USING (true);  -- true = ve TODAS las filas
```

**Efecto:**
```
Admin: SELECT * FROM ventas
  → Retorna: 10,000 filas (todas)
```

### Política 2: SuperUser (Por región)
```sql
CREATE POLICY superuser_region_ventas ON ventas
    FOR SELECT
    TO superuser_role
    USING (region_id = current_setting('app.current_region', true)::int);
```

**Efecto:**
```
SuperUser: SELECT * FROM ventas
  → Si app.current_region = 1 (norte)
  → Retorna: 3,000 filas (solo region_id = 1)
```

**Nota:** Requiere que antes de la query se ejecute:
```sql
SET app.current_region = 1;
```

### Política 3: User (Solo sus datos)
```sql
CREATE POLICY user_own_ventas ON ventas
    FOR SELECT
    TO user_role
    USING (vendedor_id = current_setting('app.current_user_id', true)::int);
```

**Efecto:**
```
User: SELECT * FROM ventas
  → Si app.current_user_id = 42 (Juan)
  → Retorna: 50 filas (solo vendedor_id = 42)
```

**Nota:** Requiere que antes de la query se ejecute:
```sql
SET app.current_user_id = 42;
```

---

## 3️⃣ `database/rls/03_create_views.sql`

**¿Qué hace?**
- Crea VISTAS SQL que ocultan columnas sensibles
- **Column-Level Security** (no solo filas, sino columnas)

**Ejemplo de vista:**
```sql
CREATE VIEW ventas_public AS
    SELECT
        id,
        vendedor_id,
        region_id,
        amount,
        created_at
        -- ❌ Falta: salary (columnna sensible oculta)
        -- ❌ Falta: cost (información privada)
    FROM ventas;
```

**Efecto:**
```
Query: SELECT * FROM ventas_public
  → Retorna: Solo 5 columnas
  → Usuario NO ve: salary, cost, otras columnas ocultas
```

**Casos de uso:**
- Ocultar salarios de vendedores
- Ocultar márgenes de ganancia
- Ocultar datos de clientes VIP
- Ocultar información de costos

---

## 4️⃣ `database/audit/audit_log_table.sql`

**¿Qué hace?**
- Crea tabla `audit_log` para registrar TODAS las acciones en la BD

**Estructura de la tabla:**

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `audit_id` | SERIAL | ID único del registro (autoincremental) |
| `action_type` | VARCHAR(50) | Tipo de acción: LOGIN, LOGOUT, QUERY_RUN, UPDATE_DASHBOARD, etc |
| `user_id` | INT | ID del usuario en Metabase |
| `user_email` | VARCHAR(255) | Email del usuario |
| `target_entity` | VARCHAR(50) | Qué se cambió: report_dashboard, card, table, etc |
| `target_id` | INT | ID de la entidad que se modificó |
| `old_value` | JSONB | Valor anterior (en formato JSON) |
| `new_value` | JSONB | Valor nuevo (en formato JSON) |
| `raw_sql` | TEXT | Si fue una query SQL, guardar el SQL aquí |
| `created_at` | TIMESTAMP | Cuándo sucedió |

**Índices creados (para búsquedas rápidas):**
- `idx_audit_log_user` — Por usuario (¿Qué hizo Pedro?)
- `idx_audit_log_action` — Por tipo de acción (¿Todos los LOGIN?)
- `idx_audit_log_created_at` — Por fecha (¿Qué pasó ayer?)

**Ejemplo de registros:**
```
audit_id | action_type   | user_id | user_email        | created_at
---------|---------------|---------|-------------------|-------------------
1        | LOGIN         | 42      | juan@empresa.com  | 2026-02-22 08:00
2        | QUERY_RUN     | 42      | juan@empresa.com  | 2026-02-22 08:05
3        | UPDATE_DASH   | 42      | juan@empresa.com  | 2026-02-22 08:10
4        | LOGOUT        | 42      | juan@empresa.com  | 2026-02-22 17:00
```

---

## 5️⃣ `database/audit/audit_triggers.sql`

**¿Qué hace?**
- Crea TRIGGERS (funciones automáticas) que registran cambios en `audit_log`
- Cada vez que algo cambia en la BD, se registra automáticamente

**Flujo:**
```
User ejecuta: UPDATE ventas SET amount = 2000 WHERE id = 1
  ↓
PostgreSQL detecta el cambio
  ↓
TRIGGER se activa automáticamente
  ↓
Inserta registro en audit_log:
  action_type: UPDATE
  user_id: 42
  target_entity: ventas
  target_id: 1
  old_value: {"amount": 1500}
  new_value: {"amount": 2000}
  created_at: NOW()
```

**Tipos de cambios registrados:**
- `INSERT` (nuevo registro)
- `UPDATE` (cambio de datos)
- `DELETE` (eliminación)

**Para qué sirve:**
- **Compliance**: "¿Quién cambió el precio de X?"
- **Auditoría**: Historial completo de cambios
- **Debugging**: "¿Cuándo se rompió el dashboard?"
- **Investigaciones**: "¿Quién accedió a datos de Juan?"

---

## 6️⃣ `database/audit/04_ai_alerts.sql`

**¿Qué hace?**
- Crea tablas para guardar reglas de alertas predictivas
- Registra cuándo se disparan las alertas

**Tablas creadas:**

### Tabla 1: `ai_alerts` (Configuración)
```sql
CREATE TABLE ai_alerts (
    alert_id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    description TEXT,
    alert_type VARCHAR(50),  -- ej: ANOMALY, THRESHOLD, PREDICTION
    condition_nl TEXT,        -- Condición en lenguaje natural
    condition_sql TEXT,       -- Condición en SQL
    enabled BOOLEAN DEFAULT true,
    created_at TIMESTAMP
);
```

**Ejemplos de alertas:**
```
1. name: "Ventas caen"
   condition_nl: "Si ventas caen >20% en una semana"

2. name: "Cliente grande inactivo"
   condition_nl: "Si cliente con >$100k en ventas sin pedidos hace 30 días"

3. name: "Predicción stock"
   condition_nl: "Si se predice que el stock de X será 0 en 5 días"
```

### Tabla 2: `alert_notifications` (Historial)
```sql
CREATE TABLE alert_notifications (
    notification_id SERIAL PRIMARY KEY,
    alert_id INT,          -- Referencia a la alerta
    triggered_at TIMESTAMP, -- Cuándo se disparó
    condition_met BOOLEAN,  -- ¿Se cumplió la condición?
    value DECIMAL,          -- Valor que activó la alerta
    message TEXT,           -- Mensaje de alerta
    sent_to VARCHAR(255),   -- Email/Slack/etc a donde se envió
    webhook_response TEXT   -- Respuesta del webhook
);
```

**Flujo de alertas:**
```
1. El script ai_alert_engine.py se ejecuta cada 15 minutos
2. Lee todas las alertas habilitadas de la tabla ai_alerts
3. Evalúa cada condición usando Gemini + Prophet
4. Si se cumple, inserta en alert_notifications
5. Envía webhook a Slack/Email/etc
```

---

## 🎯 Resumen Visual

```
┌─────────────────────────────────────────────────────────────┐
│                      PostgreSQL BD                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Roles (01_create_roles.sql)                               │
│  ├── admin_role        (acceso total)                      │
│  ├── superuser_role    (acceso regional)                   │
│  └── user_role         (solo sus datos)                    │
│                                                             │
│  RLS Policies (02_create_policies.sql)                     │
│  ├── admin_all_ventas  (ve todas filas)                    │
│  ├── superuser_region  (filtra por region_id)             │
│  └── user_own          (filtra por vendedor_id)           │
│                                                             │
│  Views (03_create_views.sql)                               │
│  ├── ventas_public     (sin columnas sensibles)            │
│  └── clientes_public   (sin emails privados)              │
│                                                             │
│  Audit (audit_log_table.sql)                               │
│  ├── audit_log         (registro de acciones)              │
│  └── Índices (3 para búsquedas rápidas)                   │
│                                                             │
│  Triggers (audit_triggers.sql)                             │
│  └── Registran cambios automáticamente                     │
│                                                             │
│  Alerts (04_ai_alerts.sql)                                 │
│  ├── ai_alerts         (definición de alertas)             │
│  └── alert_notif.      (historial de disparos)            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Ejemplo End-to-End

**Escenario**: Juan (User Role) y María (SuperUser Role) usan Metabase

### Paso 1: Login
```
Juan → Metabase Login
  Metabase conecta a BD como role: user_role
  (Set variable: app.current_user_id = juan_id)

María → Metabase Login
  Metabase conecta a BD como role: superuser_role
  (Set variable: app.current_region = norte)
```

### Paso 2: Juan ejecuta query
```
Juan: SELECT * FROM ventas
PostgreSQL aplica política user_own_ventas:
  WHERE vendedor_id = juan_id

Juan ve: 50 filas (solo sus ventas)
Audit log registra:
  action_type: QUERY_RUN
  user_id: juan_id
```

### Paso 3: María ejecuta misma query
```
María: SELECT * FROM ventas
PostgreSQL aplica política superuser_region_ventas:
  WHERE region_id = norte

María ve: 3,000 filas (toda su región)
Audit log registra:
  action_type: QUERY_RUN
  user_id: maria_id
```

### Paso 4: Juan intenta acceder a vista privada
```
Juan: SELECT * FROM ventas_public
  (No puede ver salarios ni márgenes)

PostgreSQL: Vista oculta esas columnas

Juan ve: 5 columnas (id, vendedor_id, region_id, amount, created_at)
         ❌ No ve: salary, cost, ...
```

---

## 🚀 Próximos Pasos

1. **Ejecutar los scripts**: Usar `scripts/setup-rls.sh`
2. **Crear datos de prueba**: Tablas `ventas` y `clientes` con datos reales
3. **Conectar en Metabase**: Admin Panel → Databases
4. **Probar con diferentes roles**: Verás datos filtrados automáticamente
5. **Monitorear auditoría**: Ver `SELECT * FROM audit_log`
6. **Configurar alertas**: Usar la tabla `ai_alerts` desde Metabase

---

**Para más detalles, revisa los archivos SQL en `database/rls/` y `database/audit/`**
