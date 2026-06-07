import os
import logging
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv

# Import models to ensure they are registered on Base
from models.models import Base

# Setup logger
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

DEFAULT_DB_PATH = "database/user_data.db"

def get_db_path() -> str:
    """
    Retrieves and resolves the database file path from environment variables.
    Defaults to database/user_data.db in the project workspace.
    """
    db_path = os.getenv("DATABASE_PATH", DEFAULT_DB_PATH)
    # Ensure it's absolute to prevent session directory mismatches
    if not os.path.isabs(db_path):
        # Resolve relative to current working directory (workspace root)
        db_path = os.path.abspath(db_path)
    
    # Ensure containing directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    return db_path

def get_db_url() -> str:
    """Gets the SQLAlchemy connection URL for the SQLite database."""
    path = get_db_path()
    return f"sqlite:///{path}"

def get_engine():
    """Initializes and returns the SQLAlchemy database engine."""
    db_url = get_db_url()
    # Configure SQLite pool/timeout options for streamlit multithreading stability
    engine = create_engine(
        db_url,
        connect_args={"check_same_thread": False}
    )
    return engine

# Create a sessionmaker instance
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())

def get_session() -> Generator[Session, None, None]:
    """
    Context generator for DB sessions.
    Ensures sessions are closed properly after execution.
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Database transaction error: {str(e)}")
        raise e
    finally:
        session.close()

def init_db() -> None:
    """Initializes the database by creating all standard tables."""
    try:
        engine = get_engine()
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise e

def reset_db() -> None:
    """
    Resets the database by removing the SQLite file
    and recreating standard schema tables.
    """
    db_path = get_db_path()
    if os.path.exists(db_path):
        try:
            # Dispose engine pool connections before deleting the file
            get_engine().dispose()
            os.remove(db_path)
            logger.info("Database file removed successfully.")
        except Exception as e:
            logger.error(f"Error removing database file: {str(e)}")
            # Try to drop tables if file removal fails (e.g. locked)
            try:
                engine = get_engine()
                Base.metadata.drop_all(bind=engine)
                logger.info("Tables dropped as database file removal failed.")
            except Exception as drop_err:
                logger.error(f"Failed to drop tables: {str(drop_err)}")
                raise drop_err
    
    # Re-initialize the database
    init_db()
