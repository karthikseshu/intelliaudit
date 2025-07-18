-- Complete SQL script to update metadata_audit_areas table
-- Execute this directly in your PostgreSQL database

-- Step 1: Add the audit_framework_id column
ALTER TABLE intelliaudit_dev.metadata_audit_areas 
ADD COLUMN IF NOT EXISTS audit_framework_id INTEGER;

-- Step 2: Update existing data to link to NCQA framework (ID = 1)
UPDATE intelliaudit_dev.metadata_audit_areas 
SET audit_framework_id = 1
WHERE name IN ('Credentialing', 'Quality Management', 'Member Rights', 'General Documents', 'HEDIS Data Validation', 'Utilization Management', 'Provider Network');

-- Step 3: Add foreign key constraint
ALTER TABLE intelliaudit_dev.metadata_audit_areas 
ADD CONSTRAINT fk_audit_areas_framework 
FOREIGN KEY (audit_framework_id) 
REFERENCES intelliaudit_dev.metadata_audit_frameworks(id);

-- Step 4: Verify the changes
SELECT 
    aa.id,
    aa.name,
    aa.description,
    af.name as framework_name,
    af.version as framework_version,
    aa.audit_framework_id
FROM intelliaudit_dev.metadata_audit_areas aa
LEFT JOIN intelliaudit_dev.metadata_audit_frameworks af ON aa.audit_framework_id = af.id
ORDER BY aa.name;

-- Step 5: Show table structure
\d intelliaudit_dev.metadata_audit_areas 