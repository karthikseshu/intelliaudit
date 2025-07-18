-- Update metadata_audit_areas table to add foreign key constraint
-- First, add the audit_framework_id column if it doesn't exist
ALTER TABLE intelliaudit_dev.metadata_audit_areas 
ADD COLUMN IF NOT EXISTS audit_framework_id INTEGER;

-- Add foreign key constraint
ALTER TABLE intelliaudit_dev.metadata_audit_areas 
ADD CONSTRAINT fk_audit_areas_framework 
FOREIGN KEY (audit_framework_id) 
REFERENCES intelliaudit_dev.metadata_audit_frameworks(id);

-- Update existing audit areas to link them to frameworks
-- You can customize these mappings based on your needs
UPDATE intelliaudit_dev.metadata_audit_areas 
SET audit_framework_id = 1  -- NCQA
WHERE name IN ('Credentialing', 'Quality Management', 'Member Rights', 'General Documents', 'HEDIS Data Validation', 'Utilization Management', 'Provider Network');

-- Verify the changes
SELECT 
    aa.id,
    aa.name,
    aa.description,
    af.name as framework_name,
    af.version as framework_version
FROM intelliaudit_dev.metadata_audit_areas aa
LEFT JOIN intelliaudit_dev.metadata_audit_frameworks af ON aa.audit_framework_id = af.id
ORDER BY aa.name; 