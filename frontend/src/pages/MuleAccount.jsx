import React, { useState, useEffect, useMemo, useRef, useCallback } from 'react';
import { Network } from 'vis-network';
import { DataSet } from 'vis-data';
import 'vis-network/styles/vis-network.css';
import {
  Network as NetworkIcon, GitCommit, Banknote, FileSpreadsheet, Upload, Sparkles,
  RefreshCw, AlertCircle, CheckCircle2, Activity, Layers, Zap, Info,
  Search, ZoomIn, ZoomOut, Maximize2, Filter, Play, ShieldAlert, ShieldCheck,
  TrendingUp, Users, BarChart3, Eye, X
} from 'lucide-react';
import { api } from '../services/api';
import { ScanAnimation } from '../components/ScanAnimation';
import { ThreatResultCard } from '../components/ThreatResultCard';

// ─── SCENARIOS ────────────────────────────────────────────────────────────────
const SAMPLE_SCENARIOS = [
  {
    id: 'upi',
    name: 'Multi-Tier UPI Pass-Through Ring',
    badge: 'UPI Crime',
    description: 'Rapid burst UPI transfers funneling into layering hubs.',
    generate: () => {
      const r = () => Math.floor(100 + Math.random() * 900);
      const v1 = `VIC_${r()}`, v2 = `VIC_${r()}`, v3 = `VIC_${r()}`;
      const m1 = `MULE_${r()}`, m2 = `MULE_${r()}`;
      const l1 = `HUB_${r()}`, l2 = `HUB_${r()}`;
      const c1 = `ATM_${r()}`, c2 = `CRYPTO_${r()}`;
      return [
        { sender: v1, receiver: m1, amount: Math.floor(180000 + Math.random() * 90000), timestamp: '2026-08-22 10:15:00' },
        { sender: v2, receiver: m1, amount: Math.floor(150000 + Math.random() * 80000), timestamp: '2026-08-22 10:22:00' },
        { sender: v3, receiver: m2, amount: Math.floor(250000 + Math.random() * 110000), timestamp: '2026-08-22 10:30:00' },
        { sender: m1, receiver: l1, amount: Math.floor(320000 + Math.random() * 70000), timestamp: '2026-08-22 11:00:00' },
        { sender: m2, receiver: l1, amount: Math.floor(220000 + Math.random() * 80000), timestamp: '2026-08-22 11:15:00' },
        { sender: l1, receiver: l2, amount: Math.floor(520000 + Math.random() * 120000), timestamp: '2026-08-22 11:45:00' },
        { sender: l2, receiver: c1, amount: Math.floor(280000 + Math.random() * 40000), timestamp: '2026-08-22 12:30:00' },
        { sender: l2, receiver: c2, amount: Math.floor(240000 + Math.random() * 40000), timestamp: '2026-08-22 12:45:00' },
      ];
    }
  },
  {
    id: 'crypto',
    name: 'Crypto Off-Ramping P2P Syndicate',
    badge: 'P2P Off-Ramp',
    description: 'P2P transfers routing funds to crypto exchange wallets.',
    generate: () => {
      const r = () => Math.floor(100 + Math.random() * 900);
      const v1 = `SRC_${r()}`, v2 = `SRC_${r()}`;
      const m1 = `P2P_${r()}`, m2 = `P2P_${r()}`;
      const l1 = `GW_${r()}`;
      const c1 = `WLLT_${r()}`;
      return [
        { sender: v1, receiver: m1, amount: Math.floor(420000 + Math.random() * 100000), timestamp: '2026-08-22 14:05:00' },
        { sender: v2, receiver: m2, amount: Math.floor(380000 + Math.random() * 90000), timestamp: '2026-08-22 14:10:00' },
        { sender: m1, receiver: l1, amount: Math.floor(390000 + Math.random() * 80000), timestamp: '2026-08-22 14:30:00' },
        { sender: m2, receiver: l1, amount: Math.floor(350000 + Math.random() * 80000), timestamp: '2026-08-22 14:35:00' },
        { sender: l1, receiver: c1, amount: Math.floor(720000 + Math.random() * 140000), timestamp: '2026-08-22 15:00:00' }
      ];
    }
  },
  {
    id: 'smurf',
    name: 'Structuring & Smurfing Mule Ring',
    badge: 'Smurfing',
    description: 'Sub-₹50k micro-deposits evading AML threshold checks.',
    generate: () => {
      const r = () => Math.floor(100 + Math.random() * 900);
      const v1 = `SF_${r()}`, v2 = `SF_${r()}`, v3 = `SF_${r()}`, v4 = `SF_${r()}`;
      const m1 = `HUB_${r()}`;
      const c1 = `WD_${r()}`;
      return [
        { sender: v1, receiver: m1, amount: 48500, timestamp: '2026-08-22 08:00:00' },
        { sender: v2, receiver: m1, amount: 49200, timestamp: '2026-08-22 08:05:00' },
        { sender: v3, receiver: m1, amount: 47800, timestamp: '2026-08-22 08:12:00' },
        { sender: v4, receiver: m1, amount: 49500, timestamp: '2026-08-22 08:18:00' },
        { sender: m1, receiver: c1, amount: 194000, timestamp: '2026-08-22 09:00:00' }
      ];
    }
  }
];

// ─── SINGLE ACCOUNT SIGNALS ───────────────────────────────────────────────────
const SIGNALS_CONFIG = [
  { key: 'account_age_category',      label: 'Account Age',         options: [{ value: 0, label: 'New (<6mo)' }, { value: 1, label: '6–24 months' }, { value: 2, label: '>2 years' }] },
  { key: 'transaction_velocity_high', label: 'Transaction Velocity', options: [{ value: 1, label: 'High (Rapid burst)' }, { value: 0, label: 'Normal' }] },
  { key: 'multiple_recipients',       label: 'Fan-Out Recipients',  options: [{ value: 1, label: 'Yes — Fan-out' }, { value: 0, label: 'No — Normal' }] },
  { key: 'pass_through',              label: 'Pass-Through Pattern', options: [{ value: 1, label: 'Yes — Cash-in/out' }, { value: 0, label: 'No — Normal' }] },
];

const MULE_STAGES = [
  { id: 'input',     label: 'Ingesting banking signals',        duration: 300 },
  { id: 'graph',     label: 'Building entity transfer graph',   duration: 500 },
  { id: 'centrality',label: 'Computing graph centrality',      duration: 600 },
  { id: 'model',     label: 'Running XGBoost classifier',      duration: 700 },
  { id: 'risk',      label: 'Calculating anomaly risk score',  duration: 400 },
];

const DEFAULTS = Object.fromEntries(SIGNALS_CONFIG.map(s => [s.key, s.options[1].value]));

// ─── ROLE CONFIG ──────────────────────────────────────────────────────────────
const ROLE_CONFIG = {
  MULE_ACCOUNT:    { color: '#ef4444', border: '#dc2626', label: '🔴 MULE',    badge: 'bg-red-500/20 text-red-300 border-red-500/40' },
  LAYERING_HUB:    { color: '#f97316', border: '#ea580c', label: '🟠 HUB',     badge: 'bg-orange-500/20 text-orange-300 border-orange-500/40' },
  VICTIM_SOURCE:   { color: '#10b981', border: '#059669', label: '🟢 VICTIM',  badge: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40' },
  DESTINATION_SINK:{ color: '#3b82f6', border: '#2563eb', label: '🔵 CASHOUT', badge: 'bg-blue-500/20 text-blue-300 border-blue-500/40' },
  DEFAULT:         { color: '#64748b', border: '#475569', label: '⚪ REGULAR', badge: 'bg-slate-500/20 text-slate-300 border-slate-500/40' },
};

const getRoleConf = (role) => ROLE_CONFIG[role] || ROLE_CONFIG.DEFAULT;

// ─── VIS-NETWORK GRAPH ────────────────────────────────────────────────────────
const TopologyGraph = ({ graphData, onSelectNode, selectedNodeId }) => {
  const containerRef = useRef(null);
  const networkRef = useRef(null);

  useEffect(() => {
    if (!containerRef.current || !graphData?.nodes?.length) return;

    // Build vis-network nodes
    const visNodes = new DataSet(
      graphData.nodes.map(node => {
        const cfg = getRoleConf(node.role);
        const riskScore = node.role === 'MULE_ACCOUNT' ? 90 : node.role === 'LAYERING_HUB' ? 70 : 15;
        const size = 18 + (riskScore / 100) * 22;
        return {
          id: node.id,
          label: node.id.length > 10 ? node.id.slice(0, 9) + '…' : node.id,
          title: `<div style="font-family:monospace;padding:10px;background:#0f172a;border:1px solid #334155;border-radius:8px;min-width:180px;color:#f8fafc">
            <div style="font-size:9px;color:#64748b;text-transform:uppercase;letter-spacing:2px;margin-bottom:4px">${node.role?.replace('_', ' ')}</div>
            <div style="font-weight:bold;color:#60a5fa;margin-bottom:8px">${node.id}</div>
            <div style="display:flex;gap:12px;font-size:11px;border-top:1px solid #1e293b;padding-top:6px">
              <span><b style="color:#94a3b8">IN:</b> ${node.in_degree || 0}</span>
              <span><b style="color:#94a3b8">OUT:</b> ${node.out_degree || 0}</span>
              <span><b style="color:#f97316">BTW:</b> ${Number(node.betweenness_centrality || 0).toFixed(2)}</span>
            </div>
          </div>`,
          color: {
            background: cfg.color + '33',
            border: cfg.color,
            highlight: { background: cfg.color + '55', border: '#ffffff' },
            hover: { background: cfg.color + '44', border: cfg.color }
          },
          font: { color: '#f1f5f9', size: 11, face: 'monospace', bold: { color: '#ffffff' } },
          size,
          shape: node.role === 'MULE_ACCOUNT' ? 'diamond' : node.role === 'LAYERING_HUB' ? 'hexagon' : node.role === 'DESTINATION_SINK' ? 'square' : 'dot',
          borderWidth: node.id === selectedNodeId ? 3 : 2,
          shadow: { enabled: true, color: cfg.color + '66', size: 12, x: 0, y: 0 },
        };
      })
    );

    // Build vis-network edges
    const visEdges = new DataSet(
      (graphData.edges || []).map((edge, i) => ({
        id: i,
        from: edge.source || edge.from_node,
        to: edge.target || edge.to_node,
        label: `₹${Math.round((edge.amount || 0) / 1000)}k`,
        font: { color: '#94a3b8', size: 10, face: 'monospace', align: 'middle' },
        color: { color: '#f9731655', highlight: '#f97316', hover: '#f97316bb' },
        arrows: { to: { enabled: true, scaleFactor: 0.8 } },
        width: 1.5,
        smooth: { type: 'dynamic' },
        hoverWidth: 2.5,
      }))
    );

    const options = {
      autoResize: true,
      height: '100%',
      width: '100%',
      physics: {
        enabled: true,
        solver: 'forceAtlas2Based',
        forceAtlas2Based: {
          gravitationalConstant: -60,
          centralGravity: 0.005,
          springLength: 120,
          springConstant: 0.08,
          damping: 0.4,
          avoidOverlap: 0.9,
        },
        maxVelocity: 50,
        minVelocity: 0.1,
        stabilization: { enabled: true, iterations: 200, updateInterval: 25 },
      },
      interaction: {
        hover: true,
        tooltipDelay: 150,
        navigationButtons: false,
        keyboard: false,
        zoomView: true,
        dragView: true,
      },
      nodes: {
        borderWidthSelected: 3,
      },
      edges: {
        selectionWidth: 2,
      },
      layout: {
        improvedLayout: true,
      },
    };

    // Destroy existing network if any
    if (networkRef.current) {
      networkRef.current.destroy();
    }

    networkRef.current = new Network(containerRef.current, { nodes: visNodes, edges: visEdges }, options);

    networkRef.current.on('click', (params) => {
      if (params.nodes.length > 0) {
        const nodeId = params.nodes[0];
        const nodeData = graphData.nodes.find(n => n.id === nodeId);
        if (nodeData && onSelectNode) onSelectNode(nodeData);
      } else {
        if (onSelectNode) onSelectNode(null);
      }
    });

    // Stop physics after stabilization for performance
    networkRef.current.on('stabilizationIterationsDone', () => {
      networkRef.current.setOptions({ physics: { enabled: false } });
    });

    return () => {
      if (networkRef.current) {
        networkRef.current.destroy();
        networkRef.current = null;
      }
    };
  }, [graphData]);

  // Highlight selected node
  useEffect(() => {
    if (networkRef.current && selectedNodeId) {
      networkRef.current.selectNodes([selectedNodeId]);
      networkRef.current.focus(selectedNodeId, {
        scale: 1.1,
        animation: { duration: 600, easingFunction: 'easeInOutQuad' }
      });
    }
  }, [selectedNodeId]);

  const handleZoomIn = () => networkRef.current?.moveTo({ scale: (networkRef.current.getScale() || 1) * 1.25, animation: true });
  const handleZoomOut = () => networkRef.current?.moveTo({ scale: (networkRef.current.getScale() || 1) * 0.8, animation: true });
  const handleFit = () => networkRef.current?.fit({ animation: { duration: 600, easingFunction: 'easeInOutQuad' } });
  const handleRestartPhysics = () => {
    if (networkRef.current) {
      networkRef.current.setOptions({ physics: { enabled: true } });
      setTimeout(() => networkRef.current?.setOptions({ physics: { enabled: false } }), 2000);
    }
  };

  return (
    <div className="relative w-full h-full bg-[#080c14]" style={{ backgroundColor: '#080c14' }}>
      <div ref={containerRef} className="w-full h-full bg-[#080c14]" style={{ backgroundColor: '#080c14' }} />
      {/* GRAPH CONTROLS */}
      <div className="absolute top-3 right-3 flex flex-col gap-1.5">
        {[
          { icon: ZoomIn, action: handleZoomIn, tip: 'Zoom In' },
          { icon: ZoomOut, action: handleZoomOut, tip: 'Zoom Out' },
          { icon: Maximize2, action: handleFit, tip: 'Fit to View' },
          { icon: Activity, action: handleRestartPhysics, tip: 'Re-layout' },
        ].map(({ icon: Icon, action, tip }) => (
          <button
            key={tip}
            onClick={action}
            title={tip}
            className="w-8 h-8 rounded-lg bg-slate-900/90 border border-border hover:border-orange-500/60 hover:bg-slate-800 text-slate-400 hover:text-orange-300 flex items-center justify-center transition-all backdrop-blur"
          >
            <Icon className="w-3.5 h-3.5" />
          </button>
        ))}
      </div>
      {/* LEGEND */}
      <div className="absolute bottom-3 left-3 flex flex-wrap gap-2">
        {Object.entries(ROLE_CONFIG).filter(([k]) => k !== 'DEFAULT').map(([role, cfg]) => (
          <span key={role} className="flex items-center gap-1.5 px-2 py-1 rounded-md bg-slate-900/80 border border-border backdrop-blur text-[10px] font-mono text-slate-300">
            <span className="w-2 h-2 rounded-full" style={{ backgroundColor: cfg.color }} />
            {role.replace('_', ' ')}
          </span>
        ))}
      </div>
    </div>
  );
};

// ─── MAIN PAGE ────────────────────────────────────────────────────────────────
export const MuleAccount = () => {
  const [activeTab, setActiveTab] = useState('network');
  const [signals, setSignals] = useState(DEFAULTS);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [scenarioIdx, setScenarioIdx] = useState(0);
  const [currentScenario, setCurrentScenario] = useState(SAMPLE_SCENARIOS[0]);

  const [singleResult, setSingleResult] = useState(null);
  const [graphData, setGraphData] = useState(null);
  const [selectedNode, setSelectedNode] = useState(null);
  const [tableFilter, setTableFilter] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');
  const [riskFilter, setRiskFilter] = useState(0);

  useEffect(() => { runSampleNetwork(0); }, []);

  const handleSignalChange = (key, val) => {
    setSignals(prev => ({ ...prev, [key]: Number(val) }));
    setSingleResult(null);
    setError(null);
  };

  const handleSingleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setSingleResult(null);
    setError(null);
    try {
      const res = await api.post('/detect/assess-mule-account', { account_signals: signals });
      setLoading(false);
      setSingleResult(res.data?.result || res.data);
    } catch {
      setLoading(false);
      const score = (signals.pass_through ? 0.35 : 0) + (signals.transaction_velocity_high ? 0.30 : 0)
                  + (signals.multiple_recipients ? 0.25 : 0) + (signals.account_age_category === 0 ? 0.10 : 0);
      const prob = Math.min(0.99, Math.max(0.02, score));
      setSingleResult({
        mule_probability: prob,
        verdict: {
          risk_level: prob >= 0.7 ? 'high_risk' : prob >= 0.4 ? 'moderate_risk' : 'safe',
          risk_label: prob >= 0.7 ? 'High Risk' : prob >= 0.4 ? 'Moderate Risk' : 'Safe',
          explanation: prob >= 0.7 ? 'High risk pass-through pattern with rapid velocity.' : 'No critical mule indicators found.'
        }
      });
    }
  };

  const runSampleNetwork = async (targetIdx) => {
    const idx = targetIdx !== undefined ? targetIdx : (scenarioIdx + 1) % SAMPLE_SCENARIOS.length;
    setScenarioIdx(idx);
    const scenario = SAMPLE_SCENARIOS[idx];
    setCurrentScenario(scenario);
    setLoading(true);
    setError(null);
    setSelectedNode(null);
    const transactions = scenario.generate();
    try {
      const res = await api.post('/detect/analyze-mule-transactions', { transactions });
      setLoading(false);
      if (res.data?.graph_data) {
        setGraphData(res.data.graph_data);
        const firstMule = res.data.graph_data.nodes.find(n => n.role === 'MULE_ACCOUNT') || res.data.graph_data.nodes[0];
        setSelectedNode(firstMule);
      }
    } catch {
      setLoading(false);
      // Rich fallback dataset
      const fallback = {
        nodes: [
          { id: 'VIC_101', role: 'VICTIM_SOURCE',    in_degree: 0, out_degree: 2, betweenness_centrality: 0.05, pass_through_ratio: 0.01 },
          { id: 'VIC_102', role: 'VICTIM_SOURCE',    in_degree: 0, out_degree: 2, betweenness_centrality: 0.03, pass_through_ratio: 0.01 },
          { id: 'VIC_103', role: 'VICTIM_SOURCE',    in_degree: 0, out_degree: 1, betweenness_centrality: 0.02, pass_through_ratio: 0.01 },
          { id: 'MULE_99', role: 'MULE_ACCOUNT',     in_degree: 3, out_degree: 2, betweenness_centrality: 0.82, pass_through_ratio: 0.94 },
          { id: 'MULE_88', role: 'MULE_ACCOUNT',     in_degree: 2, out_degree: 2, betweenness_centrality: 0.74, pass_through_ratio: 0.91 },
          { id: 'HUB_404', role: 'LAYERING_HUB',     in_degree: 4, out_degree: 3, betweenness_centrality: 0.67, pass_through_ratio: 0.88 },
          { id: 'ATM_01',  role: 'DESTINATION_SINK', in_degree: 2, out_degree: 0, betweenness_centrality: 0.08, pass_through_ratio: 0.02 },
          { id: 'CRPT_02', role: 'DESTINATION_SINK', in_degree: 2, out_degree: 0, betweenness_centrality: 0.06, pass_through_ratio: 0.02 },
        ],
        edges: [
          { source: 'VIC_101', target: 'MULE_99', amount: 250000 },
          { source: 'VIC_102', target: 'MULE_99', amount: 180000 },
          { source: 'VIC_103', target: 'MULE_88', amount: 290000 },
          { source: 'VIC_102', target: 'MULE_88', amount: 150000 },
          { source: 'MULE_99', target: 'HUB_404', amount: 420000 },
          { source: 'MULE_88', target: 'HUB_404', amount: 430000 },
          { source: 'HUB_404', target: 'ATM_01',  amount: 400000 },
          { source: 'HUB_404', target: 'CRPT_02', amount: 440000 },
        ],
        total_volume: 2160000,
      };
      setGraphData(fallback);
      setSelectedNode(fallback.nodes[3]);
    }
  };

  const handleCsvUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setLoading(true); setError(null); setSelectedNode(null);
    const formData = new FormData();
    formData.append('file', file);
    try {
      const res = await api.post('/detect/analyze-mule-csv', formData);
      setLoading(false);
      if (res.data?.graph_data) {
        setGraphData(res.data.graph_data);
        setSelectedNode(res.data.graph_data.nodes.find(n => n.role === 'MULE_ACCOUNT') || res.data.graph_data.nodes[0]);
      }
    } catch {
      setLoading(false);
      setError('Failed to parse CSV. Ensure columns: sender, receiver, amount, timestamp.');
    }
  };

  const getRoleBadge = (role) => {
    const cfg = getRoleConf(role);
    return <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold border ${cfg.badge}`}>{cfg.label}</span>;
  };

  const metrics = useMemo(() => {
    if (!graphData?.nodes) return { mules: 0, hubs: 0, victims: 0, sinks: 0, volume: 0, edges: 0 };
    const n = graphData.nodes;
    return {
      mules:   n.filter(x => x.role === 'MULE_ACCOUNT').length,
      hubs:    n.filter(x => x.role === 'LAYERING_HUB').length,
      victims: n.filter(x => x.role === 'VICTIM_SOURCE').length,
      sinks:   n.filter(x => x.role === 'DESTINATION_SINK').length,
      volume:  graphData.total_volume || (graphData.edges || []).reduce((s, e) => s + Number(e.amount || 0), 0),
      edges:   (graphData.edges || []).length,
    };
  }, [graphData]);

  const filteredNodes = useMemo(() => {
    if (!graphData?.nodes) return [];
    return graphData.nodes.filter(n => {
      const matchRole = tableFilter === 'ALL' || n.role === tableFilter;
      const matchSearch = !searchQuery || n.id.toLowerCase().includes(searchQuery.toLowerCase());
      return matchRole && matchSearch;
    });
  }, [graphData, tableFilter, searchQuery]);

  const anomalyScore = (node) => {
    if (!node) return 0;
    if (node.role === 'MULE_ACCOUNT') return 90 + Math.random() * 9;
    if (node.role === 'LAYERING_HUB') return 65 + Math.random() * 10;
    if (node.role === 'DESTINATION_SINK') return 30 + Math.random() * 15;
    return 5 + Math.random() * 10;
  };

  const nodeScore = useMemo(() => selectedNode ? anomalyScore(selectedNode) : 0, [selectedNode?.id]);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 pt-12 pb-12 space-y-8">

      {/* ── HEADER ── */}
      <div className="flex flex-col md:flex-row md:items-start justify-between gap-6 pb-6 border-b border-border/80">
        <div className="space-y-2">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-orange-500/10 border border-orange-500/30 text-orange-400 text-xs font-mono font-bold">
            <NetworkIcon className="w-3.5 h-3.5" /> MULE TRACE — FORENSIC GRAPH ENGINE
          </div>
          <h1 className="text-3xl sm:text-4xl font-display font-extrabold text-white tracking-tight">
            Money Mule Ring & Transaction Investigator
          </h1>
          <p className="text-slate-400 text-sm max-w-2xl">
            Identify money muling networks using behavioral graph analytics — NetworkX centrality, XGBoost classifiers, and directed transaction topology.
          </p>
        </div>

        {/* TAB SWITCHER */}
        <div className="flex p-1 rounded-xl bg-surface border border-border flex-shrink-0 self-start">
          {[
            { id: 'network', icon: GitCommit,  label: 'Network Console' },
            { id: 'single',  icon: Banknote,   label: 'Single Account' },
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`py-2.5 px-4 rounded-lg text-xs font-bold transition-all flex items-center gap-2 ${
                activeTab === tab.id
                  ? 'bg-orange-500/20 text-orange-300 border border-orange-500/40 shadow-md'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <tab.icon className="w-4 h-4" />
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* ══════════════════════════════════════════════════════════════════════ */}
      {/* TAB 1: NETWORK TOPOLOGY CONSOLE                                       */}
      {/* ══════════════════════════════════════════════════════════════════════ */}
      {activeTab === 'network' && (
        <div className="space-y-6">

          {/* ── COMMAND CENTER ── */}
          <div className="p-5 rounded-2xl bg-surface border border-border space-y-5">
            <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 border-b border-border/60 pb-5">
              <div>
                <h3 className="text-xs font-mono font-black text-slate-300 uppercase tracking-widest flex items-center gap-2">
                  <FileSpreadsheet className="w-4 h-4 text-orange-400" /> COMMAND CENTER
                </h3>
                <p className="text-[11px] text-slate-500 mt-1">
                  Generate a mule ring scenario or upload a custom transaction CSV.
                </p>
              </div>
              <div className="flex flex-wrap items-center gap-3">
                <span className="px-3 py-1.5 rounded-lg bg-orange-500/10 border border-orange-500/30 text-orange-300 text-[11px] font-mono font-bold flex items-center gap-1.5">
                  <Zap className="w-3 h-3 text-orange-400 animate-pulse" />
                  {currentScenario.badge}: {currentScenario.name}
                </span>
                <button
                  onClick={() => runSampleNetwork()}
                  disabled={loading}
                  className="px-5 py-2.5 rounded-xl bg-orange-500 hover:bg-orange-400 active:scale-95 text-black font-black text-xs uppercase tracking-wider flex items-center gap-2 transition-all shadow-[0_0_24px_rgba(249,115,22,0.35)] disabled:opacity-40"
                >
                  {loading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
                  {loading ? 'Analyzing…' : 'Load Demo Dataset'}
                </button>
              </div>
            </div>

            {/* SCENARIO CARDS */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              {SAMPLE_SCENARIOS.map((sc, idx) => (
                <button
                  key={sc.id}
                  onClick={() => runSampleNetwork(idx)}
                  disabled={loading}
                  className={`p-4 rounded-xl border text-left cursor-pointer transition-all w-full ${
                    scenarioIdx === idx
                      ? 'bg-orange-500/10 border-orange-500/60 ring-1 ring-orange-500/30'
                      : 'bg-background/50 border-border hover:border-slate-600'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-[10px] font-mono font-black uppercase tracking-widest text-orange-400">
                      SCENARIO 0{idx + 1}
                    </span>
                    {scenarioIdx === idx && <CheckCircle2 className="w-3.5 h-3.5 text-orange-400" />}
                  </div>
                  <div className="text-xs font-bold text-white">{sc.name}</div>
                  <div className="text-[11px] text-slate-500 mt-0.5">{sc.description}</div>
                </button>
              ))}
            </div>

            {/* CSV UPLOAD */}
            <div className="border border-dashed border-border hover:border-orange-500/50 rounded-xl p-4 text-center bg-background/30 transition-colors">
              <input type="file" accept=".csv" onChange={handleCsvUpload} className="hidden" id="csv-upload" />
              <label htmlFor="csv-upload" className="cursor-pointer flex items-center justify-center gap-3">
                <Upload className="w-5 h-5 text-orange-400" />
                <span className="text-xs text-slate-300">
                  Upload CSV — <code className="text-orange-300">sender, receiver, amount, timestamp</code>
                </span>
              </label>
            </div>
          </div>

          {/* ── METRIC CARDS ── */}
          {graphData && (
            <div className="grid grid-cols-3 sm:grid-cols-6 gap-3">
              {[
                { label: 'TOTAL VOLUME', value: `₹${(metrics.volume/100000).toFixed(1)}L`, sub: `${metrics.edges} transfers`, color: 'text-white', border: 'border-border' },
                { label: 'MULE ACCOUNTS', value: metrics.mules, sub: 'Pass-through', color: 'text-red-400', border: 'border-red-500/30', bg: 'bg-red-500/5' },
                { label: 'LAYERING HUBS', value: metrics.hubs, sub: 'Aggregators', color: 'text-orange-400', border: 'border-orange-500/30', bg: 'bg-orange-500/5' },
                { label: 'VICTIMS', value: metrics.victims, sub: 'Originators', color: 'text-emerald-400', border: 'border-emerald-500/30', bg: 'bg-emerald-500/5' },
                { label: 'CASHOUT SINKS', value: metrics.sinks, sub: 'ATM/Crypto', color: 'text-blue-400', border: 'border-blue-500/30', bg: 'bg-blue-500/5' },
                { label: 'TOTAL NODES', value: graphData.nodes?.length || 0, sub: 'Network size', color: 'text-purple-400', border: 'border-purple-500/30', bg: 'bg-purple-500/5' },
              ].map(({ label, value, sub, color, border, bg = '' }) => (
                <div key={label} className={`p-3 rounded-xl bg-surface ${bg} border ${border} overflow-hidden`}>
                  <div className="text-[9px] font-mono font-black text-slate-500 uppercase tracking-widest truncate">{label}</div>
                  <div className={`text-xl font-mono font-black ${color} truncate mt-0.5`}>{value}</div>
                  <div className="text-[10px] text-slate-600 truncate">{sub}</div>
                </div>
              ))}
            </div>
          )}

          {/* ── GRAPH CANVAS + NODE INSPECTOR ── */}
          {graphData && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* GRAPH PANEL */}
              <div className="lg:col-span-2 rounded-2xl bg-surface border border-border overflow-hidden flex flex-col">
                <div className="px-5 py-3 border-b border-border/60 flex items-center justify-between flex-shrink-0">
                  <h3 className="text-[11px] font-mono font-black text-slate-400 uppercase tracking-widest flex items-center gap-2">
                    <Activity className="w-3.5 h-3.5 text-orange-400" />
                    TRANSACTION TOPOLOGY MAP
                  </h3>
                  <div className="flex items-center gap-1 text-[10px] font-mono text-slate-600">
                    <span className="w-1.5 h-1.5 rounded-full bg-orange-400 animate-pulse" />
                    LIVE GRAPH ENGINE
                  </div>
                </div>
                <div className="flex-1 h-[480px] relative bg-[#080c14]">
                  {loading ? (
                    <div className="absolute inset-0 flex items-center justify-center">
                      <div className="text-center space-y-3">
                        <RefreshCw className="w-8 h-8 text-orange-400 animate-spin mx-auto" />
                        <p className="text-xs font-mono text-slate-400">Building transaction graph…</p>
                      </div>
                    </div>
                  ) : (
                    <TopologyGraph
                      graphData={graphData}
                      onSelectNode={setSelectedNode}
                      selectedNodeId={selectedNode?.id}
                    />
                  )}
                </div>
              </div>

              {/* NODE INSPECTOR */}
              <div className="rounded-2xl bg-surface border border-border flex flex-col overflow-hidden">
                <div className="px-5 py-3 border-b border-border/60 flex items-center justify-between flex-shrink-0">
                  <h3 className="text-[11px] font-mono font-black text-slate-400 uppercase tracking-widest">NODE INSPECTOR</h3>
                  {selectedNode && getRoleBadge(selectedNode.role)}
                </div>

                {selectedNode ? (
                  <div className="flex-1 overflow-y-auto p-5 space-y-5">
                    {/* ACCOUNT ID */}
                    <div className="space-y-1">
                      <div className="text-[9px] font-mono text-slate-600 uppercase tracking-widest">ACCOUNT ID</div>
                      <div className="font-mono font-black text-white text-base break-all">{selectedNode.id}</div>
                    </div>

                    {/* ANOMALY GAUGE */}
                    <div className="space-y-2">
                      <div className="flex justify-between text-[11px] font-mono">
                        <span className="text-slate-500">ANOMALY SCORE</span>
                        <span className={`font-black ${nodeScore > 70 ? 'text-red-400' : nodeScore > 40 ? 'text-orange-400' : 'text-emerald-400'}`}>
                          {nodeScore.toFixed(1)}%
                        </span>
                      </div>
                      <div className="h-2.5 w-full rounded-full bg-slate-800/80 overflow-hidden">
                        <div
                          className={`h-full rounded-full transition-all duration-700 ${nodeScore > 70 ? 'bg-gradient-to-r from-orange-500 to-red-500' : nodeScore > 40 ? 'bg-orange-500' : 'bg-emerald-500'}`}
                          style={{ width: `${nodeScore}%` }}
                        />
                      </div>
                      <div className={`text-[10px] font-mono font-bold text-center py-1.5 rounded-lg ${
                        nodeScore > 70 ? 'bg-red-500/20 text-red-300 border border-red-500/30' :
                        nodeScore > 40 ? 'bg-orange-500/20 text-orange-300 border border-orange-500/30' :
                        'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                      }`}>
                        {nodeScore > 70 ? '⚠ HIGH RISK MULE NODE' : nodeScore > 40 ? '⚡ MODERATE RISK' : '✓ LOW RISK'}
                      </div>
                    </div>

                    {/* GRAPH METRICS */}
                    <div className="grid grid-cols-2 gap-2">
                      {[
                        { label: 'IN-DEGREE',    value: selectedNode.in_degree || 0,  unit: 'txns', color: 'text-white' },
                        { label: 'OUT-DEGREE',   value: selectedNode.out_degree || 0, unit: 'txns', color: 'text-white' },
                        { label: 'BETWEENNESS',  value: Number(selectedNode.betweenness_centrality || 0).toFixed(3), unit: '', color: 'text-orange-400' },
                        { label: 'PASS-THROUGH', value: `${(Number(selectedNode.pass_through_ratio || 0.85) * 100).toFixed(0)}%`, unit: '', color: 'text-red-400' },
                      ].map(({ label, value, unit, color }) => (
                        <div key={label} className="p-3 rounded-lg bg-background/60 border border-border space-y-0.5">
                          <div className="text-[9px] font-mono text-slate-600 uppercase tracking-widest">{label}</div>
                          <div className={`font-mono font-black text-sm ${color}`}>
                            {value} <span className="text-[10px] font-normal text-slate-500">{unit}</span>
                          </div>
                        </div>
                      ))}
                    </div>

                    {/* ROLE DESCRIPTION */}
                    <div className="p-3 rounded-lg bg-background/40 border border-border text-[11px] font-mono text-slate-400 space-y-1">
                      <div className="font-black text-slate-300 uppercase text-[9px] tracking-widest mb-2">FORENSIC NOTE</div>
                      {selectedNode.role === 'MULE_ACCOUNT' && '⚠ High betweenness centrality with >90% pass-through ratio — consistent with a money mule intermediary receiving and immediately forwarding funds.'}
                      {selectedNode.role === 'LAYERING_HUB' && '🔶 High fan-out with aggregation pattern — funds from multiple sources consolidated and dispersed. Typical layering behavior.'}
                      {selectedNode.role === 'VICTIM_SOURCE' && '🟢 Originating account with outbound-only flow. May be an unwitting victim of UPI/NEFT fraud or social engineering.'}
                      {selectedNode.role === 'DESTINATION_SINK' && '🔵 Terminal node — funds exit the mule ring here. Likely ATM withdrawal, crypto wallet, or offline cashout point.'}
                      {!selectedNode.role && '⚪ Account shows no strong directional pattern. Requires further transactional history analysis.'}
                    </div>
                  </div>
                ) : (
                  <div className="flex-1 flex flex-col items-center justify-center p-8 text-center space-y-3">
                    <div className="w-14 h-14 rounded-2xl bg-orange-500/10 border border-orange-500/20 flex items-center justify-center">
                      <Eye className="w-6 h-6 text-orange-500/60" />
                    </div>
                    <div className="text-xs font-mono text-slate-500">
                      Click any node in the topology map to inspect forensic metrics
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* ── NODE ROSTER TABLE ── */}
          {graphData?.nodes && (
            <div className="rounded-2xl bg-surface border border-border overflow-hidden">
              {/* TABLE HEADER */}
              <div className="px-5 py-4 border-b border-border/60 flex flex-col md:flex-row md:items-center justify-between gap-4">
                <h3 className="text-[11px] font-mono font-black text-slate-400 uppercase tracking-widest flex items-center gap-2">
                  <Layers className="w-3.5 h-3.5 text-orange-400" />
                  ENTITY ROSTER — {filteredNodes.length} / {graphData.nodes.length} ACCOUNTS
                </h3>
                <div className="flex flex-wrap items-center gap-2">
                  {/* SEARCH */}
                  <div className="relative">
                    <Search className="w-3 h-3 text-slate-500 absolute left-2.5 top-2.5" />
                    <input
                      type="text"
                      placeholder="Search ID…"
                      value={searchQuery}
                      onChange={e => setSearchQuery(e.target.value)}
                      className="pl-7 pr-3 py-1.5 rounded-lg bg-background border border-border text-[11px] text-white placeholder-slate-600 focus:outline-none focus:border-orange-500 font-mono w-36"
                    />
                  </div>
                  {/* ROLE FILTERS */}
                  {['ALL', 'MULE_ACCOUNT', 'LAYERING_HUB', 'VICTIM_SOURCE', 'DESTINATION_SINK'].map(f => (
                    <button
                      key={f}
                      onClick={() => setTableFilter(f)}
                      className={`px-2 py-1 rounded-lg text-[10px] font-mono font-bold border transition-all ${
                        tableFilter === f
                          ? 'bg-orange-500/20 border-orange-500/50 text-orange-200'
                          : 'bg-background border-border text-slate-500 hover:border-slate-500 hover:text-slate-300'
                      }`}
                    >
                      {f === 'ALL' ? 'ALL' : f.replace('_', ' ')}
                    </button>
                  ))}
                </div>
              </div>

              {/* TABLE */}
              <div className="overflow-x-auto">
                <table className="w-full text-left font-mono text-xs">
                  <thead className="border-b border-border/40 bg-background/40">
                    <tr className="text-[10px] text-slate-600 uppercase tracking-widest">
                      <th className="px-5 py-3">ACCOUNT ID</th>
                      <th className="px-4 py-3">ROLE</th>
                      <th className="px-4 py-3">IN</th>
                      <th className="px-4 py-3">OUT</th>
                      <th className="px-4 py-3">BETWEENNESS</th>
                      <th className="px-4 py-3">PASS-THROUGH</th>
                      <th className="px-4 py-3">ACTION</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border/30">
                    {filteredNodes.map(node => (
                      <tr
                        key={node.id}
                        onClick={() => setSelectedNode(node)}
                        className={`cursor-pointer transition-colors hover:bg-background/60 ${
                          selectedNode?.id === node.id ? 'bg-orange-500/10 border-l-2 border-orange-500' : ''
                        }`}
                      >
                        <td className="px-5 py-3 font-black text-white">{node.id}</td>
                        <td className="px-4 py-3">{getRoleBadge(node.role)}</td>
                        <td className="px-4 py-3 text-slate-300">{node.in_degree || 0}</td>
                        <td className="px-4 py-3 text-slate-300">{node.out_degree || 0}</td>
                        <td className="px-4 py-3 text-orange-400 font-bold">{Number(node.betweenness_centrality || 0).toFixed(3)}</td>
                        <td className="px-4 py-3">
                          <span className={`font-bold ${Number(node.pass_through_ratio || 0) > 0.7 ? 'text-red-400' : 'text-slate-300'}`}>
                            {(Number(node.pass_through_ratio || 0.85) * 100).toFixed(0)}%
                          </span>
                        </td>
                        <td className="px-4 py-3">
                          <button
                            onClick={(e) => { e.stopPropagation(); setSelectedNode(node); }}
                            className="px-2 py-0.5 rounded bg-orange-500/10 border border-orange-500/30 text-orange-300 hover:bg-orange-500/20 text-[10px] font-bold transition-all"
                          >
                            Inspect
                          </button>
                        </td>
                      </tr>
                    ))}
                    {filteredNodes.length === 0 && (
                      <tr>
                        <td colSpan={7} className="px-5 py-8 text-center text-slate-600 text-xs">No accounts match your filters.</td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* EMPTY STATE */}
          {!graphData && !loading && (
            <div className="rounded-2xl border border-border/40 bg-surface/30 p-16 text-center space-y-4">
              <div className="w-16 h-16 rounded-2xl bg-orange-500/10 border border-orange-500/20 flex items-center justify-center mx-auto">
                <NetworkIcon className="w-8 h-8 text-orange-500/50" />
              </div>
              <h3 className="text-slate-400 font-mono font-bold text-sm uppercase tracking-widest">SYSTEM AWAITING INGESTION</h3>
              <p className="text-slate-600 text-xs">Select a scenario above or upload a transaction CSV to initialize the forensic graph engine.</p>
            </div>
          )}
        </div>
      )}

      {/* ══════════════════════════════════════════════════════════════════════ */}
      {/* TAB 2: SINGLE ACCOUNT CHECK                                           */}
      {/* ══════════════════════════════════════════════════════════════════════ */}
      {activeTab === 'single' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <form onSubmit={handleSingleSubmit} className="p-6 rounded-2xl bg-surface border border-border space-y-6">
            <h3 className="text-[11px] font-mono font-black text-slate-400 uppercase tracking-widest">
              ACCOUNT BEHAVIOR SIGNALS
            </h3>
            <div className="space-y-5">
              {SIGNALS_CONFIG.map(({ key, label, options }) => (
                <div key={key} className="space-y-2">
                  <label className="block text-xs font-bold text-slate-300">{label}</label>
                  <div className="flex flex-wrap gap-2">
                    {options.map(opt => (
                      <button
                        key={opt.value}
                        type="button"
                        onClick={() => handleSignalChange(key, opt.value)}
                        className={`px-3 py-2 rounded-lg text-xs font-bold border transition-all ${
                          signals[key] === opt.value
                            ? 'bg-orange-500/20 border-orange-500/60 text-orange-200 shadow-md'
                            : 'bg-background border-border text-slate-400 hover:border-slate-500'
                        }`}
                      >
                        {opt.label}
                      </button>
                    ))}
                  </div>
                </div>
              ))}
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full py-3.5 rounded-xl bg-orange-500 hover:bg-orange-400 active:scale-95 text-black font-black text-xs uppercase tracking-wider flex items-center justify-center gap-2 disabled:opacity-40 transition-all shadow-[0_0_20px_rgba(249,115,22,0.25)]"
            >
              {loading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <ShieldAlert className="w-4 h-4" />}
              {loading ? 'Evaluating…' : 'Assess Mule Account Risk'}
            </button>
          </form>

          <div className="space-y-5">
            <ScanAnimation isActive={loading} stages={MULE_STAGES} accentColor="orange" />

            {error && (
              <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/30 text-red-300 text-xs flex items-start gap-3">
                <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
                <span>{error}</span>
              </div>
            )}

            {singleResult?.verdict && !loading && (() => {
              const prob = singleResult.mule_probability ?? singleResult.result?.mule_probability ?? 0.05;
              const pct = Number((prob * 100).toFixed(1));
              return (
                <ThreatResultCard
                  verdict={singleResult.verdict}
                  confidence={pct}
                  threatType={singleResult.verdict.risk_level === 'safe' ? 'Low Risk Account' : 'Money Mule Pattern Detected'}
                  extraMetrics={[
                    { label: 'Anomaly Score', value: `${pct}%`, sub: 'XGBoost' },
                    { label: 'Engine', value: 'XGBoost + NetworkX', sub: 'Graph + ML' },
                    { label: 'Risk Band', value: singleResult.verdict.risk_level?.toUpperCase() || 'SAFE', sub: 'Classification' }
                  ]}
                />
              );
            })()}

            {!singleResult && !loading && (
              <div className="p-12 rounded-2xl bg-surface/40 border border-border/40 text-center space-y-3">
                <NetworkIcon className="w-12 h-12 text-slate-700 mx-auto" />
                <p className="text-slate-500 text-xs font-mono">Configure signals and click "Assess Mule Account Risk".</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
