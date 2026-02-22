-- 02_create_policies.sql
-- Políticas de Row-Level Security (RLS)

-- Activar RLS en una tabla de ejemplo (e.g., 'ventas' y 'clientes')
-- ALTER TABLE ventas ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE clientes ENABLE ROW LEVEL SECURITY;

-- Política para Admin: Puede ver todo
CREATE POLICY admin_all_ventas ON ventas
    FOR ALL
    TO admin_role
    USING (true);

-- Política para SuperUser: Puede ver datos de todas las regiones permitidas (ejemplo usando un tenant_id o region_id)
-- Supongamos que current_setting('request.jwt.claim.region', true) trae la región del usuario (si usamos middleware JWT)
-- O podemos filtrar usando otra tabla de mapeo usuario -> region
CREATE POLICY superuser_region_ventas ON ventas
    FOR SELECT
    TO superuser_role
    USING (region_id = current_setting('app.current_region', true)::int);

-- Política para User: Solo puede ver sus propias ventas o las de su departamento
CREATE POLICY user_own_ventas ON ventas
    FOR SELECT
    TO user_role
    USING (vendedor_id = current_setting('app.current_user_id', true)::int);

-- Nota: En Metabase, configuraremos el 'Connection Impersonation' o ejecutaremos
-- un SET LOCAL app.current_user_id = 'X' antes de las queries de Metabase si usamos session variables,
-- pero lo más simple es usar cuentas de BD distintas (admin_role, superuser_role, user_role)
-- y hacer vistas/políticas atadas a CURRENT_USER.
