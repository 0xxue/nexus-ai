import { create } from 'zustand';

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: Array<{ type: string; name: string }>;
  chart?: Record<string, any>;
  confidence?: number;
  loading?: boolean;
  steps?: string[];
}

interface ChatStore {
  messages: Message[];
  conversationId: string | null;
  streaming: boolean;
  addMessage: (msg: Message) => void;
  updateLastMessage: (update: Partial<Message>) => void;
  setStreaming: (v: boolean) => void;
  setConversationId: (id: string | null) => void;
  clearMessages: () => void;
}

export const useChatStore = create<ChatStore>((set) => ({
  messages: [],
  conversationId: null,
  streaming: false,
  addMessage: (msg) => set((s) => ({ messages: [...s.messages, msg] })),
  updateLastMessage: (update) =>
    set((s) => ({
      messages: s.messages.map((m, i) =>
        i === s.messages.length - 1 ? { ...m, ...update } : m
      ),
    })),
  setStreaming: (streaming) => set({ streaming }),
  setConversationId: (conversationId) => set({ conversationId }),
  clearMessages: () => set({ messages: [], conversationId: null }),
}));
