import React, { useState, useEffect } from 'react';
import { ShieldCheck, ArrowUpRight, ArrowDownRight, Loader2, RefreshCw, CheckSquare } from 'lucide-react';
import { Link } from 'react-router-dom';
import { api } from '../services/api';
import { useAuth } from '../context/AuthContext';

const QUESTIONS = [
  { key: 'uses_2fa_on_bank_apps',   label: '2FA on banking & UPI apps',           yesPositive: true },
  { key: 'reuses_passwords',         label: 'Reuse the same password across sites', yesPositive: false },
  { key: 'clicks_unknown_links',     label: 'Click links from unknown senders',     yesPositive: false },
  { key: 'checks_sender_identity',   label: 'Verify sender before acting on requests', yesPositive: true },
  { key: 'device_lock_enabled',      label: 'Device lock (PIN / Biometric) enabled', yesPositive: true },
];

const BAND_COLORS = {
  very_high_risk: { ring: 'border-red-500',    text: 'text-red-400',     bg: 'from-red-950/60 to-surface' },
  high_risk:      { ring: 'border-orange-500', text: 'text-orange-400',  bg: 'from-orange-950/60 to-surface' },
  moderate_risk:  { ring: 'border-amber-500',  text: 'text-amber-400',   bg: 'from-amber-950/60 to-surface' },
  low_risk:       { ring: 'border-blue-500',   text: 'text-blue-400',    bg: 'from-blue-950/60 to-surface' },
  well_protected: { ring: 'border-emerald-500',text: 'text-emerald-400', bg: 'from-emerald-950/60 to-surface' },
};

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
      } catch (err) {
        // offline — show questionnaire directly
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
      // fallback: still show score if API returned it
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
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="w-8 h-8 text-primary animate-spin" />
      </div>
    );
  }

  if (!user) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-16 text-center space-y-3">
        <h1 className="text-2xl font-bold text-white">Cyber Risk Score</h1>
        <p className="text-slate-400 text-sm">Sign in to view your personalised risk score.</p>
        <Link to="/login" className="inline-block text-primary font-semibold text-sm hover:underline">Log in</Link>
      </div>
    );
  }

  const score = scoreData?.score;
  const bandKey = scoreData?.score_band || 'moderate_risk';
  const bandColors = BAND_COLORS[bandKey] || BAND_COLORS.moderate_risk;

  return (
    <div className="max-w-3xl mx-auto px-4 py-8 space-y-8">
      {/* Header */}
      <div className="space-y-2">
        <h1 className="text-3xl font-extrabold text-white flex items-center gap-3">
          <ShieldCheck className="w-8 h-8 text-purple-400" />
          Cyber Risk Score
        </h1>
        <p className="text-slate-300 text-sm">
          An explainable assessment of your online security posture based on your activity and security habits.
        </p>
      </div>

      {/* Score Gauge */}
      {score !== undefined && !showQuestionnaire && (
        <div className={`p-8 rounded-2xl bg-gradient-to-b ${bandColors.bg} border border-border text-center space-y-4`}>
          <div className={`relative w-44 h-44 mx-auto flex items-center justify-center rounded-full border-8 ${bandColors.ring} bg-background/50 shadow-inner`}>
            <div>
              <span className="text-5xl font-extrabold text-white block">{score}</span>
              <span className="text-xs uppercase tracking-wider font-semibold text-slate-400">/ 100</span>
            </div>
          </div>
          <div>
            <span className={`text-lg font-bold ${bandColors.text}`}>
              {scoreData?.score_band_label || 'Moderate Risk'}
            </span>
          </div>
          <button
            onClick={() => setShowQuestionnaire(true)}
            className="inline-flex items-center gap-2 text-xs font-semibold text-slate-400 hover:text-white transition-colors"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            Update via Questionnaire
          </button>
        </div>
      )}

      {/* Questionnaire */}
      {(showQuestionnaire || score === undefined) && (
        <form onSubmit={handleSubmit} className="p-6 rounded-2xl bg-surface border border-border space-y-6">
          <div className="flex items-center gap-2">
            <CheckSquare className="w-5 h-5 text-purple-400" />
            <h3 className="text-base font-bold text-white">Security Habits Questionnaire</h3>
          </div>
          <div className="space-y-5">
            {QUESTIONS.map(({ key, label }) => (
              <div key={key} className="space-y-2">
                <p className="text-sm font-medium text-slate-200">{label}?</p>
                <div className="flex gap-3">
                  <button
                    type="button"
                    onClick={() => handleAnswer(key, true)}
                    className={`flex-1 py-2 rounded-lg text-sm font-semibold border transition-all ${
                      answers[key] === true
                        ? 'bg-emerald-500/20 border-emerald-500/60 text-emerald-200'
                        : 'bg-background border-border text-slate-400 hover:border-slate-500'
                    }`}
                  >
                    Yes
                  </button>
                  <button
                    type="button"
                    onClick={() => handleAnswer(key, false)}
                    className={`flex-1 py-2 rounded-lg text-sm font-semibold border transition-all ${
                      answers[key] === false
                        ? 'bg-red-500/20 border-red-500/60 text-red-200'
                        : 'bg-background border-border text-slate-400 hover:border-slate-500'
                    }`}
                  >
                    No
                  </button>
                </div>
              </div>
            ))}
          </div>
          <button
            type="submit"
            disabled={!allAnswered || submitting}
            className="w-full py-3.5 rounded-xl bg-purple-600 hover:bg-purple-700 text-white font-bold flex items-center justify-center gap-2 disabled:opacity-40 transition-all"
            id="risk-score-submit"
          >
            {submitting ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Calculate My Risk Score'}
          </button>
        </form>
      )}

      {/* Signal Breakdown */}
      {scoreData?.signal_breakdown && !showQuestionnaire && (
        <div className="p-6 rounded-2xl bg-surface border border-border space-y-4">
          <h3 className="text-base font-bold text-white">Score Signal Breakdown</h3>
          <div className="space-y-3">
            {scoreData.signal_breakdown.map((sig, idx) => (
              <div key={idx} className="p-3.5 rounded-xl bg-background border border-border flex items-start gap-3">
                {sig.contribution_direction === 'positive' ? (
                  <ArrowUpRight className="w-5 h-5 text-emerald-400 flex-shrink-0 mt-0.5" />
                ) : (
                  <ArrowDownRight className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
                )}
                <div>
                  <h4 className="text-sm font-semibold text-white">{sig.label}</h4>
                  <p className="text-xs text-slate-400">{sig.description}</p>
                </div>
                <span className={`ml-auto text-xs font-bold px-2 py-0.5 rounded-full ${
                  sig.contribution_direction === 'positive'
                    ? 'bg-emerald-500/15 text-emerald-300'
                    : 'bg-red-500/15 text-red-300'
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
        <div className="p-5 rounded-2xl bg-surface border border-border space-y-3">
          <h3 className="text-sm font-bold text-white">Recommended Improvements</h3>
          <ul className="space-y-2">
            {scoreData.improvement_actions.map((action, idx) => (
              <li key={idx} className="flex items-start gap-2 text-sm text-slate-300">
                <span className="text-purple-400 mt-0.5">›</span>
                {action}
              </li>
            ))}
          </ul>
        </div>
      )}

      {scoreData?.disclaimer && !showQuestionnaire && (
        <p className="text-[11px] text-slate-500 text-center">{scoreData.disclaimer}</p>
      )}
    </div>
  );
};
