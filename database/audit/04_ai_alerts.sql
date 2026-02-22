-- 04_ai_alerts.sql
-- Tabla de configuración para el Motor de Alertas Inteligentes (Predictivas/Prophet)

CREATE TABLE IF NOT EXISTS ai_alerts (
    alert_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,               -- Propietario de la alerta
    name VARCHAR(100) NOT NULL,
    target_table VARCHAR(100) NOT NULL, -- Tabla a monitorear
    time_column VARCHAR(100) NOT NULL,  -- Columna de fecha/tiempo
    value_column VARCHAR(100) NOT NULL, -- Métrica a predecir (ej: 'ventas')
    condition_nl TEXT,                  -- "Avisarme si las ventas caen más de 10%"
    target_webhook_url TEXT,            -- URL Slack/Email trigger
    is_active BOOLEAN DEFAULT TRUE,
    last_run TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_ai_alerts_active ON ai_alerts(is_active) WHERE is_active = TRUE;
