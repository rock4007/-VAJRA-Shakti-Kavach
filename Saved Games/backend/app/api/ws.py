from fastapi import APIRouter, WebSocket

from app.services.websocket_manager import ws_manager

router = APIRouter(tags=["ws"])


@router.websocket("/ws/jobs")
async def jobs_ws(websocket: WebSocket) -> None:
    channel = "jobs"
    await ws_manager.connect(channel, websocket)
    try:
        while True:
            await websocket.receive_text()
    except Exception:
        ws_manager.disconnect(channel, websocket)
