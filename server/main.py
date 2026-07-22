"""
LocalShare Server
"""

from __future__ import annotations

from pathlib import Path
import uvicorn

from fastapi import FastAPI
from fastapi import WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from server.api.devices import router as devices_router
from server.api.files import router as files_router
from server.api.health import router as health_router
from server.api.messages import router as messages_router
from server.api.pairing import router as pairing_router
from server.database import database
from server.websocket import manager

# ==========================================================
# App
# ==========================================================

app = FastAPI(
    title="LocalShare",
    version="0.1.0",
)

# ==========================================================
# Paths
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

CLIENT_DIR = PROJECT_ROOT / "client"

STORAGE_DIR = PROJECT_ROOT / "storage"

# ==========================================================
# CORS
# ==========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================================
# Static Files
# ==========================================================

app.mount(
    "/static",
    StaticFiles(directory=CLIENT_DIR),
    name="static",
)

app.mount(
    "/storage",
    StaticFiles(directory=STORAGE_DIR),
    name="storage",
)

# ==========================================================
# API Routers
# ==========================================================

app.include_router(
    health_router,
)

app.include_router(
    messages_router,
)

app.include_router(
    files_router,
)

app.include_router(
    devices_router,
)

app.include_router(
    pairing_router,
)

# ==========================================================
# Startup / Shutdown
# ==========================================================

@app.on_event("startup")
async def startup():

    # Force database initialization

    _ = database


@app.on_event("shutdown")
async def shutdown():

    await manager.shutdown()


# ==========================================================
# Client
# ==========================================================

@app.get("/")
async def index():

    return FileResponse(
        CLIENT_DIR / "index.html"
    )


@app.get("/manifest.json")
async def manifest():

    return FileResponse(
        CLIENT_DIR / "manifest.json"
    )


@app.get("/service-worker.js")
async def service_worker():

    return FileResponse(
        CLIENT_DIR / "service-worker.js"
    )


@app.get("/favicon.ico")
async def favicon():

    path = CLIENT_DIR / "icons" / "favicon.ico"

    if path.exists():

        return FileResponse(path)

    return {
        "success": False,
        "message": "Favicon not found.",
    }





# ==========================================================
# API Information
# ==========================================================

@app.get("/api")
async def api():

    return {
        "success": True,
        "data": {
            "name": "LocalShare API",
            "version": "0.1.0",
            "websocket": "/ws/{device_id}",
            "endpoints": [
                "/api/health",
                "/api/messages",
                "/api/files",
                "/api/devices",
                "/api/pairing",
            ],
        },
    }


# ==========================================================
# WebSocket
# ==========================================================

@app.websocket("/ws/{device_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    device_id: str,
):

    await manager.connect(
        websocket,
        device_id,
    )

    await manager.listen(
        websocket,
        device_id,
    )


# ==========================================================
# PWA Fallback
# ==========================================================

@app.get("/{full_path:path}")
async def spa_fallback(
    full_path: str,
):

    file_path = CLIENT_DIR / full_path

    if file_path.exists() and file_path.is_file():

        return FileResponse(file_path)

    return FileResponse(
        CLIENT_DIR / "index.html"
    )


# ==========================================================
# Development Entry
# ==========================================================

if __name__ == "__main__":

    print("=" * 60)
    print(" LocalShare Server")
    print("=" * 60)
    print(" URL       : http://127.0.0.1:8000")
    print(" API Docs  : http://127.0.0.1:8000/docs")
    print(" WebSocket : ws://127.0.0.1:8000/ws/<device_id>")
    print("=" * 60)

    uvicorn.run(
        "server.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )