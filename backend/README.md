# IntelliAudit Backend

This is the backend for the Intelligent AI Audit Platform.

## Features
- File upload (PDF/Word)
- Text extraction
- Audit against configurable criteria (JSON)
- LLM (OpenAI) integration
- Modular, extendable APIs

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
uvicorn app.main:app --reload
```

## Configuration
- `.env` for OpenAI API key and settings
- `app/models/audit_criteria.json` for audit criteria 