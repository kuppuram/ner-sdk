from typing import List, Dict

def custom_match(tokens: List[str]) -> List[Dict]:
    spans: List[Dict] = []
    lower = [t.lower() for t in tokens]

    # Simple phrase that may span punctuation
    for i in range(len(tokens) - 1):
        if lower[i] == "three" and lower[i+1] == "times":
            spans.append({"start": i, "end": i+2, "label": "FREQUENCY"})
    return spans
