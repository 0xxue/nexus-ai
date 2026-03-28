import { createRoot } from 'react-dom/client';
import App from './App';
import './index.css';

// Initialize VRM bot plugin
import { createVRMBot, useBotStore } from '@nexus/ai-bot';

// Load the 3D bot (set enabled: false in store to disable)
const vrmBot = createVRMBot('/model.vrm');
useBotStore.getState().setBotPlugin(vrmBot);

// No StrictMode — prevents double-mounting of 3D WebGL context
createRoot(document.getElementById('app')!).render(<App />);
