import React, { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ScanEye, UploadCloud, AlertCircle, Camera, ShieldCheck, ShieldX, RefreshCw } from 'lucide-react';
import { api } from '../services/api';
import { ScanAnimation } from '../components/ScanAnimation';
import { ThreatResultCard } from '../components/ThreatResultCard';

const DEEPFAKE_STAGES = [
  { id: 'input',     label: 'Media file uploaded & verified', duration: 400 },
  { id: 'normalize', label: 'Extracting face region bounding boxes', duration: 600 },
  { id: 'extract',   label: 'Normalizing resolution & color spaces', duration: 500 },
  { id: 'model',     label: 'Evaluating EfficientNet-B4 neural feature maps', duration: 1100 },
  { id: 'risk',      label: 'Calculating deepfake anomaly confidence score', duration: 500 },
];

const POLLING_MAX = 20;
const POLLING_INTERVAL_MS = 1500;

export const DeepfakeScan = () => {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [dragOver, setDragOver] = useState(false);
  const [currentTaskId, setCurrentTaskId] = useState(null);
  const inputRef = useRef(null);

  const resetState = () => {
    setResult(null);
    setError(null);
    setCurrentTaskId(null);
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
      if (res.data.status === 'complete' && res.data.result) {
        setLoading(false);
        setResult(res.data.result);
      } else if (res.data.task_id) {
        setCurrentTaskId(res.data.task_id);
        pollTask(res.data.task_id);
      } else {
        setLoading(false);
        setError('Unexpected response from server.');
      }
    } catch (err) {
      setLoading(false);
      const msg = err.response?.data?.detail?.message || err.response?.data?.detail || err.message || 'Failed to submit image for analysis.';
      setError(typeof msg === 'string' ? msg : JSON.stringify(msg));
    }
  };

  const verdict = result?.verdict;
  const analysis = result?.media_analysis;
  const anomalyScore = analysis?.anomaly_score !== undefined ? analysis.anomaly_score * 100 : 0;
  const isFake = verdict?.risk_level === 'high_risk' || verdict?.risk_level === 'moderate_risk';

  return (
    <div className="max-w-4xl mx-auto px-4 py-10 space-y-8">
      {/* Header */}
      <div className="space-y-3">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 text-xs font-mono font-bold">
          <ScanEye className="w-3.5 h-3.5" /> EFFICIENTNET-B4 NEURAL ENGINE
        </div>
        <h1 className="text-3xl sm:text-4xl font-display font-extrabold text-white tracking-tight flex items-center gap-3">
          Deepfake Media Detection
        </h1>
        <p className="text-slate-300 text-sm max-w-2xl">
          Upload any human face image to analyze for AI-generated manipulation, face-swaps, and deepfake artifacts.
        </p>
      </div>

      {/* Main Upload & Analysis Interface */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-start">
        {/* Left: Upload Dropzone & Scanning Preview */}
        <div className="space-y-4">
          <div
            onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
            onDragLeave={() => setDragOver(false)}
            onDrop={handleDrop}
            onClick={() => !loading && inputRef.current?.click()}
            className={`relative rounded-2xl border-2 border-dashed transition-all p-6 text-center space-y-4 overflow-hidden min-h-[300px] flex flex-col items-center justify-center ${
              loading ? 'cursor-wait border-cyan-500/60 bg-cyan-950/20' :
              dragOver ? 'border-cyan-400 bg-cyan-500/10 scale-[1.01]' :
              preview ? 'border-cyan-500/40 bg-surface/90 hover:border-cyan-400' :
              'border-border bg-surface hover:border-cyan-500/40 cursor-pointer'
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
              <div className="relative w-full space-y-3">
                <div className="relative inline-block overflow-hidden rounded-xl border border-border shadow-2xl max-h-64 mx-auto">
                  <img
                    src={preview}
                    alt="Selected media for analysis"
                    className="max-h-64 object-contain rounded-xl mx-auto"
                  />

                  {/* Animated laser scan line overlay when loading */}
                  {loading && (
                    <div className="absolute inset-0 pointer-events-none overflow-hidden rounded-xl">
                      <div className="absolute left-0 right-0 h-1 bg-gradient-to-r from-transparent via-cyan-400 to-transparent shadow-[0_0_15px_#06b6d4] animate-scan-line" />
                      <div className="absolute inset-0 bg-cyan-500/10 backdrop-contrast-125" />
                    </div>
                  )}
                </div>

                <div className="text-center space-y-1">
                  <p className="text-xs font-mono font-semibold text-slate-200 truncate max-w-xs mx-auto">
                    {file?.name}
                  </p>
                  <p className="text-[11px] text-slate-500">
                    {(file?.size / 1024).toFixed(1)} KB · Click or drag to replace
                  </p>
                </div>
              </div>
            ) : (
              <div className="space-y-3 p-4">
                <div className="mx-auto w-16 h-16 rounded-2xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400 shadow-[0_0_20px_rgba(6,182,212,0.15)]">
                  <UploadCloud className="w-8 h-8" />
                </div>
                <div className="space-y-1">
                  <p className="text-slate-200 font-display font-semibold text-sm">
                    Drop face image here or <span className="text-cyan-400 underline">browse</span>
                  </p>
                  <p className="text-xs text-slate-500">
                    Supports JPEG, PNG, WebP · Human face images work best
                  </p>
                </div>
              </div>
            )}
          </div>

          {/* Analyze Action Button */}
          <button
            onClick={handleSubmit}
            disabled={!file || loading}
            className="w-full py-4 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-black font-display font-bold text-sm tracking-wider uppercase flex items-center justify-center gap-2 disabled:opacity-40 transition-all shadow-[0_0_20px_rgba(6,182,212,0.25)]"
            id="deepfake-analyze-btn"
          >
            {loading ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                Analyzing Deepfake Signals…
              </>
            ) : (
              <>
                <Camera className="w-4 h-4" />
                Analyze Media
              </>
            )}
          </button>

          {/* Model Credibility Tag */}
          <div className="p-4 rounded-xl bg-surface/60 border border-border/50 space-y-2 text-xs text-slate-400">
            <div className="flex justify-between items-center text-slate-300 font-mono text-[11px]">
              <span>MODEL: EfficientNet-B4</span>
              <span className="text-cyan-400 font-bold">AUC 98.59%</span>
            </div>
            <p className="text-[11px] leading-relaxed">
              Trained on Celeb-DF dataset. Evaluates spatial inconsistencies, blending boundaries, and neural noise distribution.
            </p>
          </div>
        </div>

        {/* Right: Live Scanning Progress & Threat Result Reveal */}
        <div className="space-y-6">
          {/* Active Scan Stage Animation */}
          <ScanAnimation
            isActive={loading}
            scanId={currentTaskId}
            stages={DEEPFAKE_STAGES}
            accentColor="cyan"
          />

          {/* Error display */}
          {error && (
            <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/30 text-red-300 text-xs flex items-start gap-3">
              <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          {/* Final Verdict Threat Result Card */}
          {verdict && !loading && (
            <div className="space-y-4">
              {/* Highlight Reveal Banner */}
              <motion.div
                initial={{ scale: 0.95, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                className={`p-5 rounded-2xl border text-center space-y-2 ${
                  isFake
                    ? 'bg-red-950/40 border-red-500/40 shadow-[0_0_30px_rgba(239,68,68,0.2)]'
                    : 'bg-emerald-950/40 border-emerald-500/40 shadow-[0_0_30px_rgba(34,197,94,0.2)]'
                }`}
              >
                <div className="flex items-center justify-center gap-2">
                  {isFake ? (
                    <ShieldX className="w-8 h-8 text-red-400" />
                  ) : (
                    <ShieldCheck className="w-8 h-8 text-emerald-400" />
                  )}
                  <span className={`text-2xl font-display font-extrabold tracking-wider ${isFake ? 'text-red-400' : 'text-emerald-400'}`}>
                    {isFake ? 'MANIPULATED MEDIA (FAKE)' : 'AUTHENTIC MEDIA (REAL)'}
                  </span>
                </div>
                <p className="text-xs text-slate-300">
                  Confidence Score: <strong className="text-white font-mono text-sm">{anomalyScore.toFixed(1)}%</strong>
                </p>
              </motion.div>

              <ThreatResultCard
                verdict={verdict}
                confidence={anomalyScore}
                threatType={isFake ? 'Deepfake Manipulation Detected' : 'Authentic Media Verified'}
                scanId={currentTaskId}
                extraMetrics={[
                  { label: 'Faces Detected', value: analysis?.faces_detected ?? 1, sub: 'Face bounding regions' },
                  { label: 'Anomaly Probability', value: `${(anomalyScore).toFixed(1)}%`, sub: 'EfficientNet output' },
                  { label: 'Model Baseline', value: 'Celeb-DF', sub: '92.8% Test Accuracy' }
                ]}
              />
            </div>
          )}

          {!verdict && !loading && (
            <div className="p-8 rounded-2xl bg-surface/40 border border-border/40 text-center space-y-3">
              <ScanEye className="w-12 h-12 text-slate-600 mx-auto" />
              <p className="text-slate-400 text-xs">
                Upload an image on the left and click "Analyze Media" to start threat scanning.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
