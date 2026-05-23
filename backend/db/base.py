import asyncio
import socket
import urllib.parse
import asyncpg
from asyncpg import PostgresError
from backend.config import settings
from backend.db.models import SCHEMA_SQL

pool = None

async def _wait_for_tcp(host: str, port: int, timeout: float = 30.0):
    deadline = asyncio.get_running_loop().time() + timeout
    while True:
        try:
            fut = asyncio.open_connection(host, port)
            reader, writer = await asyncio.wait_for(fut, timeout=2.0)
            writer.close()
            await writer.wait_closed()
            return
        except (OSError, asyncio.TimeoutError):
            if asyncio.get_running_loop().time() >= deadline:
                raise
            await asyncio.sleep(1.0)

async def init_db():
    global pool
    if pool is None:
        parsed = urllib.parse.urlparse(settings.DATABASE_URL)
        host = parsed.hostname or "localhost"
        port = parsed.port or 5432
        await _wait_for_tcp(host, port, timeout=30.0)

        retry_delay = 2
        retries = 15
        while retries > 0:
            try:
                pool = await asyncpg.create_pool(
                    settings.DATABASE_URL,
                    min_size=1,
                    max_size=5,
                )
                break
            except Exception:
                retries -= 1
                if retries <= 0:
                    raise
                await asyncio.sleep(retry_delay)

        async with pool.acquire() as connection:
            await connection.execute(SCHEMA_SQL)


def get_pool():
    if pool is None:
        raise RuntimeError("Database pool has not been initialized")
    return pool
