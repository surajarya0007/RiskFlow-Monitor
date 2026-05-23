from typing import Dict, Any, List
import json
from backend.db.base import get_pool

async def create_log(entry: Dict[str, Any]) -> Dict[str, Any]:
    pool = get_pool()
    async with pool.acquire() as connection:
        row = await connection.fetchrow(
            "INSERT INTO logs (workflow_id, event_type, metadata) VALUES ($1, $2, $3) RETURNING id, workflow_id, event_type, metadata, timestamp",
            entry.get("workflow_id"),
            entry["event_type"],
            json.dumps(entry.get("metadata", {})),
        )
    return dict(row)

async def fetch_logs() -> List[Dict[str, Any]]:
    pool = get_pool()
    async with pool.acquire() as connection:
        rows = await connection.fetch("SELECT * FROM logs ORDER BY timestamp DESC LIMIT 200")
    return [dict(row) for row in rows]
