import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

export const analyzeTicket = async (message) => {
  const response = await api.post('/tickets/analyze', { message });
  return response.data;
};

export const analyzeTicketWithAI = async (ticketId) => {
  const response = await api.post(`/tickets/${ticketId}/ai-analysis`);
  return response.data;
};

export const getTickets = async (limit = 50) => {
  const response = await api.get('/tickets', {
    params: { limit },
  });
  return response.data;
};

export default api;
