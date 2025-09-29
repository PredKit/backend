"""
Database connection and utilities
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import structlog

logger = structlog.get_logger()


def get_db_connection():
    """Get database connection"""
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        # Construct from individual components
        db_host = os.getenv("DB_HOST")
        db_port = os.getenv("DB_PORT", "5432")
        db_name = os.getenv("DB_NAME")
        db_user = os.getenv("DB_USER")
        db_password = os.getenv("DB_PASSWORD")
        
        db_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    return Session()


def get_engine():
    """Get SQLAlchemy engine"""
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        db_host = os.getenv("DB_HOST")
        db_port = os.getenv("DB_PORT", "5432")
        db_name = os.getenv("DB_NAME")
        db_user = os.getenv("DB_USER")
        db_password = os.getenv("DB_PASSWORD")
        
        db_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    
    return create_engine(db_url)
