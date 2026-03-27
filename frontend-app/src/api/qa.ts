import client from './client';

export interface QAResponse {
  answer: string;
  sources: Array<{ type: string; name: string; query_time?: string }>;
  chart: Record<string, any> | null;
  confidence: number;
  trace_id: string;
}

export const askQuestion = (query: string, conversationId?: string) =>
  client.post<any, QAResponse>('/qa/ask', { query, conversation_id: conversationId });

export const streamQuestion = (query: string, conversationId?: string) => {
  const url = `${import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'}/qa/stream`;
  const token = localStorage.getItem('token');
  return fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify({ query, conversation_id: conversationId }),
  });
};

export const getConversations = () => client.get('/qa/conversations');
export const getConversation = (id: string) => client.get(`/qa/conversations/${id}`);
export const deleteConversation = (id: string) => client.delete(`/qa/conversations/${id}`);
