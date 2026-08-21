import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ShieldAlert, AlertCircle, Loader2 } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [totpCode, setTotpCode] = useState('');
  const [twoFaToken, setTwoFaToken] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const { login, completeTwoFactor } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (twoFaToken) {
      if (!totpCode) return;
      setLoading(true);
      setError(null);
      try {
        await completeTwoFactor(twoFaToken, totpCode);
        navigate('/');
      } catch (err) {
        setError(err.response?.data?.detail?.message || 'Invalid authenticator code');
      } finally {
        setLoading(false);
      }
      return;
    }

    if (!email || !password) return;
    setLoading(true);
    setError(null);
    try {
      const data = await login(email, password);
      if (data?.requires_2fa) {
        setTwoFaToken(data.two_fa_session_token);
        return;
      }
      navigate('/');
    } catch (err) {
      setError(err.response?.data?.detail?.message || 'Invalid email or password');
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
        <h1 className="text-2xl font-bold text-white">Log in to CyberShakti</h1>
        <p className="text-slate-400 text-xs">Enter your credentials to access your security dashboard.</p>
      </div>

      <div className="p-6 rounded-2xl bg-surface border border-border space-y-4">
        <form onSubmit={handleSubmit} className="space-y-4">
          {!twoFaToken ? (
            <>
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1.5" htmlFor="login-email">Email Address</label>
                <input
                  id="login-email"
                  type="email"
                  autoComplete="username"
                  placeholder="user@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full px-4 py-2.5 rounded-xl bg-background border border-border text-white text-sm focus:outline-none focus:border-primary"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1.5" htmlFor="login-password">Password</label>
                <input
                  id="login-password"
                  type="password"
                  autoComplete="current-password"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full px-4 py-2.5 rounded-xl bg-background border border-border text-white text-sm focus:outline-none focus:border-primary"
                />
              </div>
            </>
          ) : (
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5" htmlFor="login-totp">Authenticator code</label>
              <input
                id="login-totp"
                type="text"
                inputMode="numeric"
                autoComplete="one-time-code"
                placeholder="123456"
                value={totpCode}
                onChange={(e) => setTotpCode(e.target.value)}
                className="w-full px-4 py-2.5 rounded-xl bg-background border border-border text-white text-sm focus:outline-none focus:border-primary"
              />
            </div>
          )}

          {error && (
            <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/30 text-red-300 text-xs flex items-center gap-2" role="alert">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <button
            type="submit"
            disabled={loading || (!twoFaToken && (!email || !password)) || (twoFaToken && !totpCode)}
            className="w-full py-2.5 rounded-xl bg-primary hover:bg-primary-hover text-white font-semibold text-sm flex items-center justify-center gap-2 disabled:opacity-50 transition-all"
          >
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : (twoFaToken ? 'Verify code' : 'Log In')}
          </button>
        </form>

        <p className="text-xs text-center text-slate-400 pt-2">
          Don't have an account?{' '}
          <Link to="/register" className="text-primary hover:underline font-semibold">
            Create account
          </Link>
        </p>
      </div>
    </div>
  );
};
