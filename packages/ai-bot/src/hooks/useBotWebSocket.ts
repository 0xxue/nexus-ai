/**
 * Bot WebSocket Hook — @nexus/ai-bot
 *
 * Connects to the Bot WebSocket server for real-time communication.
 * All URLs and tokens come from BotProvider config.
 */

import { useEffect, useRef, useCallback } from 'react';
import { useBotStore } from '../store';
import { useBotConfig } from '../BotProvider';

export interface BotMessage {
  type: string;
  content?: string;
  emotion?: string;
  action?: string;
  scene?: string;
  tool_calls?: Array<{ tool: string; success: boolean }>;
  mode?: string;
  priority?: string;
  user?: { id: string; role: string; username: string };
}

export function useBotWebSocket() {
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimer = useRef<ReturnType<typeof setTimeout>>();
  const { setEmotion, plugin } = useBotStore();
  const config = useBotConfig();
  const messagesRef = useRef<BotMessage[]>([]);

  const getWsUrl = useCallback(() => {
    const token = config.getToken() || '';
    const wsUrl = config.wsUrl;

    // If wsUrl is absolute (wss://...), use as-is
    if (wsUrl.startsWith('ws://') || wsUrl.startsWith('wss://')) {
      return `${wsUrl}?token=${token}`;
    }

    // Relative path: build from current host
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    return `${protocol}//${host}${wsUrl}?token=${token}`;
  }, [config]);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    const url = getWsUrl();
    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () => {
      console.log('[Bot WS] Connected');
      (window as any).__botWs = ws;
    };

    ws.onmessage = (event) => {
      try {
        const data: BotMessage = JSON.parse(event.data);
        messagesRef.current = [...messagesRef.current.slice(-50), data];

        switch (data.type) {
          case 'connected':
            console.log('[Bot WS] Authenticated:', data.user?.username);
            break;

          case 'bot_message':
            if (data.content) (window as any).__botSay?.(data.content, 5000);
            if (data.emotion) {
              setEmotion(data.emotion as any);
              if (data.emotion === 'talking') plugin?.startTalking();
              else plugin?.stopTalking();
            }
            if (data.action) plugin?.triggerAction?.(data.action as any);
            setTimeout(() => { setEmotion('idle'); plugin?.stopTalking(); }, 5000);
            break;

          case 'bot_emotion':
            if (data.emotion) {
              setEmotion(data.emotion as any);
              if (data.emotion === 'talking') plugin?.startTalking();
              else plugin?.stopTalking();
            }
            break;

          case 'bot_action':
            if (data.action) plugin?.triggerAction?.(data.action as any);
            break;

          case 'bot_alert':
            if (data.content) (window as any).__botSay?.(data.content, 10000);
            if (data.emotion) {
              setEmotion(data.emotion as any);
              if (data.action) plugin?.triggerAction?.(data.action as any);
              setTimeout(() => setEmotion('idle'), 8000);
            }
            break;

          case 'pong':
            break;
        }

        _listeners.forEach(fn => fn(data));
      } catch {}
    };

    ws.onclose = () => {
      console.log('[Bot WS] Disconnected, reconnecting in 3s...');
      reconnectTimer.current = setTimeout(connect, 3000);
    };

    ws.onerror = () => { ws.close(); };
  }, [getWsUrl, setEmotion, plugin]);

  useEffect(() => {
    connect();
    return () => {
      if (reconnectTimer.current) clearTimeout(reconnectTimer.current);
      wsRef.current?.close();
    };
  }, [connect]);

  const send = useCallback((data: Record<string, unknown>) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(data));
    }
  }, []);

  const sendChat = useCallback((message: string) => send({ type: 'chat', message, page: window.location.pathname }), [send]);
  const sendScene = useCallback((scene: string) => send({ type: 'scene', scene }), [send]);
  const sendPoke = useCallback(() => send({ type: 'poke' }), [send]);
  const sendModeChange = useCallback((mode: string) => send({ type: 'mode_change', mode }), [send]);

  return { send, sendChat, sendScene, sendPoke, sendModeChange, messages: messagesRef };
}

// Pub/sub for chat panel
type Listener = (msg: BotMessage) => void;
const _listeners: Set<Listener> = new Set();
export function onBotMessage(fn: Listener) { _listeners.add(fn); return () => _listeners.delete(fn); }
