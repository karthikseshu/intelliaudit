from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, date
from uuid import uuid4, UUID
import json
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.config.database import get_db

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

class AuditRequest(BaseModel):
    id: Optional[UUID] = None
    audit_name: str
    audit_type: str
    framework_version: Optional[str] = None
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
async def get_audit_frameworks(db: Session = Depends(get_db)):
    """Get all audit frameworks with their related audit areas"""
    try:
        result = db.execute(text("""
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
        """))
        
        frameworks = []
        for row in result:
            # Convert audit_areas from JSON to list, handling null values
            audit_areas = row.audit_areas if row.audit_areas and row.audit_areas != [None] else []
            
            framework_data = {
                "id": row.id,
                "name": row.name,
                "version": row.version,
                "audit_areas": audit_areas
            }
            frameworks.append(framework_data)
        
        return frameworks
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch audit frameworks: {str(e)}")

@router.get("/areas", response_model=List[AuditArea])
async def get_audit_areas(db: Session = Depends(get_db)):
    """Get all audit areas"""
    try:
        result = db.execute(text("SELECT id, audit_framework_id, name, description, created_at FROM metadata_audit_areas ORDER BY name"))
        areas = []
        for row in result:
            areas.append(AuditArea(
                id=row.id,
                audit_framework_id=row.audit_framework_id,
                name=row.name,
                description=row.description,
                created_at=row.created_at
            ))
        return areas
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch audit areas: {str(e)}")

@router.post("/audits", response_model=AuditRequest)
async def create_audit_request(audit: AuditRequest, db: Session = Depends(get_db)):
    """Create a new audit request"""
    try:
        audit_id = uuid4()
        now = datetime.utcnow()
        
        query = text("""
            INSERT INTO audit_requests (
                id, audit_name, audit_type, framework_version, audit_areas, checklist,
                status, current_step, started_at, last_active_at, completed_at, due_date,
                description, compliance_score, risk_assessment, final_comments, created_by, created_at
            ) VALUES (
                :id, :audit_name, :audit_type, :framework_version, :audit_areas, :checklist,
                :status, :current_step, :started_at, :last_active_at, :completed_at, :due_date,
                :description, :compliance_score, :risk_assessment, :final_comments, :created_by, :created_at
            ) RETURNING *
        """)
        
        result = db.execute(query, {
            "id": str(audit_id),
            "audit_name": audit.audit_name,
            "audit_type": audit.audit_type,
            "framework_version": audit.framework_version,
            "audit_areas": audit.audit_areas,
            "checklist": json.dumps(audit.checklist) if audit.checklist else None,
            "status": audit.status,
            "current_step": audit.current_step,
            "started_at": audit.started_at,
            "last_active_at": audit.last_active_at,
            "completed_at": audit.completed_at,
            "due_date": audit.due_date,
            "description": audit.description,
            "compliance_score": audit.compliance_score,
            "risk_assessment": audit.risk_assessment,
            "final_comments": audit.final_comments,
            "created_by": str(audit.created_by) if audit.created_by else None,
            "created_at": now
        })
        
        db.commit()
        row = result.fetchone()
        
        return AuditRequest(
            id=row.id,
            audit_name=row.audit_name,
            audit_type=row.audit_type,
            framework_version=row.framework_version,
            audit_areas=row.audit_areas if row.audit_areas else [],
            checklist=json.loads(row.checklist) if row.checklist else None,
            status=row.status,
            current_step=row.current_step,
            started_at=row.started_at,
            last_active_at=row.last_active_at,
            completed_at=row.completed_at,
            due_date=row.due_date,
            description=row.description,
            compliance_score=row.compliance_score,
            risk_assessment=row.risk_assessment,
            final_comments=row.final_comments,
            created_by=row.created_by,
            created_at=row.created_at
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create audit request: {str(e)}")

@router.get("/audits", response_model=List[AuditRequest])
async def get_audit_requests(db: Session = Depends(get_db)):
    """Get all audit requests"""
    try:
        result = db.execute(text("SELECT * FROM audit_requests ORDER BY created_at DESC"))
        audits = []
        for row in result:
            audits.append(AuditRequest(
                id=row.id,
                audit_name=row.audit_name,
                audit_type=row.audit_type,
                framework_version=row.framework_version,
                audit_areas=row.audit_areas if row.audit_areas else [],
                checklist=json.loads(row.checklist) if row.checklist else None,
                status=row.status,
                current_step=row.current_step,
                started_at=row.started_at,
                last_active_at=row.last_active_at,
                completed_at=row.completed_at,
                due_date=row.due_date,
                description=row.description,
                compliance_score=row.compliance_score,
                risk_assessment=row.risk_assessment,
                final_comments=row.final_comments,
                created_by=row.created_by,
                created_at=row.created_at
            ))
        return audits
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch audit requests: {str(e)}")

@router.get("/audits/{audit_id}", response_model=AuditRequest)
async def get_audit_request(audit_id: UUID, db: Session = Depends(get_db)):
    """Get a specific audit request"""
    try:
        result = db.execute(text("SELECT * FROM audit_requests WHERE id = :audit_id"), {"audit_id": str(audit_id)})
        row = result.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Audit request not found")
        
        return AuditRequest(
            id=row.id,
            audit_name=row.audit_name,
            audit_type=row.audit_type,
            framework_version=row.framework_version,
            audit_areas=row.audit_areas if row.audit_areas else [],
            checklist=json.loads(row.checklist) if row.checklist else None,
            status=row.status,
            current_step=row.current_step,
            started_at=row.started_at,
            last_active_at=row.last_active_at,
            completed_at=row.completed_at,
            due_date=row.due_date,
            description=row.description,
            compliance_score=row.compliance_score,
            risk_assessment=row.risk_assessment,
            final_comments=row.final_comments,
            created_by=row.created_by,
            created_at=row.created_at
        )
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

@router.get("/audits/{audit_id}/documents", response_model=List[Document])
async def get_audit_documents(audit_id: UUID, db: Session = Depends(get_db)):
    """Get all documents for an audit request"""
    try:
        result = db.execute(text("SELECT * FROM documents WHERE audit_id = :audit_id ORDER BY uploaded_at DESC"), {"audit_id": str(audit_id)})
        documents = []
        for row in result:
            documents.append(Document(
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
            ))
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

@router.get("/audits/{audit_id}/evidence", response_model=List[Evidence])
async def get_audit_evidence(audit_id: UUID, db: Session = Depends(get_db)):
    """Get all evidence for an audit request"""
    try:
        result = db.execute(text("SELECT * FROM evidence WHERE audit_id = :audit_id ORDER BY created_at DESC"), {"audit_id": str(audit_id)})
        evidence_list = []
        for row in result:
            evidence_list.append(Evidence(
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
            ))
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

@router.get("/audits/{audit_id}/findings", response_model=List[AuditFinding])
async def get_audit_findings(audit_id: UUID, db: Session = Depends(get_db)):
    """Get all findings for an audit request"""
    try:
        result = db.execute(text("SELECT * FROM audit_findings WHERE audit_id = :audit_id ORDER BY created_at DESC"), {"audit_id": str(audit_id)})
        findings = []
        for row in result:
            findings.append(AuditFinding(
                id=row.id,
                audit_id=row.audit_id,
                finding_type=row.finding_type,
                description=row.description,
                ai_suggestion=row.ai_suggestion,
                reviewed_by=row.reviewed_by,
                resolved=row.resolved,
                created_at=row.created_at
            ))
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

@router.get("/audits/{audit_id}/reports", response_model=List[Report])
async def get_audit_reports(audit_id: UUID, db: Session = Depends(get_db)):
    """Get all reports for an audit request"""
    try:
        result = db.execute(text("SELECT * FROM reports WHERE audit_id = :audit_id ORDER BY created_at DESC"), {"audit_id": str(audit_id)})
        reports = []
        for row in result:
            reports.append(Report(
                id=row.id,
                audit_id=row.audit_id,
                report_type=row.report_type,
                file_path=row.file_path,
                generated_by=row.generated_by,
                references=json.loads(row.references) if row.references else None,
                created_at=row.created_at
            ))
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

@router.get("/audits/{audit_id}/logs", response_model=List[AuditLog])
async def get_audit_logs(audit_id: UUID, db: Session = Depends(get_db)):
    """Get all logs for an audit request"""
    try:
        result = db.execute(text("SELECT * FROM audit_logs WHERE related_id = :audit_id ORDER BY created_at DESC"), {"audit_id": str(audit_id)})
        logs = []
        for row in result:
            logs.append(AuditLog(
                id=row.id,
                related_type=row.related_type,
                related_id=row.related_id,
                action=row.action,
                performed_by=row.performed_by,
                is_ai_action=row.is_ai_action,
                ai_details=json.loads(row.ai_details) if row.ai_details else None,
                created_at=row.created_at
            ))
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

@router.get("/audits/{audit_id}/progress", response_model=List[AuditProgress])
async def get_audit_progress(audit_id: UUID, db: Session = Depends(get_db)):
    """Get progress for an audit request"""
    try:
        result = db.execute(text("SELECT * FROM audit_progress WHERE audit_id = :audit_id ORDER BY updated_at DESC"), {"audit_id": str(audit_id)})
        progress_list = []
        for row in result:
            progress_list.append(AuditProgress(
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
            ))
        return progress_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch progress: {str(e)}") 