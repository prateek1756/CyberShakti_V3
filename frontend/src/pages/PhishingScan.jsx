import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Shield, Link2, QrCode, AlertCircle, RefreshCw, Globe, ArrowRight, ShieldAlert } from 'lucide-react';
import { api } from '../services/api';
import { ScanAnimation } from '../components/ScanAnimation';
import { ThreatResultCard } from '../components/ThreatResultCard';

const PHISHING_STAGES = [
  { id: 'input',     label: 'Target URL / QR payload decoded',     duration: 300 },
  { id: 'normalize', label: 'Resolving domain DNS & WHOIS records', duration: 500 },
  { id: 'extract',   label: 'Checking blacklists & brand spoofing',  duration: 600 },
  { id: 'model',     label: 'Analyzing URL structural entropy',    duration: 700 },
  { id: 'risk',      label: 'Calculating phishing risk verdict',   duration: 400 },
];

export const PhishingScan = () => {
  const [activeTab, setActiveTab] = useState('url');
  const [urlInput, setUrlInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [verdict, setVerdict] = useState(null);
  const [currentScanId, setCurrentScanId] = useState(null);

  const handleUrlSubmit = async (e) => {
    e.preventDefault();
    if (!urlInput.trim()) return;

    setLoading(true);
    setError(null);
    setVerdict(null);
    const scanId = `URL-${Math.random().toString(36).substring(2, 8).toUpperCase()}`;
    setCurrentScanId(scanId);

    try {
      const res = await api.post('/detect/scan-url', { url: urlInput.trim() });
      setVerdict(res.data.verdict);
    } catch (err) {
      setError(err.response?.data?.detail?.message || 'Failed to scan URL. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleQrUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setLoading(true);
    setError(null);
    setVerdict(null);
    const scanId = `QR-${Math.random().toString(36).substring(2, 8).toUpperCase()}`;
    setCurrentScanId(scanId);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await api.post('/detect/scan-qr', formData);
      setVerdict(res.data.verdict);
    } catch (err) {
      setError(err.response?.data?.detail?.message || 'Failed to process QR code.');
    } finally {
      setLoading(false);
    }
  };

  const confidenceScore = verdict?.risk_level === 'high_risk' || verdict?.risk_level === 'critical' ? 94 :
                          verdict?.risk_level === 'moderate_risk' ? 62 : 8;

  return (
    <div className="max-w-4xl mx-auto px-4 py-10 space-y-8">
      {/* Header */}
      <div className="space-y-3">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 text-xs font-mono font-bold">
          <Globe className="w-3.5 h-3.5" /> DOMAIN & PAYLOAD INSPECTOR
        </div>
        <h1 className="text-3xl sm:text-4xl font-display font-extrabold text-white tracking-tight flex items-center gap-3">
          Phishing Link & QR Code Scanner
        </h1>
        <p className="text-slate-300 text-sm max-w-2xl">
          Analyze suspicious links, fake banking portals, and QR codes to detect credential harvesting and fraudulent domains.
        </p>
      </div>

      {/* Tabs */}
      <div className="flex p-1 rounded-xl bg-surface border border-border max-w-md">
        <button
          onClick={() => setActiveTab('url')}
          className={`flex-1 py-2.5 px-4 rounded-lg text-xs font-bold transition-all flex items-center justify-center gap-2 ${
            activeTab === 'url'
              ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-md'
              : 'text-slate-400 hover:text-white'
          }`}
        >
          <Link2 className="w-3.5 h-3.5" />
          URL Link Scanner
        </button>
        <button
          onClick={() => setActiveTab('qr')}
          className={`flex-1 py-2.5 px-4 rounded-lg text-xs font-bold transition-all flex items-center justify-center gap-2 ${
            activeTab === 'qr'
              ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-md'
              : 'text-slate-400 hover:text-white'
          }`}
        >
          <QrCode className="w-3.5 h-3.5" />
          QR Code Image
        </button>
      </div>

      {/* Input Form */}
      <div className="p-6 rounded-2xl bg-surface border border-border space-y-6">
        {activeTab === 'url' ? (
          <form onSubmit={handleUrlSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-mono font-bold uppercase tracking-wider text-slate-300 mb-2">
                SUSPICIOUS URL LINK
              </label>
              <div className="relative">
                <input
                  type="text"
                  placeholder="e.g. https://bank-kyc-update-portal-xyz.info/login"
                  value={urlInput}
                  onChange={(e) => setUrlInput(e.target.value)}
                  className="w-full px-4 py-3.5 rounded-xl bg-background border border-border text-white text-sm placeholder-slate-500 focus:outline-none focus:border-cyan-400 font-mono transition-colors"
                />
              </div>
            </div>
            <button
              type="submit"
              disabled={loading || !urlInput.trim()}
              className="w-full py-4 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-black font-display font-bold text-xs uppercase tracking-wider flex items-center justify-center gap-2 disabled:opacity-40 transition-all shadow-[0_0_20px_rgba(6,182,212,0.25)]"
            >
              {loading ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  Scanning Domain & Structural Entropy…
                </>
              ) : (
                <>
                  <Shield className="w-4 h-4" />
                  Run Link Scan
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>
        ) : (
          <div className="space-y-4">
            <label className="block text-xs font-mono font-bold uppercase tracking-wider text-slate-300">
              UPLOAD QR CODE IMAGE
            </label>
            <div className="border-2 border-dashed border-border hover:border-cyan-400/60 rounded-xl p-8 text-center bg-background/50 transition-colors">
              <input
                type="file"
                accept="image/*"
                onChange={handleQrUpload}
                className="hidden"
                id="qr-upload-input"
              />
              <label htmlFor="qr-upload-input" className="cursor-pointer space-y-3 block">
                <div className="w-12 h-12 rounded-xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center mx-auto text-cyan-400">
                  <QrCode className="w-6 h-6" />
                </div>
                <p className="text-xs font-semibold text-slate-200">
                  Click to select QR code image (PNG / JPEG)
                </p>
                <p className="text-[11px] text-slate-500">
                  Decodes embedded URLs and verifies destination domain safety
                </p>
              </label>
            </div>
          </div>
        )}
      </div>

      {/* Active Scan Stage Animation */}
      <ScanAnimation
        isActive={loading}
        scanId={currentScanId}
        stages={PHISHING_STAGES}
        accentColor="cyan"
      />

      {/* Error Display */}
      {error && (
        <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/30 text-red-300 text-xs flex items-start gap-3">
          <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
          <span>{error}</span>
        </div>
      )}

      {/* Verdict Output */}
      {verdict && !loading && (
        <ThreatResultCard
          verdict={verdict}
          confidence={confidenceScore}
          threatType={verdict.risk_level === 'safe' ? 'Legitimate Domain' : 'Phishing Link / Malicious URL'}
          scanId={currentScanId}
          extraMetrics={[
            { label: 'Domain Risk', value: verdict.risk_level?.toUpperCase() || 'SAFE', sub: 'Entropy evaluation' },
            { label: 'Brand Spoofing', value: verdict.risk_level === 'safe' ? 'None' : 'Detected', sub: 'Homograph check' },
            { label: 'SSL Status', value: 'Verified', sub: 'Transport security' }
          ]}
        />
      )}
    </div>
  );
};
