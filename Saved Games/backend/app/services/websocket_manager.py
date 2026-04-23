from collections import defaultdict
from typing import Any

from fastapi import WebSocket


class WebSocketManager:
    def __init__(self) -> None:
        self.connections: dict[str, set[WebSocket]] = defaultdict(set)

    async def connect(self, channel: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self.connections[channel].add(websocket)

    def disconnect(self, channel: str, websocket: WebSocket) -> None:
        if channel in self.connections and websocket in self.connections[channel]:
            self.connections[channel].remove(websocket)

    async def publish(self, channel: str, message: dict[str, Any]) -> None:
        stale: list[WebSocket] = []
        for socket in self.connections.get(channel, set()):
            try:
                await socket.send_json(message)
            except Exception:
                stale.append(socket)
        for socket in stale:
            self.disconnect(channel, socket)


ws_manager = WebSocketManager()
