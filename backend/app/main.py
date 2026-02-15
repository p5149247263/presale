from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.core.config import settings

app = FastAPI(title=settings.app_name, version="0.1.0")

origins_raw = settings.cors_origins.strip()
if origins_raw == "*":
    cors_origins = ["*"]
else:
    cors_origins = [x.strip() for x in origins_raw.split(",") if x.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")
