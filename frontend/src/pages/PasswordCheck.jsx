import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Lock, Eye, EyeOff, CheckCircle2, ShieldAlert, KeyRound, RefreshCw } from 'lucide-react';
import { api } from '../services/api';

export const PasswordCheck = () => {
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleCheck = async (e) => {
    e.preventDefault();
    if (!password) return;

    setLoading(true);
    try {
      const res = await api.post('/protect/check-password', { password });
      setResult(res.data.verdict);
    } catch {
      // Handled silently
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto px-4 py-10 space-y-8">
      {/* Header */}
      <div className="space-y-3">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-mono font-bold">
          <KeyRound className="w-3.5 h-3.5" /> ENTROPY & PATTERN ANALYSIS
        </div>
        <h1 className="text-3xl sm:text-4xl font-display font-extrabold text-white tracking-tight flex items-center gap-3">
          Password Security Checker
        </h1>
        <p className="text-slate-300 text-sm max-w-xl">
          Evaluate password length, entropy bits, and complexity against automated cracking patterns.
        </p>
      </div>

      {/* Prominent Mandatory Safety Notice (CSHAKTI-UX-001) */}
      <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-200 text-xs flex items-start gap-3">
        <ShieldAlert className="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5" />
        <div>
          <strong className="font-semibold block text-amber-300 mb-0.5">Safety Notice:</strong>
          Do not enter your actual live account passwords here. Use a representative pattern or test password to assess security strength.
        </div>
      </div>

      {/* Form */}
      <div className="p-6 rounded-2xl bg-surface border border-border space-y-4">
        <form onSubmit={handleCheck} className="space-y-4">
          <div>
            <label className="block text-xs font-mono font-bold uppercase tracking-wider text-slate-300 mb-2">
              TEST PASSWORD INPUT
            </label>
            <div className="relative">
              <input
                type={showPassword ? 'text' : 'password'}
                placeholder="Enter a test password to evaluate..."
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-3.5 rounded-xl bg-background border border-border text-white text-sm placeholder-slate-500 focus:outline-none focus:border-emerald-400 pr-12 transition-colors font-mono"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3.5 top-3.5 text-slate-400 hover:text-white"
              >
                {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
              </button>
            </div>
          </div>

          <button
            type="submit"
            disabled={loading || !password}
            className="w-full py-4 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-black font-display font-bold text-xs uppercase tracking-wider flex items-center justify-center gap-2 disabled:opacity-40 transition-all shadow-[0_0_20px_rgba(16,185,129,0.25)]"
          >
            {loading ? <RefreshCw className="w-4 h-4 animate-spin" /> : 'Check Password Strength'}
          </button>
        </form>
      </div>

      {/* Result Display */}
      {result && (
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          className="p-6 rounded-2xl bg-surface border border-border space-y-6"
        >
          <div className="flex items-center justify-between border-b border-border pb-4">
            <span className="text-xs font-mono font-bold uppercase tracking-wider text-slate-400">Strength Verdict</span>
            <span className="text-lg font-display font-extrabold text-emerald-400 uppercase tracking-wide">
              {result.strength_label}
            </span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 text-center">
            <div className="p-4 rounded-xl bg-background border border-border">
              <span className="text-[10px] font-mono text-slate-400 block mb-1">ENTROPY</span>
              <span className="text-xl font-display font-bold text-white">{result.entropy_bits} bits</span>
            </div>
            <div className="p-4 rounded-xl bg-background border border-border">
              <span className="text-[10px] font-mono text-slate-400 block mb-1">LENGTH</span>
              <span className="text-xl font-display font-bold text-white">{result.length} chars</span>
            </div>
            <div className="p-4 rounded-xl bg-background border border-border col-span-2 sm:col-span-1">
              <span className="text-[10px] font-mono text-slate-400 block mb-1">DICTIONARY PATTERN</span>
              <span className={`text-xl font-display font-bold ${result.is_common_password ? 'text-red-400' : 'text-emerald-400'}`}>
                {result.is_common_password ? 'Common (Weak)' : 'Unique'}
              </span>
            </div>
          </div>

          {result.improvements && result.improvements.length > 0 && (
            <div className="space-y-3">
              <h4 className="text-xs font-mono font-bold uppercase tracking-wider text-slate-300">Improvement Recommendations:</h4>
              <ul className="space-y-2">
                {result.improvements.map((rec, idx) => (
                  <li key={idx} className="text-xs text-slate-300 flex items-start gap-2.5">
                    <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0 mt-0.5" />
                    <span>{rec}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Safety Notice after result */}
          <div className="pt-3 border-t border-border text-[11px] text-slate-500 italic">
            {result.disclaimer}
          </div>
        </motion.div>
      )}
    </div>
  );
};
