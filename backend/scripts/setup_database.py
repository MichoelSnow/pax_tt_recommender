import os
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.database import engine
from app.models import Base
from alembic.config import Config
from alembic import command

def setup_database():
    """Set up the database for production."""
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Run migrations
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")

if __name__ == "__main__":
    setup_database()