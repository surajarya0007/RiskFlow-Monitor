import json
from tornado.web import RequestHandler
from backend.db.base import get_pool


class BaseHandler(RequestHandler):
    def set_default_headers(self):
        self.set_header("Content-Type", "application/json")
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "content-type")
        self.set_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")

    def options(self, *args, **kwargs):
        self.set_status(204)
        self.finish()


class MarketLatestHandler(BaseHandler):
    async def get(self):
        pool = get_pool()
        if pool is None:
            self.set_status(503)
            self.write(json.dumps({"error": "database_unavailable"}))
            return

        try:
            async with pool.acquire() as conn:
                rows = await conn.fetch(
                    "SELECT DISTINCT ON (asset) asset, price_usd, latency_ms, request_status, created_at FROM market_data ORDER BY asset, created_at DESC"
                )
        except Exception as e:
            self.set_status(503)
            self.write(json.dumps({"error": "database_unavailable", "details": str(e)}))
            return

        data = {
            row["asset"]: {
                "price_usd": float(row["price_usd"]),
                "latency_ms": row["latency_ms"],
                "request_status": row["request_status"],
                "created_at": row["created_at"].isoformat(),
            }
            for row in rows
        }
        self.write(json.dumps({"data": data}, default=str))
