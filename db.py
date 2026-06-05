"""PostgreSQL + pgvector 連線與 schema。

連的是 docker-compose.yml 起的 Postgres（pgvector/pgvector:pg17）。
連線參數可用 .env 覆寫，預設值對應 docker-compose.yml。
"""
import os
import psycopg
from pgvector.psycopg import register_vector

DSN = (
    f"host={os.environ.get('PGHOST','localhost')} "
    f"port={os.environ.get('PGPORT','5433')} "
    f"dbname={os.environ.get('PGDATABASE','ragdemo')} "
    f"user={os.environ.get('PGUSER','rag')} "
    f"password={os.environ.get('PGPASSWORD','ragpw')}"
)


def get_conn():
    conn = psycopg.connect(DSN, connect_timeout=4)
    conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
    register_vector(conn)
    return conn


def init_schema(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS chunks (
            id          SERIAL PRIMARY KEY,
            source      TEXT NOT NULL,
            chunk_index INT  NOT NULL,
            content     TEXT NOT NULL,
            embedding   vector(1536)
        )
    """)
    conn.commit()


def db_ready() -> bool:
    try:
        with get_conn() as c:
            c.execute("SELECT 1")
        return True
    except Exception:
        return False
