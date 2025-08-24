from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime, date
from app.config.database_simple import get_db_connection

router = APIRouter(prefix="/user-management", tags=["User Management"])

# ==========
# Pydantic Models
# ==========

class UserCreate(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    role_id: UUID
    department: Optional[str] = Field(None, max_length=100)
    auth_type: Optional[str] = Field(None, max_length=50)
    status: str = Field(default="active", max_length=20)

class UserUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    role_id: Optional[UUID] = None
    department: Optional[str] = Field(None, max_length=100)
    auth_type: Optional[str] = Field(None, max_length=50)
    status: Optional[str] = Field(None, max_length=20)

class UserResponse(BaseModel):
    user_uid: UUID
    first_name: str
    last_name: str
    email: str
    role_id: UUID
    role_name: str
    department: Optional[str]
    auth_type: Optional[str]
    status: str
    last_login_dt: Optional[datetime]
    created_at: datetime
    updated_at: datetime

class RoleResponse(BaseModel):
    role_id: UUID
    role_name: str

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
# User CRUD Operations
# ==========

@router.post("/users", response_model=Dict[str, Any])
async def create_user(user_data: UserCreate):
    """Create a new user"""
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            # Validate role exists
            cur.execute(
                "SELECT role_id FROM intelliaudit_dev.user_role_lkup WHERE role_id = %s AND is_active = TRUE",
                (str(user_data.role_id),)
            )
            if not cur.fetchone():
                raise HTTPException(status_code=400, detail="Invalid or inactive role_id")

            # Check if email already exists
            cur.execute(
                "SELECT user_uid FROM intelliaudit_dev.app_user WHERE email = %s",
                (user_data.email,)
            )
            if cur.fetchone():
                raise HTTPException(status_code=400, detail="Email already exists")

            # Create user
            user_uid = uuid4()
            cur.execute(
                """
                INSERT INTO intelliaudit_dev.app_user (
                    user_uid, first_name, last_name, email, role, department,
                    auth_type, status, created_at, updated_at
                ) VALUES (
                    %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s
                ) RETURNING user_uid
                """,
                (
                    str(user_uid),
                    user_data.first_name,
                    user_data.last_name,
                    user_data.email,
                    str(user_data.role_id),
                    user_data.department,
                    user_data.auth_type,
                    user_data.status,
                    _now(),
                    _now(),
                ),
            )
            
            new_user_id = cur.fetchone()[0]
            conn.commit()
            
            return {
                "user_uid": str(new_user_id),
                "message": "User created successfully"
            }
            
    except HTTPException:
        raise
    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create user: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()

@router.get("/users", response_model=List[UserResponse])
async def get_all_users():
    """Get all users with role information"""
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT 
                    u.user_uid, u.first_name, u.last_name, u.email, u.role,
                    u.department, u.auth_type, u.status, u.last_login_dt,
                    u.created_at, u.updated_at, r.role_name
                FROM intelliaudit_dev.app_user u
                LEFT JOIN intelliaudit_dev.user_role_lkup r ON u.role = r.role_id
                ORDER BY u.created_at DESC
                """
            )
            
            users = []
            for row in cur.fetchall():
                users.append({
                    "user_uid": row[0],
                    "first_name": row[1],
                    "last_name": row[2],
                    "email": row[3],
                    "role_id": row[4],
                    "role_name": row[11] or "Unknown",
                    "department": row[5],
                    "auth_type": row[6],
                    "status": row[7],
                    "last_login_dt": row[8],
                    "created_at": row[9],
                    "updated_at": row[10],
                })
            
            return users
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch users: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()

@router.get("/users/{user_uid}", response_model=UserResponse)
async def get_user_by_id(user_uid: UUID):
    """Get user details by user_uid"""
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT 
                    u.user_uid, u.first_name, u.last_name, u.email, u.role,
                    u.department, u.auth_type, u.status, u.last_login_dt,
                    u.created_at, u.updated_at, r.role_name
                FROM intelliaudit_dev.app_user u
                LEFT JOIN intelliaudit_dev.user_role_lkup r ON u.role = r.role_id
                WHERE u.user_uid = %s
                """,
                (str(user_uid),)
            )
            
            row = cur.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="User not found")
            
            return {
                "user_uid": row[0],
                "first_name": row[1],
                "last_name": row[2],
                "email": row[3],
                "role_id": row[4],
                "role_name": row[11] or "Unknown",
                "department": row[5],
                "auth_type": row[6],
                "status": row[7],
                "last_login_dt": row[8],
                "created_at": row[9],
                "updated_at": row[10],
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch user: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()

@router.put("/users/{user_uid}")
async def update_user(user_uid: UUID, user_data: UserUpdate):
    """Update user information"""
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            # Check if user exists
            cur.execute(
                "SELECT user_uid FROM intelliaudit_dev.app_user WHERE user_uid = %s",
                (str(user_uid),)
            )
            if not cur.fetchone():
                raise HTTPException(status_code=404, detail="User not found")

            # Validate role if being updated
            if user_data.role_id:
                cur.execute(
                    "SELECT role_id FROM intelliaudit_dev.user_role_lkup WHERE role_id = %s AND is_active = TRUE",
                    (str(user_data.role_id),)
                )
                if not cur.fetchone():
                    raise HTTPException(status_code=400, detail="Invalid or inactive role_id")

            # Check email uniqueness if being updated
            if user_data.email:
                cur.execute(
                    "SELECT user_uid FROM intelliaudit_dev.app_user WHERE email = %s AND user_uid != %s",
                    (user_data.email, str(user_uid))
                )
                if cur.fetchone():
                    raise HTTPException(status_code=400, detail="Email already exists")

            # Build update query
            fields = []
            values = []
            mapping = user_data.model_dump(exclude_unset=True)
            
            for col, val in mapping.items():
                col_db = {
                    "first_name": "first_name",
                    "last_name": "last_name",
                    "email": "email",
                    "role_id": "role",
                    "department": "department",
                    "auth_type": "auth_type",
                    "status": "status",
                }[col]
                fields.append(f"{col_db} = %s")
                if col == "role_id":
                    values.append(str(val))
                else:
                    values.append(val)

            if not fields:
                return {"message": "No updates provided"}

            fields.append("updated_at = %s")
            values.append(_now())
            values.append(str(user_uid))

            cur.execute(
                f"""
                UPDATE intelliaudit_dev.app_user
                SET {', '.join(fields)}
                WHERE user_uid = %s
                """,
                tuple(values),
            )
            
            conn.commit()
            return {"message": "User updated successfully"}
            
    except HTTPException:
        raise
    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update user: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()

@router.delete("/users/{user_uid}")
async def delete_user(user_uid: UUID):
    """Delete a user"""
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            # Check if user exists
            cur.execute(
                "SELECT user_uid FROM intelliaudit_dev.app_user WHERE user_uid = %s",
                (str(user_uid),)
            )
            if not cur.fetchone():
                raise HTTPException(status_code=404, detail="User not found")

            # Delete user
            cur.execute(
                "DELETE FROM intelliaudit_dev.app_user WHERE user_uid = %s",
                (str(user_uid),)
            )
            
            conn.commit()
            return {"message": "User deleted successfully"}
            
    except HTTPException:
        raise
    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete user: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()

# ==========
# Role Management
# ==========

@router.get("/roles", response_model=List[RoleResponse])
async def get_active_roles():
    """Get all active roles"""
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT role_id, role_name
                FROM intelliaudit_dev.user_role_lkup
                WHERE is_active = TRUE
                ORDER BY role_name
                """
            )
            
            roles = []
            for row in cur.fetchall():
                roles.append({
                    "role_id": row[0],
                    "role_name": row[1],
                })
            
            return roles
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch roles: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()
