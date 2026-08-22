import React, { useEffect, useRef } from 'react';

// Lightweight animated network topology background
// Pure canvas + requestAnimationFrame — no external dependencies
export const CyberBackground = ({ className = '' }) => {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    let animFrame;
    let W = canvas.offsetWidth;
    let H = canvas.offsetHeight;
    canvas.width = W;
    canvas.height = H;

    // Respect reduced motion
    const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    const NODE_COUNT = Math.min(28, Math.floor((W * H) / 22000));
    const CONNECT_DIST = Math.min(180, W * 0.18);
    const PULSE_INTERVAL = 4000;

    // Node types for variety
    const NODE_TYPES = ['device', 'user', 'threat', 'server', 'file'];

    const nodes = Array.from({ length: NODE_COUNT }, (_, i) => ({
      x: Math.random() * W,
      y: Math.random() * H,
      vx: (Math.random() - 0.5) * 0.12,
      vy: (Math.random() - 0.5) * 0.12,
      r: 2.5 + Math.random() * 2,
      type: NODE_TYPES[i % NODE_TYPES.length],
      pulsePhase: Math.random() * Math.PI * 2,
      opacity: 0.4 + Math.random() * 0.4,
    }));

    // Threat node pulses along a connection path
    let pulses = [];
    let lastPulse = 0;

    const getNodeColor = (type) => {
      switch (type) {
        case 'threat': return 'rgba(239,68,68,';
        case 'server': return 'rgba(6,182,212,';
        case 'user':   return 'rgba(99,179,237,';
        case 'file':   return 'rgba(52,211,153,';
        default:       return 'rgba(100,160,200,';
      }
    };

    const draw = (timestamp) => {
      ctx.clearRect(0, 0, W, H);

      if (!prefersReduced) {
        // Update node positions
        nodes.forEach(n => {
          n.x += n.vx;
          n.y += n.vy;
          if (n.x < 0 || n.x > W) n.vx *= -1;
          if (n.y < 0 || n.y > H) n.vy *= -1;
          n.x = Math.max(0, Math.min(W, n.x));
          n.y = Math.max(0, Math.min(H, n.y));
        });

        // Occasional pulse along edges
        if (timestamp - lastPulse > PULSE_INTERVAL) {
          const i = Math.floor(Math.random() * nodes.length);
          const j = Math.floor(Math.random() * nodes.length);
          if (i !== j) {
            pulses.push({ from: nodes[i], to: nodes[j], t: 0, speed: 0.008 });
          }
          lastPulse = timestamp;
        }
      }

      // Draw connections
      for (let i = 0; i < nodes.length; i++) {
        for (let j = i + 1; j < nodes.length; j++) {
          const dx = nodes[i].x - nodes[j].x;
          const dy = nodes[i].y - nodes[j].y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < CONNECT_DIST) {
            const alpha = (1 - dist / CONNECT_DIST) * 0.12;
            ctx.beginPath();
            ctx.moveTo(nodes[i].x, nodes[i].y);
            ctx.lineTo(nodes[j].x, nodes[j].y);
            ctx.strokeStyle = `rgba(6,182,212,${alpha})`;
            ctx.lineWidth = 0.7;
            ctx.stroke();
          }
        }
      }

      // Draw data pulses
      pulses = pulses.filter(p => {
        p.t += p.speed;
        if (p.t > 1) return false;
        const px = p.from.x + (p.to.x - p.from.x) * p.t;
        const py = p.from.y + (p.to.y - p.from.y) * p.t;
        ctx.beginPath();
        ctx.arc(px, py, 2, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(6,182,212,${0.8 * (1 - p.t)})`;
        ctx.fill();
        return true;
      });

      // Draw nodes
      nodes.forEach(n => {
        const pulse = prefersReduced ? 0 : Math.sin(timestamp * 0.001 + n.pulsePhase) * 0.2;
        const color = getNodeColor(n.type);

        // Outer glow ring for certain node types
        if (n.type === 'threat' || n.type === 'server') {
          ctx.beginPath();
          ctx.arc(n.x, n.y, n.r + 4, 0, Math.PI * 2);
          ctx.fillStyle = `${color}${(n.opacity * 0.15 + pulse * 0.1).toFixed(2)})`;
          ctx.fill();
        }

        ctx.beginPath();
        ctx.arc(n.x, n.y, n.r, 0, Math.PI * 2);
        ctx.fillStyle = `${color}${(n.opacity + pulse).toFixed(2)})`;
        ctx.fill();
      });

      animFrame = requestAnimationFrame(draw);
    };

    animFrame = requestAnimationFrame(draw);

    const handleResize = () => {
      W = canvas.offsetWidth;
      H = canvas.offsetHeight;
      canvas.width = W;
      canvas.height = H;
    };
    window.addEventListener('resize', handleResize);

    return () => {
      cancelAnimationFrame(animFrame);
      window.removeEventListener('resize', handleResize);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className={`absolute inset-0 w-full h-full pointer-events-none ${className}`}
      aria-hidden="true"
    />
  );
};
