-- 01_create_roles.sql
-- Creación de roles base para Row-Level Security en PostgreSQL

-- Role 1: Admin (Acceso total)
CREATE ROLE admin_role NOLOGIN;

-- Role 2: SuperUser (Acceso regional/departamental amplio)
CREATE ROLE superuser_role NOLOGIN;

-- Role 3: User (Acceso restrictivo a datos propios)
CREATE ROLE user_role NOLOGIN;

-- Asignar permisos básicos a las tablas del Data Warehouse (DW)
-- (Reemplazar 'public' con el schema específico si aplica)
GRANT USAGE ON SCHEMA public TO admin_role, superuser_role, user_role;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO admin_role;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO superuser_role;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO user_role;

-- Configurar default privileges para futuras tablas
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO admin_role, superuser_role, user_role;
