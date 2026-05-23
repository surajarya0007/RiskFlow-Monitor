import json
from tornado.web import RequestHandler
from backend.services.log_service import fetch_logs

class BaseHandler(RequestHandler):
    def set_default_headers(self):
        self.set_header("Content-Type", "application/json")
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "content-type")
        self.set_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")

    def options(self, *args, **kwargs):
        self.set_status(204)
        self.finish()

class LogsHandler(BaseHandler):
    async def get(self):
        logs = await fetch_logs()
        self.write(json.dumps({"data": logs}, default=str))
