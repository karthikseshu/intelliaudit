# IntelliAudit API Documentation

## 🚀 Live API Endpoints

**Base URL:** `https://your-render-app.onrender.com`

**Interactive Documentation:** `https://your-render-app.onrender.com/docs`

**Alternative Documentation:** `https://your-render-app.onrender.com/redoc`

---

## 📋 API Overview

The IntelliAudit API provides comprehensive audit workflow management capabilities including:
- Audit framework and area management
- Document upload and classification
- Evidence extraction and validation
- Audit findings and reporting
- Progress tracking and logging

---

## 🔗 Core Endpoints

### 1. Health Check
**GET** `/api/workflow/health`

**Response:**
```json
{
  "status": "healthy",
  "message": "Database connection successful"
}
```

### 2. Audit Frameworks
**GET** `/api/workflow/frameworks`

**Description:** Get all audit frameworks with their related audit areas

**Response:**
```json
[
  {
    "id": 1,
    "name": "NCQA",
    "version": "2024",
    "audit_areas": [
      {
        "id": 1,
        "name": "Credentialing",
        "description": "Verification of provider credentials and licenses"
      },
      {
        "id": 2,
        "name": "Quality Management",
        "description": "Oversight of quality improvement programs"
      }
    ]
  },
  {
    "id": 2,
    "name": "HIPAA",
    "version": "2023",
    "audit_areas": []
  }
]
```

### 3. Audit Areas
**GET** `/api/workflow/areas`

**Description:** Get all audit areas

**Response:**
```json
[
  {
    "id": 1,
    "audit_framework_id": 1,
    "name": "Credentialing",
    "description": "Verification of provider credentials and licenses",
    "created_at": "2024-01-15T10:30:00"
  },
  {
    "id": 2,
    "audit_framework_id": 1,
    "name": "Quality Management",
    "description": "Oversight of quality improvement programs",
    "created_at": "2024-01-15T10:30:00"
  }
]
```

---

## 🗄️ Database Schema

### Core Tables

#### `metadata_audit_frameworks`
- `id` (SERIAL PRIMARY KEY)
- `name` (TEXT UNIQUE NOT NULL) - e.g., NCQA, HIPAA, SOX
- `version` (TEXT)
- `created_at` (TIMESTAMP DEFAULT now())

#### `metadata_audit_areas`
- `id` (SERIAL PRIMARY KEY)
- `audit_framework_id` (INTEGER REFERENCES metadata_audit_frameworks(id))
- `name` (TEXT UNIQUE NOT NULL)
- `description` (TEXT)
- `created_at` (TIMESTAMP DEFAULT now())

#### `audit_requests`
- `id` (UUID PRIMARY KEY)
- `audit_name` (TEXT)
- `audit_type` (TEXT)
- `framework_version` (TEXT)
- `audit_areas` (TEXT[])
- `checklist` (JSONB)
- `status` (TEXT)
- `current_step` (TEXT)
- `due_date` (DATE)
- `description` (TEXT)
- `compliance_score` (NUMERIC)
- `risk_assessment` (TEXT)
- `created_by` (UUID)
- `created_at` (TIMESTAMP DEFAULT now())

#### `documents`
- `id` (UUID PRIMARY KEY)
- `audit_id` (UUID REFERENCES audit_requests(id))
- `name` (TEXT)
- `file_path` (TEXT)
- `file_type` (TEXT)
- `file_size_kb` (NUMERIC)
- `doc_type` (TEXT)
- `audit_area` (TEXT)
- `upload_source` (TEXT)
- `status` (TEXT)
- `ai_classification` (JSONB)
- `uploaded_by` (UUID)
- `uploaded_at` (TIMESTAMP DEFAULT now())

#### `evidence`
- `id` (UUID PRIMARY KEY)
- `audit_id` (UUID REFERENCES audit_requests(id))
- `document_id` (UUID REFERENCES documents(id))
- `audit_area` (TEXT)
- `checklist_item` (TEXT)
- `definition` (TEXT)
- `page_number` (INT)
- `extracted_text` (TEXT)
- `ai_explanation` (JSONB)
- `confidence_score` (NUMERIC)
- `reviewed_by` (UUID)
- `review_status` (TEXT)
- `created_at` (TIMESTAMP DEFAULT now())

#### `audit_findings`
- `id` (UUID PRIMARY KEY)
- `audit_id` (UUID REFERENCES audit_requests(id))
- `finding_type` (TEXT)
- `description` (TEXT)
- `ai_suggestion` (TEXT)
- `reviewed_by` (UUID)
- `resolved` (BOOLEAN DEFAULT false)
- `created_at` (TIMESTAMP DEFAULT now())

#### `reports`
- `id` (UUID PRIMARY KEY)
- `audit_id` (UUID REFERENCES audit_requests(id))
- `report_type` (TEXT)
- `file_path` (TEXT)
- `generated_by` (UUID)
- `references` (JSONB)
- `created_at` (TIMESTAMP DEFAULT now())

---

## 🔧 Technical Details

### Environment Variables
```bash
DB_USERNAME=postgres.gestigjpiefkwstawvzx
DB_PASSWORD=IntelliAudit$2025
DB_HOST=aws-0-us-east-2.pooler.supabase.com
DB_PORT=6543
DB_NAME=postgres
DB_SCHEMA=intelliaudit_dev
LLM_PROVIDER=gemini
PYTHON_VERSION=3.11.7
```

### Technology Stack
- **Framework:** FastAPI
- **Database:** PostgreSQL (Supabase)
- **Database Driver:** psycopg3
- **Documentation:** Swagger UI / OpenAPI
- **Deployment:** Render

### Authentication
Currently, no authentication is required for testing endpoints.

---

## 📝 Usage Examples

### Testing with curl

```bash
# Health check
curl https://your-render-app.onrender.com/api/workflow/health

# Get frameworks
curl https://your-render-app.onrender.com/api/workflow/frameworks

# Get areas
curl https://your-render-app.onrender.com/api/workflow/areas
```

### Testing with Postman

1. **Import the collection** from `backend/postman_tests.md`
2. **Set the base URL** to `https://your-render-app.onrender.com`
3. **Test the endpoints** using the provided examples

---

## 🚨 Error Handling

All endpoints return consistent error responses:

```json
{
  "detail": "Error message describing what went wrong"
}
```

**Common HTTP Status Codes:**
- `200` - Success
- `201` - Created (for POST requests)
- `400` - Bad Request (invalid payload)
- `404` - Not Found (resource doesn't exist)
- `500` - Internal Server Error (database/application error)

---

## 📞 Support

For technical support or questions about the API:
- **Repository:** https://github.com/karthikseshu/intelliaudit
- **Documentation:** https://your-render-app.onrender.com/docs
- **Health Check:** https://your-render-app.onrender.com/api/workflow/health

---

*Last Updated: January 2025*
*Version: 1.0.0* 