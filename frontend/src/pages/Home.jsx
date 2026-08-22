import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  Shield, Lock, MessageSquare, BookOpen, ArrowRight, ScanEye,
  Banknote, ShieldAlert, Activity, CheckCircle2, Cpu, FileCheck,
  AlertTriangle, KeyRound
} from 'lucide-react';
import { CyberBackground } from '../components/CyberBackground';
import { StatusPulse } from '../components/StatusPulse';

export const Home = () => {
  return (
    <div className="space-y-16 pb-20 overflow-hidden">
      {/* HERO SECTION */}
      <section className="relative min-h-[580px] flex items-center justify-center pt-16 pb-20 border-b border-border/60 bg-gradient-to-b from-surface via-background to-background">
        {/* Animated Cyber Environment Background */}
        <CyberBackground />
        
        {/* Subtle Glow Overlay */}
        <div className="absolute inset-0 bg-radial-glow pointer-events-none" />

        <div className="relative z-10 max-w-5xl mx-auto text-center space-y-8 px-4">
          {/* System Status Banner */}
          <motion.div
            initial={{ opacity: 0, y: -12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="inline-flex items-center gap-3 px-4 py-2 rounded-full bg-surface/90 border border-cyan-500/30 backdrop-blur-md shadow-[0_0_20px_rgba(6,182,212,0.15)]"
          >
            <StatusPulse status="active" size="xs" />
            <span className="text-xs font-mono font-bold tracking-widest text-cyan-400 uppercase">
              CYBERSHAKTI INTELLIGENCE ENGINE
            </span>
            <span className="text-slate-600">|</span>
            <span className="text-xs text-slate-300 font-medium">PROTECTION ACTIVE</span>
          </motion.div>

          {/* Main Title & Brand Statement */}
          <div className="space-y-4 max-w-4xl mx-auto">
            <motion.h1
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.1 }}
              className="text-4xl sm:text-6xl font-display font-extrabold text-white tracking-tight leading-tight"
            >
              CyberShakti
              <span className="block text-2xl sm:text-4xl font-semibold mt-2 text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-blue-400 to-purple-400">
                Intelligent Protection for the Digital World
              </span>
            </motion.h1>
            
            <motion.p
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="text-slate-300 text-base sm:text-lg max-w-2xl mx-auto leading-relaxed"
            >
              Detect scams, manipulated media, suspicious identities and digital threats before they become real-world damage.
            </motion.p>

            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.6, delay: 0.3 }}
              className="text-xs font-mono text-cyan-400/80 tracking-widest uppercase font-semibold"
            >
              DETECT. ANALYZE. PROTECT.
            </motion.p>
          </div>

          {/* Primary & Secondary Call to Actions */}
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
            className="flex flex-wrap justify-center gap-4 pt-2"
          >
            <Link
              to="/detect/phishing-link"
              className="px-8 py-4 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-black font-display font-bold text-sm tracking-wide shadow-[0_0_25px_rgba(6,182,212,0.35)] flex items-center gap-3 transition-all hover:scale-[1.02] active:scale-[0.98]"
            >
              <ShieldAlert className="w-5 h-5" />
              START SECURITY SCAN
              <ArrowRight className="w-4 h-4" />
            </Link>
            <Link
              to="/detect"
              className="px-8 py-4 rounded-xl bg-surface-raised/80 hover:bg-surface-high text-slate-200 font-display font-semibold text-sm border border-border flex items-center gap-2 backdrop-blur-md transition-all hover:border-cyan-500/40"
            >
              EXPLORE THREATS
            </Link>
          </motion.div>
        </div>
      </section>

      {/* SYSTEM STATUS DASHBOARD STRIP */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="p-6 rounded-2xl bg-surface/90 border border-border/80 shadow-2xl backdrop-blur-xl space-y-6">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center border-b border-border/60 pb-4 gap-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-emerald-500/10 border border-emerald-500/30">
                <Activity className="w-5 h-5 text-emerald-400" />
              </div>
              <div>
                <h3 className="text-sm font-display font-bold uppercase tracking-wider text-white">SYSTEM STATUS</h3>
                <div className="flex items-center gap-2 mt-0.5">
                  <StatusPulse status="active" size="xs" />
                  <span className="text-xs font-mono font-bold text-emerald-400">OPERATIONAL</span>
                </div>
              </div>
            </div>
            <div className="text-xs font-mono text-slate-400">
              SECURITY ENGINE STATUS: ACTIVE
            </div>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="p-4 rounded-xl bg-background/60 border border-border/50 flex items-center justify-between">
              <div>
                <p className="text-[11px] font-mono text-slate-400 uppercase">Threat Detection</p>
                <p className="text-sm font-bold text-emerald-400 mt-1">ACTIVE</p>
              </div>
              <StatusPulse status="active" size="sm" />
            </div>
            <div className="p-4 rounded-xl bg-background/60 border border-border/50 flex items-center justify-between">
              <div>
                <p className="text-[11px] font-mono text-slate-400 uppercase">AI Analysis</p>
                <p className="text-sm font-bold text-emerald-400 mt-1">ACTIVE</p>
              </div>
              <StatusPulse status="active" size="sm" />
            </div>
            <div className="p-4 rounded-xl bg-background/60 border border-border/50 flex items-center justify-between">
              <div>
                <p className="text-[11px] font-mono text-slate-400 uppercase">File Protection</p>
                <p className="text-sm font-bold text-emerald-400 mt-1">ACTIVE</p>
              </div>
              <StatusPulse status="active" size="sm" />
            </div>
            <div className="p-4 rounded-xl bg-background/60 border border-border/50 flex items-center justify-between">
              <div>
                <p className="text-[11px] font-mono text-slate-400 uppercase">Risk Engine</p>
                <p className="text-sm font-bold text-emerald-400 mt-1">ACTIVE</p>
              </div>
              <StatusPulse status="active" size="sm" />
            </div>
          </div>
        </div>
      </section>

      {/* CORE THREAT DETECTION & PROTECTION CAPABILITIES */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-10">
        <div className="text-center space-y-3">
          <h2 className="text-3xl font-display font-extrabold text-white tracking-tight">
            Threat Intelligence & Protection Engine
          </h2>
          <p className="text-slate-400 text-sm max-w-xl mx-auto">
            Powered by specialized AI models trained for real-world digital safety and cybersecurity.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {/* Card 1: Deepfake Detection */}
          <div className="p-6 rounded-2xl bg-surface border border-border hover:border-cyan-500/50 transition-all space-y-4 group relative overflow-hidden">
            <div className="absolute top-0 right-0 w-24 h-24 bg-cyan-500/5 rounded-bl-full pointer-events-none" />
            <div className="p-3 bg-cyan-500/10 text-cyan-400 rounded-xl w-fit border border-cyan-500/20 group-hover:scale-110 transition-transform">
              <ScanEye className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-display font-bold text-white group-hover:text-cyan-400 transition-colors">
              Deepfake Media Scan
            </h3>
            <p className="text-slate-300 text-xs leading-relaxed">
              Detect AI-generated facial manipulations, face swaps, and deepfake imagery using EfficientNet-B4.
            </p>
            <div className="pt-2">
              <Link
                to="/detect/deepfake"
                className="inline-flex items-center gap-2 text-xs font-bold text-cyan-400 hover:text-cyan-300 transition-colors"
              >
                Launch Deepfake Scanner <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          </div>

          {/* Card 2: Scam & Phishing Detection */}
          <div className="p-6 rounded-2xl bg-surface border border-border hover:border-purple-500/50 transition-all space-y-4 group relative overflow-hidden">
            <div className="absolute top-0 right-0 w-24 h-24 bg-purple-500/5 rounded-bl-full pointer-events-none" />
            <div className="p-3 bg-purple-500/10 text-purple-400 rounded-xl w-fit border border-purple-500/20 group-hover:scale-110 transition-transform">
              <MessageSquare className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-display font-bold text-white group-hover:text-purple-400 transition-colors">
              Scam & Phishing Analysis
            </h3>
            <p className="text-slate-300 text-xs leading-relaxed">
              Analyze suspicious URLs, SMS texts, WhatsApp forwards, and screenshots for fraudulent urgency signals.
            </p>
            <div className="pt-2">
              <Link
                to="/detect/message-scan"
                className="inline-flex items-center gap-2 text-xs font-bold text-purple-400 hover:text-purple-300 transition-colors"
              >
                Analyze Message <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          </div>

          {/* Card 3: Money Mule Account Detection */}
          <div className="p-6 rounded-2xl bg-surface border border-border hover:border-orange-500/50 transition-all space-y-4 group relative overflow-hidden">
            <div className="absolute top-0 right-0 w-24 h-24 bg-orange-500/5 rounded-bl-full pointer-events-none" />
            <div className="p-3 bg-orange-500/10 text-orange-400 rounded-xl w-fit border border-orange-500/20 group-hover:scale-110 transition-transform">
              <Banknote className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-display font-bold text-white group-hover:text-orange-400 transition-colors">
              Money Mule Account Risk
            </h3>
            <p className="text-slate-300 text-xs leading-relaxed">
              Evaluate bank account transaction patterns and velocity for money mule behavior using XGBoost.
            </p>
            <div className="pt-2">
              <Link
                to="/detect/mule-account"
                className="inline-flex items-center gap-2 text-xs font-bold text-orange-400 hover:text-orange-300 transition-colors"
              >
                Assess Account Signals <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          </div>

          {/* Card 4: Secure Vault & File Protection */}
          <div className="p-6 rounded-2xl bg-surface border border-border hover:border-emerald-500/50 transition-all space-y-4 group relative overflow-hidden">
            <div className="absolute top-0 right-0 w-24 h-24 bg-emerald-500/5 rounded-bl-full pointer-events-none" />
            <div className="p-3 bg-emerald-500/10 text-emerald-400 rounded-xl w-fit border border-emerald-500/20 group-hover:scale-110 transition-transform">
              <Lock className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-display font-bold text-white group-hover:text-emerald-400 transition-colors">
              Secure Files & Passwords
            </h3>
            <p className="text-slate-300 text-xs leading-relaxed">
              AES-256-GCM file encryption with Argon2id key derivation & automated password strength checking.
            </p>
            <div className="pt-2">
              <Link
                to="/protect/file-encryption"
                className="inline-flex items-center gap-2 text-xs font-bold text-emerald-400 hover:text-emerald-300 transition-colors"
              >
                Open File Vault <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* QUICK COMMAND CENTER SHORTCUTS */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="p-8 rounded-2xl bg-gradient-to-r from-surface via-surface-raised to-surface border border-border/80 flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="space-y-2">
            <h3 className="text-xl font-display font-bold text-white flex items-center gap-2">
              <Activity className="w-5 h-5 text-cyan-400" />
              Want to check your overall digital security score?
            </h3>
            <p className="text-slate-300 text-xs sm:text-sm">
              Answer our explainable security habits questionnaire to calculate your personalized Cyber Risk Score.
            </p>
          </div>
          <Link
            to="/assist/risk-score"
            className="px-6 py-3 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-black font-display font-bold text-xs uppercase tracking-wider flex-shrink-0 transition-all shadow-lg shadow-cyan-500/20"
          >
            Calculate Risk Score
          </Link>
        </div>
      </section>
    </div>
  );
};
