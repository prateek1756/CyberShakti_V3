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


def analyze_transaction_network(transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Parses a transaction log and builds a directed transaction graph.
    Computes NetworkX graph metrics, identifies node roles (VICTIM_SOURCE, MULE_ACCOUNT,
    LAYERING_HUB, DESTINATION_SINK), calculates risk scores, and detects mule rings.
    """
    if not transactions:
        return {
            "nodes": [],
            "edges": [],
            "summary": {
                "total_accounts": 0,
                "flagged_mules": 0,
                "total_volume": 0.0,
                "suspicious_volume": 0.0,
                "mule_rings_detected": 0
            }
        }

    G = nx.DiGraph()
    node_stats: Dict[str, Dict[str, Any]] = {}

    total_volume = 0.0

    for tx in transactions:
        sender = str(tx.get("sender") or tx.get("sender_account") or tx.get("from") or "UNKNOWN_SRC").strip()
        receiver = str(tx.get("receiver") or tx.get("receiver_account") or tx.get("to") or "UNKNOWN_DEST").strip()
        try:
            amount = float(tx.get("amount") or tx.get("txn_amount") or 0.0)
        except (ValueError, TypeError):
            amount = 0.0

        timestamp = str(tx.get("timestamp") or tx.get("time") or "")

        total_volume += amount

        for node_id in (sender, receiver):
            if node_id not in node_stats:
                node_stats[node_id] = {
                    "in_degree": 0,
                    "out_degree": 0,
                    "in_volume": 0.0,
                    "out_volume": 0.0,
                    "tx_count": 0,
                }
                G.add_node(node_id)

        node_stats[sender]["out_degree"] += 1
        node_stats[sender]["out_volume"] += amount
        node_stats[sender]["tx_count"] += 1

        node_stats[receiver]["in_degree"] += 1
        node_stats[receiver]["in_volume"] += amount
        node_stats[receiver]["tx_count"] += 1

        if G.has_edge(sender, receiver):
            G[sender][receiver]["amount"] += amount
            G[sender][receiver]["count"] += 1
        else:
            G.add_edge(sender, receiver, amount=amount, count=1, timestamp=timestamp)

    # Compute graph centrality metrics
    betweenness = nx.betweenness_centrality(G) if len(G) > 2 else {n: 0.0 for n in G.nodes}
    
    # Simple undirected graph for clustering calculation
    undirected_G = G.to_undirected()
    clustering = nx.clustering(undirected_G)

    nodes_output = []
    flagged_mules_count = 0
    suspicious_volume = 0.0

    for node_id, stats in node_stats.items():
        in_deg = stats["in_degree"]
        out_deg = stats["out_degree"]
        in_vol = stats["in_volume"]
        out_vol = stats["out_volume"]
        btw = betweenness.get(node_id, 0.0)
        clust = clustering.get(node_id, 0.0)

        # Pass-through ratio evaluation (funds rapidly enter and leave)
        min_vol = min(in_vol, out_vol)
        max_vol = max(in_vol, out_vol) if max(in_vol, out_vol) > 0 else 1.0
        pass_through_ratio = min_vol / max_vol if in_vol > 0 and out_vol > 0 else 0.0

        # Heuristic Risk Score (0-100)
        risk_score = 15.0
        if in_deg > 0 and out_deg > 0:
            risk_score += pass_through_ratio * 40.0  # Pass-through behavior
        if in_deg >= 3 and out_deg >= 3:
            risk_score += 25.0  # High fan-in and fan-out
        if btw > 0.15:
            risk_score += 20.0  # Central bottleneck in flow

        risk_score = min(99.0, max(5.0, round(risk_score, 1)))

        # Node Role Classification
        if in_deg == 0 and out_deg > 0:
            role = "VICTIM_SOURCE"
            risk_tier = "low_risk"
        elif in_deg > 0 and out_deg == 0:
            role = "DESTINATION_SINK"
            risk_tier = "moderate_risk" if risk_score > 50 else "low_risk"
        elif in_deg >= 2 and out_deg >= 2 and pass_through_ratio >= 0.7:
            role = "MULE_ACCOUNT"
            risk_tier = "high_risk"
            flagged_mules_count += 1
            suspicious_volume += in_vol
        elif in_deg >= 1 and out_deg >= 1 and pass_through_ratio >= 0.5:
            role = "LAYERING_HUB"
            risk_tier = "moderate_risk"
            if risk_score >= 60:
                flagged_mules_count += 1
                suspicious_volume += in_vol
        else:
            role = "REGULAR_ACCOUNT"
            risk_tier = "safe"

        nodes_output.append({
            "id": node_id,
            "label": node_id,
            "role": role,
            "risk_score": risk_score,
            "risk_tier": risk_tier,
            "in_degree": in_deg,
            "out_degree": out_deg,
            "in_volume": round(in_vol, 2),
            "out_volume": round(out_vol, 2),
            "betweenness_centrality": round(btw, 4),
            "clustering_coefficient": round(clust, 4),
            "pass_through_ratio": round(pass_through_ratio, 2)
        })

    edges_output = []
    for u, v, data in G.edges(data=True):
        edges_output.append({
            "source": u,
            "target": v,
            "amount": round(data.get("amount", 0.0), 2),
            "count": data.get("count", 1),
            "timestamp": data.get("timestamp", "")
        })

    # Detect mule rings (connected components containing at least one mule)
    weak_components = list(nx.weakly_connected_components(G))
    mule_rings_count = sum(
        1 for comp in weak_components
        if any(n["role"] in ("MULE_ACCOUNT", "LAYERING_HUB") for n in nodes_output if n["id"] in comp)
    )

    return {
        "nodes": nodes_output,
        "edges": edges_output,
        "summary": {
            "total_accounts": len(nodes_output),
            "flagged_mules": flagged_mules_count,
            "total_volume": round(total_volume, 2),
            "suspicious_volume": round(suspicious_volume, 2),
            "mule_rings_detected": mule_rings_count
        }
    }


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
