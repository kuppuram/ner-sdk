# src/ner_sdk/cli.py
from __future__ import annotations

import argparse
import os
import sys
from typing import List
from pathlib import Path
import pkgutil
import importlib
import yaml

from .labeler import bulk_tag
from .io_utils import save_json, save_jsonl, load_json, load_jsonl
from .loader import load_pack


# -------------------- helpers --------------------
def _infer_format_from_path(path: str) -> str:
    ext = os.path.splitext(path.lower())[1]
    return "jsonl" if ext == ".jsonl" else "json"


# -------------------- commands: tag --------------------
def _cmd_tag(args: argparse.Namespace) -> int:
    try:
        with open(args.infile, "r", encoding="utf-8") as f:
            texts: List[str] = [ln.strip() for ln in f if ln.strip()]
    except FileNotFoundError:
        print(f"ERROR: Input file not found: {args.infile}", file=sys.stderr)
        return 2

    data = bulk_tag(texts, domains=args.domains or [])
    out_fmt = args.format or _infer_format_from_path(args.outfile)

    try:
        if out_fmt == "jsonl":
            save_jsonl(data, args.outfile)
        else:
            save_json(data, args.outfile, pretty=not args.no_pretty)
    except Exception as e:
        print(f"ERROR: Failed to write output: {e}", file=sys.stderr)
        return 3

    print(f"Tagged {len(data)} texts → {args.outfile}")
    return 0


# -------------------- commands: roundtrip --------------------
def _cmd_roundtrip(args: argparse.Namespace) -> int:
    in_fmt = "jsonl" if args.infile.lower().endswith(".jsonl") else "json"
    try:
        data = load_jsonl(args.infile) if in_fmt == "jsonl" else load_json(args.infile)
    except FileNotFoundError:
        print(f"ERROR: Input file not found: {args.infile}", file=sys.stderr)
        return 2
    except Exception as e:
        print(f"ERROR: Failed to load {args.infile}: {e}", file=sys.stderr)
        return 2

    out_fmt = args.format or _infer_format_from_path(args.outfile)
    try:
        if out_fmt == "jsonl":
            save_jsonl(data, args.outfile)
        else:
            save_json(data, args.outfile, pretty=not args.no_pretty)
    except Exception as e:
        print(f"ERROR: Failed to write output: {e}", file=sys.stderr)
        return 3

    print(f"Loaded {len(data)} records from {args.infile} → {args.outfile}")
    return 0


# -------------------- commands: doctor --------------------
def _cmd_doctor(args: argparse.Namespace) -> int:
    print("nersdk doctor — environment diagnostics\n")

    packs = args.domains or ["ner_sdk.domains.finance"]
    ok = True

    for name in packs:
        print(f"🔍 Checking pack: {name}")
        try:
            pack = load_pack(name)
            base = pack.base
            pat_path = base / "patterns.yaml"
            hook_path = base / "hooks.py"

            if pat_path.exists():
                try:
                    with open(pat_path, "r", encoding="utf-8") as f:
                        yaml.safe_load(f)
                    print(f"  ✅ patterns.yaml found ({len(pack.patterns)} entity patterns)")
                except Exception as e:
                    print(f"  ⚠️  patterns.yaml invalid YAML: {e}")
                    ok = False
            else:
                print(f"  ⚠️  patterns.yaml missing")
                ok = False

            if hook_path.exists():
                if pack.hook_fn:
                    print("  ✅ hooks.py found and custom_match callable loaded")
                else:
                    print("  ⚠️  hooks.py exists but no callable named 'custom_match'")
                    ok = False
            else:
                print("  ℹ️  hooks.py not present (optional)")
        except Exception as e:
            print(f"  ❌ Failed to load: {e}")
            ok = False
        print()

    if ok:
        print("✅ All domain packs look healthy!\n")
        return 0
    else:
        print("⚠️  Some checks failed. Please review above output.\n")
        return 1


# -------------------- commands: domains list/info --------------------
def _discover_builtin_domains() -> List[str]:
    """
    Discover built-in domain packs under ner_sdk.domains.*.

    Works for:
    - regular packages (with __init__.py)
    - namespace packages (PEP 420, no __init__.py)
    - src/ layouts (editable installs)
    Falls back to scanning the filesystem for folders that contain patterns.yaml
    inside ner_sdk/domains.
    """
    base_pkg = "ner_sdk.domains"
    found: List[str] = []

    # 1) Try module-based discovery (pkgutil over __path__)
    try:
        pkg = importlib.import_module(base_pkg)
        if hasattr(pkg, "__path__"):
            for modinfo in pkgutil.iter_modules(pkg.__path__, base_pkg + "."):
                if modinfo.ispkg:
                    found.append(modinfo.name)
    except Exception:
        pass  # we'll try filesystem fallback next

    # 2) Filesystem fallback via importlib.resources (Py3.9+)
    try:
        from importlib import resources as importlib_resources
        try:
            base = importlib_resources.files("ner_sdk") / "domains"
        except Exception:
            base = None

        if base and base.is_dir():
            for p in base.iterdir():
                if p.is_dir() and (p / "patterns.yaml").exists():
                    found.append(f"{base_pkg}.{p.name}")
    except Exception:
        pass

    # De-dupe + sort
    return sorted(set(found))


def _cmd_domains_list(args: argparse.Namespace) -> int:
    builtins = _discover_builtin_domains()
    if not builtins:
        print("No built-in domain packs found.")
        return 0
    print("Built-in domain packs:")
    for name in builtins:
        try:
            pack = load_pack(name)
            print(f"  • {name}  (entities: {len(pack.patterns)}, hook: {'yes' if pack.hook_fn else 'no'})")
        except Exception as e:
            print(f"  • {name}  (failed to load: {e})")
    return 0

def _cmd_domains_info(args: argparse.Namespace) -> int:
    if not args.domains:
        print("Please provide at least one domain pack module or folder path.", file=sys.stderr)
        return 2
    ok = True
    for name in args.domains:
        print(f"ℹ️  Info: {name}")
        try:
            pack = load_pack(name)
            base = pack.base
            print(f"   - base: {base}")
            print(f"   - entities: {len(pack.patterns)}")
            if pack.patterns:
                labels = [ent.get('name','?') for ent in pack.patterns if isinstance(ent, dict)]
                print(f"   - labels: {', '.join(labels)}")
            print(f"   - hook: {'yes' if pack.hook_fn else 'no'}")
        except Exception as e:
            ok = False
            print(f"   - ERROR: {e}")
        print()
    return 0 if ok else 1


# -------------------- parser --------------------
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="nersdk",
        description="nersdk: rule-based NER labeling (core + optional domain packs) with JSON/JSONL IO.",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    # tag
    p_tag = sub.add_parser(
        "tag",
        help="Read newline-delimited text file, label, and save to JSON or JSONL.",
    )
    p_tag.add_argument("--in", dest="infile", required=True, help="Input .txt (one text per line).")
    p_tag.add_argument("--out", dest="outfile", required=True, help="Output path (.json or .jsonl).")
    p_tag.add_argument("--format", choices=["json", "jsonl"], default=None,
                       help="Force output format; otherwise inferred from --out extension.")
    p_tag.add_argument("--domains", nargs="*", default=[],
                       help="Optional domain packs (module paths or folders).")
    p_tag.add_argument("--no-pretty", action="store_true",
                       help="When saving JSON, disable pretty indentation (ignored for JSONL).")
    p_tag.set_defaults(func=_cmd_tag)

    # roundtrip
    p_rt = sub.add_parser(
        "roundtrip",
        help="Load JSON/JSONL and re-save (format conversion / pretty toggle).",
    )
    p_rt.add_argument("--in", dest="infile", required=True, help="Input .json or .jsonl file.")
    p_rt.add_argument("--out", dest="outfile", required=True, help="Output path (.json or .jsonl).")
    p_rt.add_argument("--format", choices=["json", "jsonl"], default=None,
                      help="Force output format; otherwise inferred from --out extension.")
    p_rt.add_argument("--no-pretty", action="store_true",
                      help="When saving JSON, disable pretty indentation (ignored for JSONL).")
    p_rt.set_defaults(func=_cmd_roundtrip)

    # doctor
    p_doc = sub.add_parser(
        "doctor",
        help="Run environment and domain pack diagnostics.",
    )
    p_doc.add_argument("--domains", nargs="*", default=[],
                       help="Domain packs to verify (modules or folders).")
    p_doc.set_defaults(func=_cmd_doctor)

    # domains (group)
    p_domains = sub.add_parser("domains", help="Domain pack utilities.")
    dsub = p_domains.add_subparsers(dest="dcmd", required=True)

    p_list = dsub.add_parser("list", help="List built-in domain packs.")
    p_list.set_defaults(func=_cmd_domains_list)

    p_info = dsub.add_parser("info", help="Show detailed info for domain packs.")
    p_info.add_argument("--domains", nargs="*", required=True,
                        help="Domain packs (modules or folders) to inspect.")
    p_info.set_defaults(func=_cmd_domains_info)

    return p


# -------------------- entrypoint --------------------
def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    # dispatch
    if hasattr(args, "func"):
        rc = args.func(args)
        sys.exit(rc)
    else:
        parser.print_help()
        sys.exit(2)


if __name__ == "__main__":
    main()
