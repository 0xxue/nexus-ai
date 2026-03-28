/**
 * API Voice Provider — Uses backend TTS proxy (Edge TTS / OpenAI)
 *
 * STT: Still uses browser SpeechRecognition (best UX, no upload latency)
 * TTS: Calls backend POST /bot/tts → returns audio → plays via AudioContext
 *
 * Supports:
 * - Edge TTS (free, high quality, many voices)
 * - OpenAI TTS (paid, highest quality)
 * - Any backend TTS provider via the /bot/tts endpoint
 */

import type { VoiceProvider, VoiceTTSOptions } from '../types';

const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

export class APIVoiceProvider implements VoiceProvider {
  readonly name = 'api';
  private recognition: any = null;
  private audioCtx: AudioContext | null = null;
  private currentSource: AudioBufferSourceNode | null = null;
  private _isSpeaking = false;
  private ttsProvider: string;
  private apiBase: string;
  private getToken: () => string | null | undefined;

  onResult: ((text: string, isFinal: boolean) => void) | null = null;
  onError: ((error: string) => void) | null = null;
  onSpeakingChange: ((speaking: boolean) => void) | null = null;

  constructor(ttsProvider: 'edge' | 'openai' = 'edge', apiBase = '/api/v1/bot', getToken: () => string | null | undefined = () => localStorage.getItem('token')) {
    this.ttsProvider = ttsProvider;
    this.apiBase = apiBase;
    this.getToken = getToken;
  }

  isAvailable(): boolean {
    // STT needs browser support, TTS uses backend
    return !!SpeechRecognition;
  }

  // ── STT (same as browser — no reason to upload audio for STT) ──

  startListening(options?: { lang?: string }): void {
    if (!SpeechRecognition) {
      this.onError?.('SpeechRecognition not supported');
      return;
    }

    this.recognition = new SpeechRecognition();
    this.recognition.continuous = false;
    this.recognition.interimResults = true;
    this.recognition.lang = options?.lang || 'zh-CN';

    this.recognition.onresult = (event: any) => {
      let transcript = '';
      let isFinal = false;
      for (let i = event.resultIndex; i < event.results.length; i++) {
        transcript += event.results[i][0].transcript;
        if (event.results[i].isFinal) isFinal = true;
      }
      this.onResult?.(transcript, isFinal);
    };

    this.recognition.onerror = (event: any) => {
      if (event.error !== 'aborted') this.onError?.(event.error);
    };

    this.recognition.start();
  }

  stopListening(): void {
    this.recognition?.stop();
    this.recognition = null;
  }

  // ── TTS (via backend API) ──

  async speak(text: string, options?: VoiceTTSOptions): Promise<void> {
    this.stopSpeaking();

    const token = this.getToken();
    try {
      const res = await fetch(`${this.apiBase}/tts`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({
          text,
          provider: this.ttsProvider,
          lang: options?.lang || 'zh-CN',
          rate: options?.rate ?? 1.0,
          voice: options?.voice,
        }),
      });

      if (!res.ok) {
        this.onError?.(`TTS failed: ${res.status}`);
        return;
      }

      const arrayBuffer = await res.arrayBuffer();
      if (!this.audioCtx) {
        this.audioCtx = new AudioContext();
      }

      const audioBuffer = await this.audioCtx.decodeAudioData(arrayBuffer);
      const source = this.audioCtx.createBufferSource();
      source.buffer = audioBuffer;
      source.connect(this.audioCtx.destination);

      this._isSpeaking = true;
      this.onSpeakingChange?.(true);
      this.currentSource = source;

      return new Promise((resolve) => {
        source.onended = () => {
          this._isSpeaking = false;
          this.onSpeakingChange?.(false);
          this.currentSource = null;
          resolve();
        };
        source.start();
      });
    } catch (e) {
      this._isSpeaking = false;
      this.onSpeakingChange?.(false);
      this.onError?.(`TTS error: ${e}`);
    }
  }

  stopSpeaking(): void {
    try { this.currentSource?.stop(); } catch {}
    this._isSpeaking = false;
    this.onSpeakingChange?.(false);
    this.currentSource = null;
  }

  isSpeaking(): boolean {
    return this._isSpeaking;
  }

  destroy(): void {
    this.stopListening();
    this.stopSpeaking();
    this.audioCtx?.close();
    this.audioCtx = null;
    this.onResult = null;
    this.onError = null;
    this.onSpeakingChange = null;
  }
}
