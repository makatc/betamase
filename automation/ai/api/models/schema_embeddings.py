import psycopg2
import os

DB_HOST = os.getenv("POSTGRES_DW_HOST", "metabase-db")
DB_NAME = os.getenv("POSTGRES_DW_NAME", "metabaseappdb")
DB_USER = os.getenv("POSTGRES_DW_USER_ADMIN", "metabase_user")
DB_PASS = os.getenv("POSTGRES_DW_PASSWORD", "metabase_password")

def get_database_schema():
    """
    Extracts the public schema of the target database to feed context to the LLM.
    Uses PostgreSQL information_schema.
    Returns a formatted string describing tables and columns.
    """
    try:
        conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)
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

        # Format into a readable prompt string
        schema_context = "Database Schema:\n"
        for table, cols in schema_dict.items():
            schema_context += f"Table: {table}\nColumns: {', '.join(cols)}\n\n"

        if not schema_dict:
            return "No public tables found in the database. Please ensure the target database has data."

        return schema_context

    except Exception as e:
        print(f"Error fetching schema: {e}")
        return "Warning: Could not fetch live database schema. Assume generic standard tables like 'ventas', 'productos'."
