from psycopg_pool import AsyncConnectionPool
from psycopg.rows import dict_row
# DB_URL = "postgresql://usuario:password@host:puerto/nameBD"
DB_URL = "postgresql://postgres:7294@localhost:5432/academia"
pool=AsyncConnectionPool(conninfo=DB_URL)
async def get_conexion():
    async with pool.connection() as conn:
        conn.row_factory = dict_row
        yield conn
        