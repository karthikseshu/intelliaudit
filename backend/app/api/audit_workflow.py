from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, date
from uuid import uuid4, UUID
import psycopg
import json
import uuid
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.config.database import get_db
from app.config.database_simple import get_db_connection

router = APIRouter(tags=["audit-workflow"])

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

class AuditRequest(BaseModel):
    audit_request_id: Optional[UUID] = None
    audit_name: str
    framework_id: str
    audit_areas: List[str] = []
    checklist: Optional[Dict[str, Any]] = None
    status: str = "not_started"
    current_step: Optional[str] = None
    started_at: Optional[datetime] = None
    last_active_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    due_date: Optional[date] = None
    description: Optional[str] = None
    compliance_score: Optional[float] = None
    risk_assessment: Optional[str] = None
    final_comments: Optional[str] = None
    created_by: Optional[UUID] = None
    created_at: Optional[datetime] = None

class AuditRequestResponse(BaseModel):
    audit_request_id: UUID
    audit_name: str

class Document(BaseModel):
    id: Optional[UUID] = None
    audit_id: UUID
    name: str
    file_path: Optional[str] = None
    file_type: Optional[str] = None
    file_size_kb: Optional[float] = None
    doc_type: Optional[str] = None
    audit_area: Optional[str] = None
    upload_source: str = "manual"
    status: str = "pending"
    ai_classification: Optional[Dict[str, Any]] = None
    uploaded_by: Optional[UUID] = None
    uploaded_at: Optional[datetime] = None

class DocumentCollaborator(BaseModel):
    id: Optional[UUID] = None
    document_id: UUID
    user_id: UUID
    role: str
    joined_at: Optional[datetime] = None

class DocumentReview(BaseModel):
    id: Optional[UUID] = None
    document_id: UUID
    user_id: UUID
    review_step: str
    status: str = "pending"
    comments: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    last_updated: Optional[datetime] = None

class Evidence(BaseModel):
    id: Optional[UUID] = None
    audit_id: UUID
    document_id: UUID
    audit_area: str
    checklist_item: str
    definition: Optional[str] = None
    page_number: Optional[int] = None
    extracted_text: str
    ai_explanation: Optional[Dict[str, Any]] = None
    confidence_score: Optional[float] = None
    reviewed_by: Optional[UUID] = None
    review_status: str = "pending"
    reviewed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

class AuditFinding(BaseModel):
    id: Optional[UUID] = None
    audit_id: UUID
    finding_type: str
    description: str
    ai_suggestion: Optional[str] = None
    reviewed_by: Optional[UUID] = None
    resolved: bool = False
    created_at: Optional[datetime] = None

class Report(BaseModel):
    id: Optional[UUID] = None
    audit_id: UUID
    report_type: str
    file_path: Optional[str] = None
    generated_by: Optional[UUID] = None
    references: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None

class AuditLog(BaseModel):
    id: Optional[UUID] = None
    related_type: str
    related_id: UUID
    action: str
    performed_by: Optional[UUID] = None
    is_ai_action: bool = False
    ai_details: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None

class AuditProgress(BaseModel):
    id: Optional[UUID] = None
    audit_id: UUID
    user_id: UUID
    document_id: Optional[UUID] = None
    current_step: str
    status: str = "in_progress"
    started_at: Optional[datetime] = None
    resumed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    time_spent_seconds: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None
    updated_at: Optional[datetime] = None

class UserActivityLog(BaseModel):
    id: Optional[UUID] = None
    audit_id: UUID
    user_id: UUID
    action: str
    details: Optional[Dict[str, Any]] = None
    timestamp: Optional[datetime] = None

# API Endpoints

@router.get("/frameworks", response_model=List[Dict[str, Any]])
# async def get_audit_frameworks(db: Session = Depends(get_db)):
#     """Get all audit frameworks with their related audit areas"""
#     try:
#         result = db.execute(text("""
#             SELECT 
#                 f.id,
#                 f.name,
#                 f.version,
#                 json_agg(
#                     json_build_object(
#                         'id', aa.id,
#                         'name', aa.name,
#                         'description', aa.description
#                     )
#                 ) as audit_areas
#             FROM metadata_audit_frameworks f
#             LEFT JOIN metadata_audit_areas aa ON f.id = aa.audit_framework_id
#             GROUP BY f.id, f.name, f.version
#             ORDER BY f.name
#         """))
#         frameworks = []
#         columns = [desc[0] for desc in result.cursor.description]
#         for row in result:
#             row_dict = row_to_dict(row, columns)
#             # Convert audit_areas UUIDs to strings in nested list
#             audit_areas = row_dict.get('audit_areas', [])
#             if isinstance(audit_areas, list):
#                 for area in audit_areas:
#                     for k, v in area.items():
#                         if isinstance(v, uuid.UUID):
#                             area[k] = str(v)
#             row_dict['audit_areas'] = audit_areas
#             frameworks.append(row_dict)
#         return frameworks
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to fetch audit frameworks: {str(e)}")
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

@router.get("/areas", response_model=List[Dict[str, Any]])
async def get_audit_areas(db: Session = Depends(get_db)):
    """Get all audit areas"""
    try:
        result = db.execute(text("SELECT id, audit_framework_id, name, description, created_at FROM metadata_audit_areas ORDER BY name"))
        areas = []
        columns = [desc[0] for desc in result.cursor.description]
        for row in result:
            area_dict = row_to_dict(row, columns)
            areas.append(area_dict)
        return areas
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch audit areas: {str(e)}")

# @router.post("/audits", response_model=AuditRequest)
# async def create_audit_request(audit: AuditRequest, db: Session = Depends(get_db)):
#     """Create a new audit request"""
#     try:
#         audit_id = uuid4()
#         now = datetime.utcnow()
#         conn = get_db_connection()
        
#         # query = text("""
#         #     INSERT INTO audit_requests (
#         #         id, audit_name, audit_type, framework_version, audit_areas, checklist,
#         #         status, current_step, started_at, last_active_at, completed_at, due_date,
#         #         description, compliance_score, risk_assessment, final_comments, created_by, created_at
#         #     ) VALUES (
#         #         :id, :audit_name, :audit_type, :framework_version, :audit_areas, :checklist,
#         #         :status, :current_step, :started_at, :last_active_at, :completed_at, :due_date,
#         #         :description, :compliance_score, :risk_assessment, :final_comments, :created_by, :created_at
#         #     ) RETURNING *
#         # """)
#         query = text("""
#             INSERT INTO audit_requests (
#                 id, audit_name, framework_id, audit_areas,
#                 status, current_step, started_at, last_active_at, created_by, created_at
#             ) VALUES (
#                 :id, :audit_name, :framework_id, :audit_areas,
#                 :status, :current_step, :started_at, :last_active_at, :created_by, :created_at
#             ) RETURNING *
#         """)
        
#         result = db.execute(query, {
#             "id": str(audit_id),
#             "audit_name": audit.audit_name,
#             "framework_id": audit.framework_id,
#             "audit_areas": audit.audit_areas,
#             "status": audit.status,
#             "current_step": audit.current_step,
#             "started_at": now,
#             "last_active_at": now,
#             "created_by": str(audit.created_by) if audit.created_by else None,
#             "created_at": now
#         })
        
#         db.commit()
#         row = result.fetchone()
        
#         return AuditRequest(
#             id=row.id,
#             audit_name=row.audit_name
#         )
#     except Exception as e:
#         db.rollback()
#         raise HTTPException(status_code=500, detail=f"Failed to create audit request: {str(e)}")

@router.post("/audits", response_model=AuditRequestResponse)
async def create_audit_request(audit: AuditRequest):
    """Create a new audit request using psycopg2"""
    try:
        audit_request_id = uuid4()
        now = datetime.utcnow()

        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO intelliaudit_dev.audit_requests (
                        audit_request_id, audit_name, framework_id, audit_areas,
                        status, current_step, started_at, last_active_at, created_at
                    ) VALUES (
                        %s, %s, %s, %s,
                        %s, %s, %s, %s, %s
                    ) RETURNING audit_request_id, audit_name
                """, (
                    str(audit_request_id),
                    audit.audit_name,
                    str(audit.framework_id) if audit.framework_id else None,
                    audit.audit_areas,  # Should be a list or JSON-serializable
                    audit.status,
                    audit.current_step,
                    now,
                    now,
                    now
                ))

                row = cursor.fetchone()
                conn.commit()

                return {
                    "audit_request_id": str(row[0]),
                    "audit_name": row[1]
                }

        finally:
            conn.close()

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create audit request: {str(e)}")

@router.get("/audits", response_model=List[Dict[str, Any]])
async def get_audit_requests(db: Session = Depends(get_db)):
    """Get all audit requests"""
    try:
        result = db.execute(text("SELECT * FROM audit_requests ORDER BY created_at DESC"))
        audits = []
        columns = [desc[0] for desc in result.cursor.description]
        for row in result:
            audits.append(row_to_dict(row, columns))
        return audits
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch audit requests: {str(e)}")

@router.get("/audits/{audit_id}", response_model=Dict[str, Any])
async def get_audit_request(audit_id: UUID, db: Session = Depends(get_db)):
    """Get a specific audit request"""
    try:
        result = db.execute(text("SELECT * FROM audit_requests WHERE id = :audit_id"), {"audit_id": str(audit_id)})
        row = result.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Audit request not found")
        
        columns = [desc[0] for desc in result.cursor.description]
        return row_to_dict(row, columns)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch audit request: {str(e)}")

@router.post("/documents", response_model=Document)
async def create_document(document: Document, db: Session = Depends(get_db)):
    """Create a new document record"""
    try:
        doc_id = uuid4()
        now = datetime.utcnow()
        
        query = text("""
            INSERT INTO documents (
                id, audit_id, name, file_path, file_type, file_size_kb, doc_type,
                audit_area, upload_source, status, ai_classification, uploaded_by, uploaded_at
            ) VALUES (
                :id, :audit_id, :name, :file_path, :file_type, :file_size_kb, :doc_type,
                :audit_area, :upload_source, :status, :ai_classification, :uploaded_by, :uploaded_at
            ) RETURNING *
        """)
        
        result = db.execute(query, {
            "id": str(doc_id),
            "audit_id": str(document.audit_id),
            "name": document.name,
            "file_path": document.file_path,
            "file_type": document.file_type,
            "file_size_kb": document.file_size_kb,
            "doc_type": document.doc_type,
            "audit_area": document.audit_area,
            "upload_source": document.upload_source,
            "status": document.status,
            "ai_classification": json.dumps(document.ai_classification) if document.ai_classification else None,
            "uploaded_by": str(document.uploaded_by) if document.uploaded_by else None,
            "uploaded_at": now
        })
        
        db.commit()
        row = result.fetchone()
        
        return Document(
            id=row.id,
            audit_id=row.audit_id,
            name=row.name,
            file_path=row.file_path,
            file_type=row.file_type,
            file_size_kb=row.file_size_kb,
            doc_type=row.doc_type,
            audit_area=row.audit_area,
            upload_source=row.upload_source,
            status=row.status,
            ai_classification=json.loads(row.ai_classification) if row.ai_classification else None,
            uploaded_by=row.uploaded_by,
            uploaded_at=row.uploaded_at
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create document: {str(e)}")

@router.get("/audits/{audit_id}/documents", response_model=List[Dict[str, Any]])
async def get_audit_documents(audit_id: UUID, db: Session = Depends(get_db)):
    """Get all documents for an audit request"""
    try:
        result = db.execute(text("SELECT * FROM documents WHERE audit_id = :audit_id ORDER BY uploaded_at DESC"), {"audit_id": str(audit_id)})
        documents = []
        columns = [desc[0] for desc in result.cursor.description]
        for row in result:
            documents.append(row_to_dict(row, columns))
        return documents
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch documents: {str(e)}")

@router.post("/evidence", response_model=Evidence)
async def create_evidence(evidence: Evidence, db: Session = Depends(get_db)):
    """Create new evidence"""
    try:
        evidence_id = uuid4()
        now = datetime.utcnow()
        
        query = text("""
            INSERT INTO evidence (
                id, audit_id, document_id, audit_area, checklist_item, definition,
                page_number, extracted_text, ai_explanation, confidence_score,
                reviewed_by, review_status, reviewed_at, created_at
            ) VALUES (
                :id, :audit_id, :document_id, :audit_area, :checklist_item, :definition,
                :page_number, :extracted_text, :ai_explanation, :confidence_score,
                :reviewed_by, :review_status, :reviewed_at, :created_at
            ) RETURNING *
        """)
        
        result = db.execute(query, {
            "id": str(evidence_id),
            "audit_id": str(evidence.audit_id),
            "document_id": str(evidence.document_id),
            "audit_area": evidence.audit_area,
            "checklist_item": evidence.checklist_item,
            "definition": evidence.definition,
            "page_number": evidence.page_number,
            "extracted_text": evidence.extracted_text,
            "ai_explanation": json.dumps(evidence.ai_explanation) if evidence.ai_explanation else None,
            "confidence_score": evidence.confidence_score,
            "reviewed_by": str(evidence.reviewed_by) if evidence.reviewed_by else None,
            "review_status": evidence.review_status,
            "reviewed_at": evidence.reviewed_at,
            "created_at": now
        })
        
        db.commit()
        row = result.fetchone()
        
        return Evidence(
            id=row.id,
            audit_id=row.audit_id,
            document_id=row.document_id,
            audit_area=row.audit_area,
            checklist_item=row.checklist_item,
            definition=row.definition,
            page_number=row.page_number,
            extracted_text=row.extracted_text,
            ai_explanation=json.loads(row.ai_explanation) if row.ai_explanation else None,
            confidence_score=row.confidence_score,
            reviewed_by=row.reviewed_by,
            review_status=row.review_status,
            reviewed_at=row.reviewed_at,
            created_at=row.created_at
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create evidence: {str(e)}")

@router.get("/audits/{audit_id}/evidence", response_model=List[Dict[str, Any]])
async def get_audit_evidence(audit_id: UUID, db: Session = Depends(get_db)):
    """Get all evidence for an audit request"""
    try:
        result = db.execute(text("SELECT * FROM evidence WHERE audit_id = :audit_id ORDER BY created_at DESC"), {"audit_id": str(audit_id)})
        evidence_list = []
        columns = [desc[0] for desc in result.cursor.description]
        for row in result:
            evidence_list.append(row_to_dict(row, columns))
        return evidence_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch evidence: {str(e)}")

@router.post("/findings", response_model=AuditFinding)
async def create_finding(finding: AuditFinding, db: Session = Depends(get_db)):
    """Create a new audit finding"""
    try:
        finding_id = uuid4()
        now = datetime.utcnow()
        
        query = text("""
            INSERT INTO audit_findings (
                id, audit_id, finding_type, description, ai_suggestion,
                reviewed_by, resolved, created_at
            ) VALUES (
                :id, :audit_id, :finding_type, :description, :ai_suggestion,
                :reviewed_by, :resolved, :created_at
            ) RETURNING *
        """)
        
        result = db.execute(query, {
            "id": str(finding_id),
            "audit_id": str(finding.audit_id),
            "finding_type": finding.finding_type,
            "description": finding.description,
            "ai_suggestion": finding.ai_suggestion,
            "reviewed_by": str(finding.reviewed_by) if finding.reviewed_by else None,
            "resolved": finding.resolved,
            "created_at": now
        })
        
        db.commit()
        row = result.fetchone()
        
        return AuditFinding(
            id=row.id,
            audit_id=row.audit_id,
            finding_type=row.finding_type,
            description=row.description,
            ai_suggestion=row.ai_suggestion,
            reviewed_by=row.reviewed_by,
            resolved=row.resolved,
            created_at=row.created_at
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create finding: {str(e)}")

@router.get("/audits/{audit_id}/findings", response_model=List[Dict[str, Any]])
async def get_audit_findings(audit_id: UUID, db: Session = Depends(get_db)):
    """Get all findings for an audit request"""
    try:
        result = db.execute(text("SELECT * FROM audit_findings WHERE audit_id = :audit_id ORDER BY created_at DESC"), {"audit_id": str(audit_id)})
        findings = []
        columns = [desc[0] for desc in result.cursor.description]
        for row in result:
            findings.append(row_to_dict(row, columns))
        return findings
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch findings: {str(e)}")

@router.post("/reports", response_model=Report)
async def create_report(report: Report, db: Session = Depends(get_db)):
    """Create a new report"""
    try:
        report_id = uuid4()
        now = datetime.utcnow()
        
        query = text("""
            INSERT INTO reports (
                id, audit_id, report_type, file_path, generated_by, references, created_at
            ) VALUES (
                :id, :audit_id, :report_type, :file_path, :generated_by, :references, :created_at
            ) RETURNING *
        """)
        
        result = db.execute(query, {
            "id": str(report_id),
            "audit_id": str(report.audit_id),
            "report_type": report.report_type,
            "file_path": report.file_path,
            "generated_by": str(report.generated_by) if report.generated_by else None,
            "references": json.dumps(report.references) if report.references else None,
            "created_at": now
        })
        
        db.commit()
        row = result.fetchone()
        
        return Report(
            id=row.id,
            audit_id=row.audit_id,
            report_type=row.report_type,
            file_path=row.file_path,
            generated_by=row.generated_by,
            references=json.loads(row.references) if row.references else None,
            created_at=row.created_at
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create report: {str(e)}")

@router.get("/audits/{audit_id}/reports", response_model=List[Dict[str, Any]])
async def get_audit_reports(audit_id: UUID, db: Session = Depends(get_db)):
    """Get all reports for an audit request"""
    try:
        result = db.execute(text("SELECT * FROM reports WHERE audit_id = :audit_id ORDER BY created_at DESC"), {"audit_id": str(audit_id)})
        reports = []
        columns = [desc[0] for desc in result.cursor.description]
        for row in result:
            reports.append(row_to_dict(row, columns))
        return reports
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch reports: {str(e)}")

@router.post("/logs", response_model=AuditLog)
async def create_audit_log(log: AuditLog, db: Session = Depends(get_db)):
    """Create a new audit log entry"""
    try:
        log_id = uuid4()
        now = datetime.utcnow()
        
        query = text("""
            INSERT INTO audit_logs (
                id, related_type, related_id, action, performed_by,
                is_ai_action, ai_details, created_at
            ) VALUES (
                :id, :related_type, :related_id, :action, :performed_by,
                :is_ai_action, :ai_details, :created_at
            ) RETURNING *
        """)
        
        result = db.execute(query, {
            "id": str(log_id),
            "related_type": log.related_type,
            "related_id": str(log.related_id),
            "action": log.action,
            "performed_by": str(log.performed_by) if log.performed_by else None,
            "is_ai_action": log.is_ai_action,
            "ai_details": json.dumps(log.ai_details) if log.ai_details else None,
            "created_at": now
        })
        
        db.commit()
        row = result.fetchone()
        
        return AuditLog(
            id=row.id,
            related_type=row.related_type,
            related_id=row.related_id,
            action=row.action,
            performed_by=row.performed_by,
            is_ai_action=row.is_ai_action,
            ai_details=json.loads(row.ai_details) if row.ai_details else None,
            created_at=row.created_at
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create audit log: {str(e)}")

@router.get("/audits/{audit_id}/logs", response_model=List[Dict[str, Any]])
async def get_audit_logs(audit_id: UUID, db: Session = Depends(get_db)):
    """Get all logs for an audit request"""
    try:
        result = db.execute(text("SELECT * FROM audit_logs WHERE related_id = :audit_id ORDER BY created_at DESC"), {"audit_id": str(audit_id)})
        logs = []
        columns = [desc[0] for desc in result.cursor.description]
        for row in result:
            logs.append(row_to_dict(row, columns))
        return logs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch audit logs: {str(e)}")

@router.post("/progress", response_model=AuditProgress)
async def create_progress(progress: AuditProgress, db: Session = Depends(get_db)):
    """Create or update audit progress"""
    try:
        progress_id = uuid4()
        now = datetime.utcnow()
        
        query = text("""
            INSERT INTO audit_progress (
                id, audit_id, user_id, document_id, current_step, status,
                started_at, resumed_at, completed_at, time_spent_seconds,
                metadata, updated_at
            ) VALUES (
                :id, :audit_id, :user_id, :document_id, :current_step, :status,
                :started_at, :resumed_at, :completed_at, :time_spent_seconds,
                :metadata, :updated_at
            ) RETURNING *
        """)
        
        result = db.execute(query, {
            "id": str(progress_id),
            "audit_id": str(progress.audit_id),
            "user_id": str(progress.user_id),
            "document_id": str(progress.document_id) if progress.document_id else None,
            "current_step": progress.current_step,
            "status": progress.status,
            "started_at": progress.started_at or now,
            "resumed_at": progress.resumed_at,
            "completed_at": progress.completed_at,
            "time_spent_seconds": progress.time_spent_seconds,
            "metadata": json.dumps(progress.metadata) if progress.metadata else None,
            "updated_at": now
        })
        
        db.commit()
        row = result.fetchone()
        
        return AuditProgress(
            id=row.id,
            audit_id=row.audit_id,
            user_id=row.user_id,
            document_id=row.document_id,
            current_step=row.current_step,
            status=row.status,
            started_at=row.started_at,
            resumed_at=row.resumed_at,
            completed_at=row.completed_at,
            time_spent_seconds=row.time_spent_seconds,
            metadata=json.loads(row.metadata) if row.metadata else None,
            updated_at=row.updated_at
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create progress: {str(e)}")

@router.get("/audits/{audit_id}/progress", response_model=List[Dict[str, Any]])
async def get_audit_progress(audit_id: UUID, db: Session = Depends(get_db)):
    """Get progress for an audit request"""
    try:
        result = db.execute(text("SELECT * FROM audit_progress WHERE audit_id = :audit_id ORDER BY updated_at DESC"), {"audit_id": str(audit_id)})
        progress_list = []
        columns = [desc[0] for desc in result.cursor.description]
        for row in result:
            progress_list.append(row_to_dict(row, columns))
        return progress_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch progress: {str(e)}") 