import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings

logger = logging.getLogger(__name__)

Base = declarative_base()

active_db_type = "unknown"
engine = None
SessionLocal = None

def init_db():
    global engine, SessionLocal, active_db_type
    
    # Try PostgreSQL first (PostGIS)
    try:
        logger.info(f"Connecting to database: {settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else settings.DATABASE_URL}")
        pg_engine = create_engine(
            settings.DATABASE_URL,
            pool_pre_ping=True,
            connect_args={"connect_timeout": 3}
        )
        with pg_engine.connect() as conn:
            conn.execute(text("SELECT 1;"))
            try:
                # Enable PostGIS if running on PostgreSQL
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
                conn.commit()
                logger.info("PostGIS extension verified/enabled.")
            except Exception as ext_err:
                logger.warning(f"Note on PostGIS extension: {ext_err}")
        
        engine = pg_engine
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        active_db_type = "PostgreSQL + PostGIS"
        logger.info("Successfully connected to PostgreSQL + PostGIS.")
        return
    except Exception as e:
        logger.warning(f"Could not connect to PostgreSQL ({e}). Falling back to SQLite local database.")
    
    # Fallback to SQLite
    engine = create_engine(
        settings.SQLITE_URL,
        connect_args={"check_same_thread": False}
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    active_db_type = "SQLite (Local Standalone)"
    logger.info("Initialized local SQLite database.")

init_db()

def get_db():
    if SessionLocal is None:
        init_db()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
