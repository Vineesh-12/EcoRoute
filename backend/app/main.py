import logging
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.config import settings
from app.routes.api import router as api_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("ecoroute")

app = FastAPI(
    title="EcoRoute — Municipal Waste Collection Route Optimizer",
    description="Capacitated Vehicle Routing Problem (CVRP) Optimization Engine comparing Nearest Neighbor, Genetic Algorithm, and Google OR-Tools using OpenStreetMap/OSRM.",
    version="1.0.0"
)

# Enable CORS for React frontend (development and production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

# Serve the React frontend in production
# When deployed, the built frontend files are copied to backend/static/
STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")

if os.path.isdir(STATIC_DIR):
    # Serve JS, CSS, images, and other assets
    app.mount("/assets", StaticFiles(directory=os.path.join(STATIC_DIR, "assets")), name="assets")

    # Serve the React index.html for all non-API routes (SPA fallback)
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        # If a specific static file exists, serve it
        file_path = os.path.join(STATIC_DIR, full_path)
        if full_path and os.path.isfile(file_path):
            return FileResponse(file_path)
        # Otherwise serve index.html (React Router handles client-side routing)
        return FileResponse(os.path.join(STATIC_DIR, "index.html"))

    logger.info(f"Production mode: serving React frontend from {STATIC_DIR}")
else:
    # Development mode — frontend is served by Vite dev server
    @app.get("/")
    def root():
        return {
            "message": "EcoRoute — Municipal Solid Waste Collection Route Optimization API is active.",
            "docs_url": "/docs",
            "api_health": "/api/health"
        }
    logger.info("Development mode: frontend served by Vite dev server")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
