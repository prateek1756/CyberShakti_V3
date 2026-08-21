import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Shield, Lock, MessageSquare, BookOpen, User, LogOut, ShieldAlert } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export const Navbar = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <nav className="bg-surface border-b border-border sticky top-0 z-50 backdrop-blur-md bg-surface/90">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand Logo */}
          <Link to="/" className="flex items-center gap-2.5 group">
            <div className="p-2 bg-primary/20 text-primary rounded-xl border border-primary/30 group-hover:bg-primary group-hover:text-white transition-colors">
              <ShieldAlert className="w-6 h-6" />
            </div>
            <div>
              <span className="text-xl font-bold tracking-tight text-white">CyberShakti</span>
              <span className="text-xs font-semibold px-1.5 py-0.5 ml-1.5 rounded bg-primary/20 text-primary border border-primary/30">v3</span>
            </div>
          </Link>

          {/* Pillar Navigation Links */}
          <div className="hidden md:flex items-center gap-6">
            <Link to="/detect" className="flex items-center gap-1.5 text-sm font-medium text-slate-300 hover:text-white transition-colors">
              <Shield className="w-4 h-4 text-blue-400" />
              Detect & Analyze
            </Link>
            <Link to="/protect" className="flex items-center gap-1.5 text-sm font-medium text-slate-300 hover:text-white transition-colors">
              <Lock className="w-4 h-4 text-emerald-400" />
              Protect
            </Link>
            <Link to="/assist" className="flex items-center gap-1.5 text-sm font-medium text-slate-300 hover:text-white transition-colors">
              <MessageSquare className="w-4 h-4 text-purple-400" />
              Assist & Respond
            </Link>
            <Link to="/learn" className="flex items-center gap-1.5 text-sm font-medium text-slate-300 hover:text-white transition-colors">
              <BookOpen className="w-4 h-4 text-amber-400" />
              Safety Hub
            </Link>
          </div>

          {/* Auth Action Buttons */}
          <div className="flex items-center gap-3">
            {user ? (
              <div className="flex items-center gap-3">
                <span className="text-sm font-medium text-slate-300 hidden sm:inline">{user.email}</span>
                <button
                  onClick={handleLogout}
                  className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg bg-slate-800 text-slate-300 hover:bg-slate-700 hover:text-white border border-slate-700 transition-colors"
                >
                  <LogOut className="w-3.5 h-3.5" />
                  Logout
                </button>
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <Link
                  to="/login"
                  className="px-3.5 py-1.5 text-xs font-semibold text-slate-300 hover:text-white transition-colors"
                >
                  Log In
                </Link>
                <Link
                  to="/register"
                  className="px-4 py-1.5 text-xs font-semibold rounded-lg bg-primary hover:bg-primary-hover text-white shadow-md transition-all"
                >
                  Get Started
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};
