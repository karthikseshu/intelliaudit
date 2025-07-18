#!/usr/bin/env python3
"""
Debug database connection issues
"""
import json
from urllib.parse import quote_plus
import psycopg2

def test_connection_formats():
    """Test different connection string formats"""
    
    # Original connection string
    original_url = "postgresql://postgres.gestigjpiefkwstawvzx:.MyvqBC9p22#Dd9@aws-0-us-east-2.pooler.supabase.com:5432/postgres"
    
    # URL-encoded password
    username = "postgres.gestigjpiefkwstawvzx"
    password = quote_plus(".MyvqBC9p22#Dd9")
    host = "aws-0-us-east-2.pooler.supabase.com"
    port = "5432"
    database = "postgres"
    
    encoded_url = f"postgresql://{username}:{password}@{host}:{port}/{database}"
    
    print("Testing connection formats...")
    print(f"Original URL: {original_url}")
    print(f"Encoded URL: {encoded_url}")
    print(f"Encoded password: {password}")
    print()
    
    # Test with psycopg2 directly
    try:
        print("Testing with psycopg2 direct connection...")
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=username,
            password=".MyvqBC9p22#Dd9"  # Use original password
        )
        print("✅ Direct psycopg2 connection successful!")
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Direct psycopg2 connection failed: {e}")
        return False

if __name__ == "__main__":
    test_connection_formats() 