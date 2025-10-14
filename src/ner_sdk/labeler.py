# src/ner_sdk/labeler.py
from __future__ import annotations
from typing import List, Dict, Iterable, Optional
from .core.rules import match_core
from .loader import load_pack, apply_pack
from .resolve import resolve_overlaps

def _spans_to_bio(tokens: List[str], spans: List[Dict]) -> str:
    labels = ["O"] * len(tokens)
    for sp in spans:
        lab = sp["label"]
        labels[sp["start"]] = f"B-{lab}"
        for i in range(sp["start"] + 1, sp["end"]):
            labels[i] = f"I-{lab}"
    return " ".join(labels)

def generate_ner_labels(text: str, domains: Optional[List[str]] = None) -> str:
    tokens = text.split()
    spans: List[Dict] = []
    # core
    spans.extend(match_core(tokens))
    # domains
    for name in (domains or []):
        pack = load_pack(name, priority=50)
        spans.extend(apply_pack(pack, tokens))
    merged = resolve_overlaps(spans)
    return _spans_to_bio(tokens, merged)

def tag_text_to_dict(text: str, domains: Optional[List[str]] = None) -> Dict[str, str]:
    return {"text": text, "labels": generate_ner_labels(text, domains)}

def bulk_tag(texts: Iterable[str], domains: Optional[List[str]] = None) -> List[Dict[str, str]]:
    return [tag_text_to_dict(t, domains) for t in texts]
