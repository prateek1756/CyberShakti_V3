import React from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import { AnimatePresence, motion } from 'framer-motion';
import { AuthProvider } from './context/AuthContext';
import { Navbar } from './components/Navbar';

import { Home } from './pages/Home';
import { PhishingScan } from './pages/PhishingScan';
import { MessageScan } from './pages/MessageScan';
import { PasswordCheck } from './pages/PasswordCheck';
import { FileEncrypt } from './pages/FileEncrypt';
import { RiskScore } from './pages/RiskScore';
import { SafetyHub } from './pages/SafetyHub';
import { DeepfakeScan } from './pages/DeepfakeScan';
import { MuleAccount } from './pages/MuleAccount';
import { Login } from './pages/Login';
import { Register } from './pages/Register';

function AnimatedRoutes() {
  const location = useLocation();

  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={location.pathname}
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -8 }}
        transition={{ duration: 0.25, ease: 'easeOut' }}
        className="flex-1 flex flex-col"
      >
        <Routes location={location}>
          <Route path="/" element={<Home />} />
          <Route path="/detect" element={<PhishingScan />} />
          <Route path="/detect/phishing-link" element={<PhishingScan />} />
          <Route path="/detect/message-scan" element={<MessageScan />} />
          <Route path="/detect/deepfake" element={<DeepfakeScan />} />
          <Route path="/detect/mule-account" element={<MuleAccount />} />
          <Route path="/protect" element={<PasswordCheck />} />
          <Route path="/protect/password-check" element={<PasswordCheck />} />
          <Route path="/protect/file-encryption" element={<FileEncrypt />} />
          <Route path="/assist" element={<RiskScore />} />
          <Route path="/assist/risk-score" element={<RiskScore />} />
          <Route path="/learn" element={<SafetyHub />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
        </Routes>
      </motion.div>
    </AnimatePresence>
  );
}

export function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="min-h-screen flex flex-col bg-background text-slate-100 font-sans selection:bg-cyan-500/30 selection:text-cyan-200">
          <Navbar />
          <main className="flex-1 flex flex-col relative z-10">
            <AnimatedRoutes />
          </main>
          <footer className="border-t border-border/60 py-8 bg-surface/80 backdrop-blur-md text-center text-xs text-slate-400 relative z-10 space-y-2">
            <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row justify-between items-center gap-4">
              <div className="flex items-center gap-2">
                <span className="font-display font-bold text-white tracking-wider text-sm">CyberShakti</span>
                <span className="text-slate-500">•</span>
                <span className="text-slate-400">Intelligent Protection for the Digital World</span>
              </div>
              <p className="text-slate-500">
                Detect scams, manipulated media & digital threats in real-time.
              </p>
            </div>
          </footer>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
