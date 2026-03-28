import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';
import path from 'path';

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      '@nexus/ai-bot': path.resolve(__dirname, '../packages/ai-bot/src'),
      '@nexus/bot-admin': path.resolve(__dirname, '../packages/bot-admin/src'),
    },
    dedupe: ['react', 'react-dom', 'zustand', 'three', '@pixiv/three-vrm', 'lucide-react'],
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8001',
        changeOrigin: true,
      },
      '/ws': {
        target: 'ws://localhost:8001',
        ws: true,
      },
    },
  },
});
