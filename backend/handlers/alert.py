import json
from tornado.web import RequestHandler
from backend.services.alert_service import fetch_alerts, acknowledge_alert

class BaseHandler(RequestHandler):
    def set_default_headers(self):
        self.set_header("Content-Type", "application/json")
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "content-type")
        self.set_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")

    def options(self, *args, **kwargs):
        self.set_status(204)
        self.finish()

class AlertListHandler(BaseHandler):
    async def get(self):
        alerts = await fetch_alerts()
        self.write(json.dumps({"data": alerts}, default=str))

class AlertAcknowledgeHandler(BaseHandler):
    async def post(self):
        payload = json.loads(self.request.body.decode() or "{}")
        alert_id = payload.get("id")
        if not alert_id:
            self.set_status(400)
            self.write(json.dumps({"error": "alert id is required"}, default=str))
            return
        success = await acknowledge_alert(alert_id)
        if success:
            self.write(json.dumps({"status": "acknowledged"}, default=str))
        else:
            self.set_status(404)
            self.write(json.dumps({"error": "alert not found"}, default=str))
