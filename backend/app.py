import asyncio
import os
import json
import tornado.ioloop
import tornado.web
import tornado.websocket
from tornado.web import Application
from backend.config import settings
from backend.db.base import init_db
from backend.handlers.workflow import WorkflowListHandler, WorkflowDetailHandler
from backend.handlers.alert import AlertListHandler, AlertAcknowledgeHandler
from backend.handlers.logs import LogsHandler
from backend.handlers.health import HealthHandler
from backend.handlers.metrics import MetricsHandler
from backend.handlers.market import MarketLatestHandler
from backend.websocket.manager import manager
from backend.utils.logging import setup_logging
from backend.services.market_service import run_market_monitor

setup_logging()

class WebSocketUpdatesHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        manager.add(self)

    def on_message(self, message):
        pass

    def on_close(self):
        manager.remove(self)

    def check_origin(self, origin):
        return True

async def make_app():
    app = Application(
        [
            (r"/api/workflows", WorkflowListHandler),
            (r"/api/workflows/([0-9a-fA-F-]+)", WorkflowDetailHandler),
            (r"/api/alerts", AlertListHandler),
            (r"/api/alerts/acknowledge", AlertAcknowledgeHandler),
            (r"/api/logs", LogsHandler),
            (r"/api/system/health", HealthHandler),
            (r"/api/dashboard/metrics", MetricsHandler),
            (r"/api/market/latest", MarketLatestHandler),
            (r"/ws/stream", WebSocketUpdatesHandler),
        ],
        debug=settings.DEBUG,
        autoreload=settings.DEBUG,
    )
    await init_db()
    # start background market monitor
    try:
        asyncio.create_task(run_market_monitor())
    except Exception:
        pass
    return app

if __name__ == "__main__":
    # Install asyncio-based IOLoop so asyncpg pool binds to the running loop
    from tornado.platform.asyncio import AsyncIOMainLoop

    AsyncIOMainLoop().install()
    loop = asyncio.get_event_loop()
    app = loop.run_until_complete(make_app())
    app.listen(settings.PORT)
    print(f"GovernanceOps backend listening on http://0.0.0.0:{settings.PORT}")
    loop.run_forever()
