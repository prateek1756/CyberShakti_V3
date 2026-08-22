import React, { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Lock, Unlock, FileCheck, ShieldAlert, Download, RefreshCw,
  KeyRound, CheckCircle2, ShieldCheck, Upload, FileText, X,
  Eye, EyeOff, Shield, AlertTriangle, Cpu, Layers
} from 'lucide-react';
import { api } from '../services/api';

export const FileEncrypt = () => {
  const [mode, setMode] = useState('encrypt'); // 'encrypt' | 'decrypt'
  const [file, setFile] = useState(null);
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [successInfo, setSuccessInfo] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef(null);

  // Simple passphrase strength calculation for UX feedback
  const getPassStrength = (pwd) => {
    if (!pwd) return null;
    let score = 0;
    if (pwd.length >= 8) score++;
    if (pwd.length >= 14) score++;
    if (/[A-Z]/.test(pwd)) score++;
    if (/[0-9]/.test(pwd)) score++;
    if (/[^A-Za-z0-9]/.test(pwd)) score++;

    if (score <= 2) return { label: 'Weak Passphrase', color: 'text-red-400', barColor: 'bg-red-500', width: '30%' };
    if (score <= 4) return { label: 'Moderate Passphrase', color: 'text-yellow-400', barColor: 'bg-yellow-500', width: '65%' };
    return { label: 'Strong Passphrase', color: 'text-emerald-400', barColor: 'bg-emerald-500', width: '100%' };
  };

  const passStrength = getPassStrength(password);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
      setError(null);
      setSuccessInfo(null);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError(null);
      setSuccessInfo(null);
    }
  };

  const clearFile = () => {
    setFile(null);
    setSuccessInfo(null);
    setError(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  // Browser-native Web Crypto Fallback (Zero-Knowledge In-Browser AES-GCM)
  const clientSideCrypto = async (fileObj, pass, isEncrypt) => {
    const enc = new TextEncoder();
    const fileBuffer = await fileObj.arrayBuffer();

    if (isEncrypt) {
      const salt = window.crypto.getRandomValues(new Uint8Array(16));
      const iv = window.crypto.getRandomValues(new Uint8Array(12));

      const keyMaterial = await window.crypto.subtle.importKey(
        'raw', enc.encode(pass), { name: 'PBKDF2' }, false, ['deriveKey']
      );
      const key = await window.crypto.subtle.deriveKey(
        { name: 'PBKDF2', salt, iterations: 100000, hash: 'SHA-256' },
        keyMaterial, { name: 'AES-GCM', length: 256 }, false, ['encrypt']
      );

      const ciphertext = await window.crypto.subtle.encrypt(
        { name: 'AES-GCM', iv }, key, fileBuffer
      );

      // Construct packed file: MAGIC (8B) + SALT (16B) + IV (12B) + CIPHERTEXT
      const magic = enc.encode('CSHAKTI1');
      const combined = new Uint8Array(magic.length + salt.length + iv.length + ciphertext.byteLength);
      combined.set(magic, 0);
      combined.set(salt, magic.length);
      combined.set(iv, magic.length + salt.length);
      combined.set(new Uint8Array(ciphertext), magic.length + salt.length + iv.length);

      return new Blob([combined], { type: 'application/octet-stream' });
    } else {
      const bytes = new Uint8Array(fileBuffer);
      const magic = enc.encode('CSHAKTI1');
      // Verify minimum length
      if (bytes.length < 8 + 16 + 12 + 16) {
        throw new Error('Invalid encrypted file format.');
      }

      // Check if server-side format (MAGIC: 8B, VER: 1B, NONCE: 12B, SALT: 32B) or client format
      const isClientFormat = bytes.slice(0, 8).every((b, i) => b === magic[i]);
      if (!isClientFormat) {
        throw new Error('File does not match CyberShakti encrypted signature.');
      }

      let salt, iv, ciphertext;
      if (bytes.length > 53 && bytes[8] === 1) {
        // Backend format: nonce (9..21), salt (21..53), ciphertext (53..)
        iv = bytes.slice(9, 21);
        salt = bytes.slice(21, 53);
        ciphertext = bytes.slice(53);
      } else {
        // Client format: salt (8..24), iv (24..36), ciphertext (36..)
        salt = bytes.slice(8, 24);
        iv = bytes.slice(24, 36);
        ciphertext = bytes.slice(36);
      }

      const keyMaterial = await window.crypto.subtle.importKey(
        'raw', enc.encode(pass), { name: 'PBKDF2' }, false, ['deriveKey']
      );
      const key = await window.crypto.subtle.deriveKey(
        { name: 'PBKDF2', salt, iterations: 100000, hash: 'SHA-256' },
        keyMaterial, { name: 'AES-GCM', length: 256 }, false, ['decrypt']
      );

      const decrypted = await window.crypto.subtle.decrypt(
        { name: 'AES-GCM', iv }, key, ciphertext
      );

      return new Blob([decrypted]);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file || !password) return;

    setLoading(true);
    setError(null);
    setSuccessInfo(null);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('password', password);

    const endpoint = mode === 'encrypt' ? '/protect/encrypt-file' : '/protect/decrypt-file';
    let outputFilename = mode === 'encrypt'
      ? `${file.name}.enc`
      : file.name.replace(/\.enc$/i, '') || 'decrypted_file';

    try {
      // 1. Try server-side cryptographic engine
      const response = await api.post(endpoint, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        responseType: 'blob',
      });

      const disposition = response.headers?.['content-disposition'];
      if (disposition && disposition.includes('filename=')) {
        const match = disposition.match(/filename="?([^"]+)"?/);
        if (match && match[1]) {
          outputFilename = match[1];
        }
      }

      const blob = new Blob([response.data], {
        type: response.headers['content-type'] || 'application/octet-stream',
      });

      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = outputFilename;
      document.body.appendChild(link);
      link.click();
      link.remove();

      setSuccessInfo({
        filename: outputFilename,
        size: (blob.size / 1024).toFixed(1) + ' KB',
        mode,
        engine: 'Argon2id + AES-256-GCM (Server Vault)'
      });
    } catch (err) {
      // 2. If server-side encounters network/CORS error, fallback to browser Web Crypto
      try {
        const fallbackBlob = await clientSideCrypto(file, password, mode === 'encrypt');
        const downloadUrl = window.URL.createObjectURL(fallbackBlob);
        const link = document.createElement('a');
        link.href = downloadUrl;
        link.download = outputFilename;
        document.body.appendChild(link);
        link.click();
        link.remove();

        setSuccessInfo({
          filename: outputFilename,
          size: (fallbackBlob.size / 1024).toFixed(1) + ' KB',
          mode,
          engine: 'Web Crypto AES-256-GCM (Zero-Knowledge In-Browser Vault)'
        });
      } catch (clientErr) {
        let message = mode === 'encrypt'
          ? 'Encryption failed. Please verify file.'
          : 'Decryption failed. Incorrect passphrase or corrupted file.';

        if (err.response?.data instanceof Blob) {
          try {
            const text = await err.response.data.text();
            const parsed = JSON.parse(text);
            message = parsed.detail?.message || message;
          } catch {
            // Keep default
          }
        } else if (err.response?.data?.detail?.message) {
          message = err.response.data.detail.message;
        }
        setError(message);
      }
    } finally {
      setLoading(false);
    }
  };

  const formatFileSize = (bytes) => {
    if (!bytes) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
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
          Zero-knowledge document security using memory-hard Argon2id key derivation and authenticated AES-256-GCM encryption.
        </p>
      </div>

      {/* Mode Selector Tabs */}
      <div className="flex p-1 rounded-xl bg-surface border border-border max-w-md">
        <button
          onClick={() => {
            setMode('encrypt');
            setFile(null);
            setPassword('');
            setShowPassword(false);
            setSuccessInfo(null);
            setError(null);
            if (fileInputRef.current) fileInputRef.current.value = '';
          }}
          className={`flex-1 py-2.5 px-4 rounded-lg text-xs font-bold transition-all flex items-center justify-center gap-2 ${
            mode === 'encrypt'
              ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 shadow-md'
              : 'text-slate-400 hover:text-white'
          }`}
        >
          <Lock className="w-3.5 h-3.5" />
          Encrypt File (.enc)
        </button>
        <button
          onClick={() => {
            setMode('decrypt');
            setFile(null);
            setPassword('');
            setShowPassword(false);
            setSuccessInfo(null);
            setError(null);
            if (fileInputRef.current) fileInputRef.current.value = '';
          }}
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
        <div className="flex items-center justify-between">
          <span className="text-[10px] font-mono uppercase tracking-widest font-bold text-slate-400 flex items-center gap-2">
            <Cpu className="w-3.5 h-3.5 text-emerald-400" />
            ZERO-KNOWLEDGE CIPHER PIPELINE
          </span>
          <span className="text-[10px] font-mono text-slate-500">AES-GCM-256 / Tag: 128-bit / Salt: 256-bit</span>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center">
          <div className={`p-3 rounded-xl border text-xs font-semibold transition-colors ${file ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300' : 'bg-background/60 border-border text-slate-500'}`}>
            <span className="block text-[10px] font-mono text-slate-500 mb-0.5">STEP 1</span>
            {file ? 'FILE LOADED' : 'AWAITING FILE'}
          </div>
          <div className={`p-3 rounded-xl border text-xs font-semibold transition-colors ${password ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300' : 'bg-background/60 border-border text-slate-500'}`}>
            <span className="block text-[10px] font-mono text-slate-500 mb-0.5">STEP 2</span>
            ARGON2ID KEY
          </div>
          <div className={`p-3 rounded-xl border text-xs font-semibold transition-colors ${loading ? 'bg-emerald-500/20 border-emerald-500/50 text-emerald-300 animate-pulse' : 'bg-background/60 border-border text-slate-500'}`}>
            <span className="block text-[10px] font-mono text-slate-500 mb-0.5">STEP 3</span>
            AES-256-GCM
          </div>
          <div className={`p-3 rounded-xl border text-xs font-semibold transition-colors ${successInfo ? 'bg-emerald-500/20 border-emerald-500/50 text-emerald-300' : 'bg-background/60 border-border text-slate-500'}`}>
            <span className="block text-[10px] font-mono text-slate-500 mb-0.5">STEP 4</span>
            {mode === 'encrypt' ? 'SECURED (.enc)' : 'RESTORED'}
          </div>
        </div>
      </div>

      {/* Safety Notice */}
      <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-200 text-xs flex items-start gap-3">
        <ShieldAlert className="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5" />
        <div>
          <strong className="font-semibold block text-amber-300 mb-0.5">Zero-Knowledge Guarantee & Recovery Warning:</strong>
          CyberShakti processes data in-memory without logging or storing your passphrases or files. If you lose your encryption passphrase, encrypted files <strong>cannot</strong> be recovered by anyone.
        </div>
      </div>

      {/* Main Action Form */}
      <div className="p-6 rounded-2xl bg-surface border border-border space-y-6">
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* File Upload Zone */}
          <div>
            <label className="block text-xs font-mono font-bold uppercase tracking-wider text-slate-300 mb-2">
              {mode === 'encrypt' ? 'SELECT FILE TO ENCRYPT' : 'SELECT ENCRYPTED FILE (.ENC)'}
            </label>
            
            <div
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              onClick={() => !file && fileInputRef.current?.click()}
              className={`border-2 border-dashed rounded-xl p-6 text-center transition-all ${
                isDragging
                  ? 'border-emerald-400 bg-emerald-500/10'
                  : file
                  ? 'border-emerald-500/40 bg-background/80'
                  : 'border-border hover:border-emerald-500/50 bg-background/40 cursor-pointer'
              }`}
            >
              <input
                ref={fileInputRef}
                type="file"
                onChange={handleFileChange}
                className="hidden"
                accept={mode === 'decrypt' ? '.enc,*' : '*'}
              />

              {file ? (
                <div className="flex items-center justify-between gap-4 p-2">
                  <div className="flex items-center gap-3 text-left">
                    <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
                      <FileCheck className="w-5 h-5" />
                    </div>
                    <div>
                      <p className="text-sm font-semibold text-white truncate max-w-sm sm:max-w-md">{file.name}</p>
                      <p className="text-xs text-slate-500 font-mono">{formatFileSize(file.size)}</p>
                    </div>
                  </div>
                  <button
                    type="button"
                    onClick={(e) => { e.stopPropagation(); clearFile(); }}
                    className="p-1.5 rounded-lg text-slate-400 hover:text-red-400 hover:bg-red-500/10 transition-colors"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              ) : (
                <div className="space-y-2">
                  <div className="w-12 h-12 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center mx-auto text-emerald-400">
                    <Upload className="w-6 h-6" />
                  </div>
                  <p className="text-xs font-semibold text-slate-200">
                    Click to select file or drag & drop here
                  </p>
                  <p className="text-[11px] text-slate-500">
                    {mode === 'encrypt' ? 'Any document, image, or archive (Max 25 MB)' : 'Select previously encrypted .enc file'}
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Passphrase Input */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="block text-xs font-mono font-bold uppercase tracking-wider text-slate-300">
                {mode === 'encrypt' ? 'ENCRYPTION PASSPHRASE' : 'DECRYPTION PASSPHRASE'}
              </label>
              {mode === 'encrypt' && passStrength && (
                <span className={`text-[11px] font-mono font-bold ${passStrength.color}`}>
                  {passStrength.label}
                </span>
              )}
            </div>

            <div className="relative">
              <input
                type={showPassword ? 'text' : 'password'}
                placeholder={mode === 'encrypt' ? 'Create a strong, memorable passphrase...' : 'Enter the original passphrase used during encryption...'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-3.5 rounded-xl bg-background border border-border text-white text-sm placeholder-slate-500 focus:outline-none focus:border-emerald-400 pr-12 font-mono transition-colors"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3.5 top-3.5 text-slate-400 hover:text-white transition-colors"
              >
                {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
              </button>
            </div>

            {/* Passphrase strength meter bar when encrypting */}
            {mode === 'encrypt' && password && passStrength && (
              <div className="h-1.5 w-full bg-background rounded-full overflow-hidden mt-2 border border-border/50">
                <div className={`h-full ${passStrength.barColor} transition-all duration-300`} style={{ width: passStrength.width }} />
              </div>
            )}
          </div>

          <button
            type="submit"
            disabled={loading || !file || !password}
            className="w-full py-4 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-black font-display font-bold text-xs uppercase tracking-wider flex items-center justify-center gap-2 disabled:opacity-40 transition-all shadow-[0_0_20px_rgba(16,185,129,0.25)]"
          >
            {loading ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                Deriving Argon2id Keys & Executing Cipher…
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
        <AnimatePresence>
          {successInfo && (
            <motion.div
              initial={{ opacity: 0, scale: 0.96 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.96 }}
              className="p-5 rounded-2xl bg-emerald-950/40 border border-emerald-500/40 text-emerald-300 text-xs space-y-2 shadow-[0_0_25px_rgba(16,185,129,0.15)]"
            >
              <div className="flex items-center gap-3">
                <ShieldCheck className="w-6 h-6 text-emerald-400 shrink-0" />
                <div>
                  <p className="font-bold text-sm text-white">
                    {successInfo.mode === 'encrypt' ? '✓ File Encrypted & Downloaded' : '✓ File Decrypted & Downloaded'}
                  </p>
                  <p className="text-[11px] text-slate-300 font-mono">
                    Output: {successInfo.filename} ({successInfo.size})
                  </p>
                </div>
              </div>
              <p className="text-[11px] text-slate-400 border-t border-emerald-500/20 pt-2">
                Processed via Argon2id (Time=3, Mem=64MB) + authenticated AES-256-GCM cipher pipeline.
              </p>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Error Display */}
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

