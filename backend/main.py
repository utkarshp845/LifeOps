import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

from routes import auth as auth_routes
from routes import body as body_routes
from routes import build as build_routes
from routes import capture as capture_routes
from routes import markets as markets_routes
from routes import mind as mind_routes
from routes import wealth as wealth_routes

app = FastAPI(title="Life OS", version="0.1.0")

origins = [origin.strip() for origin in os.getenv("CORS_ORIGINS", "").split(",") if origin.strip()]
if origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(auth_routes.router)
app.include_router(body_routes.router)
app.include_router(build_routes.router)
app.include_router(capture_routes.router)
app.include_router(markets_routes.router)
app.include_router(mind_routes.router)
app.include_router(wealth_routes.router)
