const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const config = {
  API: {
    AUDIT: `${API_BASE_URL}/api/audit`,
    LLM: `${API_BASE_URL}/api/llm`,
    CONFIG: `${API_BASE_URL}/api/config`,
  },
  UI: {
    BANNER_TEXT: 'IntelliAudit - Intelligent AI Audit Platform',
  },
}; 