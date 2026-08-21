"""F-07 graph feature engineering (NetworkX). Elliptic-trained weights are not loaded unless present."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import networkx as nx

from app.ml.loader import load_joblib, load_json
from app.shared.explanation_engine import generate_explanation

DISCLAIMERS = {
    "experimental": "Research/experimental feature.",
    "domain_mismatch": (
        "Elliptic/Elliptic2 represent cryptocurrency transaction networks, not Indian bank accounts (ADR-024)."
    ),
    "general_notice": "Statistical indicator only; not proof of criminal activity.",
}

_model = None
_metrics: Optional[dict] = None
_loaded = False


def graph_features(account_signals: Dict[str, Any]) -> Dict[str, float]:
    graph = account_signals.get("graph") or {}
    nodes = graph.get("nodes") or []
    edges = graph.get("edges") or []
    if not nodes:
        return {
            "degree_centrality": 0.0,
            "clustering_coefficient": 0.0,
            "betweenness_centrality": 0.0,
            "node_count": 0.0,
            "edge_count": 0.0,
        }
    g = nx.Graph()
    g.add_nodes_from(nodes)
    for edge in edges:
        if isinstance(edge, (list, tuple)) and len(edge) >= 2:
            g.add_edge(edge[0], edge[1])
    node = account_signals.get("account_id") or (nodes[0] if nodes else None)
    deg = nx.degree_centrality(g)
    clust = nx.clustering(g)
    btw = nx.betweenness_centrality(g, k=min(20, len(g))) if len(g) > 2 else {n: 0.0 for n in g.nodes}
    return {
        "degree_centrality": float(deg.get(node, 0.0)),
        "clustering_coefficient": float(clust.get(node, 0.0)),
        "betweenness_centrality": float(btw.get(node, 0.0)),
        "node_count": float(g.number_of_nodes()),
        "edge_count": float(g.number_of_edges()),
    }


def tabular_features(account_signals: Dict[str, Any]) -> List[float]:
    g = graph_features(account_signals)
    return [
        float(account_signals.get("account_age_days") or 0),
        float(account_signals.get("inbound_txn_count") or 0),
        float(account_signals.get("outbound_txn_count") or 0),
        float(account_signals.get("rapid_fund_pass_through") or 0),
        g["degree_centrality"],
        g["clustering_coefficient"],
        g["betweenness_centrality"],
        g["node_count"],
        g["edge_count"],
    ]


def _ensure_loaded() -> None:
    global _model, _metrics, _loaded
    if _loaded:
        return
    _model = load_joblib("f07_xgboost.joblib")
    _metrics = load_json("f07_metrics.json")
    _loaded = True


def infer_mule(account_signals: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(account_signals, dict) or not account_signals:
        raise ValueError("empty_signals")
    _ensure_loaded()
    g = graph_features(account_signals)
    if _model is not None:
        import numpy as np

        prob = float(_model.predict_proba(np.array([tabular_features(account_signals)]))[0][1])
        risk = "high_risk" if prob >= 0.7 else "moderate_risk" if prob >= 0.4 else "low_risk"
        source = "ml_model"
        note = "XGBoost artefact present. Domain mismatch with Indian bank networks still applies (ADR-024)."
        model_loaded = True
    else:
        prob = None
        flags = []
        if account_signals.get("rapid_fund_pass_through"):
            flags.append("rapid_fund_pass_through")
        if (account_signals.get("account_age_days") or 9999) < 30 and (
            (account_signals.get("inbound_txn_count") or 0) + (account_signals.get("outbound_txn_count") or 0)
        ) > 20:
            flags.append("new_account_high_velocity")
        if g["degree_centrality"] >= 0.5:
            flags.append("high_degree_centrality")
        risk = "high_risk" if len(flags) >= 2 else "moderate_risk" if flags else "low_risk"
        source = "heuristic"
        note = "Elliptic dataset was not present; no F-07 XGBoost weights were trained or loaded."
        model_loaded = False

    verdict = generate_explanation(
        feature_id="F-07",
        risk_level=risk,
        signals=list(g.keys())[:3],
        is_experimental=True,
    )
    return {
        "verdict": verdict,
        "probability": prob,
        "verdict_source": source,
        "model_note": note,
        "model_loaded": model_loaded,
        "graph_features": g,
        "disclaimers": DISCLAIMERS,
        "evaluation": _metrics,
    }
