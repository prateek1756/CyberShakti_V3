"""F-11 RAG retrieval + prompt assembly. LLM generation is blocked while ADR-013 is Open."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Tuple

KB_DIR = Path(__file__).resolve().parents[2] / "ml" / "knowledge_base"

SYSTEM_PROMPT = """You are the CyberShakti cybersecurity assistant for everyday people in India.
Answer only from the retrieved knowledge-base context.
Do not invent threat statistics, threat actors, or incident details.
Do not give legal, financial, or medical advice.
Never tell a user to share an OTP, UPI PIN, or password.
If the context is insufficient, say so.
Always include that this is AI-generated informational guidance, not guaranteed protection.
"""


def _chunk(text: str, size: int = 400, overlap: int = 50) -> List[str]:
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = " ".join(words[i : i + size])
        if chunk.strip():
            chunks.append(chunk.strip())
        i += max(size - overlap, 1)
    return chunks


def load_chunks() -> List[Dict[str, str]]:
    chunks: List[Dict[str, str]] = []
    if not KB_DIR.is_dir():
        return chunks
    for path in sorted(KB_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        for idx, chunk in enumerate(_chunk(text)):
            chunks.append({"document_title": path.stem, "chunk_id": f"{path.stem}-{idx}", "content": chunk})
    return chunks


def _tokens(text: str) -> List[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def retrieve(query: str, k: int = 4) -> List[Dict[str, Any]]:
    q = set(_tokens(query))
    scored: List[Tuple[float, Dict[str, str]]] = []
    for chunk in load_chunks():
        tokens = _tokens(chunk["content"])
        if not tokens or not q:
            continue
        overlap = len(q.intersection(tokens))
        score = overlap / max(len(q), 1)
        scored.append((score, chunk))
    scored.sort(key=lambda x: x[0], reverse=True)
    results = []
    for score, chunk in scored[:k]:
        if score <= 0:
            continue
        results.append({**chunk, "score": round(score, 4)})
    return results


def assemble_prompt(query: str, chunks: List[Dict[str, Any]]) -> str:
    context = "\n\n".join(f"[{c['document_title']}] {c['content']}" for c in chunks) or "(no matching knowledge-base chunks)"
    return (
        f"{SYSTEM_PROMPT}\n\n"
        f"Retrieved context:\n{context}\n\n"
        f"User query:\n{query}\n"
    )


def out_of_scope(query: str) -> bool:
    lowered = query.lower()
    blocked = ("diagnose my illness", "write malware", "how to hack", "make a bomb")
    return any(p in lowered for p in blocked)


def run_rag(query: str) -> Dict[str, Any]:
    cleaned = (query or "").strip()
    if not cleaned:
        raise ValueError("empty_query")
    if out_of_scope(cleaned):
        return {
            "llm_status": "blocked_out_of_scope",
            "response": None,
            "knowledge_sources": [],
            "assembled_prompt_present": False,
            "ai_disclaimer": (
                "This assistant only discusses consumer cybersecurity. The query was declined."
            ),
        }
    chunks = retrieve(cleaned)
    prompt = assemble_prompt(cleaned, chunks)
    return {
        "llm_status": "blocked_adr_013",
        "response": None,
        "knowledge_sources": [
            {"document_title": c["document_title"], "chunk_id": c["chunk_id"], "relevance": c["score"]}
            for c in chunks
        ],
        "retrieved_context": [c["content"] for c in chunks],
        "assembled_prompt_present": bool(prompt),
        "ai_disclaimer": (
            "LLM generation is not enabled: ADR-013 (LLM provider) remains Open. "
            "Retrieved knowledge-base excerpts are shown without a generated answer so the system does not fabricate advice."
        ),
    }
