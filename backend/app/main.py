
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.chat import router as chat_router
from app.api.user import router as user_router
from app.api.auth import router as auth_router
from app.api.appointment_request import router as appointment_request_router
from app.api.hospital_appointments import (
    router as hospital_appointments_router,
)
from app.api.hospital_websocket import (
    router as hospital_websocket_router,
)
from app.api.patient_websocket import (
    router as patient_websocket_router,
)
from app.api.patient_appointments import (
    router as patient_appointments_router,
)
from app.api.conversation import router as conversation_router
from app.api.hospital import router as hospital_router
from app.api.hospital_auth import router as hospital_auth_router
from app.api.hospital_notifications import router as hospital_notifications_router


app = FastAPI(
    title="LightningQ AI Automation Labs",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:8000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================================
# AI BACKEND ROUTES
# ==========================================================

app.include_router(
    chat_router,
    prefix="/ai",
)

app.include_router(
    user_router,
    prefix="/ai",
)

app.include_router(
    auth_router,
    prefix="/ai",
)

app.include_router(
    appointment_request_router,
    prefix="/ai",
)

app.include_router(
    hospital_appointments_router,
    prefix="/ai",
)

app.include_router(
    hospital_websocket_router,
    prefix="/ai",
)

app.include_router(
    patient_websocket_router,
    prefix="/ai",
)

app.include_router(
    patient_appointments_router,
    prefix="/ai",
)

app.include_router(
    conversation_router,
    prefix="/ai",
)


# ==========================================================
# HOSPITAL AUTHENTICATION
# ==========================================================

app.include_router(
    hospital_auth_router,
    prefix="/ai/hospital/auth",
    tags=["Hospital Authentication"],
)


# ==========================================================
# HOSPITAL ROUTES
# ==========================================================

# Uncomment when hospital.py routes are ready.
#
app.include_router(
    hospital_router,
    prefix="/ai/hospital",
)

app.include_router(
    hospital_notifications_router,
    prefix="/ai",
)

# ==========================================================
# ROOT
# ==========================================================

@app.get("/ai")
async def ai_root():
    return {
        "message": "LightningQ AI Backend Running",
    }
