import React, { useState } from 'react';
import { Lock, Unlock, FileCheck, ShieldAlert, Download, Loader2 } from 'lucide-react';
import { api } from '../services/api';

export const FileEncrypt = () => {
  const [mode, setMode] = useState('encrypt'); // 'encrypt' or 'decrypt'
  const [file, setFile] = useState(null);
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file || !password) return;

    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('password', password);

    const endpoint = mode === 'encrypt' ? '/protect/encrypt-file' : '/protect/decrypt-file';

    try {
      const response = await api.post(endpoint, formData, {
        responseType: 'blob',
      });

      // Trigger browser download
      const blob = new Blob([response.data]);
      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = mode === 'encrypt' ? `${file.name}.enc` : file.name.replace('.enc', '');
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      setError(mode === 'encrypt' ? 'Encryption failed.' : 'Decryption failed. Verify password.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto px-4 py-8 space-y-8">
      {/* Header */}
      <div className="space-y-2">
        <h1 className="text-3xl font-extrabold text-white flex items-center gap-3">
          <Lock className="w-8 h-8 text-emerald-400" />
          Secure File Encryption & Decryption
        </h1>
        <p className="text-slate-300 text-sm">
          Encrypt sensitive documents using client-password derived Argon2id keys and AES-256-GCM authenticated encryption.
        </p>
      </div>

      {/* Mode Toggle Tabs */}
      <div className="flex border-b border-border">
        <button
          onClick={() => setMode('encrypt')}
          className={`px-5 py-3 text-sm font-semibold flex items-center gap-2 border-b-2 transition-all ${
            mode === 'encrypt' ? 'border-emerald-400 text-emerald-400' : 'border-transparent text-slate-400 hover:text-white'
          }`}
        >
          <Lock className="w-4 h-4" />
          Encrypt File
        </button>
        <button
          onClick={() => setMode('decrypt')}
          className={`px-5 py-3 text-sm font-semibold flex items-center gap-2 border-b-2 transition-all ${
            mode === 'decrypt' ? 'border-emerald-400 text-emerald-400' : 'border-transparent text-slate-400 hover:text-white'
          }`}
        >
          <Unlock className="w-4 h-4" />
          Decrypt File
        </button>
      </div>

      {/* Warning Box */}
      <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-200 text-xs flex items-start gap-2.5">
        <ShieldAlert className="w-4 h-4 text-amber-400 flex-shrink-0 mt-0.5" />
        <div>
          <strong className="font-semibold block text-amber-300 mb-0.5">Password-Loss Warning:</strong>
          CyberShakti does not store your encryption password or plaintext files. If you forget your password, your encrypted files cannot be recovered.
        </div>
      </div>

      {/* Form */}
      <div className="p-6 rounded-2xl bg-surface border border-border space-y-6">
        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label className="block text-sm font-medium text-slate-200 mb-2">
              Select File to {mode === 'encrypt' ? 'Encrypt' : 'Decrypt'}
            </label>
            <input
              type="file"
              onChange={(e) => setFile(e.target.files[0])}
              className="w-full text-sm text-slate-300 file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-slate-700 file:text-white hover:file:bg-slate-600 cursor-pointer"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-200 mb-2">Encryption Password</label>
            <input
              type="password"
              placeholder="Enter strong password..."
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-3 rounded-xl bg-background border border-border text-white placeholder-slate-500 focus:outline-none focus:border-emerald-400 transition-colors"
            />
          </div>

          <button
            type="submit"
            disabled={loading || !file || !password}
            className="w-full py-3 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-semibold flex items-center justify-center gap-2 disabled:opacity-50 transition-all"
          >
            {loading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <>
                <Download className="w-4 h-4" />
                {mode === 'encrypt' ? 'Encrypt and Download' : 'Decrypt and Download'}
              </>
            )}
          </button>
        </form>
      </div>
    </div>
  );
};
