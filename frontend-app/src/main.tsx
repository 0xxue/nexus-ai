import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App';
import './index.css';

// Initialize VRM bot plugin
import { createVRMBot } from './components/bot/VRMBotPlugin';
import { useBotStore } from './store/bot';

// Load the 3D bot (set enabled: false in store to disable)
const vrmBot = createVRMBot('/model.vrm');
useBotStore.getState().setBotPlugin(vrmBot);

createRoot(document.getElementById('app')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
