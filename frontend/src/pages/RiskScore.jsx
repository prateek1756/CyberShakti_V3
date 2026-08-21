import React, { useState, useEffect } from 'react';
import { ShieldCheck, ArrowUpRight, ArrowDownRight, Loader2 } from 'lucide-react';
import { Link } from 'react-router-dom';
import { api } from '../services/api';
import { useAuth } from '../context/AuthContext';

export const RiskScore = () => {
  const { user } = useAuth();
  const [scoreData, setScoreData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchScore = async () => {
      try {
        const res = await api.get('/assist/risk-score');
        setScoreData(res.data);
      } catch (err) {
        // Handle error
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

  if (!scoreData) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-16 text-center space-y-3">
        <h1 className="text-2xl font-bold text-white">Cyber Risk Score</h1>
        <p className="text-slate-400 text-sm">Unable to load your risk score. Please try again.</p>
      </div>
    );
  }

  const score = scoreData.score;

  return (
    <div className="max-w-3xl mx-auto px-4 py-8 space-y-8">
      {/* Header */}
      <div className="space-y-2">
        <h1 className="text-3xl font-extrabold text-white flex items-center gap-3">
          <ShieldCheck className="w-8 h-8 text-purple-400" />
          Cyber Risk Score
        </h1>
        <p className="text-slate-300 text-sm">
          An explainable assessment of your online security posture based on recent activity and security practices.
        </p>
      </div>

      {/* Score Gauge Circular Display */}
      <div className="p-8 rounded-2xl bg-surface border border-border text-center space-y-4">
        <div className="relative w-44 h-44 mx-auto flex items-center justify-center rounded-full border-8 border-purple-500/20 bg-background/50 shadow-inner">
          <div>
            <span className="text-5xl font-extrabold text-white block">{score}</span>
            <span className="text-xs uppercase tracking-wider font-semibold text-slate-400">/ 100</span>
          </div>
        </div>
        <div>
          <span className="text-lg font-bold text-purple-300">{scoreData?.score_band_label || 'Moderate Risk'}</span>
        </div>
      </div>

      {/* Breakdown List */}
      {scoreData?.signal_breakdown && (
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
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
