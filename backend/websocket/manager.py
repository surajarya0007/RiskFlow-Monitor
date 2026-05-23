import json
from typing import Set
import tornado.websocket

class WebSocketManager:
    def __init__(self):
        self.connections: Set[tornado.websocket.WebSocketHandler] = set()

    def add(self, connection: tornado.websocket.WebSocketHandler):
        self.connections.add(connection)

    def remove(self, connection: tornado.websocket.WebSocketHandler):
        self.connections.discard(connection)

    async def broadcast(self, event: dict):
        data = json.dumps(event, default=str)
        for connection in list(self.connections):
            try:
                connection.write_message(data)
            except Exception:
                self.connections.discard(connection)

manager = WebSocketManager()
