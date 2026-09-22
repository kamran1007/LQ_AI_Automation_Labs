# app/services/websocket_manager.py

from fastapi import WebSocket


class ConnectionManager:

    def __init__(self):
        self.connections: dict[int, list[WebSocket]] = {}

    async def connect(
        self,
        hospital_id: int,
        websocket: WebSocket,
    ):
        await websocket.accept()

        if hospital_id not in self.connections:
            self.connections[hospital_id] = []

        self.connections[hospital_id].append(websocket)

        print(
            f"WebSocket connected "
            f"hospital_id={hospital_id}"
        )

    def disconnect(
        self,
        hospital_id: int,
        websocket: WebSocket,
    ):
        connections = self.connections.get(hospital_id)

        if not connections:
            return

        if websocket in connections:
            connections.remove(websocket)

        if not connections:
            del self.connections[hospital_id]

        print(
            f"WebSocket disconnected "
            f"hospital_id={hospital_id}"
        )

    async def send_to_hospital(
        self,
        hospital_id: int,
        message: dict,
    ):
        connections = self.connections.get(
            hospital_id,
            [],
        )

        disconnected = []

        for websocket in connections:
            try:
                await websocket.send_json(message)

            except Exception:
                disconnected.append(websocket)

        for websocket in disconnected:
            self.disconnect(
                hospital_id,
                websocket,
            )


manager = ConnectionManager()