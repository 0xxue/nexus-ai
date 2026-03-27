/**
 * NEXUS Background — Geometric lines, arcs, floating markers
 * Replicates the retro sci-fi aesthetic from indexv2.html
 */

import { useEffect, useRef } from 'react';

export function GeoLines() {
  return (
    <svg
      style={{ position: 'fixed', inset: 0, zIndex: 1, pointerEvents: 'none', width: '100%', height: '100%' }}
      viewBox="0 0 1400 900" preserveAspectRatio="none"
    >
      {/* Corner diagonals */}
      <line x1="0" y1="0" x2="700" y2="900" stroke="rgba(212,82,26,0.12)" strokeWidth="1" />
      <line x1="1400" y1="0" x2="400" y2="900" stroke="rgba(26,20,8,0.08)" strokeWidth="1" />
      <line x1="80" y1="0" x2="1400" y2="700" stroke="rgba(212,82,26,0.08)" strokeWidth="1" />
      {/* Arcs */}
      <circle cx="0" cy="900" r="300" fill="none" stroke="rgba(212,82,26,0.1)" strokeWidth="1" />
      <circle cx="0" cy="900" r="450" fill="none" stroke="rgba(212,82,26,0.07)" strokeWidth="1" />
      <circle cx="0" cy="900" r="600" fill="none" stroke="rgba(212,82,26,0.05)" strokeWidth="1" />
      {/* Text markers */}
      <text x="120" y="400" fontFamily="IBM Plex Mono" fontSize="9" fill="rgba(26,20,8,0.2)" transform="rotate(-90 120 400)">
        TRAJECTORY · 01 · LAUNCH VECTOR
      </text>
      <text x="1280" y="200" fontFamily="IBM Plex Mono" fontSize="8" fill="rgba(212,82,26,0.3)">
        4TH ORBIT TRY.
      </text>
      <text x="200" y="860" fontFamily="IBM Plex Mono" fontSize="8" fill="rgba(26,20,8,0.2)">2ND ALTITUDE</text>
      <text x="440" y="860" fontFamily="IBM Plex Mono" fontSize="8" fill="rgba(26,20,8,0.2)">3RD ALTITUDE</text>
      <line x1="240" y1="856" x2="240" y2="840" stroke="rgba(26,20,8,0.2)" strokeWidth="1" />
      <line x1="480" y1="856" x2="480" y2="840" stroke="rgba(26,20,8,0.2)" strokeWidth="1" />
    </svg>
  );
}

/**
 * Floating warm dust particles — lightweight canvas version
 */
export function DustCanvas() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let raf: number;
    const N = 60;
    const particles: { x: number; y: number; vx: number; vy: number; size: number }[] = [];

    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    resize();
    window.addEventListener('resize', resize);

    for (let i = 0; i < N; i++) {
      particles.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        vx: (Math.random() - 0.5) * 0.3,
        vy: (Math.random() - 0.5) * 0.3,
        size: 2 + Math.random() * 4,
      });
    }

    function draw() {
      ctx!.clearRect(0, 0, canvas!.width, canvas!.height);

      // Grid — very subtle
      ctx!.strokeStyle = 'rgba(212, 82, 26, 0.025)';
      ctx!.lineWidth = 0.5;
      const gridX = 80, gridY = 60;
      for (let x = 0; x < canvas!.width; x += gridX) {
        ctx!.beginPath(); ctx!.moveTo(x, 0); ctx!.lineTo(x, canvas!.height); ctx!.stroke();
      }
      for (let y = 0; y < canvas!.height; y += gridY) {
        ctx!.beginPath(); ctx!.moveTo(0, y); ctx!.lineTo(canvas!.width, y); ctx!.stroke();
      }

      // Particles — warm small squares
      for (const p of particles) {
        p.x += p.vx; p.y += p.vy;
        if (p.x < 0 || p.x > canvas!.width) p.vx *= -1;
        if (p.y < 0 || p.y > canvas!.height) p.vy *= -1;

        ctx!.fillStyle = `rgba(212, 82, 26, ${0.08 + Math.random() * 0.07})`;
        ctx!.fillRect(p.x, p.y, p.size, p.size);
      }

      raf = requestAnimationFrame(draw);
    }
    draw();

    return () => {
      cancelAnimationFrame(raf);
      window.removeEventListener('resize', resize);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      style={{ position: 'fixed', inset: 0, zIndex: 0, opacity: 0.5, pointerEvents: 'none' }}
    />
  );
}
