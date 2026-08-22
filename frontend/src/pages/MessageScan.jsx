import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { MessageSquare, FileImage, AlertCircle, RefreshCw, Send, ShieldAlert, Cpu, FileText } from 'lucide-react';
import { api } from '../services/api';
import { ScanAnimation } from '../components/ScanAnimation';
import { ThreatResultCard } from '../components/ThreatResultCard';

const MESSAGE_STAGES = [
  { id: 'input',     label: 'Text content ingested',             duration: 300 },
  { id: 'normalize', label: 'Cleaning & tokenizing text',         duration: 400 },
  { id: 'extract',   label: 'Extracting urgency & financial keywords', duration: 500 },
  { id: 'model',     label: 'Running NLP scam classification model', duration: 800 },
  { id: 'risk',      label: 'Compiling threat indicators',       duration: 400 },
];

export const MessageScan = () => {
  const [activeTab, setActiveTab] = useState('text');
  const [textInput, setTextInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [verdict, setVerdict] = useState(null);
  const [extractedText, setExtractedText] = useState(null);
  const [currentScanId, setCurrentScanId] = useState(null);

  const handleTextSubmit = async (e) => {
    e.preventDefault();
    if (!textInput.trim()) return;

    setLoading(true);
    setError(null);
    setVerdict(null);
    const scanId = `MSG-${Math.random().toString(36).substring(2, 8).toUpperCase()}`;
    setCurrentScanId(scanId);

    try {
      const res = await api.post('/detect/scan-message', { text: textInput.trim() });
      setVerdict(res.data.verdict);
    } catch (err) {
      setError(err.response?.data?.detail?.message || 'Failed to analyze text message.');
    } finally {
      setLoading(false);
    }
  };

  const handleScreenshotUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setLoading(true);
    setError(null);
    setVerdict(null);
    setExtractedText(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await api.post('/detect/scan-screenshot', formData);
      const taskId = res.data.task_id;
      setCurrentScanId(taskId);

      let attempts = 0;
      const interval = setInterval(async () => {
        attempts++;
        try {
          const statusRes = await api.get(`/tasks/${taskId}/status`);
          if (statusRes.data.status === 'complete') {
            clearInterval(interval);
            setLoading(false);
            setVerdict(statusRes.data.result.verdict);
            setExtractedText(statusRes.data.result.ocr_result?.text_extracted);
          } else if (statusRes.data.status === 'error' || attempts > 12) {
            clearInterval(interval);
            setLoading(false);
            setError(statusRes.data.message || 'Screenshot analysis timed out.');
          }
        } catch {
          clearInterval(interval);
          setLoading(false);
          setError('Task polling failed.');
        }
      }, 1500);
    } catch (err) {
      setLoading(false);
      setError(err.response?.data?.detail?.message || 'Failed to upload screenshot.');
    }
  };

  const riskScore = verdict?.risk_level === 'high_risk' || verdict?.risk_level === 'critical' ? 88 :
                    verdict?.risk_level === 'moderate_risk' ? 58 : 12;

  return (
    <div className="max-w-6xl mx-auto px-4 py-10 space-y-8">
      {/* Header */}
      <div className="space-y-3">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-purple-500/10 border border-purple-500/30 text-purple-400 text-xs font-mono font-bold">
          <MessageSquare className="w-3.5 h-3.5" /> THREAT INTEL CONSOLE
        </div>
        <h1 className="text-3xl sm:text-4xl font-display font-extrabold text-white tracking-tight flex items-center gap-3">
          Scam Text & Email Analyzer
        </h1>
        <p className="text-slate-300 text-sm max-w-2xl">
          Analyze suspicious WhatsApp forwards, SMS messages, phishing emails, or uploaded chat screenshots for financial fraud indicators.
        </p>
      </div>

      {/* Split Console Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left Column: Input Terminal (5 cols) */}
        <div className="lg:col-span-5 space-y-6">
          {/* Mode Selector Tabs */}
          <div className="flex p-1 rounded-xl bg-surface border border-border">
            <button
              onClick={() => setActiveTab('text')}
              className={`flex-1 py-2.5 px-3 rounded-lg text-xs font-bold transition-all flex items-center justify-center gap-2 ${
                activeTab === 'text'
                  ? 'bg-purple-500/20 text-purple-300 border border-purple-500/40 shadow-md'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <MessageSquare className="w-3.5 h-3.5" />
              Text / Email Body
            </button>
            <button
              onClick={() => setActiveTab('screenshot')}
              className={`flex-1 py-2.5 px-3 rounded-lg text-xs font-bold transition-all flex items-center justify-center gap-2 ${
                activeTab === 'screenshot'
                  ? 'bg-purple-500/20 text-purple-300 border border-purple-500/40 shadow-md'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <FileImage className="w-3.5 h-3.5" />
              OCR Screenshot
            </button>
          </div>

          {/* Form container */}
          <div className="p-6 rounded-2xl bg-surface border border-border space-y-4">
            {activeTab === 'text' ? (
              <form onSubmit={handleTextSubmit} className="space-y-4">
                <div>
                  <label className="block text-xs font-mono font-bold uppercase tracking-wider text-slate-300 mb-2">
                    MESSAGE / EMAIL INPUT
                  </label>
                  <textarea
                    rows={6}
                    placeholder="Paste suspect message text here (e.g. 'Dear customer, your bank account will be suspended. Click link immediately to verify KYC...')"
                    value={textInput}
                    onChange={(e) => setTextInput(e.target.value)}
                    className="w-full px-4 py-3 rounded-xl bg-background border border-border text-white text-sm placeholder-slate-500 focus:outline-none focus:border-purple-400 font-sans transition-colors resize-none"
                  />
                </div>

                <button
                  type="submit"
                  disabled={loading || !textInput.trim()}
                  className="w-full py-3.5 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-display font-bold text-xs uppercase tracking-wider flex items-center justify-center gap-2 disabled:opacity-40 transition-all shadow-[0_0_20px_rgba(147,51,234,0.25)]"
                >
                  {loading ? (
                    <>
                      <RefreshCw className="w-4 h-4 animate-spin" />
                      Analyzing Message…
                    </>
                  ) : (
                    <>
                      <Send className="w-4 h-4" />
                      Run Threat Analysis
                    </>
                  )}
                </button>
              </form>
            ) : (
              <div className="space-y-4">
                <label className="block text-xs font-mono font-bold uppercase tracking-wider text-slate-300">
                  UPLOAD CHAT SCREENSHOT
                </label>
                <div className="border-2 border-dashed border-border hover:border-purple-400/60 rounded-xl p-8 text-center bg-background/50 transition-colors">
                  <input
                    type="file"
                    accept="image/*"
                    onChange={handleScreenshotUpload}
                    className="hidden"
                    id="screenshot-input"
                  />
                  <label htmlFor="screenshot-input" className="cursor-pointer space-y-3 block">
                    <div className="w-12 h-12 rounded-xl bg-purple-500/10 border border-purple-500/30 flex items-center justify-center mx-auto text-purple-400">
                      <FileImage className="w-6 h-6" />
                    </div>
                    <p className="text-xs font-semibold text-slate-200">
                      Click to select screenshot (PNG / JPEG)
                    </p>
                    <p className="text-[11px] text-slate-500">
                      Tesseract OCR will extract text from the chat image
                    </p>
                  </label>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Threat Intel Output Console (7 cols) */}
        <div className="lg:col-span-7 space-y-6">
          {/* Active Scan Stage Animation */}
          <ScanAnimation
            isActive={loading}
            scanId={currentScanId}
            stages={MESSAGE_STAGES}
            accentColor="purple"
          />

          {/* OCR Extracted Text Box */}
          {extractedText && !loading && (
            <motion.div
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              className="p-4 rounded-xl bg-surface border border-purple-500/30 space-y-1.5"
            >
              <span className="text-[10px] font-mono uppercase tracking-wider font-bold text-purple-400 flex items-center gap-1.5">
                <FileText className="w-3.5 h-3.5" /> OCR EXTRACTED TEXT CONTENT
              </span>
              <p className="text-slate-200 text-xs font-mono bg-background/80 p-3 rounded-lg border border-border">
                "{extractedText}"
              </p>
            </motion.div>
          )}

          {/* Error display */}
          {error && (
            <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/30 text-red-300 text-xs flex items-start gap-3">
              <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          {/* Final Verdict Output Card */}
          {verdict && !loading && (
            <ThreatResultCard
              verdict={verdict}
              confidence={riskScore}
              threatType={verdict.scam_category ? verdict.scam_category.replace(/_/g, ' ') : 'Potential Scam'}
              scanId={currentScanId}
              extraMetrics={[
                { label: 'Urgency Signals', value: verdict.risk_level === 'safe' ? '0' : 'High', sub: 'Urgent action demands' },
                { label: 'Scam Classification', value: verdict.risk_level === 'safe' ? 'Legitimate' : 'Fraudulent', sub: 'NLP engine output' },
                { label: 'Risk Band', value: verdict.risk_level?.toUpperCase() || 'SAFE', sub: 'Threat severity' }
              ]}
            />
          )}

          {!verdict && !loading && (
            <div className="p-12 rounded-2xl bg-surface/40 border border-border/40 text-center space-y-3">
              <ShieldAlert className="w-12 h-12 text-slate-600 mx-auto" />
              <p className="text-slate-400 text-xs">
                Enter message text or upload a screenshot on the left to begin threat analysis.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
