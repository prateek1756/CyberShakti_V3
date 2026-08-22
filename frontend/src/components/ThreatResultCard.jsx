import React, { useEffect } from 'react';
import { motion, useMotionValue, useTransform, animate } from 'framer-motion';
import {
  ShieldX, ShieldCheck, AlertTriangle, AlertOctagon, Shield, Info,
  Clock, Hash, Cpu, AlertCircle,
} from 'lucide-react';
import { RiskMeter } from './RiskMeter';

const RISK_CONFIG = {
  safe: {
    label: 'SAFE',
    subLabel: 'No Threat Detected',
    colors: {
      bg:     'bg-emerald-950/40',
      border: 'border-emerald-500/30',
      badge:  'bg-emerald-500/20 text-emerald-300 border-emerald-500/40',
      text:   'text-emerald-400',
      meter:  { stroke: '#22C55E', text: 'text-emerald-400', glow: 'rgba(34,197,94,0.3)' },
    },
    icon: ShieldCheck,
  },
  low_risk: {
    label: 'LOW RISK',
    subLabel: 'Minor Indicators Found',
    colors: {
      bg:     'bg-lime-950/40',
      border: 'border-lime-500/30',
      badge:  'bg-lime-500/20 text-lime-300 border-lime-500/40',
      text:   'text-lime-400',
      meter:  { stroke: '#84CC16', text: 'text-lime-400', glow: 'rgba(132,204,22,0.3)' },
    },
    icon: Info,
  },
  moderate_risk: {
    label: 'MODERATE RISK',
    subLabel: 'Suspicious Activity',
    colors: {
      bg:     'bg-amber-950/40',
      border: 'border-amber-500/30',
      badge:  'bg-amber-500/20 text-amber-300 border-amber-500/40',
      text:   'text-amber-400',
      meter:  { stroke: '#F59E0B', text: 'text-amber-400', glow: 'rgba(245,158,11,0.3)' },
    },
    icon: AlertTriangle,
  },
  high_risk: {
    label: 'HIGH RISK',
    subLabel: 'Threat Detected',
    colors: {
      bg:     'bg-orange-950/40',
      border: 'border-orange-500/30',
      badge:  'bg-orange-500/20 text-orange-300 border-orange-500/40',
      text:   'text-orange-400',
      meter:  { stroke: '#F97316', text: 'text-orange-400', glow: 'rgba(249,115,22,0.3)' },
    },
    icon: ShieldX,
  },
  critical: {
    label: 'CRITICAL',
    subLabel: 'Active Threat',
    colors: {
      bg:     'bg-red-950/40',
      border: 'border-red-500/30',
      badge:  'bg-red-500/20 text-red-300 border-red-500/40',
      text:   'text-red-400',
      meter:  { stroke: '#EF4444', text: 'text-red-400', glow: 'rgba(239,68,68,0.3)' },
    },
    icon: AlertOctagon,
  },
  unknown: {
    label: 'UNKNOWN',
    subLabel: 'Unverified / Unreachable Destination',
    colors: {
      bg:     'bg-slate-900/60',
      border: 'border-slate-500/40',
      badge:  'bg-slate-500/20 text-slate-300 border-slate-500/40',
      text:   'text-slate-300',
      meter:  { stroke: '#94A3B8', text: 'text-slate-300', glow: 'rgba(148,163,184,0.3)' },
    },
    icon: Info,
  },
};

// Animated confidence number
const AnimatedNumber = ({ value, suffix = '%', className }) => {
  const motionVal = useMotionValue(0);
  const displayed = useTransform(motionVal, v => v.toFixed(1));

  useEffect(() => {
    const c = animate(motionVal, value, { duration: 1.4, ease: [0.16, 1, 0.3, 1] });
    return c.stop;
  }, [value]);

  return (
    <motion.span className={className}>
      <motion.span>{displayed}</motion.span>{suffix}
    </motion.span>
  );
};

export const ThreatResultCard = ({
  verdict,          // { risk_level, risk_label, explanation, recommended_action, disclaimer, scam_category, is_experimental }
  confidence,       // 0–100 number (anomaly_score * 100)
  threatType,       // e.g. "Deepfake Detected", "Phishing Link", "Scam Message"
  scanId,
  timestamp,
  extraMetrics,     // array of { label, value, sub }
}) => {
  if (!verdict) return null;

  const riskKey = (verdict.risk_level || 'safe').toLowerCase();
  const config = RISK_CONFIG[riskKey] || RISK_CONFIG.safe;
  const IconComponent = config.icon;
  const c = config.colors;

  const scanTimestamp = timestamp || new Date().toISOString();
  const displayId = scanId || `CS-${Math.random().toString(36).substring(2, 9).toUpperCase()}`;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
      className={`rounded-2xl border ${c.border} ${c.bg} overflow-hidden`}
    >
      {/* Header strip */}
      <div className={`px-6 py-4 flex items-center justify-between border-b ${c.border} backdrop-blur-sm`}>
        <div className="flex items-center gap-3">
          <div className={`p-2 rounded-lg ${c.badge} border`}>
            <IconComponent className="w-5 h-5" />
          </div>
          <div>
            <p className={`text-xs font-bold uppercase tracking-widest ${c.text}`}>
              Threat Analysis
            </p>
            <p className="text-white font-bold text-lg leading-tight">
              {verdict.risk_label || config.label}
            </p>
          </div>
        </div>
        <div className={`px-3 py-1 rounded-full border text-xs font-bold uppercase tracking-wider ${c.badge}`}>
          {config.label}
        </div>
      </div>

      {/* Body */}
      <div className="p-6 space-y-5">
        {/* Confidence + Threat type */}
        <div className="flex items-center gap-6">
          {confidence !== undefined && (
            <div className="text-center">
              <RiskMeter
                value={Math.min(confidence, 100)}
                size={120}
                color={config.colors.meter}
                sublabel="/ 100"
              />
              <p className="text-xs text-slate-400 mt-1">Confidence</p>
            </div>
          )}

          <div className="flex-1 space-y-3">
            {threatType && (
              <div>
                <p className="text-[10px] uppercase tracking-wider text-slate-500 mb-0.5">
                  Threat Classification
                </p>
                <p className={`text-lg font-bold ${c.text}`}>{threatType}</p>
              </div>
            )}
            {verdict.scam_category && (
              <div>
                <p className="text-[10px] uppercase tracking-wider text-slate-500 mb-0.5">
                  Category
                </p>
                <span className={`inline-block text-xs font-medium px-2 py-0.5 rounded-md border ${c.badge}`}>
                  {verdict.scam_category.replace(/_/g, ' ')}
                </span>
              </div>
            )}
            {verdict.is_experimental && (
              <span className="inline-block px-2 py-0.5 text-xs font-bold uppercase rounded-full bg-purple-500/20 text-purple-300 border border-purple-400/30">
                Experimental
              </span>
            )}
          </div>
        </div>

        {/* Extra metrics row */}
        {extraMetrics && extraMetrics.length > 0 && (
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
            {extraMetrics.map((m, i) => (
              <div key={i} className="p-3 rounded-xl bg-background/60 border border-white/5 text-center space-y-0.5">
                <p className="text-[10px] uppercase tracking-wider text-slate-500">{m.label}</p>
                <p className={`text-lg font-extrabold ${c.text}`}>{m.value}</p>
                {m.sub && <p className="text-[10px] text-slate-600">{m.sub}</p>}
              </div>
            ))}
          </div>
        )}

        {/* Analysis explanation */}
        {verdict.explanation && (
          <div className="p-4 rounded-xl bg-background/50 border border-white/5 space-y-1">
            <p className="text-[10px] uppercase tracking-wider text-slate-500 font-semibold">
              Analysis
            </p>
            <p className="text-slate-200 text-sm leading-relaxed">{verdict.explanation}</p>
          </div>
        )}

        {/* Recommended action */}
        {verdict.recommended_action && (
          <div className={`p-4 rounded-xl border ${c.border} bg-background/30 space-y-1`}>
            <p className="text-[10px] uppercase tracking-wider text-slate-500 font-semibold flex items-center gap-1.5">
              <AlertCircle className="w-3 h-3" />
              Recommended Action
            </p>
            <p className={`text-sm font-medium ${c.text}`}>{verdict.recommended_action}</p>
          </div>
        )}

        {/* Scan metadata */}
        <div className="flex flex-wrap gap-x-5 gap-y-1.5 pt-1 border-t border-white/5">
          <div className="flex items-center gap-1.5 text-[10px] text-slate-500">
            <Hash className="w-3 h-3" />
            <span className="font-mono">{displayId}</span>
          </div>
          <div className="flex items-center gap-1.5 text-[10px] text-slate-500">
            <Clock className="w-3 h-3" />
            <span>{new Date(scanTimestamp).toLocaleString()}</span>
          </div>
          <div className="flex items-center gap-1.5 text-[10px] text-slate-500">
            <Cpu className="w-3 h-3" />
            <span>CyberShakti AI Engine</span>
          </div>
        </div>

        {/* Disclaimer */}
        <p className="text-[10px] text-slate-600 italic">
          {verdict.disclaimer || 'AI model output is advisory. Human verification recommended for critical decisions.'}
        </p>
      </div>
    </motion.div>
  );
};
