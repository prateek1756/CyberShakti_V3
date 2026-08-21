import React from 'react';
import { Link } from 'react-router-dom';
import { Shield, Lock, MessageSquare, BookOpen, AlertTriangle, ArrowRight, CheckCircle } from 'lucide-react';

export const Home = () => {
  return (
    <div className="space-y-12 pb-16">
      {/* Hero Section */}
      <section className="relative overflow-hidden pt-12 pb-16 border-b border-border/50 bg-gradient-to-b from-surface/50 to-background">
        <div className="max-w-5xl mx-auto text-center space-y-6 px-4">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-primary/10 border border-primary/20 text-primary text-xs font-semibold">
            <Shield className="w-3.5 h-3.5" />
            AI-Powered Digital Safety & Cybersecurity Platform
          </div>
          <h1 className="text-4xl sm:text-5xl font-extrabold text-white tracking-tight leading-tight">
            Protect Yourself from <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-400">Online Threats & Fraud</span>
          </h1>
          <p className="text-slate-300 text-base sm:text-lg max-w-2xl mx-auto leading-relaxed">
            Verify suspicious links, detect message scams, encrypt sensitive files, and assess your cyber risk score with India's dedicated AI safety platform.
          </p>
          <div className="flex flex-wrap justify-center gap-4 pt-4">
            <Link
              to="/detect/phishing-link"
              className="px-6 py-3 rounded-xl bg-primary hover:bg-primary-hover text-white font-semibold shadow-lg shadow-primary/25 flex items-center gap-2 transition-all"
            >
              Check a Suspicious Link
              <ArrowRight className="w-4 h-4" />
            </Link>
            <Link
              to="/detect/message-scan"
              className="px-6 py-3 rounded-xl bg-surface-raised hover:bg-slate-600 text-white font-semibold border border-slate-600 flex items-center gap-2 transition-all"
            >
              Check Scam Message
            </Link>
          </div>
        </div>
      </section>

      {/* Product Pillars Grid */}
      <section className="max-w-6xl mx-auto px-4 space-y-8">
        <div className="text-center space-y-2">
          <h2 className="text-2xl font-bold text-white">Four Pillars of Protection</h2>
          <p className="text-slate-400 text-sm">Comprehensive digital safety tools designed for everyday citizens.</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Pillar 1 */}
          <div className="p-6 rounded-2xl bg-surface border border-border space-y-4 hover:border-blue-500/50 transition-all">
            <div className="p-3 bg-blue-500/10 text-blue-400 rounded-xl w-fit border border-blue-500/20">
              <Shield className="w-6 h-6" />
            </div>
            <h3 className="text-xl font-bold text-white">Detect & Analyze</h3>
            <p className="text-slate-300 text-sm leading-relaxed">
              Identify phishing links, fake KYC messages, fraudulent QR codes, and suspicious profile signals using AI classifiers.
            </p>
            <div className="pt-2 flex flex-wrap gap-2">
              <Link to="/detect/phishing-link" className="text-xs font-semibold px-3 py-1.5 rounded-lg bg-slate-800 text-slate-200 hover:text-white border border-slate-700">Link Scanner</Link>
              <Link to="/detect/message-scan" className="text-xs font-semibold px-3 py-1.5 rounded-lg bg-slate-800 text-slate-200 hover:text-white border border-slate-700">Message Scan</Link>
            </div>
          </div>

          {/* Pillar 2 */}
          <div className="p-6 rounded-2xl bg-surface border border-border space-y-4 hover:border-emerald-500/50 transition-all">
            <div className="p-3 bg-emerald-500/10 text-emerald-400 rounded-xl w-fit border border-emerald-500/20">
              <Lock className="w-6 h-6" />
            </div>
            <h3 className="text-xl font-bold text-white">Protect</h3>
            <p className="text-slate-300 text-sm leading-relaxed">
              Verify phone numbers against scam threat databases, test password strength, and encrypt sensitive documents with AES-256-GCM.
            </p>
            <div className="pt-2 flex flex-wrap gap-2">
              <Link to="/protect/password-check" className="text-xs font-semibold px-3 py-1.5 rounded-lg bg-slate-800 text-slate-200 hover:text-white border border-slate-700">Password Checker</Link>
              <Link to="/protect/file-encryption" className="text-xs font-semibold px-3 py-1.5 rounded-lg bg-slate-800 text-slate-200 hover:text-white border border-slate-700">File Encryption</Link>
            </div>
          </div>

          {/* Pillar 3 */}
          <div className="p-6 rounded-2xl bg-surface border border-border space-y-4 hover:border-purple-500/50 transition-all">
            <div className="p-3 bg-purple-500/10 text-purple-400 rounded-xl w-fit border border-purple-500/20">
              <MessageSquare className="w-6 h-6" />
            </div>
            <h3 className="text-xl font-bold text-white">Assist & Respond</h3>
            <p className="text-slate-300 text-sm leading-relaxed">
              Query our AI Assistant for instant guidance, compute your Cyber Risk Score, and view location-based scam alerts.
            </p>
            <div className="pt-2 flex flex-wrap gap-2">
              <Link to="/assist/risk-score" className="text-xs font-semibold px-3 py-1.5 rounded-lg bg-slate-800 text-slate-200 hover:text-white border border-slate-700">Cyber Risk Score</Link>
            </div>
          </div>

          {/* Pillar 4 */}
          <div className="p-6 rounded-2xl bg-surface border border-border space-y-4 hover:border-amber-500/50 transition-all">
            <div className="p-3 bg-amber-500/10 text-amber-400 rounded-xl w-fit border border-amber-500/20">
              <BookOpen className="w-6 h-6" />
            </div>
            <h3 className="text-xl font-bold text-white">Learn & Prevent</h3>
            <p className="text-slate-300 text-sm leading-relaxed">
              Stay ahead of fraudsters with daily safety tips, awareness articles, and interactive cybersecurity quizzes.
            </p>
            <div className="pt-2 flex flex-wrap gap-2">
              <Link to="/learn" className="text-xs font-semibold px-3 py-1.5 rounded-lg bg-slate-800 text-slate-200 hover:text-white border border-slate-700">Cyber Safety Hub</Link>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};
