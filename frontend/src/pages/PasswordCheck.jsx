import React, { useState } from 'react';
import { Lock, Eye, EyeOff, AlertTriangle, CheckCircle, ShieldAlert } from 'lucide-react';
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
    } catch (err) {
      // Error
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto px-4 py-8 space-y-8">
      {/* Header */}
      <div className="space-y-2">
        <h1 className="text-3xl font-extrabold text-white flex items-center gap-3">
          <Lock className="w-8 h-8 text-emerald-400" />
          Password Security Checker
        </h1>
        <p className="text-slate-300 text-sm">
          Evaluate password length, entropy, and complexity against automated cracking patterns.
        </p>
      </div>

      {/* Prominent Mandatory Safety Notice (CSHAKTI-UX-001) */}
      <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-200 text-sm flex items-start gap-3">
        <ShieldAlert className="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5" />
        <div>
          <strong className="font-semibold block text-amber-300 mb-0.5">Safety Notice:</strong>
          Do not enter your actual account passwords here. Use a representative pattern or test password to assess strength.
        </div>
      </div>

      {/* Form */}
      <div className="p-6 rounded-2xl bg-surface border border-border space-y-4">
        <form onSubmit={handleCheck} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-200 mb-2">Test Password</label>
            <div className="relative">
              <input
                type={showPassword ? 'text' : 'password'}
                placeholder="Enter a test password to evaluate..."
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-3 rounded-xl bg-background border border-border text-white placeholder-slate-500 focus:outline-none focus:border-emerald-400 pr-12 transition-colors"
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
            className="w-full py-3 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-semibold flex items-center justify-center gap-2 disabled:opacity-50 transition-all"
          >
            Check Password Strength
          </button>
        </form>
      </div>

      {/* Result Display */}
      {result && (
        <div className="p-6 rounded-2xl bg-surface border border-border space-y-6">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-slate-400">Strength Verdict</span>
            <span className="text-lg font-bold text-emerald-400 uppercase tracking-wide">
              {result.strength_label}
            </span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 text-center">
            <div className="p-3 rounded-xl bg-background border border-border">
              <span className="text-xs text-slate-400 block mb-1">Entropy</span>
              <span className="text-lg font-bold text-white">{result.entropy_bits} bits</span>
            </div>
            <div className="p-3 rounded-xl bg-background border border-border">
              <span className="text-xs text-slate-400 block mb-1">Length</span>
              <span className="text-lg font-bold text-white">{result.length} chars</span>
            </div>
            <div className="p-3 rounded-xl bg-background border border-border col-span-2 sm:col-span-1">
              <span className="text-xs text-slate-400 block mb-1">Common Pattern</span>
              <span className={`text-lg font-bold ${result.is_common_password ? 'text-red-400' : 'text-emerald-400'}`}>
                {result.is_common_password ? 'Yes (Weak)' : 'No'}
              </span>
            </div>
          </div>

          {result.improvements && result.improvements.length > 0 && (
            <div className="space-y-2">
              <h4 className="text-sm font-semibold text-slate-300">Improvement Recommendations:</h4>
              <ul className="space-y-1.5">
                {result.improvements.map((rec, idx) => (
                  <li key={idx} className="text-xs text-slate-400 flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-emerald-400 flex-shrink-0 mt-0.5" />
                    <span>{rec}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Safety Notice after result */}
          <div className="pt-3 border-t border-slate-700/60 text-xs text-slate-400 italic">
            {result.disclaimer}
          </div>
        </div>
      )}
    </div>
  );
};
