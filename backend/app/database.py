# ===== BEGIN app/database.py =====
import time
from sqlalchemy.exc import OperationalError
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables(retries: int = 10, delay: float = 1.0):
    """
    Try to create tables, retrying if the DB isn't up yet.
    - retries: number of attempts
    - delay: seconds between attempts
    """
    for attempt in range(1, retries + 1):
        try:
            Base.metadata.create_all(bind=engine)
            return
        except OperationalError as e:
            if attempt == retries:
                raise  # Give up
            print(f"[database] attempt {attempt}/{retries} failed, retrying in {delay}s…")
            time.sleep(delay)

# ===== END app/database.py =====
