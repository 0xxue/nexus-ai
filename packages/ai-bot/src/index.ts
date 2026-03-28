/**
 * @nexus/ai-bot — 3D AI Bot Engine
 *
 * Embedded intelligent assistant with:
 * - Pluggable 3D/2D avatar (BotPlugin interface)
 * - Pluggable voice system (VoiceProvider interface)
 * - WebSocket real-time communication
 * - Event-driven scene/behavior system
 * - Built-in VRM (Three.js) avatar support
 *
 * Quick start:
 *   import { BotProvider, BotContainer, createVRMBot } from '@nexus/ai-bot';
 *
 *   <BotProvider wsUrl="/ws/bot" apiBase="/api/v1/bot" getToken={() => token}>
 *     <BotContainer />
 *   </BotProvider>
 */

// ── Provider ──
export { BotProvider, useBotConfig } from './BotProvider';
export type { BotProviderConfig } from './BotProvider';

// ── Components ──
export { BotContainer } from './components/BotContainer';
export { BotChatPanel } from './components/BotChatPanel';
export { createVRMBot } from './components/VRMBotPlugin';

// ── Hooks ──
export { useBotWebSocket, onBotMessage } from './hooks/useBotWebSocket';
export type { BotMessage } from './hooks/useBotWebSocket';
export { botEngine } from './hooks/useBotEngine';
export { useBotVoice } from './hooks/useBotVoice';

// ── Voice Providers ──
export { BrowserVoiceProvider } from './voice/BrowserVoiceProvider';
export { APIVoiceProvider } from './voice/APIVoiceProvider';

// ── Store ──
export { useBotStore } from './store';
export type { BotChatMessage } from './store';

// ── API ──
export { createBotApi } from './api';
export type { BotApi } from './api';

// ── Types (for custom plugin/voice development) ──
export type {
  BotPlugin,
  BotEmotion,
  BotAction,
  VoiceProvider,
  VoiceTTSOptions,
  VoiceConfig,
  SceneConfig,
  SceneStep,
  BotConfig,
} from './types';
