import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { Shield, Lock, MessageSquare, BookOpen, LogOut, ShieldAlert, Menu, X, Activity } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { StatusPulse } from './StatusPulse';

export const Navbar = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const isActive = (path) => {
    if (path === '/detect') {
      return location.pathname.startsWith('/detect');
    }
    if (path === '/protect') {
      return location.pathname.startsWith('/protect');
    }
    if (path === '/assist') {
      return location.pathname.startsWith('/assist');
    }
    return location.pathname === path;
  };

  return (
    <nav className="bg-surface/90 border-b border-border/80 sticky top-0 z-50 backdrop-blur-xl shadow-2xl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand Logo */}
          <Link to="/" className="flex items-center gap-3 group">
            <div className="p-2 bg-cyan-500/10 text-cyan-400 rounded-xl border border-cyan-500/30 group-hover:bg-cyan-500 group-hover:text-black transition-all shadow-[0_0_15px_rgba(6,182,212,0.2)]">
              <ShieldAlert className="w-5 h-5" />
            </div>
            <div className="flex flex-col">
              <span className="text-xl font-display font-bold tracking-tight text-white group-hover:text-cyan-400 transition-colors">
                CyberShakti
              </span>
              <span className="text-[10px] text-slate-400 font-mono tracking-widest -mt-1 hidden sm:block">
                INTELLIGENT PROTECTION
              </span>
            </div>
          </Link>

          {/* System Status Live Indicator */}
          <div className="hidden lg:flex items-center gap-2 px-3 py-1 rounded-full bg-background/60 border border-emerald-500/20 text-xs text-slate-300">
            <StatusPulse status="active" size="xs" />
            <span className="text-[11px] font-mono text-emerald-400 font-bold uppercase tracking-wider">SYSTEM OPERATIONAL</span>
          </div>

          {/* Navigation Links */}
          <div className="hidden md:flex items-center gap-1.5">
            <Link
              to="/detect"
              className={`flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-semibold transition-all ${
                isActive('/detect')
                  ? 'bg-cyan-500/15 text-cyan-300 border border-cyan-500/30 shadow-[0_0_12px_rgba(6,182,212,0.15)]'
                  : 'text-slate-300 hover:text-white hover:bg-surface-raised'
              }`}
            >
              <Shield className="w-4 h-4 text-cyan-400" />
              Threat Detection
            </Link>
            <Link
              to="/protect"
              className={`flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-semibold transition-all ${
                isActive('/protect')
                  ? 'bg-emerald-500/15 text-emerald-300 border border-emerald-500/30'
                  : 'text-slate-300 hover:text-white hover:bg-surface-raised'
              }`}
            >
              <Lock className="w-4 h-4 text-emerald-400" />
              Protection Tools
            </Link>
            <Link
              to="/assist"
              className={`flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-semibold transition-all ${
                isActive('/assist')
                  ? 'bg-purple-500/15 text-purple-300 border border-purple-500/30'
                  : 'text-slate-300 hover:text-white hover:bg-surface-raised'
              }`}
            >
              <Activity className="w-4 h-4 text-purple-400" />
              Risk Center
            </Link>
            <Link
              to="/learn"
              className={`flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-semibold transition-all ${
                isActive('/learn')
                  ? 'bg-amber-500/15 text-amber-300 border border-amber-500/30'
                  : 'text-slate-300 hover:text-white hover:bg-surface-raised'
              }`}
            >
              <BookOpen className="w-4 h-4 text-amber-400" />
              Safety Hub
            </Link>
          </div>

          {/* Auth Actions */}
          <div className="hidden md:flex items-center gap-3">
            {user ? (
              <div className="flex items-center gap-3">
                <div className="text-right">
                  <span className="block text-xs font-semibold text-white">{user.email}</span>
                  <span className="block text-[10px] text-emerald-400 font-mono">AUTHENTICATED</span>
                </div>
                <button
                  onClick={handleLogout}
                  className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-xl bg-surface-raised text-slate-300 hover:text-red-300 hover:bg-red-500/10 border border-border transition-all"
                >
                  <LogOut className="w-3.5 h-3.5" />
                  Logout
                </button>
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <Link
                  to="/login"
                  className="px-4 py-2 text-xs font-semibold text-slate-300 hover:text-white transition-colors"
                >
                  Log In
                </Link>
                <Link
                  to="/register"
                  className="px-4 py-2 text-xs font-semibold rounded-xl bg-cyan-500 hover:bg-cyan-400 text-black font-bold shadow-[0_0_15px_rgba(6,182,212,0.3)] transition-all"
                >
                  Get Started
                </Link>
              </div>
            )}
          </div>

          {/* Mobile menu button */}
          <div className="flex md:hidden items-center gap-2">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 rounded-xl bg-surface-raised text-slate-300 hover:text-white border border-border"
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Drawer */}
      {mobileMenuOpen && (
        <div className="md:hidden border-b border-border bg-surface px-4 pt-2 pb-6 space-y-3">
          <Link
            to="/detect"
            onClick={() => setMobileMenuOpen(false)}
            className="flex items-center gap-3 p-3 rounded-xl bg-surface-raised text-sm font-semibold text-slate-200"
          >
            <Shield className="w-5 h-5 text-cyan-400" /> Threat Detection
          </Link>
          <Link
            to="/protect"
            onClick={() => setMobileMenuOpen(false)}
            className="flex items-center gap-3 p-3 rounded-xl bg-surface-raised text-sm font-semibold text-slate-200"
          >
            <Lock className="w-5 h-5 text-emerald-400" /> Protection Tools
          </Link>
          <Link
            to="/assist"
            onClick={() => setMobileMenuOpen(false)}
            className="flex items-center gap-3 p-3 rounded-xl bg-surface-raised text-sm font-semibold text-slate-200"
          >
            <Activity className="w-5 h-5 text-purple-400" /> Risk Center
          </Link>
          <Link
            to="/learn"
            onClick={() => setMobileMenuOpen(false)}
            className="flex items-center gap-3 p-3 rounded-xl bg-surface-raised text-sm font-semibold text-slate-200"
          >
            <BookOpen className="w-5 h-5 text-amber-400" /> Safety Hub
          </Link>

          <div className="pt-2 border-t border-border flex flex-col gap-2">
            {user ? (
              <button
                onClick={() => { setMobileMenuOpen(false); handleLogout(); }}
                className="w-full py-2.5 rounded-xl bg-red-500/10 text-red-300 font-semibold text-xs border border-red-500/30 flex items-center justify-center gap-2"
              >
                <LogOut className="w-4 h-4" /> Logout ({user.email})
              </button>
            ) : (
              <>
                <Link
                  to="/login"
                  onClick={() => setMobileMenuOpen(false)}
                  className="w-full py-2.5 text-center text-xs font-semibold text-slate-300"
                >
                  Log In
                </Link>
                <Link
                  to="/register"
                  onClick={() => setMobileMenuOpen(false)}
                  className="w-full py-2.5 text-center text-xs font-bold rounded-xl bg-cyan-500 text-black shadow-lg"
                >
                  Get Started
                </Link>
              </>
            )}
          </div>
        </div>
      )}
    </nav>
  );
};
