from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.chat import router as chat_router
from app.api.user import router as user_router
from app.api.auth import router as auth_router

app = FastAPI(
    title="LightningQ AI Automation Labs",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)
app.include_router(user_router)
app.include_router(auth_router)

@app.get("/")
async def root():
    return {
        "message": "LightningQ AI Backend Running"
    }