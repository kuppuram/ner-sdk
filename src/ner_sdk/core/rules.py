# src/ner_sdk/core/rules.py
from __future__ import annotations
import re
from typing import Dict, List

MONTHS_RE = r"(jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:t)?|sept(?:ember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)"
YEAR_RE = r"(?:19\d{2}|20\d{2})"

def match_core(tokens: List[str]) -> List[Dict]:
    """
    Return spans (start,end,label,priority,length) for core entities:
    MONTH, YEAR, DATE, TOPK, SCORE.
    """
    spans: List[Dict] = []
    lower = [t.lower() for t in tokens]
    CORE_PRI = 100

    # MONTH + naive "X to Y" chaining window
    for i, tok in enumerate(lower):
        if re.fullmatch(MONTHS_RE, tok):
            spans.append({"start": i, "end": i+1, "label": "MONTH",
                          "priority": CORE_PRI, "length": 1})
            if i + 2 < len(tokens) and re.fullmatch(MONTHS_RE, lower[i+2]):
                # tag "to <MONTH>" as continuation
                spans.append({"start": i+1, "end": i+3, "label": "MONTH",
                              "priority": CORE_PRI, "length": 2})

    # YEAR
    for i, tok in enumerate(tokens):
        if re.fullmatch(YEAR_RE, tok):
            spans.append({"start": i, "end": i+1, "label": "YEAR",
                          "priority": CORE_PRI, "length": 1})

    # Relative DATE: "this|last|next (month|year|quarter)"
    for i in range(len(tokens) - 1):
        if re.fullmatch(r"(this|last|next)", lower[i]) and \
           re.fullmatch(r"(month|year|quarter)", lower[i+1]):
            spans.append({"start": i, "end": i+2, "label": "DATE",
                          "priority": CORE_PRI, "length": 2})

    # TOPK: "top 10" / "top-10"
    for i in range(len(tokens) - 1):
        if lower[i] == "top" and re.fullmatch(r"\d+", tokens[i+1]):
            spans.append({"start": i, "end": i+2, "label": "TOPK",
                          "priority": CORE_PRI, "length": 2})
    for i, tok in enumerate(lower):
        if re.fullmatch(r"top-\d+", tok):
            spans.append({"start": i, "end": i+1, "label": "TOPK",
                          "priority": CORE_PRI, "length": 1})

    # SCORE & SCORE RANGE
    for i, tok in enumerate(tokens):
        # bare number
        if re.fullmatch(r"\d+", tok):
            # "<num> or above/more/higher/greater"
            if i + 2 < len(tokens) and lower[i+1] == "or" and \
               re.fullmatch(r"(above|more|higher|greater)", lower[i+2]):
                spans.append({"start": i, "end": i+3, "label": "SCORE",
                              "priority": CORE_PRI, "length": 3})
            else:
                spans.append({"start": i, "end": i+1, "label": "SCORE",
                              "priority": CORE_PRI, "length": 1})

        # "score <num>"
        if lower[i] == "score" and i + 1 < len(tokens) and re.fullmatch(r"\d+", tokens[i+1]):
            spans.append({"start": i+1, "end": i+2, "label": "SCORE",
                          "priority": CORE_PRI, "length": 1})

        # "<num> score"
        if re.fullmatch(r"\d+", tok) and i + 1 < len(tokens) and lower[i+1] == "score":
            spans.append({"start": i, "end": i+1, "label": "SCORE",
                          "priority": CORE_PRI, "length": 1})

    return spans
