-- 03_create_views.sql
-- Column-Level Security (CLS)

-- Suponiendo que la tabla original es 'clientes_data'
-- CREATE TABLE clientes_data (
--   id INT PRIMARY KEY,
--   nombre VARCHAR(100),
--   email VARCHAR(100),
--   tarjeta_credito VARCHAR(20) -- Dato sensible PII
-- );

-- Para los usuarios no administradores (superuser y user), creamos una vista
-- que excluye la tarjeta de crédito.

CREATE VIEW vw_clientes_seguros AS
SELECT id, nombre, email
FROM clientes_data;

-- Damos permisos a los roles menores a la VISTA, no a la TABLA
GRANT SELECT ON vw_clientes_seguros TO superuser_role, user_role;

-- Revocar permisos de la tabla original para asegurarse de que no se la salten
REVOKE SELECT ON clientes_data FROM superuser_role, user_role;

-- Nota: Recordar conectar la base de datos de Metabase para los roles 'superuser' y 'user'
-- para que vean 'vw_clientes_seguros' en lugar de 'clientes_data'.
