from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core.llm import query_llm
from app.settings import LLM_PROVIDER

router = APIRouter()

class PromptRequest(BaseModel):
    prompt: str
    model: str = "gemini-1.5-flash"  # Default to Gemini model
    provider: str = "gemini"  # New provider parameter
    temperature: float = 0.2

@router.post('/prompt')
async def prompt_llm(req: PromptRequest):
    try:
        # Use the provider from the request, fallback to environment setting
        provider = req.provider or LLM_PROVIDER
        
        # If using Hugging Face, allow user to specify model (default to Llama-2-7b)
        model = req.model if provider == 'huggingface' else req.model
        response = query_llm(req.prompt, model, req.temperature, provider)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 