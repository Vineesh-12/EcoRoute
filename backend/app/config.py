import os

class Settings:
    PROJECT_NAME: str = "EcoRoute Optimization Engine"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    OSRM_ROUTER_URL: str = os.getenv("OSRM_ROUTER_URL", "http://router.project-osrm.org")

settings = Settings()
