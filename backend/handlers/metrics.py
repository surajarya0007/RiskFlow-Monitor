import json
from tornado.web import RequestHandler
from backend.services.metrics_service import fetch_dashboard_metrics

class MetricsHandler(RequestHandler):
    def set_default_headers(self):
        self.set_header("Content-Type", "application/json")
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "content-type")
        self.set_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")

    def options(self, *args, **kwargs):
        self.set_status(204)
        self.finish()

    async def get(self):
        metrics = await fetch_dashboard_metrics()
        self.write(json.dumps(metrics))
