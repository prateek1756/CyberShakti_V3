import React, { useState } from 'react';
import { MessageSquare, FileImage, AlertCircle, Loader2 } from 'lucide-react';
import { api } from '../services/api';
import { VerdictCard } from '../components/VerdictCard';

export const MessageScan = () => {
  const [activeTab, setActiveTab] = useState('text');
  const [textInput, setTextInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [verdict, setVerdict] = useState(null);
  const [extractedText, setExtractedText] = useState(null);

  const handleTextSubmit = async (e) => {
    e.preventDefault();
    if (!textInput.trim()) return;

    setLoading(true);
    setError(null);
    setVerdict(null);

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
      // Poll task status
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
          } else if (statusRes.data.status === 'error' || attempts > 10) {
            clearInterval(interval);
            setLoading(false);
            setError(statusRes.data.message || 'Screenshot analysis timed out.');
          }
        } catch (pollErr) {
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

  return (
    <div className="max-w-3xl mx-auto px-4 py-8 space-y-8">
      {/* Header */}
      <div className="space-y-2">
        <h1 className="text-3xl font-extrabold text-white flex items-center gap-3">
          <MessageSquare className="w-8 h-8 text-purple-400" />
          Message & Email Scam Detection
        </h1>
        <p className="text-slate-300 text-sm">
          Check suspicious WhatsApp messages, emails, SMS, or uploaded screenshots for scam and fraud indicators.
        </p>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-border">
        <button
          onClick={() => setActiveTab('text')}
          className={`px-5 py-3 text-sm font-semibold flex items-center gap-2 border-b-2 transition-all ${
            activeTab === 'text' ? 'border-purple-400 text-purple-400' : 'border-transparent text-slate-400 hover:text-white'
          }`}
        >
          <MessageSquare className="w-4 h-4" />
          Text / Email Copy
        </button>
        <button
          onClick={() => setActiveTab('screenshot')}
          className={`px-5 py-3 text-sm font-semibold flex items-center gap-2 border-b-2 transition-all ${
            activeTab === 'screenshot' ? 'border-purple-400 text-purple-400' : 'border-transparent text-slate-400 hover:text-white'
          }`}
        >
          <FileImage className="w-4 h-4" />
          Screenshot Scan
        </button>
      </div>

      {/* Input */}
      <div className="p-6 rounded-2xl bg-surface border border-border space-y-6">
        {activeTab === 'text' ? (
          <form onSubmit={handleTextSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-200 mb-2">Paste Message / Email Body</label>
              <textarea
                rows={5}
                placeholder="e.g. Dear customer, your electricity connection will be disconnected tonight. Pay bill immediately at bit.ly/power-pay"
                value={textInput}
                onChange={(e) => setTextInput(e.target.value)}
                className="w-full px-4 py-3 rounded-xl bg-background border border-border text-white placeholder-slate-500 focus:outline-none focus:border-purple-400 transition-colors"
              />
            </div>
            <button
              type="submit"
              disabled={loading || !textInput.trim()}
              className="w-full py-3 rounded-xl bg-purple-600 hover:bg-purple-700 text-white font-semibold flex items-center justify-center gap-2 disabled:opacity-50 transition-all"
            >
              {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Analyze Message'}
            </button>
          </form>
        ) : (
          <div className="space-y-4">
            <label className="block text-sm font-medium text-slate-200">Upload Screenshot Image</label>
            <div className="border-2 border-dashed border-border rounded-xl p-8 text-center bg-background/50 hover:border-purple-400 transition-colors">
              <input
                type="file"
                accept="image/*"
                onChange={handleScreenshotUpload}
                className="hidden"
                id="screenshot-input"
              />
              <label htmlFor="screenshot-input" className="cursor-pointer space-y-2">
                <FileImage className="w-10 h-10 text-slate-400 mx-auto" />
                <p className="text-sm font-medium text-slate-300">Click to upload screenshot (PNG / JPEG)</p>
              </label>
            </div>
          </div>
        )}
      </div>

      {/* Extracted OCR Text Box */}
      {extractedText && (
        <div className="p-4 rounded-xl bg-surface border border-border space-y-1">
          <span className="text-xs uppercase tracking-wider font-semibold text-slate-400">OCR Extracted Text</span>
          <p className="text-slate-200 text-sm italic">"{extractedText}"</p>
        </div>
      )}

      {error && (
        <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/30 text-red-300 text-sm flex items-center gap-3">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {verdict && <VerdictCard verdict={verdict} />}
    </div>
  );
};
