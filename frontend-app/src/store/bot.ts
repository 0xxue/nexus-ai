import { create } from 'zustand';
import type { BotPlugin, BotEmotion } from '../types/bot';

interface BotStore {
  enabled: boolean;
  plugin: BotPlugin | null;
  size: number;
  emotion: BotEmotion;
  setEnabled: (v: boolean) => void;
  setBotPlugin: (p: BotPlugin | null) => void;
  setSize: (s: number) => void;
  setEmotion: (e: BotEmotion) => void;
}

export const useBotStore = create<BotStore>((set) => ({
  enabled: true,
  plugin: null,
  size: 180,
  emotion: 'idle',
  setEnabled: (enabled) => set({ enabled }),
  setBotPlugin: (plugin) => set({ plugin }),
  setSize: (size) => set({ size }),
  setEmotion: (emotion) => set({ emotion }),
}));
