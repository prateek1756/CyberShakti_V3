import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { ShieldAlert, AlertCircle, RefreshCw, CheckCircle } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export const Register = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [consent, setConsent] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [successMsg, setSuccessMsg] = useState(null);
  const { register } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email || !password || !consent) return;

    setLoading(true);
    setError(null);
    setSuccessMsg(null);

    try {
      const res = await register(email, password, consent);
      setSuccessMsg(res.data.message || 'Registration successful. Check your email to verify account.');
    } catch (err) {
      const detail = err.response?.data?.detail;
      const msg = typeof detail === 'string' ? detail : detail?.message || err.response?.data?.message || err.message || 'Registration failed.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto px-4 py-20 space-y-6">
      <div className="text-center space-y-3">
        <div className="p-3 bg-cyan-500/10 text-cyan-400 rounded-2xl w-fit mx-auto border border-cyan-500/30 shadow-[0_0_20px_rgba(6,182,212,0.15)]">
          <ShieldAlert className="w-8 h-8" />
        </div>
        <h1 className="text-3xl font-display font-extrabold text-white tracking-tight">
          Create CyberShakti Account
        </h1>
        <p className="text-slate-400 text-xs">
          Join CyberShakti to access personalized risk scores and real-time threat alerts.
        </p>
      </div>

      <div className="p-6 rounded-2xl bg-surface border border-border space-y-4 shadow-xl">
        {successMsg ? (
          <div className="p-5 rounded-xl bg-emerald-950/40 border border-emerald-500/40 text-emerald-300 text-sm space-y-3 text-center">
            <CheckCircle className="w-8 h-8 text-emerald-400 mx-auto" />
            <p className="font-semibold text-white">{successMsg}</p>
            <Link to="/login" className="inline-block px-5 py-2.5 rounded-xl bg-cyan-500 text-black font-bold text-xs uppercase tracking-wider">
              Proceed to Login
            </Link>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-mono font-bold uppercase tracking-wider text-slate-300 mb-1.5">
                EMAIL ADDRESS
              </label>
              <input
                type="email"
                placeholder="user@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-3 rounded-xl bg-background border border-border text-white text-sm focus:outline-none focus:border-cyan-400 transition-colors"
              />
            </div>

            <div>
              <label className="block text-xs font-mono font-bold uppercase tracking-wider text-slate-300 mb-1.5">
                PASSWORD (MIN 8 CHARACTERS)
              </label>
              <input
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-3 rounded-xl bg-background border border-border text-white text-sm focus:outline-none focus:border-cyan-400 transition-colors font-mono"
              />
            </div>

            <div className="flex items-start gap-2.5 pt-1">
              <input
                type="checkbox"
                id="consent-check"
                checked={consent}
                onChange={(e) => setConsent(e.target.checked)}
                className="mt-1 rounded border-border bg-background text-cyan-500 focus:ring-cyan-500"
              />
              <label htmlFor="consent-check" className="text-xs text-slate-300 leading-relaxed">
                I consent to CyberShakti processing my email and scan submissions for digital threat analysis per the Privacy Policy.
              </label>
            </div>

            {error && (
              <div className="p-3 rounded-xl bg-red-500/10 border border-red-500/30 text-red-300 text-xs flex items-center gap-2">
                <AlertCircle className="w-4 h-4 flex-shrink-0" />
                <span>{error}</span>
              </div>
            )}

            <button
              type="submit"
              disabled={loading || !email || !password || !consent}
              className="w-full py-3.5 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-black font-display font-bold text-xs uppercase tracking-wider flex items-center justify-center gap-2 disabled:opacity-40 transition-all shadow-[0_0_20px_rgba(6,182,212,0.25)]"
            >
              {loading ? <RefreshCw className="w-4 h-4 animate-spin" /> : 'Create Account'}
            </button>
          </form>
        )}

        <p className="text-xs text-center text-slate-400 pt-2">
          Already have an account?{' '}
          <Link to="/login" className="text-cyan-400 hover:underline font-bold">
            Log in
          </Link>
        </p>
      </div>
    </div>
  );
};
