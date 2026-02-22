# Row-Level Security (RLS) en Metabase OSS

Este documento define la arquitectura para implementar seguridad a nivel de filas y columnas en Metabase Open Source, replicando la funcionalidad de Metabase Enterprise.

## Arquitectura

En Metabase Enterprise, el "Data Sandboxing" permite aplicar filtros a los usuarios basándose en sus atributos. En nuestra versión OSS, transferimos esta responsabilidad directamente al motor de base de datos subyacente (PostgreSQL) aprovechando el soporte nativo de RLS (Row-Level Security).

### Pasos de Implementación

1. **Creación de Roles en PostgreSQL**:
   Ejecutar `database/rls/01_create_roles.sql`. Esto crea `admin_role`, `superuser_role` y `user_role`.

2. **Habilitar RLS en Tablas**:
   Ejecutar `database/rls/02_create_policies.sql`. Habilita `ENABLE ROW LEVEL SECURITY` en las tablas sensibles y acopla políticas (`CREATE POLICY`) asociadas a cada rol.

3. **Vistas para Column-Level Security (CLS)**:
   Si deseas ocultar columnas específicas (como PII: emails, tarjetas), ejecuta `database/rls/03_create_views.sql`. Las vistas excluyen las columnas sensibles y se otorgan permisos a los roles limitados directamente sobre las vistas, revocando acceso a la tabla base.

### Configuración en Metabase

1. En el panel de Administración de Metabase, ir a **Bases de datos**.
2. Crear **3 conexiones separadas** apuntando a la misma base de datos, pero usando las 3 credenciales diferentes (una para el `admin_role`, otra para `superuser_role`, y otra para `user_role`).
   - `DB_Principal_Admin`
   - `DB_Principal_SuperUser`
   - `DB_Principal_User`
3. Ir a **Permisos** -> **Datos**.
4. Mapear los **Grupos de Metabase** a la base de datos correspondiente:
   - Grupo _Administradores_ -> Acceso total a `DB_Principal_Admin` (sin acceso a las otras).
   - Grupo _Gerentes_ -> Acceso total a `DB_Principal_SuperUser`.
   - Grupo _Operadores_ -> Acceso total a `DB_Principal_User`.

De esta forma, cuando un operador entra a Metabase y consulta los datos, Metabase utiliza el pool de conexiones de `user_role`. PostgreSQL evalúa la política RLS del rol `user_role` y filtra los datos de forma nativa e inviolable para el usuario.
