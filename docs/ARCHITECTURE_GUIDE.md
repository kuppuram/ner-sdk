📄 **`docs/ARCHITECTURE.md`**

---

# 🧩 NER-SDK Architecture

> **Version:** 1.0.0  
> **Purpose:** Explain the internal design, module interactions, and extension hooks for developers.  
> **Audience:** Contributors extending the SDK’s core engine, loader, or CLI.

---

## 🧠 High-Level Concept

NER-SDK implements a **layered, declarative-to-procedural pipeline**:

```

Input text
│
▼
┌──────────────┐
│ Tokenizer    │  → splits text into normalized tokens
└──────────────┘
│
▼
┌────────────────────┐
│  Domain Loader     │  → loads patterns.yaml and optional hooks.py
└────────────────────┘
│
▼
┌────────────────────┐
│  Labeler           │  → applies regex, phrase, and hook-based rules
└────────────────────┘
│
▼
┌────────────────────┐
│  Resolver          │  → merges overlaps, produces final spans
└────────────────────┘
│
▼
┌────────────────────┐
│  IO Utils / CLI    │  → saves tagged output, orchestrates CLI commands
└────────────────────┘

````

---

## ⚙️ Module Overview

### 1. `core/`
Low-level components used by all other modules.

| File | Purpose |
|------|----------|
| `tokenize.py` | Splits input into normalized tokens |
| `resolve.py` | Handles overlapping entity spans |
| `utils.py` | Common helpers and constants |

All functions here are *domain-agnostic*.  

---

### 2. `loader.py`

Responsible for discovering and loading **domain packs**.

#### Key Functions
```python
def load_pack(name_or_path: str, priority: int = 50) -> DomainPack
````

#### `DomainPack` structure:

```python
@dataclass
class DomainPack:
    name: str
    base: Path
    patterns: list[dict]
    hook_fn: Optional[Callable]
    priority: int
```

#### Loader Workflow

1. Detects whether `name_or_path` is:

   * A Python module (e.g., `ner_sdk.domains.finance`)
   * A filesystem folder (`./packs/finance`)
2. Loads `patterns.yaml`
3. Dynamically imports `hooks.py` (if exists)
4. Returns a structured `DomainPack`

#### Loader Extension Points

* Add new domain packs under `src/ner_sdk/domains/`
* Optionally extend to support remote or JSON-defined patterns

---

### 3. `labeler.py`

Converts text → BIO tags.

#### Key Functions

```python
def generate_ner_labels(text: str, domains: List[str]) -> str
def bulk_tag(texts: List[str], domains: List[str]) -> list[dict]
```

#### Responsibilities

* Tokenizes input
* Iterates through all active `DomainPack`s
* Applies regex and phrase rules from YAML
* Executes `custom_match()` from each `hooks.py`
* Resolves overlapping spans via `resolve.py`
* Converts final spans → BIO string

#### Extension Points

* Modify tokenization (add smarter handling for punctuation)
* Add new rule types (e.g., contextual, numeric-range)
* Integrate ML classifiers as hybrid modules

---

### 4. `resolve.py`

Merges conflicting or overlapping spans between packs.

Typical rules:

* Prefer longer spans over shorter ones
* Resolve conflicts by domain priority
* Eliminate duplicates

Can be replaced or extended to use advanced span-merging algorithms.

---

### 5. `io_utils.py`

Handles all JSON/JSONL I/O.

| Function                        | Description                  |
| ------------------------------- | ---------------------------- |
| `save_json(data, path, pretty)` | Write list of dicts to JSON  |
| `save_jsonl(data, path)`        | Write newline-delimited JSON |
| `load_json(path)`               | Load JSON file               |
| `load_jsonl(path)`              | Load JSONL file              |

This module ensures consistent data exchange format across CLI and programmatic use.

---

### 6. `cli.py`

Implements the **Command-Line Interface** entry point.

#### Commands

| Command                    | Description          |
| -------------------------- | -------------------- |
| `nersdk tag`               | Tag input text lines |
| `nersdk doctor`            | Validate packs       |
| `nersdk domains list/info` | Explore domain packs |
| `nersdk roundtrip`         | Convert JSON ↔ JSONL |

Each subcommand maps to a `_cmd_<name>(args)` function, registered via:

```python
parser.set_defaults(func=_cmd_tag)
```

---

### 7. `domains/`

Self-contained modules defining **domain-specific knowledge**.

Example layout:

```
ner_sdk/domains/finance/
├─ patterns.yaml
├─ hooks.py
└─ __init__.py
```

#### `patterns.yaml`

Contains declarative entity definitions.

```yaml
entities:
  - name: MONEY
    kind: regex-token
    pattern: "^[\\$€£]\\d+(?:\\.\\d{1,2})?$"
  - name: PERCENT
    kind: regex-token
    pattern: "^\\d+(\\.\\d+)?%$"
```

#### `hooks.py`

Contains optional procedural rules.

```python
def custom_match(tokens):
    # "top 10 companies" → detect "top 10"
    spans = []
    for i, t in enumerate(tokens[:-1]):
        if t.lower() == "top" and tokens[i+1].isdigit():
            spans.append({"start": i, "end": i+2, "label": "RANK"})
    return spans
```

---

## 🔄 Data Flow Summary

```
[ Text Input ]
      │
      ▼
Tokenization (core)
      │
      ▼
Domain Loader → Load all packs
      │
      ▼
Pattern Matching → regex-token, phrase
      │
      ▼
Hook Execution → procedural spans
      │
      ▼
Span Resolver → merge overlaps
      │
      ▼
BIO Label Builder
      │
      ▼
[ JSON / JSONL Output ]
```

---

## 🧩 Extension Hooks

You can extend NER-SDK at three levels:

| Layer      | Hook Type     | Example                                      |
| ---------- | ------------- | -------------------------------------------- |
| **Domain** | YAML or Hook  | Add new `patterns.yaml` or `custom_match()`  |
| **Core**   | Rule/Resolver | Modify `labeler.py` / `resolve.py`           |
| **CLI**    | Command       | Add `_cmd_<name>()` and register in `cli.py` |

---

## 🧠 How `nersdk doctor` Works

`doctor` is a self-check command that ensures integrity across packs.

Algorithm:

1. Import pack via `load_pack()`
2. Check `patterns.yaml` existence and syntax
3. Check for callable `custom_match`
4. Report issues (missing, invalid, or malformed)

---

## 🧪 Typical Developer Workflows

| Goal            | Files to Modify                 | Commands to Run |
| --------------- | ------------------------------- | --------------- |
| Add new domain  | `src/ner_sdk/domains/<domain>/` | `nersdk doctor` |
| Add regex rule  | `patterns.yaml`                 | `pytest`        |
| Add custom rule | `hooks.py`                      | `pytest`        |
| Extend core     | `labeler.py`, `resolve.py`      | `pytest`        |
| Add CLI feature | `cli.py`                        | `nersdk --help` |
| Run tests       | `tests/`                        | `pytest -q`     |

---

## 🧮 Example Call Flow

```mermaid
graph TD
A[CLI: nersdk tag] --> B[labeler.bulk_tag()]
B --> C[loader.load_pack()]
C --> D[patterns.yaml + hooks.py]
B --> E[resolver.merge_spans()]
E --> F[io_utils.save_json()]
```

---

## 🔍 Module Dependency Graph

```
cli.py
  ├── labeler.py
  │     ├── loader.py
  │     │     └── core/
  │     ├── resolve.py
  │     └── core/
  ├── io_utils.py
  └── loader.py
```

---

## 🧭 Design Principles

* **Declarative-first**: Prefer `patterns.yaml` over hardcoded logic.
* **Composable**: Multiple domain packs can be loaded simultaneously.
* **Pluggable**: No modification of core code is required to add new domains.
* **Transparent I/O**: Data always saved in open formats (JSON/JSONL).
* **CLI parity**: Everything callable via both CLI and Python API.

---

## 🧩 Future Architectural Plans

| Area      | Improvement                                              |
| --------- | -------------------------------------------------------- |
| Tokenizer | Replace with regex-aware tokenizer for multilingual text |
| Resolver  | Graph-based overlap handling                             |
| Core      | Optional embedding layer for hybrid rule+ML              |
| Domains   | Auto-discovery & pip-installable domain packs            |
| CLI       | `nersdk scaffold domain <name>` generator                |

---

## 🏁 Summary

NER-SDK is structured for clarity, modularity, and domain specialization.

When extending:

1. Keep new logic within the relevant domain folder.
2. Never modify another domain’s rules directly.
3. Use `nersdk doctor` before committing.
4. Add tests for every new entity or hook.

---

*Maintained by the NER-SDK Core Team. Contributions are welcome.*


