import json
from tornado.web import RequestHandler
from backend.config import settings

class HealthHandler(RequestHandler):
    def set_default_headers(self):
        self.set_header("Content-Type", "application/json")
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "content-type")
        self.set_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")

    def options(self, *args, **kwargs):
        self.set_status(204)
        self.finish()

    async def get(self):
        self.write(json.dumps({
            "status": "ok",
            "backend": "GovernanceOps Platform",
            "debug": settings.DEBUG,
        }))
