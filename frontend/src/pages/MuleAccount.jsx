import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Banknote, AlertCircle, RefreshCw, ShieldX, ShieldCheck, Info, Network, GitCommit } from 'lucide-react';
import { api } from '../services/api';
import { ScanAnimation } from '../components/ScanAnimation';
import { ThreatResultCard } from '../components/ThreatResultCard';

const SIGNALS_CONFIG = [
  { key: 'account_age_category',       label: 'Account Age',              options: [{ value: 0, label: 'Less than 6 months (New)' }, { value: 1, label: '6–24 months' }, { value: 2, label: 'More than 2 years' }] },
  { key: 'transaction_velocity_high',  label: 'Transaction Velocity',     options: [{ value: 1, label: 'High (Rapid burst transfers)' }, { value: 0, label: 'Normal velocity' }] },
  { key: 'multiple_recipients',        label: 'Fan-Out Recipients',       options: [{ value: 1, label: 'Yes — Fan-out to many accounts' }, { value: 0, label: 'No — Normal recipient list' }] },
  { key: 'pass_through',               label: 'Pass-Through Pattern',   options: [{ value: 1, label: 'Yes — Rapid cash-in & cash-out' }, { value: 0, label: 'No — Normal balance retention' }] },
];

const MULE_STAGES = [
  { id: 'input',     label: 'Ingesting banking transaction signals', duration: 300 },
  { id: 'normalize', label: 'Constructing entity transfer graph',   duration: 500 },
  { id: 'extract',   label: 'Evaluating velocity & pass-through', duration: 600 },
  { id: 'model',     label: 'Running XGBoost mule classifier',   duration: 700 },
  { id: 'risk',      label: 'Calculating anomaly probability score', duration: 400 },
];

const DEFAULTS = Object.fromEntries(SIGNALS_CONFIG.map(s => [s.key, s.options[1].value]));
const POLLING_MAX = 20;
const POLLING_INTERVAL_MS = 1500;

export const MuleAccount = () => {
  const [signals, setSignals] = useState(DEFAULTS);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [currentTaskId, setCurrentTaskId] = useState(null);

  const handleSignalChange = (key, val) => {
    setSignals(prev => ({ ...prev, [key]: Number(val) }));
    setResult(null);
    setError(null);
  };

  const pollTask = (taskId) => {
    let attempts = 0;
    const interval = setInterval(async () => {
      attempts++;
      try {
        const res = await api.get(`/tasks/${taskId}/status`);
        const { status, result: taskResult, message } = res.data;
        if (status === 'complete') {
          clearInterval(interval);
          setLoading(false);
          setResult(taskResult);
        } else if (status === 'error' || attempts >= POLLING_MAX) {
          clearInterval(interval);
          setLoading(false);
          setError(message || 'Analysis timed out.');
        }
      } catch {
        clearInterval(interval);
        setLoading(false);
        setError('Connection error during analysis.');
      }
    }, POLLING_INTERVAL_MS);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);
    setError(null);
    try {
      const res = await api.post('/detect/assess-mule-account', { account_signals: signals });
      if (res.data.task_id) {
        setCurrentTaskId(res.data.task_id);
        pollTask(res.data.task_id);
      } else {
        setLoading(false);
        setError('Unexpected response from server.');
      }
    } catch (err) {
      setLoading(false);
      const msg = err.response?.data?.detail?.message || err.response?.data?.detail || 'Failed to submit signal data.';
      setError(typeof msg === 'string' ? msg : JSON.stringify(msg));
    }
  };

  const verdict = result?.verdict;
  const anomalyScore = result?.analysis?.anomaly_score !== undefined ? result.analysis.anomaly_score * 100 : 0;

  return (
    <div className="max-w-5xl mx-auto px-4 py-10 space-y-8">
      {/* Header */}
      <div className="space-y-3">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-orange-500/10 border border-orange-500/30 text-orange-400 text-xs font-mono font-bold">
          <Network className="w-3.5 h-3.5" /> GRAPH & BEHAVIORAL INVESTIGATOR
        </div>
        <h1 className="text-3xl sm:text-4xl font-display font-extrabold text-white tracking-tight flex items-center gap-3">
          Money Mule Account Detection
        </h1>
        <p className="text-slate-300 text-sm max-w-2xl">
          Identify banking accounts used as financial crime money mules using our XGBoost behavioral signal analysis model.
        </p>
      </div>

      {/* Network Investigation Graphic Visualizer */}
      <div className="p-6 rounded-2xl bg-surface border border-border space-y-4">
        <div className="flex items-center justify-between">
          <span className="text-xs font-mono font-bold uppercase tracking-wider text-orange-400 flex items-center gap-2">
            <GitCommit className="w-4 h-4" /> INVESTIGATION NODE GRAPH TOPOLOGY
          </span>
          <span className="text-[10px] font-mono text-slate-500">XGBoost Engine v1.0</span>
        </div>

        {/* Node Connection Flow Graphic */}
        <div className="p-6 rounded-xl bg-background/80 border border-border flex flex-wrap items-center justify-around gap-4 text-center">
          <div className="space-y-1">
            <div className="w-10 h-10 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center mx-auto text-slate-300 text-xs font-mono font-bold">
              SRC
            </div>
            <p className="text-[10px] font-mono text-slate-400">VICTIM ENTITY</p>
          </div>

          <div className="flex-1 max-w-[80px] h-0.5 bg-gradient-to-r from-slate-700 via-orange-500/50 to-slate-700 relative">
            <div className="absolute top-1/2 -translate-y-1/2 left-1/2 -translate-x-1/2 w-2 h-2 rounded-full bg-orange-400 animate-pulse" />
          </div>

          <div className="space-y-1">
            <div className="w-12 h-12 rounded-full bg-orange-500/20 border border-orange-500/50 flex items-center justify-center mx-auto text-orange-300 text-xs font-mono font-bold shadow-[0_0_15px_rgba(249,115,22,0.2)]">
              MULE
            </div>
            <p className="text-[10px] font-mono text-orange-400 font-bold">TARGET ACCOUNT</p>
          </div>

          <div className="flex-1 max-w-[80px] h-0.5 bg-gradient-to-r from-slate-700 via-orange-500/50 to-slate-700 relative">
            <div className="absolute top-1/2 -translate-y-1/2 left-1/2 -translate-x-1/2 w-2 h-2 rounded-full bg-orange-400 animate-pulse" />
          </div>

          <div className="space-y-1">
            <div className="w-10 h-10 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center mx-auto text-slate-300 text-xs font-mono font-bold">
              DEST
            </div>
            <p className="text-[10px] font-mono text-slate-400">OFFSHORE / CASH</p>
          </div>
        </div>
      </div>

      {/* Signal Selector & Scan Stage */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Form Signals */}
        <form onSubmit={handleSubmit} className="p-6 rounded-2xl bg-surface border border-border space-y-6">
          <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-slate-300">
            ACCOUNT BEHAVIOR SIGNALS
          </h3>

          <div className="space-y-5">
            {SIGNALS_CONFIG.map(({ key, label, options }) => (
              <div key={key} className="space-y-2">
                <label className="block text-xs font-semibold text-slate-200">{label}</label>
                <div className="flex flex-wrap gap-2">
                  {options.map(opt => (
                    <button
                      key={opt.value}
                      type="button"
                      onClick={() => handleSignalChange(key, opt.value)}
                      className={`px-3.5 py-2 rounded-lg text-xs font-bold border transition-all ${
                        signals[key] === opt.value
                          ? 'bg-orange-500/20 border-orange-500/60 text-orange-200 shadow-md'
                          : 'bg-background border-border text-slate-400 hover:border-slate-500'
                      }`}
                    >
                      {opt.label}
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-4 rounded-xl bg-orange-500 hover:bg-orange-400 text-black font-display font-bold text-xs uppercase tracking-wider flex items-center justify-center gap-2 disabled:opacity-40 transition-all shadow-[0_0_20px_rgba(249,115,22,0.25)]"
            id="mule-analyze-btn"
          >
            {loading ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                Evaluating Behavioral Features…
              </>
            ) : (
              <>
                <Banknote className="w-4 h-4" />
                Assess Mule Account Risk
              </>
            )}
          </button>
        </form>

        {/* Right Output */}
        <div className="space-y-6">
          <ScanAnimation
            isActive={loading}
            scanId={currentTaskId}
            stages={MULE_STAGES}
            accentColor="orange"
          />

          {error && (
            <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/30 text-red-300 text-xs flex items-start gap-3">
              <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          {verdict && !loading && (
            <ThreatResultCard
              verdict={verdict}
              confidence={anomalyScore}
              threatType={verdict.risk_level === 'safe' ? 'Low Risk Account' : 'Money Mule Account Pattern'}
              scanId={currentTaskId}
              extraMetrics={[
                { label: 'Mule Anomaly Score', value: `${anomalyScore.toFixed(1)}%`, sub: 'XGBoost probability' },
                { label: 'Classifier Engine', value: 'XGBoost', sub: 'Behavioral model' },
                { label: 'Risk Band', value: verdict.risk_level?.toUpperCase() || 'SAFE', sub: 'Threat level' }
              ]}
            />
          )}

          {!verdict && !loading && (
            <div className="p-12 rounded-2xl bg-surface/40 border border-border/40 text-center space-y-3">
              <Network className="w-12 h-12 text-slate-600 mx-auto" />
              <p className="text-slate-400 text-xs">
                Configure account behavioral signals on the left and click "Assess Mule Account Risk".
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
