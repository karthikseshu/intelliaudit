# IntelliAudit API Documentation

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

#### Example Usage

**Using curl:**
```bash
curl -X PUT "http://localhost:8000/api/workflow/evidence/550e8400-e29b-41d4-a716-446655440000/status" \
  -H "Content-Type: application/json" \
  -d '{
    "evidence_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "approved",
    "reviewed_by": "123e4567-e89b-12d3-a456-426614174000"
  }'
```

**Using Python requests:**
```python
import requests

evidence_id = "550e8400-e29b-41d4-a716-446655440000"
status_update_data = {
    "evidence_id": evidence_id,
    "status": "approved",
    "reviewed_by": "123e4567-e89b-12d3-a456-426614174000"
}

response = requests.put(
    f"http://localhost:8000/api/workflow/evidence/{evidence_id}/status",
    json=status_update_data,
    headers={"Content-Type": "application/json"}
)

if response.status_code == 200:
    print("Success:", response.json())
else:
    print("Error:", response.text)
```

#### Database Changes

The API updates the following fields in the `evidence` table:
- `review_status`: Set to the provided status
- `reviewed_by`: Set to the provided reviewer UUID (if provided)
- `reviewed_at`: Set to the current timestamp
- `updated_at`: Set to the current timestamp

#### Notes

1. The evidence must exist in the database for the update to succeed
2. The `reviewed_by` field is optional - if not provided, it will remain unchanged
3. The API automatically sets timestamps for `reviewed_at` and `updated_at`
4. The endpoint uses the `intelliaudit_dev` schema as configured in the database connection 