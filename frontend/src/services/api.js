import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const uploadReport = async (file, role) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('role', role);

  const response = await api.post('/upload-report', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const getDocuments = async () => {
  const response = await api.get('/documents');
  return response.data;
};

export const deleteDocument = async (documentId) => {
  const response = await api.delete(`/document/${documentId}`);
  return response.data;
};

export const getExplanation = async (reportId, role) => {
  const response = await api.get(`/explain/${reportId}?role=${role}`);
  return response.data;
};

export const feedKnowledge = async (text, source) => {
  const response = await api.post('/rag/feed', null, {
    params: { text, source }
  });
  return response.data;
};

export const chatWithReport = async (reportId, question, role) => {
  const response = await api.post(`/chat/${reportId}`, null, {
    params: { question, role }
  });
  return response.data;
};

export default api;
