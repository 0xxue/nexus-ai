export type { BotPlugin, BotEmotion, BotAction, BotConfig } from './bot';

export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  sources?: Source[];
  chart?: Record<string, unknown>;
  confidence?: number;
  loading?: boolean;
  steps?: string[];
  model_used?: string;
}

export interface Source {
  type: string;
  name: string;
  endpoint?: string;
  query_time?: string;
}

export interface Conversation {
  id: number;
  title: string;
  message_count: number;
  created_at: string;
  updated_at: string;
}

export interface KBCollection {
  id: number;
  name: string;
  description?: string;
  doc_count: number;
  status: string;
  created_at: string;
}

export interface KBDocument {
  id: number;
  filename: string;
  file_type: string;
  file_size: number;
  chunk_count: number;
  status: 'processing' | 'ready' | 'failed';
  error_msg?: string;
  created_at: string;
}
