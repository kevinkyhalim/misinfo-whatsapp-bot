from __future__ import annotations
import logging
from typing import Dict, Any, List
from app.rag.faiss_store import get_faiss_retriever
from app.rag.private_matcher import is_private_domain_claim
from app.gemini import gemini_verify_with_search, gemini_verify_with_evidence, gemini_url_check
from app.utils import detect_url, extract_text_from_url

logger = logging.getLogger(__name__)

def _extract_text_or_url(message: str) -> Dict[str, str]:
    """
    Check if a message is a url
    """
    url = detect_url(message)
    if url:
        return {"mode": "url", "content": url}
    return {"mode": "text", "content": (message or "").strip()}

def process_incoming_message_hybrid(message_body: str) -> str:
    """
    Hybrid fact-checking:
      - If link -> Gemini
      - If private domain -> FAISS retrieval -> Gemini with evidence
      - Else -> Gemini with Google Search
    Returns plain text (no XML) for WhatsApp reply.
    """

    parsed = _extract_text_or_url(message_body)

    # 1) Pass the answers to gemini if it's an URL
    if parsed["mode"] == "url":
        # You can pass the URL to Gemini to assess the answers
        article_text = extract_text_from_url(parsed["content"])
        response = gemini_url_check(article_text)
        return response
    else:
        claim = parsed["content"]
        claim_source = None

    if not claim:
        return "Sorry, I couldn't read a claim from your message. Please send a statement or a link."

    # 2) Decide path: private domain (RAG) vs public (Gemini Search)
    use_private = is_private_domain_claim(claim, extra_signals=[claim_source] if claim_source else None)

    if use_private:
        # 3a) PRIVATE: FAISS retrieval (local small corpus)
        retriever = get_faiss_retriever()
        hits = retriever.search(claim, k=5, min_score=0.30)
        if not hits:
            # fall back to public search if private has no signal
            response = gemini_verify_with_search(claim)
        else:
            print("using internal document")
            # Prepare evidence strings for Gemini
            evidence_blocks = []
            for h in hits:
                evidence_blocks.append(f"[{h.title}] {h.text}\nSource: {h.url}")
            evidence = "\n\n".join(evidence_blocks)
            response = gemini_verify_with_evidence(
                claim=claim,
                evidence=evidence
            )
    else:
        # 3b) PUBLIC: Ask Gemini to search the web directly
        response = gemini_verify_with_search(claim)

    return response