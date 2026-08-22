import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { ShieldCheck, ArrowUpRight, ArrowDownRight, RefreshCw, CheckSquare, Activity, AlertTriangle } from 'lucide-react';
import { Link } from 'react-router-dom';
import { api } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { RiskMeter } from '../components/RiskMeter';

const QUESTIONS = [
  { key: 'uses_2fa_on_bank_apps',   label: '2FA / Multi-Factor enabled on banking & UPI apps', yesPositive: true },
  { key: 'reuses_passwords',         label: 'Reuse the same password across multiple online sites', yesPositive: false },
  { key: 'clicks_unknown_links',     label: 'Click links or download files from unknown senders', yesPositive: false },
  { key: 'checks_sender_identity',   label: 'Verify sender identity before acting on financial requests', yesPositive: true },
  { key: 'device_lock_enabled',      label: 'Device lock (Biometric / PIN) enabled on all personal devices', yesPositive: true },
];

export const RiskScore = () => {
  const { user } = useAuth();
  const [scoreData, setScoreData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [answers, setAnswers] = useState({});
  const [showQuestionnaire, setShowQuestionnaire] = useState(false);

  useEffect(() => {
    const fetchScore = async () => {
      try {
        const res = await api.get('/assist/risk-score');
        setScoreData(res.data);
      } catch {
        setShowQuestionnaire(true);
      } finally {
        setLoading(false);
      }
    };
    if (user) {
      fetchScore();
    } else {
      setLoading(false);
    }
  }, [user]);

  const handleAnswer = (key, value) => {
    setAnswers(prev => ({ ...prev, [key]: value }));
  };

  const allAnswered = QUESTIONS.every(q => answers[q.key] !== undefined);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!allAnswered) return;
    setSubmitting(true);
    try {
      const res = await api.post('/assist/risk-score/questionnaire', answers);
      setScoreData(res.data);
      setShowQuestionnaire(false);
    } catch (err) {
      const data = err.response?.data;
      if (data?.score !== undefined) {
        setScoreData(data);
        setShowQuestionnaire(false);
      }
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] space-y-3">
        <RefreshCw className="w-8 h-8 text-cyan-400 animate-spin" />
        <p className="text-xs font-mono text-slate-400">Loading risk profile…</p>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="max-w-md mx-auto px-4 py-20 text-center space-y-4">
        <div className="p-4 rounded-2xl bg-cyan-500/10 border border-cyan-500/30 w-fit mx-auto text-cyan-400">
          <ShieldCheck className="w-10 h-10" />
        </div>
        <h1 className="text-2xl font-display font-bold text-white">Cyber Risk Score</h1>
        <p className="text-slate-400 text-xs">
          Sign in to view your explainable digital safety risk assessment and personalized threat metrics.
        </p>
        <Link
          to="/login"
          className="inline-block px-6 py-2.5 rounded-xl bg-cyan-500 text-black font-bold text-xs uppercase tracking-wider shadow-lg"
        >
          Log In to Access Score
        </Link>
      </div>
    );
  }

  const score = scoreData?.score ?? 78; // Default demo score if first time

  return (
    <div className="max-w-4xl mx-auto px-4 py-10 space-y-8">
      {/* Header */}
      <div className="space-y-3">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-purple-500/10 border border-purple-500/30 text-purple-400 text-xs font-mono font-bold">
          <Activity className="w-3.5 h-3.5" /> EXPLAINABLE THREAT ENGINE
        </div>
        <h1 className="text-3xl sm:text-4xl font-display font-extrabold text-white tracking-tight flex items-center gap-3">
          Cyber Risk Score Center
        </h1>
        <p className="text-slate-300 text-sm max-w-2xl">
          An explainable security assessment reflecting your digital safety posture based on habits, multi-factor auth, and threat exposure.
        </p>
      </div>

      {/* Main Score Gauge Display */}
      {score !== undefined && !showQuestionnaire && (
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.4 }}
          className="p-8 rounded-2xl bg-surface border border-border shadow-2xl space-y-6 text-center relative overflow-hidden"
        >
          <div className="absolute top-0 right-0 w-48 h-48 bg-purple-500/5 rounded-bl-full pointer-events-none" />

          {/* Animated Radial Arc Gauge */}
          <div className="py-4">
            <RiskMeter
              value={score}
              maxValue={100}
              size={220}
              label={scoreData?.score_band_label || (score > 70 ? 'PROTECTED / LOW RISK' : 'MODERATE RISK')}
              sublabel="CYBER POSTURE INDEX"
            />
          </div>

          <div className="flex justify-center">
            <button
              onClick={() => setShowQuestionnaire(true)}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-surface-raised hover:bg-slate-700 text-xs font-semibold text-slate-300 transition-colors border border-border"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              Re-assess Security Habits Questionnaire
            </button>
          </div>
        </motion.div>
      )}

      {/* Questionnaire Form */}
      {(showQuestionnaire || score === undefined) && (
        <motion.form
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          onSubmit={handleSubmit}
          className="p-6 sm:p-8 rounded-2xl bg-surface border border-border space-y-6"
        >
          <div className="flex items-center gap-3 border-b border-border/60 pb-4">
            <div className="p-2 rounded-lg bg-purple-500/10 text-purple-400">
              <CheckSquare className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-display font-bold text-white">Security Habits Assessment</h3>
              <p className="text-xs text-slate-400">Answer 5 questions to generate your personalized Cyber Risk Score</p>
            </div>
          </div>

          <div className="space-y-5">
            {QUESTIONS.map(({ key, label }) => (
              <div key={key} className="space-y-2.5 p-4 rounded-xl bg-background/50 border border-border/50">
                <p className="text-sm font-medium text-slate-200">{label}?</p>
                <div className="flex gap-3">
                  <button
                    type="button"
                    onClick={() => handleAnswer(key, true)}
                    className={`flex-1 py-2.5 rounded-lg text-xs font-bold border transition-all ${
                      answers[key] === true
                        ? 'bg-emerald-500/20 border-emerald-500/60 text-emerald-300 shadow-md'
                        : 'bg-surface border-border text-slate-400 hover:border-slate-500'
                    }`}
                  >
                    YES
                  </button>
                  <button
                    type="button"
                    onClick={() => handleAnswer(key, false)}
                    className={`flex-1 py-2.5 rounded-lg text-xs font-bold border transition-all ${
                      answers[key] === false
                        ? 'bg-red-500/20 border-red-500/60 text-red-300 shadow-md'
                        : 'bg-surface border-border text-slate-400 hover:border-slate-500'
                    }`}
                  >
                    NO
                  </button>
                </div>
              </div>
            ))}
          </div>

          <button
            type="submit"
            disabled={!allAnswered || submitting}
            className="w-full py-4 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-display font-bold text-xs uppercase tracking-wider flex items-center justify-center gap-2 disabled:opacity-40 transition-all shadow-lg shadow-purple-600/25"
            id="risk-score-submit"
          >
            {submitting ? <RefreshCw className="w-4 h-4 animate-spin" /> : 'Calculate Cyber Risk Score'}
          </button>
        </motion.form>
      )}

      {/* Signal Breakdown */}
      {scoreData?.signal_breakdown && !showQuestionnaire && (
        <div className="p-6 rounded-2xl bg-surface border border-border space-y-4">
          <h3 className="text-sm font-display font-bold text-white uppercase tracking-wider">
            Explainable Signal Contributions
          </h3>
          <div className="space-y-3">
            {scoreData.signal_breakdown.map((sig, idx) => (
              <div key={idx} className="p-4 rounded-xl bg-background/60 border border-border flex items-start gap-3">
                {sig.contribution_direction === 'positive' ? (
                  <ArrowUpRight className="w-5 h-5 text-emerald-400 flex-shrink-0 mt-0.5" />
                ) : (
                  <ArrowDownRight className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
                )}
                <div className="flex-1">
                  <h4 className="text-xs font-bold text-white">{sig.label}</h4>
                  <p className="text-[11px] text-slate-400 mt-0.5">{sig.description}</p>
                </div>
                <span className={`text-xs font-mono font-bold px-2 py-0.5 rounded-md ${
                  sig.contribution_direction === 'positive'
                    ? 'bg-emerald-500/15 text-emerald-300 border border-emerald-500/30'
                    : 'bg-red-500/15 text-red-300 border border-red-500/30'
                }`}>
                  {sig.weight > 0 ? '+' : ''}{sig.weight}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Improvement Actions */}
      {scoreData?.improvement_actions && !showQuestionnaire && (
        <div className="p-6 rounded-2xl bg-surface border border-border space-y-3">
          <h3 className="text-sm font-display font-bold text-white uppercase tracking-wider">
            Recommended Security Hardening Actions
          </h3>
          <ul className="space-y-2">
            {scoreData.improvement_actions.map((action, idx) => (
              <li key={idx} className="flex items-start gap-2.5 text-xs text-slate-300">
                <span className="text-cyan-400 font-bold">›</span>
                {action}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};
