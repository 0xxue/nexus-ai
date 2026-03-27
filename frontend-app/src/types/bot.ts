/**
 * Bot Plugin Interface
 *
 * Any bot implementation (VRM 3D, 2D sprite, Lottie, etc.)
 * must implement this interface to be used with BotContainer.
 *
 * To create a custom bot:
 * 1. Implement BotPlugin interface
 * 2. Register it in BotContainer or via config
 */

export interface BotPlugin {
  /** Mount the bot into a DOM container */
  mount(container: HTMLElement): void;
  /** Unmount and clean up resources */
  unmount(): void;
  /** Set emotional state */
  setEmotion(state: BotEmotion): void;
  /** Start talking animation (mouth moves) */
  startTalking(): void;
  /** Stop talking animation */
  stopTalking(): void;
  /** Trigger a one-shot action (wave, nod, think) */
  triggerAction?(action: BotAction): void;
}

export type BotEmotion = 'idle' | 'happy' | 'angry' | 'sad' | 'thinking' | 'talking' | 'surprised';
export type BotAction = 'wave' | 'nod' | 'think';

export interface BotConfig {
  enabled: boolean;
  /** Size in pixels */
  size: number;
  /** Initial position */
  position: { right: number; bottom: number };
  /** Bot plugin factory */
  createPlugin?: () => BotPlugin;
}
