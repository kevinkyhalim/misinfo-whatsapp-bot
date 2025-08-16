# app/rag/private_matcher.py
from __future__ import annotations
import os
import re
from typing import Iterable, List
from dotenv import load_dotenv

# Ensure .env is loaded if present
load_dotenv()

def _load_keywords() -> List[str]:
    """Load and normalize PRIVATE_DOMAIN_KEYWORDS from env."""
    raw = os.getenv("PRIVATE_DOMAIN_KEYWORDS", "")
    if not raw:
        return []
    # split by comma and/or newline
    parts = re.split(r"[,\n]", raw)
    keywords = [p.strip().lower() for p in parts if p.strip()]
    return keywords

def is_private_domain_claim(text: str, extra_signals: Iterable[str] | None = None) -> bool:
    """
    Returns True if the claim appears to fall into your private dataset domain.
    Uses keywords defined in PRIVATE_DOMAIN_KEYWORDS from .env file.
    """
    keywords = _load_keywords()
    if not keywords:
        return False

    hay = (text or "").lower()

    # Check claim text
    for kw in keywords:
        if kw in hay:
            return True

    # Check optional extra signals (e.g., URL domain, sender info)
    if extra_signals:
        for sig in extra_signals:
            s = (sig or "").lower()
            for kw in keywords:
                if kw in s:
                    return True

    return False
