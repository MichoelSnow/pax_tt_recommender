from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.pool import QueuePool
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Get the backend directory path
backend_dir = Path(__file__).parent.parent
database_path = backend_dir / "database" / "boardgames.db"

# Database URL - use absolute path
SQLALCHEMY_DATABASE_URL = f"sqlite:///{database_path}"

# Create engine with optimized settings
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={
        "check_same_thread": False,  # Needed for SQLite
        "timeout": 30.0  # 30 second timeout to prevent hanging
    },
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,  # Recycle connections after 30 minutes
    pool_pre_ping=True,  # Enable connection health checks
    echo=False  # Set to True for SQL query logging
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for models
class Base(DeclarativeBase):
    pass

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()