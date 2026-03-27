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
  /** Set emotional state (idle, happy, thinking, talking, surprised) */
  setEmotion(state: BotEmotion): void;
  /** Start talking animation */
  startTalking(): void;
  /** Stop talking animation */
  stopTalking(): void;
}

export type BotEmotion = 'idle' | 'happy' | 'thinking' | 'talking' | 'surprised';

export interface BotConfig {
  enabled: boolean;
  /** Size in pixels */
  size: number;
  /** Initial position */
  position: { right: number; bottom: number };
  /** Bot plugin factory */
  createPlugin?: () => BotPlugin;
}
