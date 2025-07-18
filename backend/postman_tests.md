# IntelliAudit API - Postman Test Guide

## Base URL
```
http://localhost:8000
```

## Authentication
Currently, no authentication is required for testing.

---

## 1. Metadata Endpoints

### 1.1 Get Audit Frameworks
**GET** `/api/workflow/frameworks`

**Expected Response:**
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
      },
      {
        "id": 3,
        "name": "Member Rights",
        "description": "Review of member communication and privacy policies"
      },
      {
        "id": 4,
        "name": "General Documents",
        "description": "General policies and procedures for compliance"
      },
      {
        "id": 5,
        "name": "HEDIS Data Validation",
        "description": "Validation of HEDIS measure data sources"
      },
      {
        "id": 6,
        "name": "Utilization Management",
        "description": "Evaluation of service utilization decisions"
      },
      {
        "id": 7,
        "name": "Provider Network",
        "description": "Assessment of provider participation and contracts"
      }
    ]
  },
  {
    "id": 2,
    "name": "HIPAA",
    "version": "2023",
    "audit_areas": []
  },
  {
    "id": 3,
    "name": "SOX",
    "version": "2022",
    "audit_areas": []
  }
]
```

### 1.2 Get Audit Areas
**GET** `/api/workflow/areas`

**Expected Response:**
```json
[
  {
    "id": 1,
    "audit_framework_id": null,
    "name": "Credentialing",
    "description": "Verification of provider credentials and licenses",
    "created_at": "2024-01-01T00:00:00"
  },
  {
    "id": 2,
    "audit_framework_id": null,
    "name": "Quality Management",
    "description": "Oversight of quality improvement programs",
    "created_at": "2024-01-01T00:00:00"
  }
]
```

---

## 2. Audit Request Endpoints

### 2.1 Create Audit Request
**POST** `/api/workflow/audits`

**Request Body:**
```json
{
  "audit_name": "NCQA Annual Review 2024",
  "audit_type": "NCQA",
  "framework_version": "2024",
  "audit_areas": ["Credentialing", "Quality Management"],
  "checklist": {
    "credentialing": {
      "provider_verification": true,
      "license_validation": true
    },
    "quality_management": {
      "program_oversight": true,
      "improvement_plans": true
    }
  },
  "status": "not_started",
  "current_step": "planning",
  "due_date": "2024-12-31",
  "description": "Annual NCQA compliance audit for healthcare organization",
  "compliance_score": null,
  "risk_assessment": null,
  "final_comments": null,
  "created_by": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Expected Response:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "audit_name": "NCQA Annual Review 2024",
  "audit_type": "NCQA",
  "framework_version": "2024",
  "audit_areas": ["Credentialing", "Quality Management"],
  "checklist": {
    "credentialing": {
      "provider_verification": true,
      "license_validation": true
    },
    "quality_management": {
      "program_oversight": true,
      "improvement_plans": true
    }
  },
  "status": "not_started",
  "current_step": "planning",
  "started_at": null,
  "last_active_at": null,
  "completed_at": null,
  "due_date": "2024-12-31",
  "description": "Annual NCQA compliance audit for healthcare organization",
  "compliance_score": null,
  "risk_assessment": null,
  "final_comments": null,
  "created_by": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2024-01-15T10:30:00"
}
```

### 2.2 Get All Audit Requests
**GET** `/api/workflow/audits`

**Expected Response:**
```json
[
  {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "audit_name": "NCQA Annual Review 2024",
    "audit_type": "NCQA",
    "framework_version": "2024",
    "audit_areas": ["Credentialing", "Quality Management"],
    "checklist": {...},
    "status": "not_started",
    "current_step": "planning",
    "started_at": null,
    "last_active_at": null,
    "completed_at": null,
    "due_date": "2024-12-31",
    "description": "Annual NCQA compliance audit for healthcare organization",
    "compliance_score": null,
    "risk_assessment": null,
    "final_comments": null,
    "created_by": "550e8400-e29b-41d4-a716-446655440000",
    "created_at": "2024-01-15T10:30:00"
  }
]
```

### 2.3 Get Specific Audit Request
**GET** `/api/workflow/audits/{audit_id}`

**Expected Response:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "audit_name": "NCQA Annual Review 2024",
  "audit_type": "NCQA",
  "framework_version": "2024",
  "audit_areas": ["Credentialing", "Quality Management"],
  "checklist": {...},
  "status": "not_started",
  "current_step": "planning",
  "started_at": null,
  "last_active_at": null,
  "completed_at": null,
  "due_date": "2024-12-31",
  "description": "Annual NCQA compliance audit for healthcare organization",
  "compliance_score": null,
  "risk_assessment": null,
  "final_comments": null,
  "created_by": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2024-01-15T10:30:00"
}
```

---

## 3. Document Endpoints

### 3.1 Create Document
**POST** `/api/workflow/documents`

**Request Body:**
```json
{
  "audit_id": "123e4567-e89b-12d3-a456-426614174000",
  "name": "Provider Credentialing Policy.pdf",
  "file_path": "/uploads/documents/provider_credentialing_policy.pdf",
  "file_type": "PDF",
  "file_size_kb": 245.5,
  "doc_type": "policy",
  "audit_area": "Credentialing",
  "upload_source": "manual",
  "status": "pending",
  "ai_classification": {
    "tags": ["credentialing", "policy", "provider"],
    "confidence": 0.95,
    "extracted_text": "Provider credentialing policy document..."
  },
  "uploaded_by": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Expected Response:**
```json
{
  "id": "456e7890-e89b-12d3-a456-426614174001",
  "audit_id": "123e4567-e89b-12d3-a456-426614174000",
  "name": "Provider Credentialing Policy.pdf",
  "file_path": "/uploads/documents/provider_credentialing_policy.pdf",
  "file_type": "PDF",
  "file_size_kb": 245.5,
  "doc_type": "policy",
  "audit_area": "Credentialing",
  "upload_source": "manual",
  "status": "pending",
  "ai_classification": {
    "tags": ["credentialing", "policy", "provider"],
    "confidence": 0.95,
    "extracted_text": "Provider credentialing policy document..."
  },
  "uploaded_by": "550e8400-e29b-41d4-a716-446655440000",
  "uploaded_at": "2024-01-15T11:00:00"
}
```

### 3.2 Get Documents for Audit
**GET** `/api/workflow/audits/{audit_id}/documents`

**Expected Response:**
```json
[
  {
    "id": "456e7890-e89b-12d3-a456-426614174001",
    "audit_id": "123e4567-e89b-12d3-a456-426614174000",
    "name": "Provider Credentialing Policy.pdf",
    "file_path": "/uploads/documents/provider_credentialing_policy.pdf",
    "file_type": "PDF",
    "file_size_kb": 245.5,
    "doc_type": "policy",
    "audit_area": "Credentialing",
    "upload_source": "manual",
    "status": "pending",
    "ai_classification": {...},
    "uploaded_by": "550e8400-e29b-41d4-a716-446655440000",
    "uploaded_at": "2024-01-15T11:00:00"
  }
]
```

---

## 4. Evidence Endpoints

### 4.1 Create Evidence
**POST** `/api/workflow/evidence`

**Request Body:**
```json
{
  "audit_id": "123e4567-e89b-12d3-a456-426614174000",
  "document_id": "456e7890-e89b-12d3-a456-426614174001",
  "audit_area": "Credentialing",
  "checklist_item": "Provider License Verification",
  "definition": "Verify that all providers have valid licenses",
  "page_number": 5,
  "extracted_text": "All providers must maintain current licenses from their respective state boards...",
  "ai_explanation": {
    "highlight": "All providers must maintain current licenses",
    "logic": "This text confirms license verification requirement",
    "confidence": 0.98
  },
  "confidence_score": 0.98,
  "reviewed_by": null,
  "review_status": "pending",
  "reviewed_at": null
}
```

**Expected Response:**
```json
{
  "id": "789e0123-e89b-12d3-a456-426614174002",
  "audit_id": "123e4567-e89b-12d3-a456-426614174000",
  "document_id": "456e7890-e89b-12d3-a456-426614174001",
  "audit_area": "Credentialing",
  "checklist_item": "Provider License Verification",
  "definition": "Verify that all providers have valid licenses",
  "page_number": 5,
  "extracted_text": "All providers must maintain current licenses from their respective state boards...",
  "ai_explanation": {
    "highlight": "All providers must maintain current licenses",
    "logic": "This text confirms license verification requirement",
    "confidence": 0.98
  },
  "confidence_score": 0.98,
  "reviewed_by": null,
  "review_status": "pending",
  "reviewed_at": null,
  "created_at": "2024-01-15T11:30:00"
}
```

### 4.2 Get Evidence for Audit
**GET** `/api/workflow/audits/{audit_id}/evidence`

**Expected Response:**
```json
[
  {
    "id": "789e0123-e89b-12d3-a456-426614174002",
    "audit_id": "123e4567-e89b-12d3-a456-426614174000",
    "document_id": "456e7890-e89b-12d3-a456-426614174001",
    "audit_area": "Credentialing",
    "checklist_item": "Provider License Verification",
    "definition": "Verify that all providers have valid licenses",
    "page_number": 5,
    "extracted_text": "All providers must maintain current licenses from their respective state boards...",
    "ai_explanation": {...},
    "confidence_score": 0.98,
    "reviewed_by": null,
    "review_status": "pending",
    "reviewed_at": null,
    "created_at": "2024-01-15T11:30:00"
  }
]
```

---

## 5. Audit Findings Endpoints

### 5.1 Create Finding
**POST** `/api/workflow/findings`

**Request Body:**
```json
{
  "audit_id": "123e4567-e89b-12d3-a456-426614174000",
  "finding_type": "evidence_gap",
  "description": "Missing documentation for 3 provider license renewals",
  "ai_suggestion": "Request updated license documentation from providers A, B, and C",
  "reviewed_by": null,
  "resolved": false
}
```

**Expected Response:**
```json
{
  "id": "abc12345-e89b-12d3-a456-426614174003",
  "audit_id": "123e4567-e89b-12d3-a456-426614174000",
  "finding_type": "evidence_gap",
  "description": "Missing documentation for 3 provider license renewals",
  "ai_suggestion": "Request updated license documentation from providers A, B, and C",
  "reviewed_by": null,
  "resolved": false,
  "created_at": "2024-01-15T12:00:00"
}
```

### 5.2 Get Findings for Audit
**GET** `/api/workflow/audits/{audit_id}/findings`

**Expected Response:**
```json
[
  {
    "id": "abc12345-e89b-12d3-a456-426614174003",
    "audit_id": "123e4567-e89b-12d3-a456-426614174000",
    "finding_type": "evidence_gap",
    "description": "Missing documentation for 3 provider license renewals",
    "ai_suggestion": "Request updated license documentation from providers A, B, and C",
    "reviewed_by": null,
    "resolved": false,
    "created_at": "2024-01-15T12:00:00"
  }
]
```

---

## 6. Reports Endpoints

### 6.1 Create Report
**POST** `/api/workflow/reports`

**Request Body:**
```json
{
  "audit_id": "123e4567-e89b-12d3-a456-426614174000",
  "report_type": "draft_summary",
  "file_path": "/reports/ncqa_audit_draft_2024.pdf",
  "generated_by": "550e8400-e29b-41d4-a716-446655440000",
  "references": {
    "documents": ["456e7890-e89b-12d3-a456-426614174001"],
    "evidence": ["789e0123-e89b-12d3-a456-426614174002"],
    "findings": ["abc12345-e89b-12d3-a456-426614174003"]
  }
}
```

**Expected Response:**
```json
{
  "id": "def67890-e89b-12d3-a456-426614174004",
  "audit_id": "123e4567-e89b-12d3-a456-426614174000",
  "report_type": "draft_summary",
  "file_path": "/reports/ncqa_audit_draft_2024.pdf",
  "generated_by": "550e8400-e29b-41d4-a716-446655440000",
  "references": {
    "documents": ["456e7890-e89b-12d3-a456-426614174001"],
    "evidence": ["789e0123-e89b-12d3-a456-426614174002"],
    "findings": ["abc12345-e89b-12d3-a456-426614174003"]
  },
  "created_at": "2024-01-15T13:00:00"
}
```

### 6.2 Get Reports for Audit
**GET** `/api/workflow/audits/{audit_id}/reports`

**Expected Response:**
```json
[
  {
    "id": "def67890-e89b-12d3-a456-426614174004",
    "audit_id": "123e4567-e89b-12d3-a456-426614174000",
    "report_type": "draft_summary",
    "file_path": "/reports/ncqa_audit_draft_2024.pdf",
    "generated_by": "550e8400-e29b-41d4-a716-446655440000",
    "references": {...},
    "created_at": "2024-01-15T13:00:00"
  }
]
```

---

## 7. Audit Logs Endpoints

### 7.1 Create Audit Log
**POST** `/api/workflow/logs`

**Request Body:**
```json
{
  "related_type": "document",
  "related_id": "456e7890-e89b-12d3-a456-426614174001",
  "action": "document_uploaded",
  "performed_by": "550e8400-e29b-41d4-a716-446655440000",
  "is_ai_action": false,
  "ai_details": null
}
```

**Expected Response:**
```json
{
  "id": "ghi23456-e89b-12d3-a456-426614174005",
  "related_type": "document",
  "related_id": "456e7890-e89b-12d3-a456-426614174001",
  "action": "document_uploaded",
  "performed_by": "550e8400-e29b-41d4-a716-446655440000",
  "is_ai_action": false,
  "ai_details": null,
  "created_at": "2024-01-15T14:00:00"
}
```

### 7.2 Get Logs for Audit
**GET** `/api/workflow/audits/{audit_id}/logs`

**Expected Response:**
```json
[
  {
    "id": "ghi23456-e89b-12d3-a456-426614174005",
    "related_type": "document",
    "related_id": "456e7890-e89b-12d3-a456-426614174001",
    "action": "document_uploaded",
    "performed_by": "550e8400-e29b-41d4-a716-446655440000",
    "is_ai_action": false,
    "ai_details": null,
    "created_at": "2024-01-15T14:00:00"
  }
]
```

---

## 8. Audit Progress Endpoints

### 8.1 Create Progress
**POST** `/api/workflow/progress`

**Request Body:**
```json
{
  "audit_id": "123e4567-e89b-12d3-a456-426614174000",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "document_id": "456e7890-e89b-12d3-a456-426614174001",
  "current_step": "evidence_review",
  "status": "in_progress",
  "time_spent_seconds": 1800,
  "metadata": {
    "device": "desktop",
    "browser": "chrome",
    "actions_count": 15
  }
}
```

**Expected Response:**
```json
{
  "id": "jkl34567-e89b-12d3-a456-426614174006",
  "audit_id": "123e4567-e89b-12d3-a456-426614174000",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "document_id": "456e7890-e89b-12d3-a456-426614174001",
  "current_step": "evidence_review",
  "status": "in_progress",
  "started_at": "2024-01-15T15:00:00",
  "resumed_at": null,
  "completed_at": null,
  "time_spent_seconds": 1800,
  "metadata": {
    "device": "desktop",
    "browser": "chrome",
    "actions_count": 15
  },
  "updated_at": "2024-01-15T15:00:00"
}
```

### 8.2 Get Progress for Audit
**GET** `/api/workflow/audits/{audit_id}/progress`

**Expected Response:**
```json
[
  {
    "id": "jkl34567-e89b-12d3-a456-426614174006",
    "audit_id": "123e4567-e89b-12d3-a456-426614174000",
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "document_id": "456e7890-e89b-12d3-a456-426614174001",
    "current_step": "evidence_review",
    "status": "in_progress",
    "started_at": "2024-01-15T15:00:00",
    "resumed_at": null,
    "completed_at": null,
    "time_spent_seconds": 1800,
    "metadata": {...},
    "updated_at": "2024-01-15T15:00:00"
  }
]
```

---

## Test Flow

1. **Start with metadata endpoints** to verify basic connectivity
2. **Create an audit request** to establish the main audit
3. **Upload documents** related to the audit
4. **Create evidence** extracted from documents
5. **Add findings** based on evidence review
6. **Generate reports** summarizing the audit
7. **Track progress** and log activities throughout

## Error Responses

All endpoints return consistent error responses:

```json
{
  "detail": "Error message describing what went wrong"
}
```

Common HTTP status codes:
- `200` - Success
- `201` - Created (for POST requests)
- `400` - Bad Request (invalid payload)
- `404` - Not Found (resource doesn't exist)
- `500` - Internal Server Error (database/application error) 