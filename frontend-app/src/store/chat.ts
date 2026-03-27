import { create } from 'zustand';
import type { Message, Conversation } from '../types';

interface ChatStore {
  messages: Message[];
  conversations: Conversation[];
  conversationId: number | null;
  streaming: boolean;
  addMessage: (msg: Message) => void;
  updateLastMessage: (partial: Partial<Message>) => void;
  setMessages: (msgs: Message[]) => void;
  setStreaming: (v: boolean) => void;
  setConversationId: (id: number | null) => void;
  setConversations: (c: Conversation[]) => void;
  clearMessages: () => void;
}

export const useChatStore = create<ChatStore>((set) => ({
  messages: [],
  conversations: [],
  conversationId: null,
  streaming: false,
  addMessage: (msg) => set((s) => ({ messages: [...s.messages, msg] })),
  updateLastMessage: (partial) =>
    set((s) => {
      const msgs = [...s.messages];
      const last = msgs[msgs.length - 1];
      if (last) msgs[msgs.length - 1] = { ...last, ...partial };
      return { messages: msgs };
    }),
  setMessages: (messages) => set({ messages }),
  setStreaming: (streaming) => set({ streaming }),
  setConversationId: (conversationId) => set({ conversationId }),
  setConversations: (conversations) => set({ conversations }),
  clearMessages: () => set({ messages: [], conversationId: null }),
}));
