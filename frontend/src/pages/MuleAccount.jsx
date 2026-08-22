import React, { useState } from 'react';
import { Banknote, AlertCircle, Loader2, ShieldX, ShieldCheck, Info } from 'lucide-react';
import { api } from '../services/api';

const SIGNALS_CONFIG = [
  { key: 'account_age_category',       label: 'Account Age',              options: [{ value: 0, label: 'Less than 6 months' }, { value: 1, label: '6–24 months' }, { value: 2, label: 'More than 2 years' }] },
  { key: 'transaction_velocity_high',  label: 'Transaction Volume',       options: [{ value: 1, label: 'High (many rapid transfers)' }, { value: 0, label: 'Normal' }] },
  { key: 'multiple_recipients',        label: 'Multiple Recipients',       options: [{ value: 1, label: 'Yes — sends to many accounts' }, { value: 0, label: 'No — single/few recipients' }] },
  { key: 'pass_through',               label: 'Pass-Through Behaviour',   options: [{ value: 1, label: 'Yes — funds quickly withdrawn' }, { value: 0, label: 'No — normal spending patterns' }] },
];

const DEFAULTS = Object.fromEntries(SIGNALS_CONFIG.map(s => [s.key, s.options[1].value]));

const POLLING_MAX = 20;
const POLLING_INTERVAL_MS = 1500;

const BADGE_STYLES = {
  high_risk:     { bg: 'bg-red-500/15 border-red-500/40',        text: 'text-red-300',     label: '⚠ MULE ACCOUNT DETECTED', icon: ShieldX },
  moderate_risk: { bg: 'bg-amber-500/15 border-amber-500/40',    text: 'text-amber-300',   label: '⚠ SUSPICIOUS SIGNALS',    icon: ShieldX },
  safe:          { bg: 'bg-emerald-500/15 border-emerald-500/40', text: 'text-emerald-300', label: '✓ LOW RISK',              icon: ShieldCheck },
};

export const MuleAccount = () => {
  const [signals, setSignals] = useState(DEFAULTS);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

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
  const badge = verdict ? BADGE_STYLES[verdict.risk_level] : null;

  return (
    <div className="max-w-3xl mx-auto px-4 py-8 space-y-8">
      {/* Header */}
      <div className="space-y-2">
        <h1 className="text-3xl font-extrabold text-white flex items-center gap-3">
          <Banknote className="w-8 h-8 text-orange-400" />
          Mule Account Detection
        </h1>
        <p className="text-slate-300 text-sm">
          Identify banking accounts being used as financial crime mule accounts using our XGBoost-based signal analysis engine (F-07).
        </p>
      </div>

      {/* Info Banner */}
      <div className="flex items-start gap-3 p-4 rounded-xl bg-orange-500/8 border border-orange-500/20">
        <Info className="w-4 h-4 text-orange-400 flex-shrink-0 mt-0.5" />
        <p className="text-xs text-slate-300">
          Provide behavioural signals observed on a bank account. Our XGBoost classifier will predict whether the account pattern matches known money mule profiles used in cyber fraud.
        </p>
      </div>

      {/* Signal Input Form */}
      <form onSubmit={handleSubmit} className="p-6 rounded-2xl bg-surface border border-border space-y-6">
        <h3 className="text-base font-bold text-white">Account Behaviour Signals</h3>
        <div className="space-y-5">
          {SIGNALS_CONFIG.map(({ key, label, options }) => (
            <div key={key} className="space-y-2">
              <label className="block text-sm font-semibold text-slate-200">{label}</label>
              <div className="flex flex-wrap gap-3">
                {options.map(opt => (
                  <button
                    key={opt.value}
                    type="button"
                    onClick={() => handleSignalChange(key, opt.value)}
                    className={`px-4 py-2 rounded-lg text-sm font-medium border transition-all ${
                      signals[key] === opt.value
                        ? 'bg-orange-500/20 border-orange-500/60 text-orange-200'
                        : 'bg-background border-border text-slate-400 hover:border-slate-500 hover:text-slate-200'
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
          className="w-full py-3.5 rounded-xl bg-orange-600 hover:bg-orange-700 text-white font-bold flex items-center justify-center gap-2 disabled:opacity-40 transition-all"
          id="mule-analyze-btn"
        >
          {loading ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              Running XGBoost Classifier…
            </>
          ) : (
            <>
              <Banknote className="w-5 h-5" />
              Assess Account Risk
            </>
          )}
        </button>
      </form>

      {/* Error */}
      {error && (
        <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/30 text-red-300 text-sm flex items-start gap-3">
          <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
          <span>{error}</span>
        </div>
      )}

      {/* Verdict Card */}
      {verdict && badge && (
        <div className={`p-6 rounded-2xl border space-y-5 ${badge.bg}`}>
          {/* Verdict Header */}
          <div className="flex items-center gap-4">
            <div className={`p-3 rounded-xl border ${badge.bg}`}>
              {React.createElement(badge.icon, { className: `w-7 h-7 ${badge.text}` })}
            </div>
            <div>
              <span className={`text-xs uppercase tracking-widest font-bold ${badge.text}`}>
                {badge.label}
              </span>
              <p className="text-white font-bold text-lg">{verdict.risk_label || verdict.risk_level}</p>
            </div>
          </div>

          {/* Metrics Row */}
          <div className="grid grid-cols-2 gap-3">
            <div className="p-4 rounded-xl bg-background/60 border border-border text-center space-y-1">
              <p className="text-xs uppercase tracking-wider text-slate-400">Anomaly Score</p>
              <p className={`text-2xl font-extrabold ${badge.text}`}>
                {result?.analysis?.anomaly_score !== undefined
                  ? (result.analysis.anomaly_score * 100).toFixed(1) + '%'
                  : '—'}
              </p>
              <p className="text-[10px] text-slate-500">Mule probability</p>
            </div>
            <div className="p-4 rounded-xl bg-background/60 border border-border text-center space-y-1">
              <p className="text-xs uppercase tracking-wider text-slate-400">Model</p>
              <p className="text-xs font-bold text-slate-200 leading-tight mt-1">XGBoost<br/>Classifier</p>
              <p className="text-[10px] text-slate-500">Behavioural signals</p>
            </div>
          </div>

          {/* Explanation */}
          {verdict.explanation && (
            <div className="p-4 rounded-xl bg-background/60 border border-border space-y-1">
              <p className="text-xs uppercase tracking-wider text-slate-400 font-semibold">Analysis</p>
              <p className="text-slate-200 text-sm">{verdict.explanation}</p>
            </div>
          )}

          {/* Recommended Action */}
          {verdict.recommended_action && (
            <div className="p-4 rounded-xl bg-background/60 border border-border space-y-1">
              <p className="text-xs uppercase tracking-wider text-slate-400 font-semibold">Recommended Action</p>
              <p className="text-slate-200 text-sm">{verdict.recommended_action}</p>
            </div>
          )}

          <p className="text-[10px] text-slate-500 text-center">
            {verdict.disclaimer || 'Mule account detection uses XGBoost trained on synthetic financial crime behavioural datasets.'}
          </p>
        </div>
      )}

      {/* Info Box */}
      <div className="p-5 rounded-2xl bg-surface border border-border space-y-3">
        <h3 className="text-sm font-bold text-white">What is a Mule Account?</h3>
        <p className="text-xs text-slate-400 leading-relaxed">
          A money mule account is a bank account used by cybercriminals to receive and quickly transfer stolen funds. 
          Account holders may be witting (complicit) or unwitting (recruited as fake job candidates). 
          This tool analyses behavioural signals to flag accounts showing patterns consistent with mule usage.
        </p>
      </div>
    </div>
  );
};
