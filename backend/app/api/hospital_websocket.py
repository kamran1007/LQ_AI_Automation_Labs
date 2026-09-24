from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.services.websocket_manager import manager


router = APIRouter(
    prefix="/hospital",
    tags=["Hospital WebSocket"],
)


@router.websocket("/ws/{hospital_id}")
async def hospital_websocket(
    websocket: WebSocket,
    hospital_id: int,
):
    print(
        f"WEBSOCKET HANDSHAKE: hospital_id={hospital_id}"
    )

    await manager.connect_hospital(
        hospital_id=hospital_id,
        websocket=websocket,
    )

    print(
        f"WEBSOCKET CONNECTED: hospital_id={hospital_id}"
    )

    try:
        while True:
            data = await websocket.receive_text()

            print(
                f"WEBSOCKET MESSAGE "
                f"hospital_id={hospital_id}: {data}"
            )

    except WebSocketDisconnect:

        manager.disconnect_hospital(
            hospital_id=hospital_id,
            websocket=websocket,
        )

        print(
            f"WEBSOCKET DISCONNECTED: "
            f"hospital_id={hospital_id}"
        )