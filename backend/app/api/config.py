from fastapi import APIRouter
from app.core.audit import load_criteria
from app.settings import OPENAI_API_BASE, LLM_PROVIDER, HUGGINGFACE_DEFAULT_MODEL

router = APIRouter()

@router.get('/criteria')
def get_criteria():
    return load_criteria()

@router.get('/llm')
def get_llm_config():
    return {
        "provider": LLM_PROVIDER,
        "openai_api_base": OPENAI_API_BASE,
        "huggingface_default_model": HUGGINGFACE_DEFAULT_MODEL
    } 