-- 0. Metadata Tables (For Dropdowns and Configuration)
CREATE TABLE metadata_audit_frameworks (
  id SERIAL PRIMARY KEY,
  name TEXT UNIQUE NOT NULL,       -- e.g., NCQA, HIPAA, SOX
  version TEXT,
  created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE metadata_audit_areas (
  id SERIAL PRIMARY KEY,
  audit_framework_id UUID REFERENCES metadata_audit_frameworks(id),
  name TEXT UNIQUE NOT NULL,       -- e.g., Credentialing, HEDIS Data Validation
  description TEXT,
  created_at TIMESTAMP DEFAULT now()
);

-- Sample inserts for metadata tables
INSERT INTO metadata_audit_frameworks (name, version) VALUES
('NCQA', '2024'),
('HIPAA', '2023'),
('SOX', '2022');

INSERT INTO metadata_audit_areas (name, description) VALUES
('Credentialing', 'Verification of provider credentials and licenses'),
('Quality Management', 'Oversight of quality improvement programs'),
('Member Rights', 'Review of member communication and privacy policies'),
('General Documents', 'General policies and procedures for compliance'),
('HEDIS Data Validation', 'Validation of HEDIS measure data sources'),
('Utilization Management', 'Evaluation of service utilization decisions'),
('Provider Network', 'Assessment of provider participation and contracts');

-- 1. Audit Requests Table (Overall Audit Lifecycle)
CREATE TABLE audit_requests (
  id UUID PRIMARY KEY,
  audit_name TEXT,
  audit_type TEXT,             -- e.g., NCQA, HIPAA
  framework_version TEXT,
  audit_areas TEXT[],          -- ['Credentialing', 'HEDIS Data Validation']
  checklist JSONB,             -- audit checklist items
  status TEXT,                 -- not_started, in_progress, completed, archived, etc.
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
  created_at TIMESTAMP DEFAULT now()
);

-- 2. Documents Table (Uploaded Files + Classification)
CREATE TABLE documents (
  id UUID PRIMARY KEY,
  audit_id UUID REFERENCES audit_requests(id),
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
  uploaded_at TIMESTAMP DEFAULT now()
);

-- 2a. Document Collaborators (Users assigned or actively reviewing a document)
CREATE TABLE document_collaborators (
  id UUID PRIMARY KEY,
  document_id UUID REFERENCES documents(id),
  user_id UUID,
  role TEXT,                  -- viewer, editor, lead_reviewer
  joined_at TIMESTAMP DEFAULT now()
);

-- 2b. Document Review Stages (Tracks each user's review of a document)
CREATE TABLE document_reviews (
  id UUID PRIMARY KEY,
  document_id UUID REFERENCES documents(id),
  user_id UUID,
  review_step TEXT,           -- e.g., classification, evidence_validation, final_review
  status TEXT,                -- pending, in_progress, approved, rejected
  comments TEXT,
  started_at TIMESTAMP,
  completed_at TIMESTAMP,
  last_updated TIMESTAMP DEFAULT now()
);

-- 3. Evidence Table (Extracted Proof from Documents)
CREATE TABLE evidence (
  id UUID PRIMARY KEY,
  audit_id UUID REFERENCES audit_requests(id),
  document_id UUID REFERENCES documents(id),
  audit_area TEXT,
  checklist_item TEXT,
  definition TEXT,
  page_number INT,
  extracted_text TEXT,
  ai_explanation JSONB,       -- highlight, logic, confidence
  confidence_score NUMERIC,   -- e.g., 95.0
  reviewed_by UUID,
  review_status TEXT,         -- approved, rejected, pending
  reviewed_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT now()
);

-- 4. Audit Findings Table (Observations & Issues)
CREATE TABLE audit_findings (
  id UUID PRIMARY KEY,
  audit_id UUID REFERENCES audit_requests(id),
  finding_type TEXT,          -- evidence_gap, inconsistency, note
  description TEXT,
  ai_suggestion TEXT,
  reviewed_by UUID,
  resolved BOOLEAN DEFAULT false,
  created_at TIMESTAMP DEFAULT now()
);

-- 5. Reports Table (Drafts and Final Submissions)
CREATE TABLE reports (
  id UUID PRIMARY KEY,
  audit_id UUID REFERENCES audit_requests(id),
  report_type TEXT,           -- draft_summary, final_report
  file_path TEXT,
  generated_by UUID,
  references JSONB,           -- related docs, evidence, findings
  created_at TIMESTAMP DEFAULT now()
);

-- 6. Audit Logs Table (Traceability & Explainability)
CREATE TABLE audit_logs (
  id UUID PRIMARY KEY,
  related_type TEXT,          -- document, evidence, finding, etc.
  related_id UUID,
  action TEXT,
  performed_by UUID,
  is_ai_action BOOLEAN,
  ai_details JSONB,
  created_at TIMESTAMP DEFAULT now()
);

-- 7. Audit Progress Table (Per-User Progress Tracking)
CREATE TABLE audit_progress (
  id UUID PRIMARY KEY,
  audit_id UUID REFERENCES audit_requests(id),
  user_id UUID,
  document_id UUID REFERENCES documents(id),
  current_step TEXT,          -- classification_review, evidence_review, etc.
  status TEXT,                -- in_progress, paused, completed
  started_at TIMESTAMP,
  resumed_at TIMESTAMP,
  completed_at TIMESTAMP,
  time_spent_seconds INT,
  metadata JSONB,             -- optional device info, action count, etc.
  updated_at TIMESTAMP DEFAULT now()
);

-- 8. Optional: User Activity Log (Detailed Audit Trail)
CREATE TABLE user_activity_log (
  id UUID PRIMARY KEY,
  audit_id UUID REFERENCES audit_requests(id),
  user_id UUID,
  action TEXT,                -- e.g., approved_tag, downloaded_report
  details JSONB,
  timestamp TIMESTAMP DEFAULT now()
);