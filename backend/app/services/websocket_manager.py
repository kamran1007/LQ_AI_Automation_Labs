from fastapi import WebSocket


class ConnectionManager:

    def __init__(self):
        self.hospital_connections: dict[int, list[WebSocket]] = {}
        self.patient_connections: dict[int, list[WebSocket]] = {}

    # -------------------------
    # HOSPITAL
    # -------------------------

    async def connect_hospital(
        self,
        hospital_id: int,
        websocket: WebSocket,
    ):
        await websocket.accept()

        if hospital_id not in self.hospital_connections:
            self.hospital_connections[hospital_id] = []

        self.hospital_connections[hospital_id].append(websocket)

        print(
            f"Hospital WebSocket connected "
            f"hospital_id={hospital_id}"
        )

    def disconnect_hospital(
        self,
        hospital_id: int,
        websocket: WebSocket,
    ):
        connections = self.hospital_connections.get(hospital_id)

        if not connections:
            return

        if websocket in connections:
            connections.remove(websocket)

        if not connections:
            del self.hospital_connections[hospital_id]

        print(
            f"Hospital WebSocket disconnected "
            f"hospital_id={hospital_id}"
        )

    async def send_to_hospital(
        self,
        hospital_id: int,
        message: dict,
    ):
        connections = self.hospital_connections.get(
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
            self.disconnect_hospital(
                hospital_id,
                websocket,
            )

    # -------------------------
    # PATIENT
    # -------------------------

    async def connect_patient(
        self,
        patient_id: int,
        websocket: WebSocket,
    ):
        await websocket.accept()

        if patient_id not in self.patient_connections:
            self.patient_connections[patient_id] = []

        self.patient_connections[patient_id].append(websocket)

        print(
            f"Patient WebSocket connected "
            f"patient_id={patient_id}"
        )

    def disconnect_patient(
        self,
        patient_id: int,
        websocket: WebSocket,
    ):
        connections = self.patient_connections.get(patient_id)

        if not connections:
            return

        if websocket in connections:
            connections.remove(websocket)

        if not connections:
            del self.patient_connections[patient_id]

        print(
            f"Patient WebSocket disconnected "
            f"patient_id={patient_id}"
        )

    async def send_to_patient(
        self,
        patient_id: int,
        message: dict,
    ):
        connections = self.patient_connections.get(
            patient_id,
            [],
        )

        disconnected = []

        for websocket in connections:
            try:
                await websocket.send_json(message)

            except Exception:
                disconnected.append(websocket)

        for websocket in disconnected:
            self.disconnect_patient(
                patient_id,
                websocket,
            )


manager = ConnectionManager()