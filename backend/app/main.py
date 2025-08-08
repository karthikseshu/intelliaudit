from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import audit, llm, config, audit_workflow, config_management

app = FastAPI(title="IntelliAudit API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(audit.router, prefix="/api/audit")
app.include_router(llm.router, prefix="/api/llm")
app.include_router(config.router, prefix="/api/config")
app.include_router(audit_workflow.router, prefix="/api/workflow") 
app.include_router(config_management.router, prefix="/api")