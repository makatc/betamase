import psycopg2
import os

DB_HOST = os.getenv("POSTGRES_DW_HOST", "localhost")
DB_NAME = os.getenv("POSTGRES_DW_NAME", "postgres")
DB_USER = os.getenv("POSTGRES_DW_USER_ADMIN", "admin_role")
DB_PASS = os.getenv("POSTGRES_DW_PASSWORD", "changeme")

def get_slow_queries():
    conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)
    cur = conn.cursor()
    # Usando pg_stat_statements (DEBE ESTAR HABILITADO)
    cur.execute("""
        SELECT query, mean_exec_time, calls, queryid
        FROM pg_stat_statements
        WHERE mean_exec_time > 5000 -- más de 5000 ms = 5 seg
        ORDER BY mean_exec_time DESC
        LIMIT 10;
    """)
    rows = cur.fetchall()

    for r in rows:
        print(f"QUERY LENTA (+{int(r[1])}ms): {r[0][:100]}...")
        # Aquí crearíamos via programación el `CREATE MATERIALIZED VIEW mview_{query_id} AS {query}`

    cur.close()
    conn.close()

if __name__ == "__main__":
    get_slow_queries()
