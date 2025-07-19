-- =========================
-- IntelliAudit Pro: Tenant DB Schema (PostgreSQL)
-- Updated with UI-driven features, review status tracking, document collaboration, and multi-stage document review
-- 
-- Developer Prompting Instructions:
-- If you need to regenerate or update this schema using ChatGPT, copy-paste the entire file and include a prompt like:
-- "This is my current IntelliAudit schema. Please add/modify to include [your feature, logic, or table change]."
-- You can specify: new workflow logic, AI metadata tracking, role-based access, new review stages, etc.
-- =========================

-- ENUM type for audit status
DO $$ BEGIN
  CREATE TYPE audit_status AS ENUM ('not_started', 'in_progress', 'completed', 'archived');
EXCEPTION
  WHEN duplicate_object THEN null;
END $$;

-- All CREATE TABLE statements follow here (no CREATE INDEX yet)

-- =========================
-- Table: metadata_audit_frameworks
-- Purpose: Stores audit/compliance frameworks (e.g., NCQA, HIPAA, SOX) and their versions. Used for categorizing audits and associating audit areas.
-- =========================
CREATE TABLE IF NOT EXISTS intelliaudit_dev.metadata_audit_frameworks (
  framework_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT UNIQUE NOT NULL,       -- e.g., NCQA, HIPAA, SOX
  version TEXT,
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now(),
  created_by UUID,
  updated_by UUID
);

-- =========================
-- Table: metadata_audit_areas
-- Purpose: Stores audit areas (e.g., Credentialing, HEDIS Data Validation) that are linked to frameworks. Each area describes a specific focus or domain within an audit.
-- =========================
CREATE TABLE IF NOT EXISTS intelliaudit_dev.metadata_audit_areas (
  audit_area_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  framework_id UUID REFERENCES intelliaudit_dev.metadata_audit_frameworks(framework_id) ON DELETE SET NULL,
  name TEXT UNIQUE NOT NULL,       -- e.g., Credentialing, HEDIS Data Validation
  description TEXT,
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now(),
  created_by UUID,
  updated_by UUID
);

-- Sample inserts for metadata tables
-- First, insert frameworks and capture their UUIDs
INSERT INTO intelliaudit_dev.metadata_audit_frameworks (framework_id, name, version) VALUES
  ('00000000-0000-0000-0000-000000000001', 'NCQA', '2024'),
  ('00000000-0000-0000-0000-000000000002', 'HIPAA', '2023'),
  ('00000000-0000-0000-0000-000000000003', 'SOX', '2022');

-- Then, insert areas and assign them to frameworks (example: all to NCQA for now)
INSERT INTO intelliaudit_dev.metadata_audit_areas (audit_area_id, framework_id, name, description) VALUES
  (gen_random_uuid(), '00000000-0000-0000-0000-000000000001', 'Credentialing', 'Verification of provider credentials and licenses'),
  (gen_random_uuid(), '00000000-0000-0000-0000-000000000001', 'Quality Management', 'Oversight of quality improvement programs'),
  (gen_random_uuid(), '00000000-0000-0000-0000-000000000001', 'Member Rights', 'Review of member communication and privacy policies'),
  (gen_random_uuid(), '00000000-0000-0000-0000-000000000001', 'General Documents', 'General policies and procedures for compliance'),
  (gen_random_uuid(), '00000000-0000-0000-0000-000000000001', 'HEDIS Data Validation', 'Validation of HEDIS measure data sources'),
  (gen_random_uuid(), '00000000-0000-0000-0000-000000000001', 'Utilization Management', 'Evaluation of service utilization decisions'),
  (gen_random_uuid(), '00000000-0000-0000-0000-000000000001', 'Provider Network', 'Assessment of provider participation and contracts');

-- =========================
-- Table: audit_requests
-- Purpose: Main table for tracking audit requests. Stores audit metadata, status, workflow steps, and links to frameworks and areas. Each row represents a single audit engagement.
-- =========================
CREATE TABLE IF NOT EXISTS intelliaudit_dev.audit_requests (
  audit_request_id UUID PRIMARY KEY,
  framework_id UUID REFERENCES intelliaudit_dev.metadata_audit_frameworks(framework_id),
  audit_name TEXT,
  audit_areas TEXT[],          -- ['Credentialing', 'HEDIS Data Validation']
  checklist JSONB,             -- audit checklist items
  status audit_status,                 -- not_started, in_progress, completed, archived, etc.
  current_step TEXT,           -- e.g., evidence_review, reporting
  started_at TIMESTAMP,
  last_active_at TIMESTAMP,
  completed_at TIMESTAMP,
  due_date DATE,
  description TEXT,
  compliance_score NUMERIC,    -- e.g., 75.0
  risk_assessment TEXT,        -- Low Risk, Medium Risk, High Risk
  final_comments TEXT,
  created_by UUID,
  updated_by UUID,
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now()
);

-- =========================
-- Table: documents
-- Purpose: Stores uploaded documents and files associated with audits. Includes classification, file metadata, AI tags, and upload source.
-- =========================
CREATE TABLE IF NOT EXISTS intelliaudit_dev.documents (
  document_id UUID PRIMARY KEY,
  audit_request_id UUID REFERENCES intelliaudit_dev.audit_requests(audit_request_id),
  name TEXT,
  file_path TEXT,
  file_type TEXT,             -- PDF, Word, Excel, JPEG, etc.
  file_size_kb NUMERIC,
  doc_type TEXT,
  audit_area TEXT,
  upload_source TEXT,         -- manual / api / etc.
  status TEXT,                -- pending, reviewed, approved
  ai_classification JSONB,    -- tags + rationale
  uploaded_by UUID,
  created_by UUID,
  updated_by UUID,
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now()
);

-- =========================
-- Table: document_collaborators
-- Purpose: Tracks users assigned to or actively collaborating on a document. Supports role-based access and collaboration features.
-- =========================
CREATE TABLE IF NOT EXISTS intelliaudit_dev.document_collaborators (
  document_collaborator_id UUID PRIMARY KEY,
  document_id UUID REFERENCES intelliaudit_dev.documents(document_id),
  user_id UUID,
  role TEXT,                  -- viewer, editor, lead_reviewer
  joined_at TIMESTAMP DEFAULT now(),
  created_by UUID,
  updated_by UUID,
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now()
);

-- =========================
-- Table: document_reviews
-- Purpose: Tracks each user's review stage and status for a document. Supports multi-stage review workflows and comments.
-- =========================
CREATE TABLE IF NOT EXISTS intelliaudit_dev.document_reviews (
  document_review_id UUID PRIMARY KEY,
  document_id UUID REFERENCES intelliaudit_dev.documents(document_id),
  user_id UUID,
  review_step TEXT,           -- e.g., classification, evidence_validation, final_review
  status TEXT,                -- pending, in_progress, approved, rejected
  comments TEXT,
  started_at TIMESTAMP,
  completed_at TIMESTAMP,
  last_updated TIMESTAMP DEFAULT now(),
  created_by UUID,
  updated_by UUID,
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now()
);

-- =========================
-- Table: evidence
-- Purpose: Stores extracted evidence and proof from documents. Includes AI explanations, confidence scores, and review status for each piece of evidence.
-- =========================
CREATE TABLE IF NOT EXISTS intelliaudit_dev.evidence (
  evidence_id UUID PRIMARY KEY,
  audit_request_id UUID REFERENCES intelliaudit_dev.audit_requests(audit_request_id),
  document_id UUID REFERENCES intelliaudit_dev.documents(document_id),
  audit_area TEXT,
  checklist_item TEXT,
  category_col JSONB,
  page_number INT,
  extracted_text TEXT,
  ai_explanation JSONB,       -- highlight, logic, confidence
  confidence_score NUMERIC,   -- e.g., 95.0
  reviewed_by UUID,
  review_status TEXT,         -- approved, rejected, pending
  reviewed_at TIMESTAMP,
  created_by UUID,
  updated_by UUID,
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now()
);

-- =========================
-- Table: audit_findings
-- Purpose: Stores findings, observations, and issues identified during audits. Includes AI suggestions and resolution status.
-- =========================
CREATE TABLE IF NOT EXISTS intelliaudit_dev.audit_findings (
  audit_finding_id UUID PRIMARY KEY,
  audit_request_id UUID REFERENCES intelliaudit_dev.audit_requests(audit_request_id),
  finding_type TEXT,          -- evidence_gap, inconsistency, note
  description TEXT,
  ai_suggestion TEXT,
  reviewed_by UUID,
  resolved BOOLEAN DEFAULT false,
  created_by UUID,
  updated_by UUID,
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now()
);

-- =========================
-- Table: reports
-- Purpose: Stores generated reports (drafts and finals) for audits. Includes file metadata and references to related docs, evidence, and findings.
-- =========================
CREATE TABLE IF NOT EXISTS intelliaudit_dev.reports (
  report_id UUID PRIMARY KEY,
  audit_request_id UUID REFERENCES intelliaudit_dev.audit_requests(audit_request_id),
  report_type TEXT,           -- draft_summary, final_report
  file_path TEXT,
  generated_by UUID,
  report_references JSONB,    -- related docs, evidence, findings
  created_by UUID,
  updated_by UUID,
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now()
);

-- =========================
-- Table: audit_logs
-- Purpose: General audit log for traceability and explainability. Tracks actions performed on documents, evidence, findings, etc., including AI actions.
-- =========================
CREATE TABLE IF NOT EXISTS intelliaudit_dev.audit_logs (
  audit_log_id UUID PRIMARY KEY,
  related_type TEXT,          -- document, evidence, finding, etc.
  related_id UUID,
  action TEXT,
  performed_by UUID,
  is_ai_action BOOLEAN,
  ai_details JSONB,
  created_by UUID,
  updated_by UUID,
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now()
);

-- =========================
-- Table: audit_progress
-- Purpose: Tracks per-user progress on audits and documents. Useful for workflow management, time tracking, and user activity analysis.
-- =========================
CREATE TABLE IF NOT EXISTS intelliaudit_dev.audit_progress (
  audit_progress_id UUID PRIMARY KEY,
  audit_request_id UUID REFERENCES intelliaudit_dev.audit_requests(audit_request_id),
  user_id UUID,
  document_id UUID REFERENCES intelliaudit_dev.documents(document_id),
  current_step TEXT,          -- classification_review, evidence_review, etc.
  status TEXT,                -- in_progress, paused, completed
  started_at TIMESTAMP,
  resumed_at TIMESTAMP,
  completed_at TIMESTAMP,
  time_spent_seconds INT,
  metadata JSONB,             -- optional device info, action count, etc.
  updated_at TIMESTAMP DEFAULT now(),
  created_by UUID,
  updated_by UUID,
  created_at TIMESTAMP DEFAULT now()
);

-- =========================
-- Table: user_activity_log
-- Purpose: Detailed user activity log for audit trail and compliance. Tracks user actions, details, and timestamps for each audit.
-- =========================
CREATE TABLE IF NOT EXISTS intelliaudit_dev.user_activity_log (
  user_activity_log_id UUID PRIMARY KEY,
  audit_request_id UUID REFERENCES intelliaudit_dev.audit_requests(audit_request_id),
  user_id UUID,
  action TEXT,                -- e.g., approved_tag, downloaded_report
  details JSONB,
  created_by UUID,
  updated_by UUID,
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now()
);

-- =========================
-- Table: audit_request_areas
-- Purpose: Join table linking audit requests, audit areas, and frameworks. Supports many-to-many relationships and enables efficient querying of which areas are covered by which audits/frameworks.
-- =========================
CREATE TABLE IF NOT EXISTS intelliaudit_dev.audit_request_areas (
  audit_request_area_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  audit_request_id UUID REFERENCES intelliaudit_dev.audit_requests(audit_request_id) ON DELETE CASCADE,
  audit_area_id UUID REFERENCES intelliaudit_dev.metadata_audit_areas(audit_area_id) ON DELETE CASCADE,
  framework_id UUID REFERENCES intelliaudit_dev.metadata_audit_frameworks(framework_id) ON DELETE CASCADE,
  created_by UUID,
  updated_by UUID,
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now(),
  UNIQUE (audit_request_id, audit_area_id, framework_id)
);

-- Indexes for join tables and JSONB columns (place at the end, after all tables are created)
CREATE INDEX IF NOT EXISTS idx_audit_request_areas_audit_request_id ON intelliaudit_dev.audit_request_areas(audit_request_id);
CREATE INDEX IF NOT EXISTS idx_audit_request_areas_audit_area_id ON intelliaudit_dev.audit_request_areas(audit_area_id);
CREATE INDEX IF NOT EXISTS idx_audit_request_areas_framework_id ON intelliaudit_dev.audit_request_areas(framework_id);
CREATE INDEX IF NOT EXISTS idx_audit_request_areas_request_area ON intelliaudit_dev.audit_request_areas(audit_request_id, audit_area_id);
CREATE INDEX IF NOT EXISTS idx_documents_ai_classification ON intelliaudit_dev.documents USING GIN (ai_classification);
CREATE INDEX IF NOT EXISTS idx_evidence_ai_explanation ON intelliaudit_dev.evidence USING GIN (ai_explanation);
CREATE INDEX IF NOT EXISTS idx_evidence_category_col ON intelliaudit_dev.evidence USING GIN (category_col);