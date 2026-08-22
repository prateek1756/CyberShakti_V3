import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Lock, Unlock, FileCheck, ShieldAlert, Download, RefreshCw, KeyRound, CheckCircle2, ShieldCheck } from 'lucide-react';
import { api } from '../services/api';

export const FileEncrypt = () => {
  const [mode, setMode] = useState('encrypt');
  const [file, setFile] = useState(null);
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file || !password) return;

    setLoading(true);
    setError(null);
    setSuccess(false);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('password', password);

    const endpoint = mode === 'encrypt' ? '/protect/encrypt-file' : '/protect/decrypt-file';

    try {
      const response = await api.post(endpoint, formData, {
        responseType: 'blob',
      });

      const blob = new Blob([response.data]);
      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = mode === 'encrypt' ? `${file.name}.enc` : file.name.replace('.enc', '');
      document.body.appendChild(link);
      link.click();
      link.remove();
      setSuccess(true);
    } catch {
      setError(mode === 'encrypt' ? 'Encryption failed. Verify file.' : 'Decryption failed. Incorrect password.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-10 space-y-8">
      {/* Header */}
      <div className="space-y-3">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-mono font-bold">
          <KeyRound className="w-3.5 h-3.5" /> ARGON2ID + AES-256-GCM VAULT
        </div>
        <h1 className="text-3xl sm:text-4xl font-display font-extrabold text-white tracking-tight flex items-center gap-3">
          Secure File Encryption & Decryption
        </h1>
        <p className="text-slate-300 text-sm max-w-2xl">
          Encrypt confidential documents with password-derived Argon2id cryptographic keys and authenticated AES-256-GCM encryption.
        </p>
      </div>

      {/* Mode Selector Tabs */}
      <div className="flex p-1 rounded-xl bg-surface border border-border max-w-md">
        <button
          onClick={() => { setMode('encrypt'); setSuccess(false); setError(null); }}
          className={`flex-1 py-2.5 px-4 rounded-lg text-xs font-bold transition-all flex items-center justify-center gap-2 ${
            mode === 'encrypt'
              ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 shadow-md'
              : 'text-slate-400 hover:text-white'
          }`}
        >
          <Lock className="w-3.5 h-3.5" />
          Encrypt File
        </button>
        <button
          onClick={() => { setMode('decrypt'); setSuccess(false); setError(null); }}
          className={`flex-1 py-2.5 px-4 rounded-lg text-xs font-bold transition-all flex items-center justify-center gap-2 ${
            mode === 'decrypt'
              ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 shadow-md'
              : 'text-slate-400 hover:text-white'
          }`}
        >
          <Unlock className="w-3.5 h-3.5" />
          Decrypt File
        </button>
      </div>

      {/* Cryptographic Pipeline Status Graphic */}
      <div className="p-6 rounded-2xl bg-surface border border-border space-y-4">
        <span className="text-[10px] font-mono uppercase tracking-widest font-bold text-slate-400">
          PROTECTION PIPELINE STAGES
        </span>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center">
          <div className={`p-3 rounded-xl border text-xs font-semibold ${file ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300' : 'bg-background/60 border-border text-slate-500'}`}>
            <span className="block text-[10px] font-mono text-slate-500">STAGE 1</span>
            FILE RECEIVED
          </div>
          <div className={`p-3 rounded-xl border text-xs font-semibold ${password ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300' : 'bg-background/60 border-border text-slate-500'}`}>
            <span className="block text-[10px] font-mono text-slate-500">STAGE 2</span>
            ARGON2ID KEY
          </div>
          <div className={`p-3 rounded-xl border text-xs font-semibold ${loading ? 'bg-emerald-500/20 border-emerald-500/50 text-emerald-300 animate-pulse' : 'bg-background/60 border-border text-slate-500'}`}>
            <span className="block text-[10px] font-mono text-slate-500">STAGE 3</span>
            AES-256-GCM
          </div>
          <div className={`p-3 rounded-xl border text-xs font-semibold ${success ? 'bg-emerald-500/20 border-emerald-500/50 text-emerald-300' : 'bg-background/60 border-border text-slate-500'}`}>
            <span className="block text-[10px] font-mono text-slate-500">STAGE 4</span>
            PROTECTED
          </div>
        </div>
      </div>

      {/* Warning Box */}
      <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-200 text-xs flex items-start gap-3">
        <ShieldAlert className="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5" />
        <div>
          <strong className="font-semibold block text-amber-300 mb-0.5">Zero-Knowledge Guarantee:</strong>
          CyberShakti does not store your passphrase or plain file contents. If you lose your encryption passphrase, encrypted files cannot be recovered by anyone.
        </div>
      </div>

      {/* Main Form */}
      <div className="p-6 rounded-2xl bg-surface border border-border space-y-6">
        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label className="block text-xs font-mono font-bold uppercase tracking-wider text-slate-300 mb-2">
              SELECT FILE TO {mode.toUpperCase()}
            </label>
            <input
              type="file"
              onChange={(e) => { setFile(e.target.files[0]); setSuccess(false); }}
              className="w-full text-xs text-slate-300 file:mr-4 file:py-2.5 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-bold file:bg-emerald-500/20 file:text-emerald-300 hover:file:bg-emerald-500/30 cursor-pointer p-2 rounded-xl bg-background border border-border"
            />
          </div>

          <div>
            <label className="block text-xs font-mono font-bold uppercase tracking-wider text-slate-300 mb-2">
              ENCRYPTION PASSPHRASE
            </label>
            <input
              type="password"
              placeholder="Enter strong passphrase..."
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-3 rounded-xl bg-background border border-border text-white text-sm placeholder-slate-500 focus:outline-none focus:border-emerald-400 font-mono transition-colors"
            />
          </div>

          <button
            type="submit"
            disabled={loading || !file || !password}
            className="w-full py-4 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-black font-display font-bold text-xs uppercase tracking-wider flex items-center justify-center gap-2 disabled:opacity-40 transition-all shadow-[0_0_20px_rgba(16,185,129,0.25)]"
          >
            {loading ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                Processing Cryptographic Transformation…
              </>
            ) : (
              <>
                <Download className="w-4 h-4" />
                {mode === 'encrypt' ? 'Encrypt & Download Protected File' : 'Decrypt & Download Original File'}
              </>
            )}
          </button>
        </form>

        {/* Success Banner */}
        {success && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="p-5 rounded-xl bg-emerald-950/40 border border-emerald-500/40 text-emerald-300 text-xs flex items-center gap-3 shadow-[0_0_20px_rgba(16,185,129,0.15)]"
          >
            <ShieldCheck className="w-6 h-6 text-emerald-400 flex-shrink-0" />
            <div>
              <p className="font-bold text-sm text-white">
                {mode === 'encrypt' ? '✓ File Secured & Downloaded' : '✓ File Decrypted & Downloaded'}
              </p>
              <p className="text-[11px] text-slate-300 mt-0.5">
                Processed via Argon2id + AES-256-GCM authenticated cipher pipeline.
              </p>
            </div>
          </motion.div>
        )}

        {/* Error */}
        {error && (
          <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/30 text-red-300 text-xs flex items-start gap-3">
            <ShieldAlert className="w-5 h-5 flex-shrink-0 mt-0.5" />
            <span>{error}</span>
          </div>
        )}
      </div>
    </div>
  );
};
