import React, { useEffect, useRef } from 'react';
import { motion, useMotionValue, useTransform, animate } from 'framer-motion';

// Animated circular arc risk gauge using SVG + framer-motion
export const RiskMeter = ({ value = 0, maxValue = 100, size = 180, label, sublabel, color }) => {
  const radius = (size - 24) / 2;
  const circumference = 2 * Math.PI * radius;
  const strokeWidth = 10;
  const center = size / 2;

  // Determine color based on value if not provided
  const getColor = (v) => {
    if (v <= 20) return { stroke: '#22C55E', text: 'text-emerald-400', glow: 'rgba(34,197,94,0.3)' };
    if (v <= 40) return { stroke: '#84CC16', text: 'text-lime-400',    glow: 'rgba(132,204,22,0.3)' };
    if (v <= 60) return { stroke: '#F59E0B', text: 'text-amber-400',   glow: 'rgba(245,158,11,0.3)' };
    if (v <= 80) return { stroke: '#F97316', text: 'text-orange-400',  glow: 'rgba(249,115,22,0.3)' };
    return             { stroke: '#EF4444', text: 'text-red-400',      glow: 'rgba(239,68,68,0.3)'  };
  };

  const resolved = color || getColor(value);

  const motionVal = useMotionValue(0);
  const displayVal = useTransform(motionVal, v => Math.round(v));
  const dashOffset = useTransform(motionVal, v => {
    const pct = Math.min(v / maxValue, 1);
    return circumference - pct * circumference * 0.75; // 270deg arc
  });

  useEffect(() => {
    const controls = animate(motionVal, value, {
      duration: 1.6,
      ease: [0.16, 1, 0.3, 1],
    });
    return controls.stop;
  }, [value]);

  // 270deg arc: starts at 135deg (bottom-left), ends at 45deg (bottom-right)
  const startAngle = 135;
  const arcAngle = 270;

  return (
    <div className="flex flex-col items-center gap-2" role="meter" aria-valuenow={value} aria-valuemin={0} aria-valuemax={maxValue}>
      <div className="relative" style={{ width: size, height: size }}>
        <svg width={size} height={size} className="rotate-0">
          {/* Background track */}
          <circle
            cx={center}
            cy={center}
            r={radius}
            fill="none"
            stroke="rgba(255,255,255,0.06)"
            strokeWidth={strokeWidth}
            strokeDasharray={`${circumference * 0.75} ${circumference * 0.25}`}
            strokeDashoffset={circumference * 0.125}
            strokeLinecap="round"
            transform={`rotate(135 ${center} ${center})`}
          />
          {/* Animated progress arc */}
          <motion.circle
            cx={center}
            cy={center}
            r={radius}
            fill="none"
            stroke={resolved.stroke}
            strokeWidth={strokeWidth}
            strokeDasharray={`${circumference * 0.75} ${circumference * 0.25}`}
            strokeDashoffset={dashOffset}
            strokeLinecap="round"
            transform={`rotate(135 ${center} ${center})`}
            style={{
              filter: `drop-shadow(0 0 6px ${resolved.glow})`,
            }}
          />
        </svg>

        {/* Center content */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <motion.span
            className={`font-display text-4xl font-bold ${resolved.text}`}
          >
            <motion.span>{displayVal}</motion.span>
          </motion.span>
          {sublabel && (
            <span className="text-[10px] uppercase tracking-wider text-slate-500 mt-0.5">{sublabel}</span>
          )}
        </div>
      </div>

      {label && (
        <span className={`text-sm font-bold uppercase tracking-wider ${resolved.text}`}>{label}</span>
      )}
    </div>
  );
};
