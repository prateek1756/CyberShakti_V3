import React, { useState, useRef } from 'react';
import { ScanEye, UploadCloud, AlertCircle, Loader2, ShieldX, ShieldCheck, Camera } from 'lucide-react';
import { api } from '../services/api';

const BADGE_STYLES = {
  high_risk:     { bg: 'bg-red-500/15 border-red-500/40',     text: 'text-red-300',     label: '⚠ DEEPFAKE DETECTED',   icon: ShieldX },
  moderate_risk: { bg: 'bg-amber-500/15 border-amber-500/40', text: 'text-amber-300',   label: '⚠ SUSPICIOUS',          icon: ShieldX },
  safe:          { bg: 'bg-emerald-500/15 border-emerald-500/40', text: 'text-emerald-300', label: '✓ AUTHENTIC',        icon: ShieldCheck },
};

const POLLING_MAX = 20;
const POLLING_INTERVAL_MS = 1500;

export const DeepfakeScan = () => {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [dragOver, setDragOver] = useState(false);
  const inputRef = useRef(null);

  const resetState = () => {
    setResult(null);
    setError(null);
  };

  const handleFile = (selectedFile) => {
    if (!selectedFile) return;
    if (!selectedFile.type.startsWith('image/')) {
      setError('Please upload a JPEG, PNG, or WebP image file.');
      return;
    }
    setFile(selectedFile);
    setPreview(URL.createObjectURL(selectedFile));
    resetState();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    handleFile(e.dataTransfer.files[0]);
  };

  const pollTask = (taskId) => {
    let attempts = 0;
    const interval = setInterval(async () => {
      attempts++;
      try {
        const res = await api.get(`/tasks/${taskId}/status`);
        const { status, result: taskResult, message } = res.data;
        if (status === 'complete') {
          clearInterval(interval);
          setLoading(false);
          setResult(taskResult);
        } else if (status === 'error' || attempts >= POLLING_MAX) {
          clearInterval(interval);
          setLoading(false);
          setError(message || 'Analysis timed out. Please try again.');
        }
      } catch {
        clearInterval(interval);
        setLoading(false);
        setError('Connection error while checking analysis status.');
      }
    }, POLLING_INTERVAL_MS);
  };

  const handleSubmit = async () => {
    if (!file) return;
    setLoading(true);
    resetState();

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await api.post('/detect/analyze-media-deepfake', formData);
      if (res.data.task_id) {
        pollTask(res.data.task_id);
      } else {
        setLoading(false);
        setError('Unexpected response from server.');
      }
    } catch (err) {
      setLoading(false);
      const msg = err.response?.data?.detail?.message || err.response?.data?.detail || 'Failed to submit image for analysis.';
      setError(typeof msg === 'string' ? msg : JSON.stringify(msg));
    }
  };

  const verdict = result?.verdict;
  const analysis = result?.media_analysis;
  const badge = verdict ? BADGE_STYLES[verdict.risk_level] : null;

  return (
    <div className="max-w-3xl mx-auto px-4 py-8 space-y-8">
      {/* Header */}
      <div className="space-y-2">
        <h1 className="text-3xl font-extrabold text-white flex items-center gap-3">
          <ScanEye className="w-8 h-8 text-cyan-400" />
          Deepfake Media Detection
        </h1>
        <p className="text-slate-300 text-sm">
          Upload a face image or video frame to detect AI-generated manipulated media using our EfficientNet-B4 model (Acc: 92.80%, AUC: 98.59%).
        </p>
      </div>

      {/* Upload Zone */}
      <div
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
        className={`relative rounded-2xl border-2 border-dashed transition-all cursor-pointer p-8 text-center space-y-4 ${
          dragOver
            ? 'border-cyan-400 bg-cyan-500/5'
            : 'border-border bg-surface hover:border-cyan-500/50'
        }`}
      >
        <input
          ref={inputRef}
          type="file"
          accept="image/*"
          className="hidden"
          id="deepfake-file-input"
          onChange={(e) => handleFile(e.target.files[0])}
        />

        {preview ? (
          <div className="space-y-3">
            <img
              src={preview}
              alt="Selected for analysis"
              className="mx-auto max-h-56 rounded-xl object-cover border border-border shadow-lg"
            />
            <p className="text-sm text-slate-400">
              <span className="font-semibold text-slate-200">{file?.name}</span>{' '}
              · {(file?.size / 1024).toFixed(1)} KB
            </p>
            <p className="text-xs text-slate-500">Click or drag to replace</p>
          </div>
        ) : (
          <div className="space-y-3">
            <div className="mx-auto w-16 h-16 rounded-2xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center">
              <UploadCloud className="w-8 h-8 text-cyan-400" />
            </div>
            <p className="text-slate-300 font-semibold">Drag & drop an image, or click to browse</p>
            <p className="text-xs text-slate-500">JPEG, PNG, WebP · Max 10 MB · Human face images work best</p>
          </div>
        )}
      </div>

      {/* Analyze Button */}
      <button
        onClick={handleSubmit}
        disabled={!file || loading}
        className="w-full py-3.5 rounded-xl bg-cyan-600 hover:bg-cyan-700 text-white font-bold flex items-center justify-center gap-2 disabled:opacity-40 transition-all shadow-lg shadow-cyan-900/20"
        id="deepfake-analyze-btn"
      >
        {loading ? (
          <>
            <Loader2 className="w-5 h-5 animate-spin" />
            Analyzing with EfficientNet-B4…
          </>
        ) : (
          <>
            <Camera className="w-5 h-5" />
            Analyze for Deepfake
          </>
        )}
      </button>

      {/* Error */}
      {error && (
        <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/30 text-red-300 text-sm flex items-start gap-3">
          <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
          <span>{error}</span>
        </div>
      )}

      {/* Verdict Card */}
      {verdict && badge && (
        <div className={`p-6 rounded-2xl border space-y-5 ${badge.bg}`}>
          {/* Verdict Header */}
          <div className="flex items-center gap-4">
            <div className={`p-3 rounded-xl border ${badge.bg}`}>
              {React.createElement(badge.icon, { className: `w-7 h-7 ${badge.text}` })}
            </div>
            <div>
              <span className={`text-xs uppercase tracking-widest font-bold ${badge.text}`}>
                {badge.label}
              </span>
              <p className="text-white font-bold text-lg">{verdict.risk_label || verdict.risk_level}</p>
            </div>
          </div>

          {/* Metrics Grid */}
          {analysis && (
            <div className="grid grid-cols-3 gap-3">
              <div className="p-4 rounded-xl bg-background/60 border border-border text-center space-y-1">
                <p className="text-xs uppercase tracking-wider text-slate-400">Anomaly Score</p>
                <p className={`text-2xl font-extrabold ${badge.text}`}>
                  {(analysis.anomaly_score * 100).toFixed(1)}%
                </p>
                <p className="text-[10px] text-slate-500">Fake probability</p>
              </div>
              <div className="p-4 rounded-xl bg-background/60 border border-border text-center space-y-1">
                <p className="text-xs uppercase tracking-wider text-slate-400">Faces Detected</p>
                <p className="text-2xl font-extrabold text-white">
                  {analysis.faces_detected ?? '—'}
                </p>
                <p className="text-[10px] text-slate-500">Face regions</p>
              </div>
              <div className="p-4 rounded-xl bg-background/60 border border-border text-center space-y-1">
                <p className="text-xs uppercase tracking-wider text-slate-400">Model</p>
                <p className="text-xs font-bold text-slate-200 leading-tight mt-1">
                  EfficientNet-B4
                </p>
                <p className="text-[10px] text-slate-500">AUC 98.59%</p>
              </div>
            </div>
          )}

          {/* Explanation */}
          {verdict.explanation && (
            <div className="p-4 rounded-xl bg-background/60 border border-border space-y-1">
              <p className="text-xs uppercase tracking-wider text-slate-400 font-semibold">Analysis</p>
              <p className="text-slate-200 text-sm">{verdict.explanation}</p>
            </div>
          )}

          {/* Recommended Action */}
          {verdict.recommended_action && (
            <div className="p-4 rounded-xl bg-background/60 border border-border space-y-1">
              <p className="text-xs uppercase tracking-wider text-slate-400 font-semibold">Recommended Action</p>
              <p className="text-slate-200 text-sm">{verdict.recommended_action}</p>
            </div>
          )}

          <p className="text-[10px] text-slate-500 text-center">
            {verdict.disclaimer || 'AI model output is advisory. Visual verification is recommended for final decisions.'}
          </p>
        </div>
      )}

      {/* Info Box */}
      <div className="p-5 rounded-2xl bg-surface border border-border space-y-3">
        <h3 className="text-sm font-bold text-white">How it works</h3>
        <ul className="text-xs text-slate-400 space-y-1.5 list-disc list-inside">
          <li>Upload any image containing a human face (photo, screenshot, video frame)</li>
          <li>Our EfficientNet-B4 model extracts facial features and checks for manipulation artifacts</li>
          <li>Results include anomaly score, face count, and verdict with recommended action</li>
          <li>Trained on Celeb-DF dataset · Test Accuracy 92.80% · F1 90.58% · AUC 98.59%</li>
        </ul>
      </div>
    </div>
  );
};
