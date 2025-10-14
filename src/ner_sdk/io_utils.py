import json
from typing import List, Dict, Iterable, Union, TextIO

Record = Dict[str, str]

def _ensure_records(data: List[Record]) -> None:
    for i, rec in enumerate(data):
        if not isinstance(rec, dict) or "text" not in rec or "labels" not in rec:
            raise ValueError(f"Item {i} must be a dict with 'text' and 'labels' keys.")

# ---------- JSON ----------
def save_json(data: List[Record], path: str, *, pretty: bool = True) -> None:
    _ensure_records(data)
    with open(path, "w", encoding="utf-8") as f:
        if pretty:
            json.dump(data, f, ensure_ascii=False, indent=2)
        else:
            json.dump(data, f, ensure_ascii=False)

def load_json(path: str) -> List[Record]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("JSON root must be a list of {'text','labels'} dicts.")
    _ensure_records(data)
    return data

# ---------- JSONL ----------
def save_jsonl(data: Iterable[Record], path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        for rec in data:
            if not isinstance(rec, dict) or "text" not in rec or "labels" not in rec:
                raise ValueError("Each item must be a dict with 'text' and 'labels'.")
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

def load_jsonl(path: str) -> List[Record]:
    out: List[Record] = []
    with open(path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            if not isinstance(rec, dict) or "text" not in rec or "labels" not in rec:
                raise ValueError(f"Line {line_num}: must be a dict with 'text' and 'labels'.")
            out.append(rec)
    return out
