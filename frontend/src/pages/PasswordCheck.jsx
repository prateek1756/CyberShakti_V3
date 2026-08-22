import React, { useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Lock, Eye, EyeOff, CheckCircle2, XCircle, ShieldAlert,
  KeyRound, RefreshCw, Sparkles, Copy, Check, ShieldCheck, Zap
} from 'lucide-react';
import { api } from '../services/api';

// Common weak password dictionary
const COMMON_PASSWORDS = new Set([
  'password', 'password123', '123456', '12345678', '123456789', 'qwerty',
  'admin', 'welcome', 'login', 'iloveyou', 'india123', 'pass@123', 'admin123',
  'test@123', 'system', 'monkey', 'dragon', 'football', 'master', 'shadow'
]);

const calculateLocalMetrics = (pwd) => {
  if (!pwd) return null;
  const length = pwd.length;

  const hasLower = /[a-z]/.test(pwd);
  const hasUpper = /[A-Z]/.test(pwd);
  const hasDigit = /[0-9]/.test(pwd);
  const hasSpecial = /[^a-zA-Z0-9]/.test(pwd);

  let charset = 0;
  if (hasLower) charset += 26;
  if (hasUpper) charset += 26;
  if (hasDigit) charset += 10;
  if (hasSpecial) charset += 32;

  const entropy = charset > 0 ? length * Math.log2(charset) : 0;
  const isCommon = COMMON_PASSWORDS.has(pwd.toLowerCase()) || /^(.)\1+$/.test(pwd);

  let strength = 'very_weak';
  let strengthLabel = 'Very Weak';
  let color = 'text-red-400';
  let barColor = 'bg-red-500';
  let barWidth = '15%';

  if (isCommon || entropy < 28) {
    strength = 'very_weak';
    strengthLabel = 'Very Weak';
    color = 'text-red-400';
    barColor = 'bg-red-500';
    barWidth = '20%';
  } else if (entropy < 45) {
    strength = 'weak';
    strengthLabel = 'Weak';
    color = 'text-orange-400';
    barColor = 'bg-orange-500';
    barWidth = '40%';
  } else if (entropy < 65) {
    strength = 'moderate';
    strengthLabel = 'Moderate';
    color = 'text-yellow-400';
    barColor = 'bg-yellow-500';
    barWidth = '65%';
  } else if (entropy < 85) {
    strength = 'strong';
    strengthLabel = 'Strong';
    color = 'text-emerald-400';
    barColor = 'bg-emerald-500';
    barWidth = '85%';
  } else {
    strength = 'very_strong';
    strengthLabel = 'Very Strong';
    color = 'text-cyan-400';
    barColor = 'bg-cyan-400';
    barWidth = '100%';
  }

  // Estimated crack time assuming 10 billion guesses/sec
  let crackTime = 'Instant (< 1 ms)';
  if (isCommon) {
    crackTime = 'Instant (Found in Wordlist)';
  } else if (entropy < 28) {
    crackTime = '< 0.01 seconds';
  } else if (entropy < 38) {
    crackTime = '~2.5 minutes';
  } else if (entropy < 48) {
    crackTime = '~14 days';
  } else if (entropy < 58) {
    crackTime = '~350 years';
  } else if (entropy < 75) {
    crackTime = '~4.2 million years';
  } else {
    crackTime = 'Centuries / Impractical to brute-force';
  }

  const improvements = [];
  if (length < 14) improvements.push('Increase length to at least 14 characters for robust security.');
  if (!hasUpper) improvements.push('Add uppercase letters (A-Z) to increase character set entropy.');
  if (!hasLower) improvements.push('Add lowercase letters (a-z).');
  if (!hasDigit) improvements.push('Include numbers (0-9) to prevent dictionary matching.');
  if (!hasSpecial) improvements.push('Include special symbols (!@#$%^&*) to guard against rainbow tables.');
  if (isCommon) improvements.push('This password matches common breach wordlists. Do not use predictable phrases.');

  return {
    strength_level: strength,
    strength_label: strengthLabel,
    entropy_bits: Math.round(entropy * 10) / 10,
    length,
    is_common_password: isCommon,
    crack_time: crackTime,
    color,
    barColor,
    barWidth,
    hasLower,
    hasUpper,
    hasDigit,
    hasSpecial,
    improvements,
    disclaimer: 'Do not enter actual live passwords. This evaluation is performed for security assessment purposes.'
  };
};

export const PasswordCheck = () => {
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [copied, setCopied] = useState(false);

  // Instant local metrics for real-time visual feedback
  const localAnalysis = useMemo(() => calculateLocalMetrics(password), [password]);

  const handleCheck = async (e) => {
    e?.preventDefault();
    if (!password) return;

    setLoading(true);
    try {
      const res = await api.post('/protect/check-password', { password });
      const apiVerdict = res.data?.verdict;
      const combined = {
        ...localAnalysis,
        ...apiVerdict,
        strength_label: apiVerdict?.strength_label || localAnalysis.strength_label,
        entropy_bits: apiVerdict?.entropy_bits ?? localAnalysis.entropy_bits,
        length: apiVerdict?.length ?? localAnalysis.length,
        improvements: apiVerdict?.improvements?.length ? apiVerdict.improvements : localAnalysis.improvements
      };
      setResult(combined);
    } catch {
      // Graceful offline fallback
      setResult(localAnalysis);
    } finally {
      setLoading(false);
    }
  };

  const generateStrongPassword = () => {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()-_=+';
    let generated = '';
    const array = new Uint32Array(16);
    window.crypto.getRandomValues(array);
    for (let i = 0; i < 16; i++) {
      generated += chars[array[i] % chars.length];
    }
    setPassword(generated);
    setShowPassword(true);
    const analysis = calculateLocalMetrics(generated);
    setResult(analysis);
  };

  const copyToClipboard = () => {
    if (!password) return;
    navigator.clipboard.writeText(password);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const displayData = result || localAnalysis;

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
          Evaluate password entropy, length, character diversity, and estimated brute-force crack time against automated dictionary attacks.
        </p>
      </div>

      {/* Prominent Safety Notice */}
      <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-200 text-xs flex items-start gap-3">
        <ShieldAlert className="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5" />
        <div>
          <strong className="font-semibold block text-amber-300 mb-0.5">Privacy & Safety Notice:</strong>
          Do not enter your actual live production passwords here. Test representative patterns or evaluate candidate credentials.
        </div>
      </div>

      {/* Input Section */}
      <div className="p-6 rounded-2xl bg-surface border border-border space-y-5">
        <form onSubmit={handleCheck} className="space-y-4">
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="block text-xs font-mono font-bold uppercase tracking-wider text-slate-300">
                TEST PASSWORD INPUT
              </label>
              <button
                type="button"
                onClick={generateStrongPassword}
                className="text-xs text-emerald-400 hover:text-emerald-300 font-mono font-bold flex items-center gap-1.5 transition-colors"
              >
                <Sparkles className="w-3.5 h-3.5" />
                Generate Strong Password
              </button>
            </div>

            <div className="relative">
              <input
                type={showPassword ? 'text' : 'password'}
                placeholder="Enter a test password to evaluate..."
                value={password}
                onChange={(e) => {
                  setPassword(e.target.value);
                  setResult(null);
                }}
                className="w-full px-4 py-3.5 rounded-xl bg-background border border-border text-white text-sm placeholder-slate-500 focus:outline-none focus:border-emerald-400 pr-24 transition-colors font-mono"
              />
              <div className="absolute right-3 top-3 flex items-center gap-1">
                {password && (
                  <button
                    type="button"
                    onClick={copyToClipboard}
                    title="Copy Password"
                    className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-surface transition-colors"
                  >
                    {copied ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
                  </button>
                )}
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  title={showPassword ? 'Hide Password' : 'Show Password'}
                  className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-surface transition-colors"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>
          </div>

          {/* Real-time Strength Meter Bar */}
          {password && displayData && (
            <div className="space-y-2 pt-1">
              <div className="flex items-center justify-between text-xs font-mono">
                <span className="text-slate-400">Strength Meter:</span>
                <span className={`font-bold ${displayData.color}`}>{displayData.strength_label}</span>
              </div>
              <div className="h-2 w-full bg-background rounded-full overflow-hidden border border-border/60">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: displayData.barWidth }}
                  transition={{ duration: 0.3 }}
                  className={`h-full ${displayData.barColor}`}
                />
              </div>
            </div>
          )}

          <div className="flex gap-3">
            <button
              type="submit"
              disabled={loading || !password}
              className="flex-1 py-3.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-black font-display font-bold text-xs uppercase tracking-wider flex items-center justify-center gap-2 disabled:opacity-40 transition-all shadow-[0_0_20px_rgba(16,185,129,0.25)]"
            >
              {loading ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  Analyzing Entropy & Wordlists…
                </>
              ) : (
                <>
                  <ShieldCheck className="w-4 h-4" />
                  Analyze Password Strength
                </>
              )}
            </button>
          </div>
        </form>

        {/* Character Diversity Checklist */}
        {password && displayData && (
          <div className="pt-4 border-t border-border grid grid-cols-2 sm:grid-cols-4 gap-2.5">
            {[
              { label: '14+ Chars', ok: displayData.length >= 14 },
              { label: 'Uppercase', ok: displayData.hasUpper },
              { label: 'Lowercase', ok: displayData.hasLower },
              { label: 'Numbers & Symbols', ok: displayData.hasDigit && displayData.hasSpecial }
            ].map(({ label, ok }) => (
              <div
                key={label}
                className={`px-3 py-2 rounded-lg border text-xs font-mono flex items-center gap-2 ${
                  ok
                    ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'
                    : 'bg-background/40 border-border text-slate-500'
                }`}
              >
                {ok ? <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" /> : <XCircle className="w-3.5 h-3.5 text-slate-600 shrink-0" />}
                <span className="truncate">{label}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Comprehensive Result Cards */}
      <AnimatePresence>
        {displayData && password && (
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="p-6 rounded-2xl bg-surface border border-border space-y-6"
          >
            <div className="flex items-center justify-between border-b border-border pb-4">
              <span className="text-xs font-mono font-bold uppercase tracking-wider text-slate-400">Security Assessment</span>
              <span className={`text-lg font-display font-extrabold uppercase tracking-wide ${displayData.color}`}>
                {displayData.strength_label}
              </span>
            </div>

            {/* Metrics Grid */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center">
              <div className="p-4 rounded-xl bg-background border border-border">
                <span className="text-[10px] font-mono text-slate-400 block mb-1">ENTROPY</span>
                <span className="text-xl font-display font-bold text-white">{displayData.entropy_bits} bits</span>
                <span className="text-[10px] text-slate-500 block mt-0.5">Shannon measure</span>
              </div>
              <div className="p-4 rounded-xl bg-background border border-border">
                <span className="text-[10px] font-mono text-slate-400 block mb-1">LENGTH</span>
                <span className="text-xl font-display font-bold text-white">{displayData.length} chars</span>
                <span className="text-[10px] text-slate-500 block mt-0.5">Character count</span>
              </div>
              <div className="p-4 rounded-xl bg-background border border-border">
                <span className="text-[10px] font-mono text-slate-400 block mb-1">DICTIONARY CHECK</span>
                <span className={`text-xl font-display font-bold ${displayData.is_common_password ? 'text-red-400' : 'text-emerald-400'}`}>
                  {displayData.is_common_password ? 'Found (Weak)' : 'Pass'}
                </span>
                <span className="text-[10px] text-slate-500 block mt-0.5">Wordlist lookup</span>
              </div>
              <div className="p-4 rounded-xl bg-background border border-border">
                <span className="text-[10px] font-mono text-slate-400 block mb-1">CRACK ESTIMATE</span>
                <span className="text-sm font-display font-bold text-cyan-300 block truncate" title={displayData.crack_time}>
                  {displayData.crack_time}
                </span>
                <span className="text-[10px] text-slate-500 block mt-0.5">@ 10B guesses/sec</span>
              </div>
            </div>

            {/* Recommendations */}
            {displayData.improvements && displayData.improvements.length > 0 && (
              <div className="space-y-3">
                <h4 className="text-xs font-mono font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
                  <Zap className="w-3.5 h-3.5 text-amber-400" />
                  Hardening Recommendations:
                </h4>
                <ul className="space-y-2">
                  {displayData.improvements.map((rec, idx) => (
                    <li key={idx} className="text-xs text-slate-300 flex items-start gap-2.5 bg-background/50 p-2.5 rounded-lg border border-border/50">
                      <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0 mt-0.5" />
                      <span>{rec}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Safety Notice after result */}
            <div className="pt-3 border-t border-border text-[11px] text-slate-500 italic">
              {displayData.disclaimer}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

