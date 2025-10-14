# src/ner_sdk/resolve.py
from __future__ import annotations
from typing import Dict, List

def resolve_overlaps(spans: List[Dict]) -> List[Dict]:
    """
    Deterministic merging:
    1) longer spans first
    2) higher priority
    3) earlier start
    """
    spans = sorted(spans, key=lambda s: (-s["length"], -s["priority"], s["start"]))
    used = set()
    kept: List[Dict] = []
    for sp in spans:
        idxs = set(range(sp["start"], sp["end"]))
        if used & idxs:
            continue
        kept.append(sp)
        used |= idxs
    return sorted(kept, key=lambda s: s["start"])
