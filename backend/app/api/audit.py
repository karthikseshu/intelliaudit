from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from app.core.extractor import extract_text_from_file
from app.core.audit import run_audit_on_text

router = APIRouter()

class AuditRequest(BaseModel):
    text: str
    model: str = None
    provider: str = "gemini"  # New provider parameter

@router.post('/upload')
async def upload_file(file: UploadFile = File(...)):
    try:
        text, pages = extract_text_from_file(file)
        return {"text": text, "pages": pages}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post('/run')
async def run_audit(request: AuditRequest):
    try:
        results = run_audit_on_text(request.text, request.model, request.provider)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))