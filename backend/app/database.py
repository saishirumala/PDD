from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# If using SQLite for fallback, check scheme. 
# But for PostgreSQL, we configure standard connection.
# We can add a fallback to SQLite if postgres is not available during quick tests, 
# e.g., sqlite:///./nutriguide.db to make tests run easily if no postgres is running yet.
# Let's support both: if DATABASE_URL starts with postgresql, we might need to handle the driver.
db_url = settings.DATABASE_URL
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

# Connect args check (sqlite needs check_same_thread=False)
connect_args = {}
if db_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(db_url, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
