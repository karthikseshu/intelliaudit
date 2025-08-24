from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime, date
from app.config.database_simple import get_db_connection

router = APIRouter(prefix="/project-management", tags=["Project Management"])

# ==========
# Pydantic Models
# ==========

class ProjectCreate(BaseModel):
    project_name: str = Field(..., min_length=1, max_length=200)
    project_desc: Optional[str] = Field(None, max_length=1000)
    status: str = Field(default="active", max_length=50)
    start_dt: Optional[date] = None
    end_dt: Optional[date] = None
    framework_ids: List[UUID] = Field(..., min_items=1)
    user_ids: List[UUID] = Field(..., min_items=1)

class ProjectUpdate(BaseModel):
    project_name: Optional[str] = Field(None, min_length=1, max_length=200)
    project_desc: Optional[str] = Field(None, max_length=1000)
    status: Optional[str] = Field(None, max_length=50)
    start_dt: Optional[date] = None
    end_dt: Optional[date] = None
    framework_ids: Optional[List[UUID]] = None
    user_ids: Optional[List[UUID]] = None

class ProjectResponse(BaseModel):
    project_id: UUID
    project_name: str
    project_desc: Optional[str]
    status: str
    timeline: Dict[str, Any]
    users: List[Dict[str, Any]]
    frameworks: List[Dict[str, Any]]
    project_stats: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

class ProjectSummaryResponse(BaseModel):
    project_id: UUID
    project_name: str
    project_desc: Optional[str]
    status: str
    timeline: Dict[str, Any]
    users: List[Dict[str, Any]]
    frameworks: List[Dict[str, Any]]
    project_stats: Dict[str, Any]

# ==========
# Helper Functions
# ==========

def _now():
    return datetime.utcnow()

def _calculate_duration_days(start_dt: date, end_dt: date) -> int:
    """Calculate duration in days between two dates"""
    if start_dt and end_dt:
        return (end_dt - start_dt).days
    return 0

# ==========
# Project CRUD Operations
# ==========

@router.post("/projects", response_model=Dict[str, Any])
async def create_project(project_data: ProjectCreate):
    """Create a new project with framework and user assignments"""
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            # Validate frameworks exist
            framework_placeholders = ','.join(['%s'] * len(project_data.framework_ids))
            cur.execute(
                f"SELECT framework_id FROM intelliaudit_dev.config_frameworks WHERE framework_id IN ({framework_placeholders})",
                [str(fw_id) for fw_id in project_data.framework_ids]
            )
            valid_frameworks = cur.fetchall()
            if len(valid_frameworks) != len(project_data.framework_ids):
                raise HTTPException(status_code=400, detail="One or more framework IDs are invalid")

            # Validate users exist
            user_placeholders = ','.join(['%s'] * len(project_data.user_ids))
            cur.execute(
                f"SELECT user_uid FROM intelliaudit_dev.app_user WHERE user_uid IN ({user_placeholders})",
                [str(user_id) for user_id in project_data.user_ids]
            )
            valid_users = cur.fetchall()
            if len(valid_users) != len(project_data.user_ids):
                raise HTTPException(status_code=400, detail="One or more user IDs are invalid")

            # Create project
            project_id = uuid4()
            cur.execute(
                """
                INSERT INTO intelliaudit_dev.projects (
                    project_id, project_name, project_desc, status, start_dt, end_dt,
                    created_at, updated_at
                ) VALUES (
                    %s, %s, %s, %s, %s, %s,
                    %s, %s
                ) RETURNING project_id
                """,
                (
                    str(project_id),
                    project_data.project_name,
                    project_data.project_desc,
                    project_data.status,
                    project_data.start_dt,
                    project_data.end_dt,
                    _now(),
                    _now(),
                ),
            )
            
            new_project_id = cur.fetchone()[0]

            # Assign frameworks to project
            for framework_id in project_data.framework_ids:
                cur.execute(
                    """
                    INSERT INTO intelliaudit_dev.projects_audit_frameworks (
                        project_id, aud_frmwk_id, created_at, updated_at
                    ) VALUES (
                        %s, %s, %s, %s
                    )
                    """,
                    (
                        str(new_project_id),
                        str(framework_id),
                        _now(),
                        _now(),
                    ),
                )

            # Assign users to project
            for user_id in project_data.user_ids:
                cur.execute(
                    """
                    INSERT INTO intelliaudit_dev.projects_users (
                        project_id, user_uid, created_at, updated_at
                    ) VALUES (
                        %s, %s, %s, %s
                    )
                    """,
                    (
                        str(new_project_id),
                        str(user_id),
                        _now(),
                        _now(),
                    ),
                )
            
            conn.commit()
            
            return {
                "project_id": str(new_project_id),
                "message": "Project created successfully"
            }
            
    except HTTPException:
        raise
    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create project: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()

@router.get("/projects", response_model=List[ProjectSummaryResponse])
async def get_all_projects():
    """Get all projects with comprehensive information"""
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            # Get all projects
            cur.execute(
                """
                SELECT 
                    p.project_id, p.project_name, p.project_desc, p.status,
                    p.start_dt, p.end_dt, p.created_at, p.updated_at
                FROM intelliaudit_dev.projects p
                ORDER BY p.created_at DESC
                """
            )
            
            projects = []
            for row in cur.fetchall():
                project_id, project_name, project_desc, status, start_dt, end_dt, created_at, updated_at = row
                
                # Get frameworks for this project
                cur.execute(
                    """
                    SELECT f.framework_id, f.framework_name
                    FROM intelliaudit_dev.projects_audit_frameworks paf
                    JOIN intelliaudit_dev.config_frameworks f ON paf.aud_frmwk_id = f.framework_id
                    WHERE paf.project_id = %s
                    """,
                    (str(project_id),)
                )
                frameworks = [
                    {"framework_id": str(fw[0]), "framework_name": fw[1]}
                    for fw in cur.fetchall()
                ]

                # Get users for this project
                cur.execute(
                    """
                    SELECT u.user_uid, u.first_name, u.last_name, r.role_name
                    FROM intelliaudit_dev.projects_users pu
                    JOIN intelliaudit_dev.app_user u ON pu.user_uid = u.user_uid
                    LEFT JOIN intelliaudit_dev.user_role_lkup r ON u.role = r.role_id
                    WHERE pu.project_id = %s
                    """,
                    (str(project_id),)
                )
                users = [
                    {
                        "user_uid": str(user[0]),
                        "first_name": user[1],
                        "last_name": user[2],
                        "role": user[3] or "Unknown"
                    }
                    for user in cur.fetchall()
                ]

                # Calculate timeline and stats
                duration = _calculate_duration_days(start_dt, end_dt) if start_dt and end_dt else 0
                
                timeline = {
                    "start_date": start_dt.isoformat() if start_dt else None,
                    "end_date": end_dt.isoformat() if end_dt else None,
                    "duration": duration
                }

                project_stats = {
                    "frameworks_count": len(frameworks),
                    "users_count": len(users),
                    "duration": duration
                }

                projects.append({
                    "project_id": project_id,
                    "project_name": project_name,
                    "project_desc": project_desc,
                    "status": status,
                    "timeline": timeline,
                    "users": users,
                    "frameworks": frameworks,
                    "project_stats": project_stats
                })
            
            return projects
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch projects: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()

@router.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project_by_id(project_id: UUID):
    """Get project details by project_id"""
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            # Get project details
            cur.execute(
                """
                SELECT 
                    p.project_id, p.project_name, p.project_desc, p.status,
                    p.start_dt, p.end_dt, p.created_at, p.updated_at
                FROM intelliaudit_dev.projects p
                WHERE p.project_id = %s
                """,
                (str(project_id),)
            )
            
            row = cur.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Project not found")
            
            project_id, project_name, project_desc, status, start_dt, end_dt, created_at, updated_at = row
            
            # Get frameworks for this project
            cur.execute(
                """
                SELECT f.framework_id, f.framework_name
                FROM intelliaudit_dev.projects_audit_frameworks paf
                JOIN intelliaudit_dev.config_frameworks f ON paf.aud_frmwk_id = f.framework_id
                WHERE paf.project_id = %s
                """,
                (str(project_id),)
            )
            frameworks = [
                {"framework_id": str(fw[0]), "framework_name": fw[1]}
                for fw in cur.fetchall()
            ]

            # Get users for this project
            cur.execute(
                """
                SELECT u.user_uid, u.first_name, u.last_name, r.role_name
                FROM intelliaudit_dev.projects_users pu
                JOIN intelliaudit_dev.app_user u ON pu.user_uid = u.user_uid
                LEFT JOIN intelliaudit_dev.user_role_lkup r ON u.role = r.role_id
                WHERE pu.project_id = %s
                """,
                (str(project_id),)
            )
            users = [
                {
                    "user_uid": str(user[0]),
                    "first_name": user[1],
                    "last_name": user[2],
                    "role": user[3] or "Unknown"
                }
                for user in cur.fetchall()
            ]

            # Calculate timeline and stats
            duration = _calculate_duration_days(start_dt, end_dt) if start_dt and end_dt else 0
            
            timeline = {
                "start_date": start_dt.isoformat() if start_dt else None,
                "end_date": end_dt.isoformat() if end_dt else None,
                "duration": duration
            }

            project_stats = {
                "frameworks_count": len(frameworks),
                "users_count": len(users),
                "duration": duration
            }

            return {
                "project_id": project_id,
                "project_name": project_name,
                "project_desc": project_desc,
                "status": status,
                "timeline": timeline,
                "users": users,
                "frameworks": frameworks,
                "project_stats": project_stats,
                "created_at": created_at,
                "updated_at": updated_at
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch project: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()

@router.put("/projects/{project_id}")
async def update_project(project_id: UUID, project_data: ProjectUpdate):
    """Update project information"""
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            # Check if project exists
            cur.execute(
                "SELECT project_id FROM intelliaudit_dev.projects WHERE project_id = %s",
                (str(project_id),)
            )
            if not cur.fetchone():
                raise HTTPException(status_code=404, detail="Project not found")

            # Build update query for basic project fields
            basic_fields = []
            basic_values = []
            basic_mapping = {
                "project_name": project_data.project_name,
                "project_desc": project_data.project_desc,
                "status": project_data.status,
                "start_dt": project_data.start_dt,
                "end_dt": project_data.end_dt,
            }
            
            for col, val in basic_mapping.items():
                if val is not None:
                    basic_fields.append(f"{col} = %s")
                    basic_values.append(val)

            # Update basic project fields if any
            if basic_fields:
                basic_fields.append("updated_at = %s")
                basic_values.append(_now())
                basic_values.append(str(project_id))

                cur.execute(
                    f"""
                    UPDATE intelliaudit_dev.projects
                    SET {', '.join(basic_fields)}
                    WHERE project_id = %s
                    """,
                    tuple(basic_values),
                )

            # Update frameworks if provided
            if project_data.framework_ids is not None:
                # Validate frameworks exist
                framework_placeholders = ','.join(['%s'] * len(project_data.framework_ids))
                cur.execute(
                    f"SELECT framework_id FROM intelliaudit_dev.config_frameworks WHERE framework_id IN ({framework_placeholders})",
                    [str(fw_id) for fw_id in project_data.framework_ids]
                )
                valid_frameworks = cur.fetchall()
                if len(valid_frameworks) != len(project_data.framework_ids):
                    raise HTTPException(status_code=400, detail="One or more framework IDs are invalid")

                # Delete existing framework assignments
                cur.execute(
                    "DELETE FROM intelliaudit_dev.projects_audit_frameworks WHERE project_id = %s",
                    (str(project_id),)
                )

                # Insert new framework assignments
                for framework_id in project_data.framework_ids:
                    cur.execute(
                        """
                        INSERT INTO intelliaudit_dev.projects_audit_frameworks (
                            project_id, aud_frmwk_id, created_at, updated_at
                        ) VALUES (
                            %s, %s, %s, %s
                        )
                        """,
                        (
                            str(project_id),
                            str(framework_id),
                            _now(),
                            _now(),
                        ),
                    )

            # Update users if provided
            if project_data.user_ids is not None:
                # Validate users exist
                user_placeholders = ','.join(['%s'] * len(project_data.user_ids))
                cur.execute(
                    f"SELECT user_uid FROM intelliaudit_dev.app_user WHERE user_uid IN ({user_placeholders})",
                    [str(user_id) for user_id in project_data.user_ids]
                )
                valid_users = cur.fetchall()
                if len(valid_users) != len(project_data.user_ids):
                    raise HTTPException(status_code=400, detail="One or more user IDs are invalid")

                # Delete existing user assignments
                cur.execute(
                    "DELETE FROM intelliaudit_dev.projects_users WHERE project_id = %s",
                    (str(project_id),)
                )

                # Insert new user assignments
                for user_id in project_data.user_ids:
                    cur.execute(
                        """
                        INSERT INTO intelliaudit_dev.projects_users (
                            project_id, user_uid, created_at, updated_at
                        ) VALUES (
                            %s, %s, %s, %s
                        )
                        """,
                        (
                            str(project_id),
                            str(user_id),
                            _now(),
                            _now(),
                        ),
                    )
            
            conn.commit()
            return {"message": "Project updated successfully"}
            
    except HTTPException:
        raise
    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update project: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()

@router.delete("/projects/{project_id}")
async def delete_project(project_id: UUID):
    """Delete a project and all its associations"""
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            # Check if project exists
            cur.execute(
                "SELECT project_id FROM intelliaudit_dev.projects WHERE project_id = %s",
                (str(project_id),)
            )
            if not cur.fetchone():
                raise HTTPException(status_code=404, detail="Project not found")

            # Delete project (cascade will handle related records)
            cur.execute(
                "DELETE FROM intelliaudit_dev.projects WHERE project_id = %s",
                (str(project_id),)
            )
            
            conn.commit()
            return {"message": "Project deleted successfully"}
            
    except HTTPException:
        raise
    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete project: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()
