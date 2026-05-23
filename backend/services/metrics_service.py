from typing import Dict, Any
from backend.db.base import get_pool

async def fetch_dashboard_metrics() -> Dict[str, Any]:
    pool = get_pool()
    async with pool.acquire() as connection:
        workflow_count = await connection.fetchval("SELECT count(*) FROM workflows")
        active_alerts = await connection.fetchval("SELECT count(*) FROM alerts WHERE resolved = FALSE")
        avg_latency = await connection.fetchval("SELECT avg(latency_ms) FROM workflows")
    return {
        "workflow_count": workflow_count or 0,
        "active_alerts": active_alerts or 0,
        "average_latency_ms": int(avg_latency or 0),
    }
