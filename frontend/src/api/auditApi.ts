import axios from 'axios';
import { config } from '../config';

export const uploadFile = (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  return axios.post(`${config.API.AUDIT}/uploadandaudit`, formData);
};

export const runAudit = (text: string, model: string, provider: string) => {
  return axios.post(`${config.API.AUDIT}/run`, { text, model, provider });
}; 