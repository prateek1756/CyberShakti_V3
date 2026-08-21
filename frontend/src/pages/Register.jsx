import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ShieldAlert, AlertCircle, Loader2, CheckCircle } from 'lucide-react';
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
      setError(err.response?.data?.detail?.message || 'Registration failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto px-4 py-16 space-y-6">
      <div className="text-center space-y-2">
        <div className="p-3 bg-primary/20 text-primary rounded-2xl w-fit mx-auto border border-primary/30">
          <ShieldAlert className="w-8 h-8" />
        </div>
        <h1 className="text-2xl font-bold text-white">Create CyberShakti Account</h1>
        <p className="text-slate-400 text-xs">Join CyberShakti to access personalized risk scores and threat alerts.</p>
      </div>

      <div className="p-6 rounded-2xl bg-surface border border-border space-y-4">
        {successMsg ? (
          <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-sm space-y-3 text-center">
            <CheckCircle className="w-8 h-8 text-emerald-400 mx-auto" />
            <p>{successMsg}</p>
            <Link to="/login" className="inline-block px-4 py-2 rounded-xl bg-primary text-white font-semibold text-xs">
              Proceed to Login
            </Link>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">Email Address</label>
              <input
                type="email"
                placeholder="user@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-2.5 rounded-xl bg-background border border-border text-white text-sm focus:outline-none focus:border-primary"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">Password (Min 8 chars)</label>
              <input
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-2.5 rounded-xl bg-background border border-border text-white text-sm focus:outline-none focus:border-primary"
              />
            </div>

            <div className="flex items-start gap-2.5 pt-1">
              <input
                type="checkbox"
                id="consent-check"
                checked={consent}
                onChange={(e) => setConsent(e.target.checked)}
                className="mt-0.5 rounded border-border text-primary focus:ring-primary"
              />
              <label htmlFor="consent-check" className="text-xs text-slate-300 leading-normal">
                I consent to CyberShakti processing my email and scan submissions for digital threat analysis per the Privacy Policy.
              </label>
            </div>

            {error && (
              <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/30 text-red-300 text-xs flex items-center gap-2">
                <AlertCircle className="w-4 h-4 flex-shrink-0" />
                <span>{error}</span>
              </div>
            )}

            <button
              type="submit"
              disabled={loading || !email || !password || !consent}
              className="w-full py-2.5 rounded-xl bg-primary hover:bg-primary-hover text-white font-semibold text-sm flex items-center justify-center gap-2 disabled:opacity-50 transition-all"
            >
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Create Account'}
            </button>
          </form>
        )}

        <p className="text-xs text-center text-slate-400 pt-2">
          Already have an account?{' '}
          <Link to="/login" className="text-primary hover:underline font-semibold">
            Log in
          </Link>
        </p>
      </div>
    </div>
  );
};
