import React from 'react';

type HumanInLoopProps = {
  onSubmit: () => void;
  allAccepted: boolean;
  isLoading?: boolean;
};

const HumanInLoop: React.FC<HumanInLoopProps> = ({ onSubmit, allAccepted, isLoading = false }) => (
  <div className="human-loop-section">
    <button 
      className="submit-button" 
      onClick={onSubmit} 
      disabled={!allAccepted || isLoading}
    >
      {isLoading ? 'Generating Summary...' : 'Submit Audit Feedback'}
    </button>
    {!allAccepted && <p>Please review all criteria before submitting.</p>}
  </div>
);

export default HumanInLoop; 