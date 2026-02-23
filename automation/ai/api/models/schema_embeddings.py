import psycopg2
from urllib.parse import urlparse
import os

# Soporte para 2 formas de conexión:
# 1. Service URI (Aiven): postgresql://user:pass@host:port/dbname
# 2. Variables individuales (Local): POSTGRES_DW_HOST, POSTGRES_DW_PORT, etc.

DB_SERVICE_URI = os.getenv("DATABASE_URL") or os.getenv("POSTGRES_SERVICE_URI")

if DB_SERVICE_URI:
    # Parsear Service URI de Aiven
    parsed = urlparse(DB_SERVICE_URI)
    DB_HOST = parsed.hostname
    DB_PORT = parsed.port or 5432
    DB_NAME = parsed.path.lstrip('/')
    DB_USER = parsed.username
    DB_PASS = parsed.password
else:
    # Variables individuales (para desarrollo local)
    DB_HOST = os.getenv("POSTGRES_DW_HOST", "localhost")
    DB_PORT = int(os.getenv("POSTGRES_DW_PORT", "5432"))
    DB_NAME = os.getenv("POSTGRES_DW_NAME", "betamase_data")
    DB_USER = os.getenv("POSTGRES_DW_USER", "postgres")
    DB_PASS = os.getenv("POSTGRES_DW_PASSWORD", "")

def get_database_schema():
    """
    Extracts the public schema of the target database to feed context to the LLM.
    Uses PostgreSQL information_schema.
    Returns a formatted string describing tables and columns.
    """
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS if DB_PASS else None
        )
        cur = conn.cursor()

        # Get all tables in public schema
        cur.execute("""
            SELECT table_name, column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = 'public'
            ORDER BY table_name, ordinal_position;
        """)

        rows = cur.fetchall()
        schema_dict = {}
        for r in rows:
            table, col, dtype = r
            if table not in schema_dict:
                schema_dict[table] = []
            schema_dict[table].append(f"{col} ({dtype})")

        cur.close()
        conn.close()

        # Limit to first 20 tables, 8 cols each to keep prompt small (avoid token rate limits)
        MAX_TABLES = 20
        MAX_COLS = 8
        schema_context = "Database Schema (top tables):\n"
        for i, (table, cols) in enumerate(schema_dict.items()):
            if i >= MAX_TABLES:
                schema_context += f"...and {len(schema_dict) - MAX_TABLES} more tables.\n"
                break
            schema_context += f"Table: {table}\nColumns: {', '.join(cols[:MAX_COLS])}\n\n"

        if not schema_dict:
            return "No public tables found. Using generic schema."

        return schema_context

    except Exception as e:
        print(f"Error fetching schema: {e}")
        return "Warning: Could not fetch live database schema. Assume generic standard tables like 'ventas', 'productos'."
