# @nexus/bot-admin

Bot Management UI components for React. Drop-in admin panels to manage your AI Bot's scenes, messages, alerts, and settings.

## Features

- **Scene Editor** -- Configure bot reactions (emotion, speech, action, priority) with inline editing
- **Message History** -- View all bot conversations, cleanup old messages
- **Alert Overview** -- Monitor background health checks and anomaly detection
- **Usage Statistics** -- Message counts, tool calls, active users, breakdown charts
- **Bot Settings** -- Enable/disable, size slider, persistent preferences
- **Voice Settings** -- TTS provider, language, speed, auto-speak toggle

## Quick Start

```bash
npm install @nexus/bot-admin @nexus/ai-bot
```

```tsx
import { BotManagePanel, BotSettingsPanel, VoiceSettingsPanel } from '@nexus/bot-admin';

// Full management page
<Route path="/bot-manage" element={
  <BotManagePanel
    apiBase="/api/v1/bot"
    getToken={() => localStorage.getItem('token')}
  />
} />

// Or use individual panels in your own layout
<BotSettingsPanel onSizeChange={(s) => setBotSize(s)} />
<VoiceSettingsPanel />
```

## Exports

| Export | Description |
|--------|-------------|
| `BotManagePanel` | Full 4-tab management page (Overview, Scenes, Messages, Alerts) |
| `BotSettingsPanel` | Bot enable/disable + size slider |
| `VoiceSettingsPanel` | Voice provider, language, speed config |

## BotManagePanel Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `apiBase` | string | `/api/v1/bot` | Bot API base URL |
| `getToken` | function | `() => localStorage.getItem('token')` | Auth token getter |
| `title` | string | `'BOT MANAGE'` | Page title |

## Backend Requirements

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/bot/stats` | GET | Bot usage statistics |
| `/bot/scenes` | GET | List scene configurations |
| `/bot/scenes/:key` | PUT | Update scene (admin) |
| `/bot/messages` | GET | Bot message history |
| `/bot/cleanup` | POST | Delete old messages (admin) |
| `/bot/preferences` | GET/PUT | User bot preferences |

## License

MIT
