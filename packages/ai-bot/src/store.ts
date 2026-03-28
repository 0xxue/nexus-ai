/**
 * Bot Store — Self-contained Zustand store for the Bot system.
 * Persists chat messages across component mounts/unmounts.
 */

import { create } from 'zustand';
import type { BotPlugin, BotEmotion, BotAction } from './types';

export interface BotChatMessage {
  id: string;
  role: 'user' | 'bot';
  content: string;
  emotion?: string;
  tools?: Array<{ tool: string; success: boolean }>;
  timestamp: number;
}

interface BotStore {
  // Avatar
  enabled: boolean;
  plugin: BotPlugin | null;
  size: number;
  emotion: BotEmotion;
  setEnabled: (v: boolean) => void;
  setBotPlugin: (p: BotPlugin | null) => void;
  setSize: (s: number) => void;
  setEmotion: (e: BotEmotion) => void;
  triggerAction: (a: BotAction) => void;

  // Chat messages (persisted in store, survives component unmount)
  chatMessages: BotChatMessage[];
  botName: string;
  addChatMessage: (msg: BotChatMessage) => void;
  setChatMessages: (msgs: BotChatMessage[]) => void;
  setBotName: (name: string) => void;
}

export const useBotStore = create<BotStore>((set, get) => ({
  // Avatar
  enabled: true,
  plugin: null,
  size: 180,
  emotion: 'idle' as BotEmotion,
  setEnabled: (enabled) => set({ enabled }),
  setBotPlugin: (plugin) => set({ plugin }),
  setSize: (size) => set({ size }),
  setEmotion: (emotion) => set({ emotion }),
  triggerAction: (action) => get().plugin?.triggerAction?.(action),

  // Chat
  chatMessages: [],
  botName: 'CLAWFORD',
  addChatMessage: (msg) => set((s) => ({ chatMessages: [...s.chatMessages, msg] })),
  setChatMessages: (chatMessages) => set({ chatMessages }),
  setBotName: (botName) => set({ botName }),
}));
