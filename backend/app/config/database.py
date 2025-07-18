import os
from urllib.parse import quote_plus
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv

load_dotenv()

# Database configuration with environment variable support for Render deployment
username = os.getenv("DB_USERNAME", "postgres.gestigjpiefkwstawvzx")
password = os.getenv("DB_PASSWORD", "IntelliAudit$2025")
host = os.getenv("DB_HOST", "aws-0-us-east-2.pooler.supabase.com")
port = os.getenv("DB_PORT", "6543")
database = os.getenv("DB_NAME", "postgres")
schema = os.getenv("DB_SCHEMA", "intelliaudit_dev")

# URL-encode the password
encoded_password = quote_plus(password)

DATABASE_URL = f"postgresql://{username}:{encoded_password}@{host}:{port}/{database}"
DB_SCHEMA = schema

# Create engine
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        # Set search path to intelliaudit_dev schema on each connection
        db.execute(text(f'SET search_path TO {DB_SCHEMA}'))
        yield db
    finally:
        db.close() 