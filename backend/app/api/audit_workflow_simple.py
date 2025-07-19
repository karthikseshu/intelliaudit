from fastapi import APIRouter, HTTPException
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime
import psycopg
import uuid
from app.config.database_simple import get_db_connection

router = APIRouter(tags=["audit-workflow"])

# Pydantic Models matching the updated database schema
class AuditFramework(BaseModel):
    framework_id: Optional[str] = None
    name: str
    version: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None

class AuditArea(BaseModel):
    audit_area_id: Optional[str] = None
    framework_id: Optional[str] = None
    name: str
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None

# Helper to convert row to dict with UUIDs as strings
def row_to_dict(row, columns):
    d = {}
    for i, col in enumerate(columns):
        value = row[i]
        if hasattr(value, 'isoformat'):
            d[col] = value.isoformat()
        elif isinstance(value, uuid.UUID):
            d[col] = str(value)
        else:
            d[col] = value
    return d

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
                        f.framework_id,
                        f.name,
                        f.version,
                        f.created_at,
                        f.updated_at,
                        f.created_by,
                        f.updated_by,
                        json_agg(
                            json_build_object(
                                'audit_area_id', aa.audit_area_id,
                                'framework_id', aa.framework_id,
                                'name', aa.name,
                                'description', aa.description,
                                'created_at', aa.created_at,
                                'updated_at', aa.updated_at,
                                'created_by', aa.created_by,
                                'updated_by', aa.updated_by
                            )
                        ) FILTER (WHERE aa.audit_area_id IS NOT NULL) as audit_areas
                    FROM intelliaudit_dev.metadata_audit_frameworks f
                    LEFT JOIN intelliaudit_dev.metadata_audit_areas aa ON f.framework_id = aa.framework_id
                    GROUP BY f.framework_id, f.name, f.version, f.created_at, f.updated_at, f.created_by, f.updated_by
                    ORDER BY f.name
                """)
                frameworks = []
                for row in cursor.fetchall():
                    # Convert audit_areas UUIDs to strings
                    audit_areas = row[7] if row[7] and row[7] != [None] else []
                    if isinstance(audit_areas, list):
                        for area in audit_areas:
                            for k, v in area.items():
                                if isinstance(v, uuid.UUID):
                                    area[k] = str(v)
                    framework_data = {
                        "framework_id": str(row[0]) if isinstance(row[0], uuid.UUID) else row[0],
                        "name": row[1],
                        "version": row[2],
                        "created_at": row[3].isoformat() if hasattr(row[3], 'isoformat') else row[3],
                        "updated_at": row[4].isoformat() if hasattr(row[4], 'isoformat') else row[4],
                        "created_by": str(row[5]) if isinstance(row[5], uuid.UUID) else row[5],
                        "updated_by": str(row[6]) if isinstance(row[6], uuid.UUID) else row[6],
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
                cursor.execute("""
                    SELECT audit_area_id, framework_id, name, description, created_at, updated_at, created_by, updated_by
                    FROM intelliaudit_dev.metadata_audit_areas
                    ORDER BY name
                """)
                areas = []
                columns = [desc[0] for desc in cursor.description]
                for row in cursor.fetchall():
                    area_dict = row_to_dict(row, columns)
                    areas.append(area_dict)
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