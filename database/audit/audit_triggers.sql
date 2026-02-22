-- Ejemplo de triggers que inyectan JSON de cambios a audit_log

CREATE OR REPLACE FUNCTION log_dashboard_changes()
RETURNS TRIGGER AS $$
BEGIN
    IF (TG_OP = 'UPDATE') THEN
        INSERT INTO audit_log (action_type, target_entity, target_id, old_value, new_value)
        VALUES (
            'UPDATE_DASHBOARD',
            'report_dashboard',
            NEW.id,
            row_to_json(OLD),
            row_to_json(NEW)
        );
        RETURN NEW;
    ELSIF (TG_OP = 'INSERT') THEN
         -- Implementación
         RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Habilitar este log sobre la tabla core de Metabase de dashboards
-- NOTA: debe usarse en la BDD AppDB donde se guardan las configs de Metabase.
-- TRIGGER TEMPLATE:
-- CREATE TRIGGER trigger_dashboard_audit AFTER INSERT OR UPDATE ON report_dashboard FOR EACH ROW EXECUTE PROCEDURE log_dashboard_changes();
