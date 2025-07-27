# IntelliAudit API Documentation

## LLM Configuration

### Endpoint: `GET /api/config/llm`

Returns the current LLM configuration including the custom endpoint settings.

#### Response
```json
{
  "provider": "custom",
  "openai_api_base": "https://api.openai.com/v1",
  "huggingface_default_model": "HuggingFaceH4/zephyr-7b-beta",
  "custom_llm_endpoint": "http://20.49.1.173:8000/generate",
  "custom_llm_api_key_configured": false
}
```

#### Configuration Options

The system supports multiple LLM providers:

1. **Custom LLM Endpoint** (Default)
   - Uses your custom endpoint at `http://20.49.1.173:8000/generate`
   - No API key required (optional)
   - Configured via `LLM_PROVIDER=custom`

2. **OpenAI** (Fallback)
   - Requires OpenAI API key
   - Configured via `LLM_PROVIDER=openai`

3. **Gemini** (Fallback)
   - Requires Gemini API key
   - Configured via `LLM_PROVIDER=gemini`

4. **Hugging Face** (Fallback)
   - Requires Hugging Face API key
   - Configured via `LLM_PROVIDER=huggingface`

## Evidence Status Update API

### Endpoint: `PUT /api/workflow/evidence/{evidence_id}/status`

Updates the review status of a specific evidence record.

#### URL Parameters
- `evidence_id` (UUID, required): The unique identifier of the evidence to update

#### Request Body
```json
{
  "evidence_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "approved",
  "reviewed_by": "123e4567-e89b-12d3-a456-426614174000"
}
```

#### Request Body Fields
- `evidence_id` (UUID, required): Must match the URL parameter
- `status` (string, required): The new review status. Valid values:
  - `"approved"` - Evidence has been approved
  - `"rejected"` - Evidence has been rejected
  - `"pending"` - Evidence is pending review
- `reviewed_by` (UUID, optional): The UUID of the user who performed the review

#### Response

**Success (200 OK):**
```json
{
  "message": "Success"
}
```

**Error Responses:**

**404 Not Found:**
```json
{
  "detail": "Evidence not found"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Failed to update evidence status: [error details]"
}
```

## Evidence Annotation Update API

### Endpoint: `PUT /api/workflow/evidence/{evidence_id}/annotation`

Updates the annotation field of a specific evidence record.

#### URL Parameters
- `evidence_id` (UUID, required): The unique identifier of the evidence to update

#### Request Body
```json
{
  "evidence_id": "550e8400-e29b-41d4-a716-446655440000",
  "annotation": {
    "user_notes": "This evidence appears to be from the credentialing section",
    "highlighted_text": "Section 3.2 - Provider Credentialing Process",
    "confidence_level": "high",
    "reviewer_comments": "Clear evidence of credentialing process documentation",
    "tags": ["credentialing", "providers", "process"],
    "metadata": {
      "reviewed_by": "auditor_123",
      "review_date": "2024-01-15",
      "review_time": "14:30:00"
    }
  }
}
```

#### Request Body Fields
- `evidence_id` (UUID, required): Must match the URL parameter
- `annotation` (JSONB, required): The annotation data to store. Can contain any valid JSON structure.

#### Response

**Success (200 OK):**
```json
{
  "message": "Success"
}
```

**Error Responses:**

**404 Not Found:**
```json
{
  "detail": "Evidence not found"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Failed to update evidence annotation: [error details]"
}
```

#### Example Usage

**Using curl:**
```bash
curl -X PUT "http://localhost:8000/api/workflow/evidence/550e8400-e29b-41d4-a716-446655440000/annotation" \
  -H "Content-Type: application/json" \
  -d '{
    "evidence_id": "550e8400-e29b-41d4-a716-446655440000",
    "annotation": {
      "user_notes": "Simple annotation test",
      "confidence": "medium"
    }
  }'
```

**Using Python requests:**
```python
import requests

evidence_id = "550e8400-e29b-41d4-a716-446655440000"
annotation_data = {
    "evidence_id": evidence_id,
    "annotation": {
        "user_notes": "Simple annotation test",
        "confidence": "medium"
    }
}

response = requests.put(
    f"http://localhost:8000/api/workflow/evidence/{evidence_id}/annotation",
    json=annotation_data,
    headers={"Content-Type": "application/json"}
)

if response.status_code == 200:
    print("Success:", response.json())
else:
    print("Error:", response.text)
```

#### Database Changes

The API updates the following fields in the `evidence` table:
- `annotation`: Set to the provided JSONB annotation data
- `updated_at`: Set to the current timestamp

#### Notes

1. The evidence must exist in the database for the update to succeed
2. The `annotation` field accepts any valid JSON structure
3. The API automatically sets the `updated_at` timestamp
4. The endpoint uses the `intelliaudit_dev` schema as configured in the database connection 