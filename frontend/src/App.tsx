import { useState } from 'react';
import './App.css';
import { config } from './config';
import FileUpload from './components/FileUpload';
import AuditTable from './components/AuditTable';
import SummarySection from './components/SummarySection';
import HumanInLoop from './components/HumanInLoop';
import { runAudit } from './api/auditApi';
import { promptLLM } from './api/llmApi';

const PROVIDER_OPTIONS = [
  { label: 'Gemini (Free)', value: 'gemini' },
  { label: 'OpenAI', value: 'openai' },
  { label: 'Hugging Face', value: 'huggingface' },
];

const MODEL_OPTIONS = {
  gemini: [
    { label: 'Gemini 1.5 Flash (Fast & Free)', value: 'gemini-1.5-flash' },
    { label: 'Gemini 1.5 Pro (More Capable)', value: 'gemini-1.5-pro' },
    { label: 'Gemini Pro (Original)', value: 'gemini-pro' },
  ],
  openai: [
    { label: 'GPT-3.5 Turbo', value: 'gpt-3.5-turbo' },
    { label: 'GPT-4', value: 'gpt-4' },
  ],
  huggingface: [
    { label: 'Zephyr-7B (Free)', value: 'HuggingFaceH4/zephyr-7b-beta' },
    { label: 'Falcon-7B (Free)', value: 'tiiuae/falcon-7b-instruct' },
    { label: 'BloomZ-560M (Free)', value: 'bigscience/bloomz-560m' },
  ],
};

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

function App() {
  const [results, setResults] = useState<AuditResult[]>([]);
  const [summary, setSummary] = useState('');
  const [allAccepted, setAllAccepted] = useState(false);
  const [selectedProvider, setSelectedProvider] = useState('gemini');
  const [selectedModel, setSelectedModel] = useState('gemini-1.5-flash');
  const [isLoading, setIsLoading] = useState(false);

  const handleUpload = async (text: string) => {
    setIsLoading(true);
    try {
      const res = await runAudit(text, selectedModel, selectedProvider);
      setResults(res.data.results.map((r: AuditResult) => ({ ...r, accepted: false })));
      setSummary('');
      setAllAccepted(false);
    } catch (error) {
      console.error('Audit failed:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAccept = (idx: number) => {
    const newResults = [...results];
    newResults[idx].accepted = true;
    setResults(newResults);
    setAllAccepted(newResults.every(r => r.accepted));
  };

  const handleReject = (idx: number) => {
    const newResults = [...results];
    newResults[idx].accepted = false;
    setResults(newResults);
    setAllAccepted(false);
  };

  const handleRemarkChange = (idx: number, remark: string) => {
    const newResults = [...results];
    newResults[idx].remarks = remark;
    setResults(newResults);
  };

  const handleSubmit = async () => {
    setIsLoading(true);
    try {
      // Summarize findings using LLM with NCQA-specific focus
      const prompt = `As a healthcare compliance expert, provide a comprehensive summary of the following NCQA audit findings. Include:

1. Overall compliance assessment with compliance scores and risk levels
2. Critical findings that require immediate attention
3. Recommendations by category (Credentialing, Quality Management, Care Management, etc.)
4. Risk assessment summary
5. Priority action items

Audit Results: ${JSON.stringify(results)}

Format the response as a structured report with clear sections for each category and overall recommendations.`;
      const res = await promptLLM(prompt, selectedModel, selectedProvider);
      setSummary(res.data.response);
    } catch (error) {
      console.error('Summary generation failed:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleProviderChange = (provider: string) => {
    setSelectedProvider(provider);
    // Set default model for the selected provider
    const defaultModel = MODEL_OPTIONS[provider as keyof typeof MODEL_OPTIONS][0].value;
    setSelectedModel(defaultModel);
  };

  return (
    <div className="App">
      <div className="app-header">
        <h1 className="app-title">{config.UI.BANNER_TEXT}</h1>
      </div>
      
      <div className="provider-section">
        <div className="provider-container">
          <div className="provider-group">
            <label className="provider-label" htmlFor="provider-select">Choose LLM Provider:</label>
            <select
              id="provider-select"
              className="provider-select"
              value={selectedProvider}
              onChange={e => handleProviderChange(e.target.value)}
            >
              {PROVIDER_OPTIONS.map(opt => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </select>
          </div>
          <div className="provider-group">
            <label className="provider-label" htmlFor="model-select">Choose Model:</label>
            <select
              id="model-select"
              className="model-select"
              value={selectedModel}
              onChange={e => setSelectedModel(e.target.value)}
            >
              {MODEL_OPTIONS[selectedProvider as keyof typeof MODEL_OPTIONS].map(opt => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </select>
          </div>
        </div>
      </div>
      
      <div className="upload-section">
        <FileUpload onUpload={handleUpload} />
      </div>
      
      {isLoading && (
        <div className="loading">
          <div>Processing your document...</div>
        </div>
      )}
      
      {results.length > 0 && (
        <div className="results-section">
          <AuditTable
            results={results}
            onAccept={handleAccept}
            onReject={handleReject}
            onRemarkChange={handleRemarkChange}
          />
          <HumanInLoop onSubmit={handleSubmit} allAccepted={allAccepted} isLoading={isLoading} />
          {summary && <SummarySection summary={summary} />}
        </div>
      )}
    </div>
  );
}

export default App;
