-- Instalación de extensión pg_cron, requiere PostgreSQL configurado global
-- CREATE EXTENSION pg_cron;

-- Refresh diario de vistes materializadas generadas por el script de análisis de Python
-- a las 3:00 AM.
-- SELECT cron.schedule('0 3 * * *', $$REFRESH MATERIALIZED VIEW mt_sales_slow_query_001$$);
-- SELECT cron.schedule('0 3 * * *', $$REFRESH MATERIALIZED VIEW mt_inventory_slow_query_009$$);
