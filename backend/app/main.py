from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import audit, llm, config, audit_workflow, config_management, user_management, project_management

app = FastAPI(title="IntelliAudit API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "ok", "service": "IntelliAudit API"}

@app.get("/healthz")
def healthz():
    return {"ok": True}

app.include_router(audit.router, prefix="/api/audit")
app.include_router(llm.router, prefix="/api/llm")
app.include_router(config.router, prefix="/api/config")
app.include_router(audit_workflow.router, prefix="/api/workflow")
app.include_router(config_management.router, prefix="/api")
app.include_router(user_management.router, prefix="/api")
app.include_router(project_management.router, prefix="/api")