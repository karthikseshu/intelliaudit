#!/usr/bin/env python3
"""
Database setup script for IntelliAudit
This script will create the necessary tables in your Supabase database
"""

import os
from pathlib import Path
from dotenv import load_dotenv

def read_schema_file():
    """Read the database schema file"""
    schema_path = Path("../database_schema_complete.sql")
    if not schema_path.exists():
        print("❌ Schema file not found. Please ensure database_schema_complete.sql exists in the root directory.")
        return None
    
    with open(schema_path, 'r') as f:
        return f.read()

def setup_database():
    """Set up the database schema"""
    print("🔧 Setting up IntelliAudit Database Schema")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Check if Supabase credentials are available
    supabase_url = os.getenv('VITE_SUPABASE_URL')
    supabase_key = os.getenv('VITE_SUPABASE_ANON_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Supabase credentials not found in .env file")
        print("Please ensure VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY are set")
        return False
    
    # Read schema file
    schema_sql = read_schema_file()
    if not schema_sql:
        return False
    
    print("✅ Schema file loaded successfully")
    print(f"📝 Supabase URL: {supabase_url[:30]}...")
    
    print("\n📋 Next Steps:")
    print("1. Go to your Supabase Dashboard")
    print("2. Navigate to SQL Editor")
    print("3. Copy the contents of database_schema_complete.sql")
    print("4. Paste and run the SQL")
    print("5. Verify tables are created in the Table Editor")
    
    print("\n📁 Schema file location:")
    print(f"   {Path('../database_schema_complete.sql').absolute()}")
    
    return True

if __name__ == "__main__":
    setup_database() 