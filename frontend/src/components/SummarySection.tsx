import React from 'react';

type SummarySectionProps = {
  summary: string;
};

const SummarySection: React.FC<SummarySectionProps> = ({ summary }) => (
  <div className="summary-section">
    <h2 className="summary-title">📋 Audit Summary</h2>
    <div className="summary-content">
      {summary}
    </div>
  </div>
);

export default SummarySection; 