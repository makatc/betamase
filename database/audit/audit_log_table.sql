-- Tabla maestra para registro de auditoría.
-- En Enterprise se usa para retener los cambios de entidades

CREATE TABLE IF NOT EXISTS audit_log (
    audit_id SERIAL PRIMARY KEY,
    action_type VARCHAR(50) NOT NULL, -- Ej: LOGIN, LOGOUT, QUERY_RUN, UPDATE_DASHBOARD
    user_id INT, -- Referencia al ID real en core_user de Metabase
    user_email VARCHAR(255),
    target_entity VARCHAR(50), -- Nombre de la tabla de metabase ej 'report_dashboard'
    target_id INT,
    old_value JSONB,
    new_value JSONB,
    raw_sql TEXT, -- Utilizado cuando guardamos sentencias
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_log_user ON audit_log(user_id);
CREATE INDEX idx_audit_log_action ON audit_log(action_type);
CREATE INDEX idx_audit_log_created_at ON audit_log(created_at);
