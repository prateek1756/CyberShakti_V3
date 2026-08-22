import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle2, Circle, Loader2, Cpu, ShieldCheck } from 'lucide-react';

const DEFAULT_STAGES = [
  { id: 'input',     label: 'Input received',           duration: 500 },
  { id: 'normalize', label: 'Content normalized',        duration: 700 },
  { id: 'extract',   label: 'Threat indicators extracted', duration: 900 },
  { id: 'model',     label: 'AI model analyzing',        duration: 1200 },
  { id: 'risk',      label: 'Risk assessment',           duration: 600 },
];

export const ScanAnimation = ({
  isActive,
  scanId,
  stages = DEFAULT_STAGES,
  accentColor = 'cyan',
}) => {
  const [completedStages, setCompletedStages] = useState([]);
  const [currentStage, setCurrentStage] = useState(null);

  const colorMap = {
    cyan:   { text: 'text-cyan-400',   border: 'border-cyan-500/30', bg: 'bg-cyan-500/10',   dot: 'bg-cyan-400'   },
    purple: { text: 'text-purple-400', border: 'border-purple-500/30', bg: 'bg-purple-500/10', dot: 'bg-purple-400' },
    blue:   { text: 'text-blue-400',   border: 'border-blue-500/30', bg: 'bg-blue-500/10',   dot: 'bg-blue-400'   },
    orange: { text: 'text-orange-400', border: 'border-orange-500/30', bg: 'bg-orange-500/10', dot: 'bg-orange-400' },
  };
  const colors = colorMap[accentColor] || colorMap.cyan;

  useEffect(() => {
    if (!isActive) {
      setCompletedStages([]);
      setCurrentStage(null);
      return;
    }

    let cancelled = false;
    let elapsed = 0;

    const runStages = async () => {
      for (let i = 0; i < stages.length; i++) {
        if (cancelled) break;
        setCurrentStage(stages[i].id);
        await new Promise(r => setTimeout(r, stages[i].duration));
        if (cancelled) break;
        setCompletedStages(prev => [...prev, stages[i].id]);
      }
      if (!cancelled) setCurrentStage(null);
    };

    setCompletedStages([]);
    runStages();

    return () => { cancelled = true; };
  }, [isActive, scanId]);

  if (!isActive) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -8 }}
      transition={{ duration: 0.3 }}
      className={`rounded-xl border ${colors.border} ${colors.bg} p-5 space-y-4`}
    >
      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="relative">
          <Cpu className={`w-5 h-5 ${colors.text}`} />
        </div>
        <div>
          <p className={`text-xs font-bold uppercase tracking-widest ${colors.text}`}>
            Analyzing Threat
          </p>
          {scanId && (
            <p className="text-[10px] text-slate-500 font-mono mt-0.5">
              SCAN-ID: {scanId}
            </p>
          )}
        </div>
        <div className="ml-auto flex items-center gap-1.5">
          <span className={`inline-block w-1.5 h-1.5 rounded-full ${colors.dot} animate-pulse-slow`} />
          <span className="text-xs text-slate-400">PROCESSING</span>
        </div>
      </div>

      {/* Stage progress */}
      <div className="space-y-2.5">
        {stages.map((stage) => {
          const isDone = completedStages.includes(stage.id);
          const isRunning = currentStage === stage.id;

          return (
            <motion.div
              key={stage.id}
              initial={{ opacity: 0, x: -8 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.25 }}
              className="flex items-center gap-3"
            >
              <div className="w-5 h-5 flex-shrink-0 flex items-center justify-center">
                {isDone ? (
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{ type: 'spring', stiffness: 400, damping: 20 }}
                  >
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  </motion.div>
                ) : isRunning ? (
                  <Loader2 className={`w-4 h-4 ${colors.text} animate-spin`} />
                ) : (
                  <Circle className="w-4 h-4 text-slate-600" />
                )}
              </div>
              <span className={`text-sm ${isDone ? 'text-slate-300' : isRunning ? `${colors.text} font-medium` : 'text-slate-600'}`}>
                {stage.label}
              </span>
              {isRunning && (
                <motion.div
                  className={`ml-auto h-0.5 rounded-full ${colors.dot}`}
                  style={{ width: 0 }}
                  animate={{ width: '40%' }}
                  transition={{ duration: stage.duration / 1000, ease: 'easeOut' }}
                />
              )}
            </motion.div>
          );
        })}
      </div>
    </motion.div>
  );
};
