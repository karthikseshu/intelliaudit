import os
from urllib.parse import quote_plus
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv

load_dotenv()

# Supabase connection string with URL-encoded password
username = "postgres.gestigjpiefkwstawvzx"
password = quote_plus("IntelliAudit$2025")  # URL-encode the new password
host = "aws-0-us-east-2.pooler.supabase.com"
port = "6543"  # Correct port for Supabase
database = "postgres"

DATABASE_URL = f"postgresql://{username}:{password}@{host}:{port}/{database}"
DB_SCHEMA = 'intelliaudit_dev'

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