import React from 'react';

type AuditResult = {
  criteria: string;
  category: string;
  factor?: string;
  page: number | null;
  evidence: string;
  explanation: string;
  remarks: string;
  compliance_score?: number;
  risk_level?: string;
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

  const getComplianceScoreColor = (score: number) => {
    if (score >= 90) return '#28a745'; // Green
    if (score >= 70) return '#ffc107'; // Yellow
    if (score >= 50) return '#fd7e14'; // Orange
    if (score >= 30) return '#dc3545'; // Red
    return '#6c757d'; // Gray
  };

  const getRiskLevelColor = (riskLevel: string) => {
    switch (riskLevel?.toLowerCase()) {
      case 'low': return '#28a745';
      case 'medium': return '#ffc107';
      case 'high': return '#fd7e14';
      case 'critical': return '#dc3545';
      default: return '#6c757d';
    }
  };

  const getRiskLevelBackground = (riskLevel: string) => {
    switch (riskLevel?.toLowerCase()) {
      case 'low': return '#d4edda';
      case 'medium': return '#fff3cd';
      case 'high': return '#ffe5d0';
      case 'critical': return '#f8d7da';
      default: return '#f8f9fa';
    }
  };

  return (
    <table className="audit-table">
      <thead>
        <tr>
          <th>Criteria</th>
          <th>Category</th>
          <th>Factor</th>
          <th>Status</th>
          <th>Compliance Score</th>
          <th>Risk Level</th>
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
              {row.factor ? (
                <span style={{ 
                  background: '#f3e5f5', 
                  padding: '0.25rem 0.5rem', 
                  borderRadius: '12px', 
                  fontSize: '0.8rem',
                  color: '#7b1fa2'
                }}>
                  {row.factor}
                </span>
              ) : (
                <span style={{ color: '#6c757d', fontStyle: 'italic' }}>N/A</span>
              )}
            </td>
            <td>
              {getStatusIndicator(row.evidence)}
            </td>
            <td>
              {row.compliance_score !== undefined ? (
                <span style={{
                  background: getComplianceScoreColor(row.compliance_score),
                  color: 'white',
                  padding: '0.25rem 0.5rem',
                  borderRadius: '12px',
                  fontSize: '0.8rem',
                  fontWeight: 'bold'
                }}>
                  {row.compliance_score}%
                </span>
              ) : (
                <span style={{ color: '#6c757d', fontStyle: 'italic' }}>N/A</span>
              )}
            </td>
            <td>
              {row.risk_level ? (
                <span style={{
                  background: getRiskLevelBackground(row.risk_level),
                  color: getRiskLevelColor(row.risk_level),
                  padding: '0.25rem 0.5rem',
                  borderRadius: '12px',
                  fontSize: '0.8rem',
                  fontWeight: 'bold',
                  border: `1px solid ${getRiskLevelColor(row.risk_level)}`
                }}>
                  {row.risk_level}
                </span>
              ) : (
                <span style={{ color: '#6c757d', fontStyle: 'italic' }}>N/A</span>
              )}
            </td>
            <td>
              {row.evidence ? (
                <div style={{ 
                  background: '#f8f9fa', 
                  padding: '0.5rem', 
                  borderRadius: '8px',
                  fontSize: '0.85rem',
                  border: '1px solid #e9ecef',
                  maxWidth: '200px',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis'
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
                border: '1px solid #ffeaa7',
                maxWidth: '200px',
                overflow: 'hidden',
                textOverflow: 'ellipsis'
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