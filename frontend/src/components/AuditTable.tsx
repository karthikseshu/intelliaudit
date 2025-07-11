import React from 'react';

type AuditResult = {
  criteria: string;
  category: string;
  page: number | null;
  evidence: string;
  explanation: string;
  remarks: string;
  accepted: boolean;
};

type AuditTableProps = {
  results: AuditResult[];
  onAccept: (idx: number) => void;
  onReject: (idx: number) => void;
  onRemarkChange: (idx: number, remark: string) => void;
};

const AuditTable: React.FC<AuditTableProps> = ({ results, onAccept, onReject, onRemarkChange }) => {
  const getStatusIndicator = (evidence: string) => {
    if (evidence && evidence.trim()) {
      return <span className="status-found">Found</span>;
    }
    return <span className="status-not-found">Not Found</span>;
  };

  return (
    <table className="audit-table">
      <thead>
        <tr>
          <th>Criteria</th>
          <th>Category</th>
          <th>Status</th>
          <th>Evidence</th>
          <th>Explanation</th>
          <th>Remarks</th>
          <th>Action</th>
        </tr>
      </thead>
      <tbody>
        {results.map((row, idx) => (
          <tr key={idx}>
            <td>
              <strong>{row.criteria}</strong>
            </td>
            <td>
              <span style={{ 
                background: '#e3f2fd', 
                padding: '0.25rem 0.5rem', 
                borderRadius: '12px', 
                fontSize: '0.8rem',
                color: '#1976d2'
              }}>
                {row.category}
              </span>
            </td>
            <td>
              {getStatusIndicator(row.evidence)}
            </td>
            <td>
              {row.evidence ? (
                <div style={{ 
                  background: '#f8f9fa', 
                  padding: '0.5rem', 
                  borderRadius: '8px',
                  fontSize: '0.85rem',
                  border: '1px solid #e9ecef'
                }}>
                  {row.evidence}
                </div>
              ) : (
                <span style={{ color: '#6c757d', fontStyle: 'italic' }}>No evidence found</span>
              )}
            </td>
            <td>
              <div style={{ 
                background: '#fff3cd', 
                padding: '0.5rem', 
                borderRadius: '8px',
                fontSize: '0.85rem',
                border: '1px solid #ffeaa7'
              }}>
                {row.explanation}
              </div>
            </td>
            <td>
              <input
                type="text"
                className="remarks-input"
                value={row.remarks}
                onChange={e => onRemarkChange(idx, e.target.value)}
                placeholder="Add your remarks..."
              />
            </td>
            <td>
              <div className="action-buttons">
                <button 
                  className="accept-button"
                  onClick={() => onAccept(idx)}
                  disabled={row.accepted}
                >
                  {row.accepted ? '✓ Accepted' : 'Accept'}
                </button>
                <button 
                  className="reject-button"
                  onClick={() => onReject(idx)}
                  disabled={row.accepted}
                >
                  Reject
                </button>
              </div>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
};

export default AuditTable; 