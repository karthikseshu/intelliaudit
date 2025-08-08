from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from uuid import UUID, uuid4
from datetime import datetime
from app.config.database_simple import get_db_connection


router = APIRouter(prefix="", tags=["configuration"])


# ==========
# Pydantic models
# ==========

class FrameworkCreate(BaseModel):
    framework_code: str = Field(..., min_length=1)
    version: str = Field(..., min_length=1)
    framework_name: str = Field(..., min_length=1)
    description: Optional[str] = None
    industry_type_id: Optional[UUID] = None  # references config_metadata_types(metadata_type_id)


class FrameworkUpdate(BaseModel):
    framework_code: Optional[str] = None
    version: Optional[str] = None
    framework_name: Optional[str] = None
    description: Optional[str] = None
    industry_type_id: Optional[UUID] = None
    is_active: Optional[bool] = None


class ProcessAreaCreate(BaseModel):
    framework_id: UUID
    process_area_code: str
    process_area_name: str
    description: Optional[str] = None
    risk_level_id: Optional[UUID] = None  # metadata FK
    business_function: Optional[str] = None  # NOTE: schema uses VARCHAR(100), not metadata FK
    testing_frequency_id: Optional[UUID] = None  # metadata FK


class ProcessAreaUpdate(BaseModel):
    process_area_code: Optional[str] = None
    process_area_name: Optional[str] = None
    description: Optional[str] = None
    risk_level_id: Optional[UUID] = None
    business_function: Optional[str] = None
    testing_frequency_id: Optional[UUID] = None
    is_active: Optional[bool] = None


class ControlCreate(BaseModel):
    process_area_id: UUID
    control_code: str
    control_statement: str
    control_type_id: Optional[UUID] = None
    risk_rating_id: Optional[UUID] = None
    testing_method_id: Optional[UUID] = None
    frequency_id: Optional[UUID] = None


class ControlUpdate(BaseModel):
    control_code: Optional[str] = None
    control_statement: Optional[str] = None
    control_type_id: Optional[UUID] = None
    risk_rating_id: Optional[UUID] = None
    testing_method_id: Optional[UUID] = None
    frequency_id: Optional[UUID] = None


class CriteriaCreate(BaseModel):
    control_id: UUID
    criteria_code: str
    criteria_statement: str
    pass_fail_threshold: Optional[str] = None  # NOTE: schema has TEXT, not metadata FK
    evaluation_method_id: Optional[UUID] = None
    materiality_level_id: Optional[UUID] = None
    sampling_required: bool = False


class CriteriaUpdate(BaseModel):
    criteria_code: Optional[str] = None
    criteria_statement: Optional[str] = None
    pass_fail_threshold: Optional[str] = None
    evaluation_method_id: Optional[UUID] = None
    materiality_level_id: Optional[UUID] = None
    sampling_required: Optional[bool] = None


class RuleCreate(BaseModel):
    criteria_id: UUID
    rule_name: str
    logic_type_id: Optional[UUID] = None
    rule_logic: Optional[str] = None
    keywords_patterns: Optional[str] = None
    confidence_threshold: Optional[float] = Field(None, ge=0.0, le=1.0)
    scoring_weight: Optional[float] = Field(None, ge=0.0, le=1.0)
    status_id: Optional[UUID] = None


class RuleUpdate(BaseModel):
    rule_name: Optional[str] = None
    logic_type_id: Optional[UUID] = None
    rule_logic: Optional[str] = None
    keywords_patterns: Optional[str] = None
    confidence_threshold: Optional[float] = Field(None, ge=0.0, le=1.0)
    scoring_weight: Optional[float] = Field(None, ge=0.0, le=1.0)
    status_id: Optional[UUID] = None


# ==========
# Helper
# ==========

def _now():
    return datetime.utcnow()


# ==========
# Frameworks
# ==========

@router.post("/config/frameworks")
async def create_framework(payload: FrameworkCreate):
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            framework_id = uuid4()
            cur.execute(
                """
                INSERT INTO intelliaudit_dev.config_frameworks (
                    framework_id, framework_code, framework_name, version,
                    industry_type_id, description, is_active, created_at, updated_at
                ) VALUES (
                    %s, %s, %s, %s,
                    %s, %s, %s, %s, %s
                )
                RETURNING framework_id
                """,
                (
                    str(framework_id),
                    payload.framework_code,
                    payload.framework_name,
                    payload.version,
                    str(payload.industry_type_id) if payload.industry_type_id else None,
                    payload.description,
                    True,
                    _now(),
                    _now(),
                ),
            )
            new_id = cur.fetchone()[0]
            conn.commit()
            return {"framework_id": str(new_id), "message": "Success"}
    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create framework: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()


@router.put("/config/frameworks/{framework_id}")
async def update_framework(framework_id: UUID, payload: FrameworkUpdate):
    try:
        conn = get_db_connection()
        fields = []
        values = []
        mapping = payload.model_dump(exclude_unset=True)
        for col, val in mapping.items():
            col_db = {
                "framework_code": "framework_code",
                "version": "version",
                "framework_name": "framework_name",
                "description": "description",
                "industry_type_id": "industry_type_id",
                "is_active": "is_active",
            }[col]
            fields.append(f"{col_db} = %s")
            if col == "industry_type_id" and val is not None:
                values.append(str(val))
            else:
                values.append(val)

        if not fields:
            return {"message": "No updates provided"}

        fields.append("updated_at = %s")
        values.append(_now())
        values.append(str(framework_id))

        with conn.cursor() as cur:
            cur.execute(
                f"""
                UPDATE intelliaudit_dev.config_frameworks
                SET {', '.join(fields)}
                WHERE framework_id = %s
                """,
                tuple(values),
            )
            if cur.rowcount == 0:
                raise HTTPException(status_code=404, detail="Framework not found")
            conn.commit()
            return {"message": "Success"}
    except HTTPException:
        raise
    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update framework: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()


@router.delete("/config/frameworks/{framework_id}")
async def delete_framework(framework_id: UUID):
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM intelliaudit_dev.config_frameworks WHERE framework_id = %s",
                (str(framework_id),),
            )
            if cur.rowcount == 0:
                raise HTTPException(status_code=404, detail="Framework not found")
            conn.commit()
            return {"message": "Success"}
    except HTTPException:
        raise
    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete framework: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()


# ==========
# Process Areas
# ==========

@router.post("/config/process-areas")
async def create_process_area(payload: ProcessAreaCreate):
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            process_area_id = uuid4()
            cur.execute(
                """
                INSERT INTO intelliaudit_dev.config_process_areas (
                    process_area_id, framework_id, process_area_code, process_area_name,
                    description, risk_level_id, business_function, testing_frequency_id,
                    created_at, updated_at
                ) VALUES (
                    %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s
                ) RETURNING process_area_id
                """,
                (
                    str(process_area_id),
                    str(payload.framework_id),
                    payload.process_area_code,
                    payload.process_area_name,
                    payload.description,
                    str(payload.risk_level_id) if payload.risk_level_id else None,
                    payload.business_function,
                    str(payload.testing_frequency_id) if payload.testing_frequency_id else None,
                    _now(),
                    _now(),
                ),
            )
            new_id = cur.fetchone()[0]
            conn.commit()
            return {"process_area_id": str(new_id), "message": "Success"}
    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create process area: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()


@router.put("/config/process-areas/{process_area_id}")
async def update_process_area(process_area_id: UUID, payload: ProcessAreaUpdate):
    try:
        conn = get_db_connection()
        fields = []
        values = []
        mapping = payload.model_dump(exclude_unset=True)
        for col, val in mapping.items():
            col_db = {
                "process_area_code": "process_area_code",
                "process_area_name": "process_area_name",
                "description": "description",
                "risk_level_id": "risk_level_id",
                "business_function": "business_function",
                "testing_frequency_id": "testing_frequency_id",
                "is_active": "is_active",
            }[col]
            fields.append(f"{col_db} = %s")
            if col in ("risk_level_id", "testing_frequency_id") and val is not None:
                values.append(str(val))
            else:
                values.append(val)

        if not fields:
            return {"message": "No updates provided"}

        fields.append("updated_at = %s")
        values.append(_now())
        values.append(str(process_area_id))

        with conn.cursor() as cur:
            cur.execute(
                f"""
                UPDATE intelliaudit_dev.config_process_areas
                SET {', '.join(fields)}
                WHERE process_area_id = %s
                """,
                tuple(values),
            )
            if cur.rowcount == 0:
                raise HTTPException(status_code=404, detail="Process area not found")
            conn.commit()
            return {"message": "Success"}
    except HTTPException:
        raise
    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update process area: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()


@router.delete("/config/process-areas/{process_area_id}")
async def delete_process_area(process_area_id: UUID):
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM intelliaudit_dev.config_process_areas WHERE process_area_id = %s",
                (str(process_area_id),),
            )
            if cur.rowcount == 0:
                raise HTTPException(status_code=404, detail="Process area not found")
            conn.commit()
            return {"message": "Success"}
    except HTTPException:
        raise
    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete process area: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()


# ==========
# Controls
# ==========

@router.post("/config/controls")
async def create_control(payload: ControlCreate):
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            control_id = uuid4()
            cur.execute(
                """
                INSERT INTO intelliaudit_dev.config_controls (
                    control_id, process_area_id, control_code, control_statement,
                    control_type_id, risk_rating_id, testing_method_id, frequency_id,
                    created_at, updated_at
                ) VALUES (
                    %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s
                ) RETURNING control_id
                """,
                (
                    str(control_id),
                    str(payload.process_area_id),
                    payload.control_code,
                    payload.control_statement,
                    str(payload.control_type_id) if payload.control_type_id else None,
                    str(payload.risk_rating_id) if payload.risk_rating_id else None,
                    str(payload.testing_method_id) if payload.testing_method_id else None,
                    str(payload.frequency_id) if payload.frequency_id else None,
                    _now(),
                    _now(),
                ),
            )
            new_id = cur.fetchone()[0]
            conn.commit()
            return {"control_id": str(new_id), "message": "Success"}
    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create control: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()


@router.put("/config/controls/{control_id}")
async def update_control(control_id: UUID, payload: ControlUpdate):
    try:
        conn = get_db_connection()
        fields = []
        values = []
        mapping = payload.model_dump(exclude_unset=True)
        for col, val in mapping.items():
            col_db = {
                "control_code": "control_code",
                "control_statement": "control_statement",
                "control_type_id": "control_type_id",
                "risk_rating_id": "risk_rating_id",
                "testing_method_id": "testing_method_id",
                "frequency_id": "frequency_id",
            }[col]
            fields.append(f"{col_db} = %s")
            if col.endswith("_id") and val is not None:
                values.append(str(val))
            else:
                values.append(val)

        if not fields:
            return {"message": "No updates provided"}

        fields.append("updated_at = %s")
        values.append(_now())
        values.append(str(control_id))

        with conn.cursor() as cur:
            cur.execute(
                f"""
                UPDATE intelliaudit_dev.config_controls
                SET {', '.join(fields)}
                WHERE control_id = %s
                """,
                tuple(values),
            )
            if cur.rowcount == 0:
                raise HTTPException(status_code=404, detail="Control not found")
            conn.commit()
            return {"message": "Success"}
    except HTTPException:
        raise
    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update control: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()


@router.delete("/config/controls/{control_id}")
async def delete_control(control_id: UUID):
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM intelliaudit_dev.config_controls WHERE control_id = %s",
                (str(control_id),),
            )
            if cur.rowcount == 0:
                raise HTTPException(status_code=404, detail="Control not found")
            conn.commit()
            return {"message": "Success"}
    except HTTPException:
        raise
    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete control: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()


# ==========
# Criteria
# ==========

@router.post("/config/criteria")
async def create_criteria(payload: CriteriaCreate):
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            criteria_id = uuid4()
            cur.execute(
                """
                INSERT INTO intelliaudit_dev.config_criteria (
                    criteria_id, control_id, criteria_code, criteria_statement,
                    pass_fail_threshold, evaluation_method_id, materiality_level_id,
                    sampling_required, created_at, updated_at
                ) VALUES (
                    %s, %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s
                ) RETURNING criteria_id
                """,
                (
                    str(criteria_id),
                    str(payload.control_id),
                    payload.criteria_code,
                    payload.criteria_statement,
                    payload.pass_fail_threshold,
                    str(payload.evaluation_method_id) if payload.evaluation_method_id else None,
                    str(payload.materiality_level_id) if payload.materiality_level_id else None,
                    payload.sampling_required,
                    _now(),
                    _now(),
                ),
            )
            new_id = cur.fetchone()[0]
            conn.commit()
            return {"criteria_id": str(new_id), "message": "Success"}
    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create criteria: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()


@router.put("/config/criteria/{criteria_id}")
async def update_criteria(criteria_id: UUID, payload: CriteriaUpdate):
    try:
        conn = get_db_connection()
        fields = []
        values = []
        mapping = payload.model_dump(exclude_unset=True)
        for col, val in mapping.items():
            col_db = {
                "criteria_code": "criteria_code",
                "criteria_statement": "criteria_statement",
                "pass_fail_threshold": "pass_fail_threshold",
                "evaluation_method_id": "evaluation_method_id",
                "materiality_level_id": "materiality_level_id",
                "sampling_required": "sampling_required",
            }[col]
            fields.append(f"{col_db} = %s")
            if col.endswith("_id") and val is not None:
                values.append(str(val))
            else:
                values.append(val)

        if not fields:
            return {"message": "No updates provided"}

        fields.append("updated_at = %s")
        values.append(_now())
        values.append(str(criteria_id))

        with conn.cursor() as cur:
            cur.execute(
                f"""
                UPDATE intelliaudit_dev.config_criteria
                SET {', '.join(fields)}
                WHERE criteria_id = %s
                """,
                tuple(values),
            )
            if cur.rowcount == 0:
                raise HTTPException(status_code=404, detail="Criteria not found")
            conn.commit()
            return {"message": "Success"}
    except HTTPException:
        raise
    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update criteria: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()


@router.delete("/config/criteria/{criteria_id}")
async def delete_criteria(criteria_id: UUID):
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM intelliaudit_dev.config_criteria WHERE criteria_id = %s",
                (str(criteria_id),),
            )
            if cur.rowcount == 0:
                raise HTTPException(status_code=404, detail="Criteria not found")
            conn.commit()
            return {"message": "Success"}
    except HTTPException:
        raise
    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete criteria: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()


# ==========
# Rules
# ==========

@router.post("/config/rules")
async def create_rule(payload: RuleCreate):
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            rule_id = uuid4()
            cur.execute(
                """
                INSERT INTO intelliaudit_dev.config_assessment_rules (
                    rule_id, criteria_id, rule_name, logic_type_id, rule_logic,
                    keywords_patterns, confidence_threshold, scoring_weight, status_id,
                    created_at, updated_at
                ) VALUES (
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s
                ) RETURNING rule_id
                """,
                (
                    str(rule_id),
                    str(payload.criteria_id),
                    payload.rule_name,
                    str(payload.logic_type_id) if payload.logic_type_id else None,
                    payload.rule_logic,
                    payload.keywords_patterns,
                    payload.confidence_threshold,
                    payload.scoring_weight,
                    str(payload.status_id) if payload.status_id else None,
                    _now(),
                    _now(),
                ),
            )
            new_id = cur.fetchone()[0]
            conn.commit()
            return {"rule_id": str(new_id), "message": "Success"}
    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create rule: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()


@router.put("/config/rules/{rule_id}")
async def update_rule(rule_id: UUID, payload: RuleUpdate):
    try:
        conn = get_db_connection()
        fields = []
        values = []
        mapping = payload.model_dump(exclude_unset=True)
        for col, val in mapping.items():
            col_db = {
                "rule_name": "rule_name",
                "logic_type_id": "logic_type_id",
                "rule_logic": "rule_logic",
                "keywords_patterns": "keywords_patterns",
                "confidence_threshold": "confidence_threshold",
                "scoring_weight": "scoring_weight",
                "status_id": "status_id",
            }[col]
            fields.append(f"{col_db} = %s")
            if col.endswith("_id") and val is not None:
                values.append(str(val))
            else:
                values.append(val)

        if not fields:
            return {"message": "No updates provided"}

        fields.append("updated_at = %s")
        values.append(_now())
        values.append(str(rule_id))

        with conn.cursor() as cur:
            cur.execute(
                f"""
                UPDATE intelliaudit_dev.config_assessment_rules
                SET {', '.join(fields)}
                WHERE rule_id = %s
                """,
                tuple(values),
            )
            if cur.rowcount == 0:
                raise HTTPException(status_code=404, detail="Rule not found")
            conn.commit()
            return {"message": "Success"}
    except HTTPException:
        raise
    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update rule: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()


@router.delete("/config/rules/{rule_id}")
async def delete_rule(rule_id: UUID):
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM intelliaudit_dev.config_assessment_rules WHERE rule_id = %s",
                (str(rule_id),),
            )
            if cur.rowcount == 0:
                raise HTTPException(status_code=404, detail="Rule not found")
            conn.commit()
            return {"message": "Success"}
    except HTTPException:
        raise
    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete rule: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()


# ==========
# Framework Summary (counts + full hierarchy)
# ==========

@router.get("/config/frameworks/{framework_id}/summary")
async def get_framework_summary(framework_id: UUID):
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            # Framework
            cur.execute(
                """
                SELECT framework_id, framework_code, framework_name, version, description
                FROM intelliaudit_dev.config_frameworks
                WHERE framework_id = %s
                """,
                (str(framework_id),),
            )
            fw = cur.fetchone()
            if not fw:
                raise HTTPException(status_code=404, detail="Framework not found")

            framework_info = {
                "framework_id": str(fw[0]),
                "framework_code": fw[1],
                "framework_name": fw[2],
                "version": fw[3],
                "description": fw[4],
            }

            # Process Areas
            cur.execute(
                """
                SELECT process_area_id, process_area_code, process_area_name
                FROM intelliaudit_dev.config_process_areas
                WHERE framework_id = %s
                ORDER BY process_area_code
                """,
                (str(framework_id),),
            )
            pa_rows = cur.fetchall()

            process_areas: List[Dict[str, Any]] = []
            total_controls = 0
            total_criteria = 0
            total_rules = 0

            for pa_id, pa_code, pa_name in pa_rows:
                # Controls for this process area
                cur.execute(
                    """
                    SELECT control_id, control_code, control_statement
                    FROM intelliaudit_dev.config_controls
                    WHERE process_area_id = %s
                    ORDER BY control_code
                    """,
                    (str(pa_id),),
                )
                ctrl_rows = cur.fetchall()

                controls: List[Dict[str, Any]] = []
                for control_id, control_code, control_statement in ctrl_rows:
                    # Criteria for this control
                    cur.execute(
                        """
                        SELECT criteria_id, criteria_code, criteria_statement
                        FROM intelliaudit_dev.config_criteria
                        WHERE control_id = %s
                        ORDER BY criteria_code
                        """,
                        (str(control_id),),
                    )
                    crit_rows = cur.fetchall()

                    criterias: List[Dict[str, Any]] = []
                    for criteria_id, criteria_code, criteria_statement in crit_rows:
                        # Rules for this criteria
                        cur.execute(
                            """
                            SELECT rule_id, rule_name
                            FROM intelliaudit_dev.config_assessment_rules
                            WHERE criteria_id = %s
                            ORDER BY rule_name
                            """,
                            (str(criteria_id),),
                        )
                        rule_rows = cur.fetchall()

                        rules_list = [
                            {"rule_id": str(rid), "rule_name": rname}
                            for (rid, rname) in rule_rows
                        ]

                        criterias.append(
                            {
                                "criteria_id": str(criteria_id),
                                "criteria_code": criteria_code,
                                "criteria_name": criteria_statement,
                                "rules": rules_list,
                            }
                        )
                        total_rules += len(rule_rows)

                    controls.append(
                        {
                            "control_id": str(control_id),
                            "control_code": control_code,
                            "control_name": control_statement,
                            "criteria": criterias,
                        }
                    )
                    total_criteria += len(crit_rows)

                process_areas.append(
                    {
                        "process_area_id": str(pa_id),
                        "process_area_code": pa_code,
                        "process_area_name": pa_name,
                        "controls": controls,
                    }
                )
                total_controls += len(ctrl_rows)

            summary = {
                "framework": framework_info,
                "counts": {
                    "process_areas": len(pa_rows),
                    "controls": total_controls,
                    "criteria": total_criteria,
                    "rules": total_rules,
                },
                "hierarchy": {
                    "process_areas": process_areas
                },
            }

            return summary
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to build framework summary: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()




@router.get("/config/metadata-types/grouped")
async def list_active_metadata_types_grouped():
    """Return active metadata types grouped by type_category as a nested array."""
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT metadata_type_id, type_category, type_value, type_code,
                       display_order, description
                FROM intelliaudit_dev.config_metadata_types
                WHERE is_active = TRUE
                ORDER BY type_category, display_order, type_value
                """
            )
            rows = cur.fetchall()
            grouped: Dict[str, List[Dict[str, Any]]] = {}
            for r in rows:
                cat = r[1]
                item = {
                    "metadata_type_id": str(r[0]),
                    "type_value": r[2],
                    "type_code": r[3],
                    "display_order": r[4],
                    "description": r[5],
                }
                grouped.setdefault(cat, []).append(item)

            # Convert to nested array format
            result = [
                {"type_category": cat, "values": items}
                for cat, items in grouped.items()
            ]
            # Optional: stable sort categories alphabetically
            result.sort(key=lambda x: x["type_category"]) 
            return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch grouped metadata types: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()


