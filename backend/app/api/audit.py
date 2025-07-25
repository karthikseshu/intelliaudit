from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from pydantic import BaseModel
from app.core.extractor import extract_text_from_file
from app.core.audit import run_audit_on_text, run_audit_on_text_by_page
from app.api.audit_workflow import update_audit_request, insert_evidence_from_audit_results

router = APIRouter()

class AuditRequest(BaseModel):
    text: str
    model: str = None
    provider: str = "gemini"  # New provider parameter

@router.post('/uploadandaudit')
async def upload_file(file: UploadFile = File(...), audit_request_id: str = Form(...), document_id: str = Form(...), model: str = "gemini-1.5-flash", provider: str = "gemini"):
    print(f"audit_request_id: {audit_request_id}, document_id: {document_id}")

    try:
        text, pages = extract_text_from_file(file)
        # return {"text": text, "pages": pages}
        # results = run_audit_on_text(text, model, provider)
        update_audit_request(audit_request_id, "in_progress","Starting LLM Audit")
        results = run_audit_on_text_by_page(pages, model=model, provider=provider)
        insert_evidence_from_audit_results(results, audit_request_id, document_id)
        update_audit_request(audit_request_id, "in_progress","HITL in progress")

        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post('/run')
async def run_audit(request: AuditRequest):
    try:
        results = run_audit_on_text(request.text, request.model, request.provider)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))