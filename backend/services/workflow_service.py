from typing import Optional, Dict, Any, List
import json
from backend.db.base import get_pool

async def create_workflow(payload: Dict[str, Any]) -> Dict[str, Any]:
    pool = get_pool()
    query = """
        INSERT INTO workflows (name, status, type, latency_ms, metadata)
        VALUES ($1, $2, $3, $4, $5)
        RETURNING id, name, status, type, created_at, updated_at, latency_ms, metadata
    """
    async with pool.acquire() as connection:
        row = await connection.fetchrow(
            query,
            payload["name"],
            payload.get("status", "running"),
            payload["type"],
            payload.get("latency_ms", 0),
            json.dumps(payload.get("metadata", {})),
        )
    return dict(row)

async def fetch_workflows() -> List[Dict[str, Any]]:
    pool = get_pool()
    async with pool.acquire() as connection:
        rows = await connection.fetch("SELECT * FROM workflows ORDER BY created_at DESC LIMIT 10")
    return [dict(row) for row in rows]

async def fetch_workflow(workflow_id: str) -> Optional[Dict[str, Any]]:
    pool = get_pool()
    async with pool.acquire() as connection:
        row = await connection.fetchrow("SELECT * FROM workflows WHERE id = $1", workflow_id)
    return dict(row) if row else None
