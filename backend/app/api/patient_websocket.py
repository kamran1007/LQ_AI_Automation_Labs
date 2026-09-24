from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect,
)

from app.services.websocket_manager import manager


router = APIRouter(
    prefix="/patient",
    tags=["Patient WebSocket"],
)


@router.websocket("/ws/{patient_id}")
async def patient_websocket(
    websocket: WebSocket,
    patient_id: int,
):
    print(
        f"PATIENT WEBSOCKET HANDSHAKE: "
        f"patient_id={patient_id}"
    )

    await manager.connect_patient(
        patient_id=patient_id,
        websocket=websocket,
    )

    print(
        f"PATIENT WEBSOCKET CONNECTED: "
        f"patient_id={patient_id}"
    )

    try:
        while True:
            data = await websocket.receive_text()

            print(
                f"PATIENT WEBSOCKET MESSAGE "
                f"patient_id={patient_id}: "
                f"{data}"
            )

    except WebSocketDisconnect:

        manager.disconnect_patient(
            patient_id=patient_id,
            websocket=websocket,
        )

        print(
            f"PATIENT WEBSOCKET DISCONNECTED: "
            f"patient_id={patient_id}"
        )