import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine, Base
from app.routes.api import router as api_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("ecoroute")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing EcoRoute Application & Database Tables...")
    try:
        if engine is not None:
            Base.metadata.create_all(bind=engine)
            logger.info("Database schemas verified.")
    except Exception as e:
        logger.warning(f"Note on DB schema creation: {e}")
    yield
    logger.info("EcoRoute Application shutting down.")

app = FastAPI(
    title="EcoRoute — Municipal Waste Collection Route Optimizer",
    description="Capacitated Vehicle Routing Problem (CVRP) Optimization Engine comparing Nearest Neighbor, Genetic Algorithm, and Google OR-Tools.",
    version="1.0.0",
    lifespan=lifespan
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

@app.get("/")
def root():
    return {
        "message": "EcoRoute — Municipal Solid Waste Collection Route Optimization API is running.",
        "docs_url": "/docs",
        "api_health": "/api/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
