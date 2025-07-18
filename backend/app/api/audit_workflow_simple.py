from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, date
from uuid import uuid4, UUID
import json
import psycopg
from app.config.database_simple import get_db_connection

router = APIRouter(tags=["audit-workflow"])

# Pydantic Models matching the exact database schema

class AuditFramework(BaseModel):
    id: Optional[int] = None
    name: str
    version: Optional[str] = None
    created_at: Optional[datetime] = None

class AuditArea(BaseModel):
    id: Optional[int] = None
    audit_framework_id: Optional[UUID] = None
    name: str
    description: Optional[str] = None
    created_at: Optional[datetime] = None

# API Endpoints

@router.get("/frameworks", response_model=List[Dict[str, Any]])
async def get_audit_frameworks():
    """Get all audit frameworks with their related audit areas"""
    try:
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        f.id,
                        f.name,
                        f.version,
                        json_agg(
                            json_build_object(
                                'id', aa.id,
                                'name', aa.name,
                                'description', aa.description
                            )
                        ) as audit_areas
                    FROM metadata_audit_frameworks f
                    LEFT JOIN metadata_audit_areas aa ON f.id = aa.audit_framework_id
                    GROUP BY f.id, f.name, f.version
                    ORDER BY f.name
                """)
                
                frameworks = []
                for row in cursor.fetchall():
                    # Convert audit_areas from JSON to list, handling null values
                    audit_areas = row[3] if row[3] and row[3] != [None] else []
                    
                    framework_data = {
                        "id": row[0],
                        "name": row[1],
                        "version": row[2],
                        "audit_areas": audit_areas
                    }
                    frameworks.append(framework_data)
                
                return frameworks
        finally:
            conn.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch audit frameworks: {str(e)}")

@router.get("/areas", response_model=List[AuditArea])
async def get_audit_areas():
    """Get all audit areas"""
    try:
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id, audit_framework_id, name, description, created_at FROM metadata_audit_areas ORDER BY name")
                areas = []
                for row in cursor.fetchall():
                    areas.append(AuditArea(
                        id=row[0],
                        audit_framework_id=row[1],
                        name=row[2],
                        description=row[3],
                        created_at=row[4]
                    ))
                return areas
        finally:
            conn.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch audit areas: {str(e)}")

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        conn = get_db_connection()
        conn.close()
        return {"status": "healthy", "message": "Database connection successful"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}") 