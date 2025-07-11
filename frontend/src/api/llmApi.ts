import axios from 'axios';
import { config } from '../config';

export const promptLLM = (prompt: string, model = 'gemini-1.5-flash', provider = 'gemini', temperature = 0.2) => {
  return axios.post(`${config.API.LLM}/prompt`, { prompt, model, provider, temperature });
}; 