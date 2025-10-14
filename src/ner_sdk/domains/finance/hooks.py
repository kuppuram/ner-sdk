from __future__ import annotations
from typing import List, Dict

def custom_match(tokens: List[str]) -> List[Dict]:
    spans: List[Dict] = []
    lower = [t.lower() for t in tokens]

    # "at least 4%" => PERCENT_RANGE across 3 tokens
    for i in range(len(tokens) - 2):
        if lower[i] == "at" and lower[i+1] == "least" and tokens[i+2].endswith("%"):
            spans.append({"start": i, "end": i+3, "label": "PERCENT_RANGE"})
    return spans
