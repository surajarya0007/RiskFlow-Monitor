from typing import Dict, Any, List, Optional
from backend.db.base import get_pool


async def create_alert(workflow_id: Optional[str], alert: Dict[str, Any]) -> Dict[str, Any]:
    pool = get_pool()
    async with pool.acquire() as connection:
        row = await connection.fetchrow(
            "INSERT INTO alerts (workflow_id, severity, message, category) VALUES ($1, $2, $3, $4) RETURNING id, workflow_id, severity, message, category, resolved, created_at",
            workflow_id,
            alert["severity"],
            alert["message"],
            alert["category"],
        )
    return dict(row)

async def fetch_alerts() -> List[Dict[str, Any]]:
    pool = get_pool()
    async with pool.acquire() as connection:
        rows = await connection.fetch("SELECT * FROM alerts ORDER BY created_at DESC LIMIT 100")
    return [dict(row) for row in rows]

async def acknowledge_alert(alert_id: str) -> bool:
    pool = get_pool()
    async with pool.acquire() as connection:
        result = await connection.execute("UPDATE alerts SET resolved = TRUE WHERE id = $1", alert_id)
    return result.endswith("1")
