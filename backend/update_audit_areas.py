#!/usr/bin/env python3
"""
Update metadata_audit_areas table to add foreign key constraint
"""
import json
import sys
import os
from urllib.parse import quote_plus
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def update_audit_areas():
    """Update metadata_audit_areas table with foreign key constraint"""
    try:
        # Use the same configuration as the API
        username = "postgres.gestigjpiefkwstawvzx"
        password = quote_plus("IntelliAudit$2025")
        host = "aws-0-us-east-2.pooler.supabase.com"
        port = "6543"
        database = "postgres"

        DATABASE_URL = f"postgresql://{username}:{password}@{host}:{port}/{database}"
        DB_SCHEMA = 'intelliaudit_dev'

        # Create engine and session
        engine = create_engine(DATABASE_URL, pool_pre_ping=True)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

        print("Updating metadata_audit_areas table...")
        db = SessionLocal()
        try:
            # Set search path to intelliaudit_dev schema
            db.execute(text(f'SET search_path TO {DB_SCHEMA}'))
            
            # First, add the audit_framework_id column if it doesn't exist
            print("1. Adding audit_framework_id column...")
            db.execute(text("""
                ALTER TABLE metadata_audit_areas 
                ADD COLUMN IF NOT EXISTS audit_framework_id INTEGER
            """))
            
            # Add foreign key constraint
            print("2. Adding foreign key constraint...")
            db.execute(text("""
                ALTER TABLE metadata_audit_areas 
                ADD CONSTRAINT fk_audit_areas_framework 
                FOREIGN KEY (audit_framework_id) 
                REFERENCES metadata_audit_frameworks(id)
            """))
            
            # Update existing audit areas to link them to NCQA framework
            print("3. Updating existing audit areas to link to NCQA framework...")
            db.execute(text("""
                UPDATE metadata_audit_areas 
                SET audit_framework_id = 1
                WHERE name IN ('Credentialing', 'Quality Management', 'Member Rights', 'General Documents', 'HEDIS Data Validation', 'Utilization Management', 'Provider Network')
            """))
            
            # Commit the changes
            db.commit()
            
            # Verify the changes
            print("4. Verifying the changes...")
            result = db.execute(text("""
                SELECT 
                    aa.id,
                    aa.name,
                    aa.description,
                    af.name as framework_name,
                    af.version as framework_version
                FROM metadata_audit_areas aa
                LEFT JOIN metadata_audit_frameworks af ON aa.audit_framework_id = af.id
                ORDER BY aa.name
            """))
            
            # Convert results to list of dictionaries
            rows = []
            for row in result:
                row_dict = {}
                for column in row._fields:
                    value = getattr(row, column)
                    # Convert datetime objects to string for JSON serialization
                    if hasattr(value, 'isoformat'):
                        row_dict[column] = value.isoformat()
                    else:
                        row_dict[column] = value
                rows.append(row_dict)
            
            # Create response object
            response = {
                "status": "success",
                "message": "Successfully updated metadata_audit_areas table with foreign key constraint",
                "schema": DB_SCHEMA,
                "table": "metadata_audit_areas",
                "row_count": len(rows),
                "data": rows
            }
            
            # Print JSON response
            print("\n" + "="*50)
            print("UPDATE RESULTS")
            print("="*50)
            print(json.dumps(response, indent=2))
            print("="*50)
            
            return response

        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

    except Exception as e:
        error_response = {
            "status": "error",
            "message": f"Failed to update metadata_audit_areas table: {str(e)}",
            "error_type": type(e).__name__
        }

        print("\n" + "="*50)
        print("UPDATE FAILED")
        print("="*50)
        print(json.dumps(error_response, indent=2))
        print("="*50)

        return error_response

if __name__ == "__main__":
    update_audit_areas() 