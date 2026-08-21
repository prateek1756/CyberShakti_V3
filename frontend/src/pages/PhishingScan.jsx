import React, { useState } from 'react';
import { Shield, Link2, QrCode, AlertCircle, Loader2 } from 'lucide-react';
import { api } from '../services/api';
import { VerdictCard } from '../components/VerdictCard';

export const PhishingScan = () => {
  const [activeTab, setActiveTab] = useState('url'); // 'url' or 'qr'
  const [urlInput, setUrlInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [verdict, setVerdict] = useState(null);

  const handleUrlSubmit = async (e) => {
    e.preventDefault();
    if (!urlInput.trim()) return;

    setLoading(true);
    setError(null);
    setVerdict(null);

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

  return (
    <div className="max-w-3xl mx-auto px-4 py-8 space-y-8">
      {/* Title */}
      <div className="space-y-2">
        <h1 className="text-3xl font-extrabold text-white flex items-center gap-3">
          <Shield className="w-8 h-8 text-primary" />
          Phishing Link & QR Code Scanner
        </h1>
        <p className="text-slate-300 text-sm">
          Analyze suspicious links and QR codes to detect phishing, credential theft, and fraudulent domains.
        </p>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-border">
        <button
          onClick={() => setActiveTab('url')}
          className={`px-5 py-3 text-sm font-semibold flex items-center gap-2 border-b-2 transition-all ${
            activeTab === 'url' ? 'border-primary text-primary' : 'border-transparent text-slate-400 hover:text-white'
          }`}
        >
          <Link2 className="w-4 h-4" />
          URL Link Scan
        </button>
        <button
          onClick={() => setActiveTab('qr')}
          className={`px-5 py-3 text-sm font-semibold flex items-center gap-2 border-b-2 transition-all ${
            activeTab === 'qr' ? 'border-primary text-primary' : 'border-transparent text-slate-400 hover:text-white'
          }`}
        >
          <QrCode className="w-4 h-4" />
          QR Code Image Scan
        </button>
      </div>

      {/* Form Area */}
      <div className="p-6 rounded-2xl bg-surface border border-border space-y-6">
        {activeTab === 'url' ? (
          <form onSubmit={handleUrlSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-200 mb-2">Suspicious URL Link</label>
              <input
                type="text"
                placeholder="e.g. https://bank-kyc-update-xyz.info"
                value={urlInput}
                onChange={(e) => setUrlInput(e.target.value)}
                className="w-full px-4 py-3 rounded-xl bg-background border border-border text-white placeholder-slate-500 focus:outline-none focus:border-primary transition-colors"
              />
            </div>
            <button
              type="submit"
              disabled={loading || !urlInput.trim()}
              className="w-full py-3 rounded-xl bg-primary hover:bg-primary-hover text-white font-semibold flex items-center justify-center gap-2 disabled:opacity-50 transition-all"
            >
              {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Analyze Link'}
            </button>
          </form>
        ) : (
          <div className="space-y-4">
            <label className="block text-sm font-medium text-slate-200">Upload QR Code Image</label>
            <div className="border-2 border-dashed border-border rounded-xl p-8 text-center bg-background/50 hover:border-primary transition-colors">
              <input
                type="file"
                accept="image/*"
                onChange={handleQrUpload}
                className="hidden"
                id="qr-upload-input"
              />
              <label htmlFor="qr-upload-input" className="cursor-pointer space-y-2">
                <QrCode className="w-10 h-10 text-slate-400 mx-auto" />
                <p className="text-sm font-medium text-slate-300">Click to upload QR code image (PNG / JPEG)</p>
              </label>
            </div>
          </div>
        )}
      </div>

      {/* Error display */}
      {error && (
        <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/30 text-red-300 text-sm flex items-center gap-3">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Verdict Output */}
      {verdict && <VerdictCard verdict={verdict} />}
    </div>
  );
};
