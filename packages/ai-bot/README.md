# @nexus/ai-bot

3D AI Bot Engine for React applications. Embed an intelligent assistant with VRM avatar, voice dialogue, and tool system into any project.

## Features

- **3D VRM Avatar** -- 7 emotions, 3 actions, auto-blink, mouse follow, idle sway
- **Voice System** -- Pluggable STT/TTS (Browser native, Edge TTS, OpenAI)
- **WebSocket Real-time** -- Bidirectional communication with Bot Brain backend
- **14 System Tools** -- LLM function calling for data queries, KB search, admin ops
- **Scene Engine** -- Event-driven behavior system (page reactions, tours, alerts)
- **Chat Panel** -- Mini dialog with tool call indicators and message persistence
- **Fully Configurable** -- All URLs, auth, and providers via BotProvider context

## Quick Start

```bash
npm install @nexus/ai-bot
```

```tsx
import { BotProvider, BotContainer, createVRMBot, useBotStore } from '@nexus/ai-bot';

// Initialize VRM avatar
const vrmBot = createVRMBot('/model.vrm');
useBotStore.getState().setBotPlugin(vrmBot);

// Add to your app
function App() {
  return (
    <BotProvider
      wsUrl="/ws/bot"
      apiBase="/api/v1/bot"
      getToken={() => localStorage.getItem('token')}
    >
      <BotContainer />
    </BotProvider>
  );
}
```

## Configuration

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `wsUrl` | string | `/ws/bot` | WebSocket endpoint URL |
| `apiBase` | string | `/api/v1/bot` | Bot REST API base URL |
| `qaApiBase` | string | `/api/v1/qa` | QA API base (for conversation summary) |
| `getToken` | function | `() => localStorage.getItem('token')` | Auth token getter |
| `currentPath` | string | `window.location.pathname` | Current route (for scene awareness) |

## Exports

### Components

| Export | Description |
|--------|-------------|
| `BotContainer` | Main floating 3D bot with drag, flight, particles |
| `BotChatPanel` | Mini chat dialog with tool call display |
| `createVRMBot(url)` | Create a VRM 3D avatar plugin |

### Hooks

| Export | Description |
|--------|-------------|
| `useBotStore` | Zustand store (emotion, size, enabled, messages) |
| `useBotWebSocket` | WebSocket connection (send chat, scene, poke) |
| `useBotVoice` | Voice I/O (STT + TTS with provider switching) |
| `botEngine` | Event system (emit scenes, register behaviors) |

### Voice Providers

| Export | Description |
|--------|-------------|
| `BrowserVoiceProvider` | Web Speech API (free, zero config) |
| `APIVoiceProvider` | Backend proxy for Edge TTS / OpenAI TTS |

### Types (for custom development)

```typescript
import type { BotPlugin, VoiceProvider, BotEmotion } from '@nexus/ai-bot';
```

| Type | Use Case |
|------|----------|
| `BotPlugin` | Implement custom 3D/2D avatar |
| `VoiceProvider` | Implement custom STT/TTS service |
| `BotEmotion` | `'idle' \| 'happy' \| 'angry' \| 'sad' \| 'thinking' \| 'talking' \| 'surprised'` |
| `BotAction` | `'wave' \| 'nod' \| 'think'` |

## Custom Avatar

Implement the `BotPlugin` interface to use any 3D/2D character:

```typescript
import type { BotPlugin } from '@nexus/ai-bot';

const myPlugin: BotPlugin = {
  mount(container) { /* render your character */ },
  unmount() { /* cleanup */ },
  setEmotion(emotion) { /* change expression */ },
  startTalking() { /* mouth animation */ },
  stopTalking() { /* stop mouth */ },
  triggerAction(action) { /* wave, nod, think */ },
  resize(size) { /* handle resize */ },
};
```

## Custom Voice Provider

```typescript
import type { VoiceProvider } from '@nexus/ai-bot';

class MyVoiceProvider implements VoiceProvider {
  name = 'my-provider';
  isAvailable() { return true; }
  startListening() { /* start mic */ }
  stopListening() { /* stop mic */ }
  async speak(text) { /* play audio */ }
  // ... see VoiceProvider interface for full API
}
```

## Backend Requirements

This package expects a backend with these endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/ws/bot` | WebSocket | Bot real-time communication |
| `/bot/messages` | GET | Load persisted chat messages |
| `/bot/preferences` | GET/PUT | User bot preferences |
| `/bot/tts` | POST | Text-to-speech proxy |

See [nexus-ai](https://github.com/0xxue/nexus-ai) for a complete backend implementation.

## License

MIT
