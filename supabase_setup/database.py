import logging
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings

logger = logging.getLogger("nutriguide.database")

db_url = settings.effective_db_url

if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

connect_args = {}
engine_kwargs = {}

if db_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
elif db_url.startswith("postgresql"):
    engine_kwargs["pool_pre_ping"] = True
    engine_kwargs["pool_recycle"] = 300

try:
    engine = create_engine(db_url, connect_args=connect_args, **engine_kwargs)
except Exception as e:
    logger.error(f"Failed to initialize database engine for {db_url}: {e}")
    fallback_url = "sqlite:///./nutriguide.db"
    logger.info(f"Falling back to local database: {fallback_url}")
    engine = create_engine(fallback_url, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
