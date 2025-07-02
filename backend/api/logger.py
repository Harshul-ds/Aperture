# backend/api/logger.py

import asyncio
import logging
from typing import List
from fastapi import WebSocket, APIRouter, WebSocketDisconnect

# --- NEW: Create the APIRouter instance ---
# This is the 'router' that main.py was looking for.
router = APIRouter()

# --- Connection Manager (No changes needed) ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.main_loop = None

    def set_main_loop(self):
        """Call this once on startup to capture the main event loop."""
        try:
            self.main_loop = asyncio.get_running_loop()
            logging.info("Main event loop captured by ConnectionManager.")
        except RuntimeError:
            logging.error("Could not capture main event loop. Websocket logging will not work.")
            self.main_loop = None

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

# --- WebSocketLogHandler (No changes needed) ---
class WebSocketLogHandler(logging.Handler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def emit(self, record):
        """This method is called by the logging framework from any thread."""
        log_entry = self.format(record)
        if manager.main_loop and manager.main_loop.is_running():
            asyncio.run_coroutine_threadsafe(
                manager.broadcast(log_entry), 
                manager.main_loop
            )
        else:
            print(f"FALLBACK LOG: {log_entry}")

# --- NEW: WebSocket Endpoint ---
# This defines the actual API endpoint that the front end can connect to.
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for streaming logs to the frontend.
    """
    await manager.connect(websocket)
    try:
        while True:
            # Keep the connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("Log viewer client disconnected.")