from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.core.config import settings
from app.api.api import api_router, include_api_routers
from app.db import init_db

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Set up CORS
    if settings.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Initialize database
    init_db()

    # Include API routers
    include_api_routers()
    app.include_router(api_router, prefix=settings.API_V1_STR)

    # Create static files directory if it doesn't exist
    os.makedirs("static", exist_ok=True)
    app.mount("/static", StaticFiles(directory="static"), name="static")

    # Import and include websocket routes
    from app.api.endpoints import websocket
    app.include_router(websocket.router)

    return app

# Create FastAPI app
# app = create_app()
