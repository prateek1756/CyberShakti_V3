import React from 'react';

// Reusable pulsing status dot with optional ring animation
export const StatusPulse = ({
  status = 'active', // 'active' | 'idle' | 'error' | 'warning'
  size = 'sm',
  showRing = true,
  label,
}) => {
  const sizeMap = {
    xs: 'w-1.5 h-1.5',
    sm: 'w-2 h-2',
    md: 'w-2.5 h-2.5',
    lg: 'w-3 h-3',
  };

  const colorMap = {
    active:  { dot: 'bg-emerald-400', ring: 'bg-emerald-400/30' },
    idle:    { dot: 'bg-slate-400',   ring: 'bg-slate-400/20'   },
    error:   { dot: 'bg-red-400',     ring: 'bg-red-400/30'     },
    warning: { dot: 'bg-amber-400',   ring: 'bg-amber-400/30'   },
  };

  const colors = colorMap[status] || colorMap.active;
  const dotSize = sizeMap[size] || sizeMap.sm;

  return (
    <span className="inline-flex items-center gap-2">
      <span className="relative inline-flex">
        {showRing && status === 'active' && (
          <span
            className={`absolute inline-flex h-full w-full rounded-full ${colors.ring} animate-pulse-ring`}
            aria-hidden="true"
          />
        )}
        <span className={`relative inline-flex rounded-full ${dotSize} ${colors.dot}`} />
      </span>
      {label && (
        <span className="text-xs font-medium text-slate-300">{label}</span>
      )}
    </span>
  );
};
