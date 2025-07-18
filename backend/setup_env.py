#!/usr/bin/env python3
"""
Setup script to help configure environment variables for IntelliAudit backend
"""

import os
from pathlib import Path
from dotenv import load_dotenv

def create_env_file():
    """Create .env file with template values"""
    env_path = Path(".env")
    
    if env_path.exists():
        print("✅ .env file already exists")
        return
    
    env_content = """# Supabase Configuration
# Get these values from your Supabase project dashboard
VITE_SUPABASE_URL=https://your-project-id.supabase.co
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key_here

# LLM Configuration (optional for testing)
GOOGLE_API_KEY=your_google_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
"""
    
    with open(env_path, "w") as f:
        f.write(env_content)
    
    print("✅ Created .env file with template values")
    print("📝 Please update the values with your actual Supabase credentials")

def check_env_variables():
    """Check if required environment variables are set"""
    # Load environment variables from .env file
    load_dotenv()
    
    required_vars = ["VITE_SUPABASE_URL", "VITE_SUPABASE_ANON_KEY"]
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if not value or value == "your_supabase_anon_key_here" or "your-project-id" in value:
            missing_vars.append(var)
        else:
            print(f"✅ {var}: {value[:20]}..." if len(value) > 20 else f"✅ {var}: {value}")
    
    if missing_vars:
        print("\n❌ Missing or invalid environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n📝 Please update these variables in your .env file with actual values")
        return False
    else:
        print("\n✅ All required environment variables are properly set")
        return True

def test_database_connection():
    """Test database connection"""
    try:
        from app.config.database import get_supabase_client
        client = get_supabase_client()
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

if __name__ == "__main__":
    print("🔧 IntelliAudit Backend Setup")
    print("=" * 40)
    
    # Create .env file if it doesn't exist
    create_env_file()
    
    print("\n🔍 Checking environment variables...")
    if check_env_variables():
        print("\n🔍 Testing database connection...")
        test_database_connection()
    
    print("\n📋 Next steps:")
    print("1. Update .env file with your Supabase credentials")
    print("2. Run this script again to test the connection")
    print("3. Start the backend server with: uvicorn app.main:app --reload") 