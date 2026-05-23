import json
import logging
from tornado.web import RequestHandler
from backend.utils.validation import validate_workflow_payload, generate_alerts
from backend.services.workflow_service import create_workflow, fetch_workflows, fetch_workflow
from backend.services.alert_service import create_alert
from backend.services.log_service import create_log
from backend.websocket.manager import manager

logger = logging.getLogger(__name__)

class BaseHandler(RequestHandler):
    def set_default_headers(self):
        self.set_header("Content-Type", "application/json")
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "content-type")
        self.set_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")

    def options(self, *args, **kwargs):
        self.set_status(204)
        self.finish()

class WorkflowListHandler(BaseHandler):
    async def get(self):
        workflows = await fetch_workflows()
        self.write(json.dumps({"data": workflows}, default=str))

    async def post(self):
        payload = json.loads(self.request.body.decode() or "{}")
        valid, errors = validate_workflow_payload(payload)
        if not valid:
            self.set_status(400)
            self.write(json.dumps({"errors": errors}, default=str))
            return

        workflow = await create_workflow(payload)
        alerts = generate_alerts(workflow)
        for alert in alerts:
            await create_alert(workflow["id"], alert)

        await create_log({
            "workflow_id": workflow["id"],
            "event_type": "workflow.created",
            "metadata": {"payload": payload},
        })

        await manager.broadcast({"type": "workflow.created", "item": workflow})
        self.set_status(201)
        self.write(json.dumps(workflow, default=str))

class WorkflowDetailHandler(BaseHandler):
    async def get(self, workflow_id: str):
        workflow = await fetch_workflow(workflow_id)
        if not workflow:
            self.set_status(404)
            self.write(json.dumps({"error": "Workflow not found"}, default=str))
            return
        self.write(json.dumps(workflow, default=str))
