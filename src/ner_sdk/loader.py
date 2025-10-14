from __future__ import annotations
import importlib, importlib.util, re, pkgutil
from pathlib import Path
from typing import Callable, Dict, List, Optional, Iterable
import yaml

class DomainPack:
    def __init__(self, name: str, base: Path, patterns: List[dict],
                 hook_fn: Optional[Callable], priority: int = 50):
        self.name = name
        self.base = base
        self.patterns = patterns or []
        self.hook_fn = hook_fn
        self.priority = priority

def _load_yaml_entities(p: Path) -> List[dict]:
    if not p.exists():
        return []
    with p.open("r", encoding="utf-8") as f:
        y = yaml.safe_load(f) or {}
    return y.get("entities", [])

def _load_hook_fn(hook_path: Path) -> Optional[Callable]:
    if not hook_path.exists():
        return None
    spec = importlib.util.spec_from_file_location(f"{hook_path.stem}_module", str(hook_path))
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)  # type: ignore
    return getattr(mod, "custom_match", None)

def _module_base_path(mod) -> Path:
    """
    Robustly get a module's base directory.
    Works for regular packages (__file__) and namespace packages (__path__).
    """
    file_attr = getattr(mod, "__file__", None)
    if file_attr:  # regular package/module
        return Path(file_attr).parent
    path_attr: Optional[Iterable[str]] = getattr(mod, "__path__", None)  # namespace package
    if path_attr:
        # __path__ is an iterable; take the first entry
        for p in path_attr:
            if p:
                return Path(p)
    raise RuntimeError(f"Cannot determine filesystem path for module {mod!r}")

def load_pack(name_or_path: str, *, priority: int = 50) -> DomainPack:
    p = Path(name_or_path)
    if p.exists():  # folder pack
        patterns = _load_yaml_entities(p / "patterns.yaml")
        hook_fn = _load_hook_fn(p / "hooks.py")
        return DomainPack(name=p.name, base=p, patterns=patterns, hook_fn=hook_fn, priority=priority)

    # module pack
    mod = importlib.import_module(name_or_path)
    base = _module_base_path(mod)
    patterns = _load_yaml_entities(base / "patterns.yaml")
    hook_fn = None
    try:
        hooks_mod = importlib.import_module(name_or_path + ".hooks")
        hook_fn = getattr(hooks_mod, "custom_match", None)
    except ImportError:
        pass
    return DomainPack(name=name_or_path.split(".")[-1], base=base, patterns=patterns, hook_fn=hook_fn, priority=priority)

def apply_pack(pack: DomainPack, tokens: List[str]) -> List[Dict]:
    spans: List[Dict] = []

    # Declarative patterns
    for ent in pack.patterns:
        kind = ent.get("kind")
        label = ent.get("name")
        if not label or not kind:
            continue

        if kind == "regex-token":
            flags = re.IGNORECASE if ent.get("case_insensitive") else 0
            rx = re.compile(ent["pattern"], flags)
            for i, tok in enumerate(tokens):
                if rx.fullmatch(tok):
                    spans.append({"start": i, "end": i+1, "label": label,
                                  "priority": pack.priority, "length": 1})

        elif kind == "phrase":
            phrases = ent.get("phrases", [])
            for ph in phrases:
                ph_tokens = ph.split()
                n = len(ph_tokens)
                for i in range(len(tokens) - n + 1):
                    if tokens[i:i+n] == ph_tokens:
                        spans.append({"start": i, "end": i+n, "label": label,
                                      "priority": pack.priority, "length": n})

    # Optional hook
    if pack.hook_fn:
        for sp in pack.hook_fn(tokens) or []:
            sp["priority"] = pack.priority
            sp["length"] = sp["end"] - sp["start"]
            spans.append(sp)

    return spans
