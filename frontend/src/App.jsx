import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { Navbar } from './components/Navbar';

import { Home } from './pages/Home';
import { PhishingScan } from './pages/PhishingScan';
import { MessageScan } from './pages/MessageScan';
import { PasswordCheck } from './pages/PasswordCheck';
import { FileEncrypt } from './pages/FileEncrypt';
import { RiskScore } from './pages/RiskScore';
import { SafetyHub } from './pages/SafetyHub';
import { Login } from './pages/Login';
import { Register } from './pages/Register';

export function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="min-h-screen flex flex-col bg-background text-slate-100 font-sans">
          <Navbar />
          <main className="flex-1">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/detect" element={<PhishingScan />} />
              <Route path="/detect/phishing-link" element={<PhishingScan />} />
              <Route path="/detect/message-scan" element={<MessageScan />} />
              <Route path="/protect" element={<PasswordCheck />} />
              <Route path="/protect/password-check" element={<PasswordCheck />} />
              <Route path="/protect/file-encryption" element={<FileEncrypt />} />
              <Route path="/assist" element={<RiskScore />} />
              <Route path="/assist/risk-score" element={<RiskScore />} />
              <Route path="/learn" element={<SafetyHub />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
            </Routes>
          </main>
          <footer className="border-t border-border py-6 bg-surface/50 text-center text-xs text-slate-400">
            CyberShakti v3 — AI Digital Safety & Cybersecurity Platform • Built for Everyday Citizens
          </footer>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
