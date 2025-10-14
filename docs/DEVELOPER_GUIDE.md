It includes:

* ✅ Quick-start domain guide
* ✅ Full architecture explanation
* ✅ A simple ASCII-diagram showing data flow (`core → loader → labeler → CLI`)
* ✅ Clear sections for future contributors

---


# 🧩 NER-SDK Developer Guide

> **Version:** 1.0.0  
> **Audience:** Developers extending or maintaining the SDK  
> **Purpose:** How to add new domains, rules, or CLI features safely and clearly  

---

## 🚀 Quick Start — Add a New Domain (10-Step Summary)

| Step | Action |
|------|--------|
| **1.** | Create folder under `src/ner_sdk/domains/<your_domain>/` |
| **2.** | Add an empty `__init__.py` |
| **3.** | Create `patterns.yaml` describing entities (regex or phrases) |
| **4.** | Optionally add `hooks.py` with a `custom_match()` function |
| **5.** | Update `pyproject.toml` → include your `patterns.yaml` under `package-data` |
| **6.** | Reinstall in editable mode: `pip install -e .` |
| **7.** | Validate: `nersdk doctor --domains ner_sdk.domains.<your_domain>` |
| **8.** | Check it appears in `nersdk domains list` |
| **9.** | Try: `nersdk tag --in raw.txt --out out.jsonl --domains ner_sdk.domains.<your_domain>` |
| **10.** | Add a test in `tests/` verifying expected labels |

---

## 🧠 Overview

NER-SDK is a **modular, rule-based Named Entity Recognition (NER) framework**.

It supports:
- 🔹 **Core engine** for tokenization and BIO tagging  
- 🔹 **Pluggable domain packs** (e.g., finance, medical, legal)  
- 🔹 **CLI tools** for labeling, inspection, and diagnostics  
- 🔹 **Editable extension model** for new domain creation  

---

## 🧱 Architecture Diagram

```

```
            ┌──────────────────────────────┐
            │         CLI Layer             │
            │  (nersdk tag / doctor / ...)  │
            └──────────────┬───────────────┘
                           │
                           ▼
            ┌──────────────────────────────┐
            │          Labeler             │
            │ generate_ner_labels(), BIO   │
            └──────────────┬───────────────┘
                           │
                           ▼
            ┌──────────────────────────────┐
            │           Loader             │
            │ load_pack(), merge rules     │
            └──────────────┬───────────────┘
                           │
                           ▼
            ┌──────────────────────────────┐
            │        Domain Packs          │
            │  finance / medical / legal   │
            │  ├─ patterns.yaml            │
            │  └─ hooks.py (optional)      │
            └──────────────┬───────────────┘
                           │
                           ▼
            ┌──────────────────────────────┐
            │          Core Utils          │
            │  tokenization, resolver, IO  │
            └──────────────────────────────┘
```

```

**Flow summary:**  
1. CLI calls `bulk_tag()`  
2. Loader imports selected domain packs  
3. Labeler merges regex, phrase, and hook results  
4. Output saved as JSON/JSONL  

---

## 📁 Project Structure

```

ner-sdk/
├─ pyproject.toml
├─ README.md
├─ docs/
│  └─ DEVELOPER_GUIDE.md
├─ src/
│  └─ ner_sdk/
│     ├─ core/
│     ├─ domains/
│     │  ├─ finance/
│     │  │  ├─ patterns.yaml
│     │  │  ├─ hooks.py
│     │  │  └─ **init**.py
│     │  ├─ medical/
│     │  │  ├─ patterns.yaml
│     │  │  ├─ hooks.py
│     │  │  └─ **init**.py
│     │  └─ **init**.py
│     ├─ labeler.py
│     ├─ loader.py
│     ├─ resolve.py
│     ├─ io_utils.py
│     ├─ cli.py
│     └─ **init**.py
└─ tests/
└─ test_finance_pack.py

````

---

## ⚙️ Core Concepts

### 🧩 Domain Pack

Each **domain pack** contributes patterns (in YAML) and optional procedural hooks (`hooks.py`).

Example usage:
```bash
nersdk tag --in raw.txt --out tagged.jsonl --domains ner_sdk.domains.finance ner_sdk.domains.medical
````

---

### 🧾 YAML Schema (`patterns.yaml`)

| Field              | Type      | Description                               |
| ------------------ | --------- | ----------------------------------------- |
| `name`             | str       | Label for entity (`MONEY`, `ICD10`, etc.) |
| `kind`             | str       | `regex-token` or `phrase`                 |
| `pattern`          | str       | Regex pattern (if kind=regex-token)       |
| `phrases`          | list[str] | Literal phrases (if kind=phrase)          |
| `case_insensitive` | bool      | Optional case flag                        |

#### Example (Finance)

```yaml
entities:
  - name: MONEY
    kind: regex-token
    pattern: "^[\\$€£]\\d+(?:\\.\\d{1,2})?$"
  - name: PERCENT
    kind: regex-token
    pattern: "^\\d+(\\.\\d+)?%$"
```

#### Example (Medical)

```yaml
entities:
  - name: DRUG
    kind: regex-token
    case_insensitive: true
    pattern: "^(aspirin|metformin|ibuprofen)$"
```

---

### 🪄 Hook Function (`hooks.py`)

```python
def custom_match(tokens: list[str]) -> list[dict]:
    """
    Return spans like {"start": 3, "end": 5, "label": "FREQUENCY"}.
    """
    spans = []
    for i in range(len(tokens)-1):
        if tokens[i].lower() == "twice" and tokens[i+1].lower() == "daily":
            spans.append({"start": i, "end": i+2, "label": "FREQUENCY"})
    return spans
```

Use hooks for:

* Multi-token expressions (e.g., “once every week”)
* Contextual patterns beyond regex capabilities

---

## 🔧 Loader + Labeler Flow

### Loader (`loader.py`)

1. Detects module vs. path
2. Reads `patterns.yaml`
3. Imports `hooks.py` (if present)
4. Returns a `DomainPack`:

   ```python
   class DomainPack:
       name: str
       base: Path
       patterns: list[dict]
       hook_fn: Optional[Callable]
   ```

### Labeler (`labeler.py`)

1. Tokenizes text
2. Applies YAML regexes + phrases
3. Runs `custom_match()` hooks
4. Resolves overlaps
5. Outputs BIO tag strings

---

## 🧪 Testing

Run all tests:

```bash
pytest -q
```

Sample test:

```python
def test_money_percent_ticker():
    s = "AAPL rose 5% to $150 in Q2"
    labels = generate_ner_labels(s, domains=["ner_sdk.domains.finance"])
    assert "B-PERCENT" in labels
```

---

## 🧰 CLI Reference

| Command               | Description                      |
| --------------------- | -------------------------------- |
| `nersdk tag`          | Label text lines from input file |
| `nersdk doctor`       | Validate domain packs            |
| `nersdk domains list` | List built-in domain packs       |
| `nersdk domains info` | Detailed info for given packs    |
| `nersdk roundtrip`    | Convert JSON ↔ JSONL             |

---

## 🩺 Doctor Command

Checks each pack for:

* Existence of `patterns.yaml`
* Valid YAML syntax
* Optional hook function

Example:

```
nersdk doctor — environment diagnostics

🔍 Checking pack: ner_sdk.domains.finance
  ✅ patterns.yaml found (4 entity patterns)
  ✅ hooks.py found and custom_match callable loaded

✅ All domain packs look healthy!
```

---

## 🧩 Extending Core Rules

1. Open `src/ner_sdk/core/` or `labeler.py`
2. Add or modify token matching logic
3. Write a test case in `tests/`
4. Run `pytest`

Common extensions:

* Add new regexes
* Improve tokenization
* Create specialized span resolver

---

## 🧠 Extending CLI

To add a new subcommand:

1. Define `_cmd_<name>(args)` in `cli.py`
2. Register parser via `build_parser()`
3. Bind with `set_defaults(func=_cmd_<name>)`
4. Follow SDK print style for user feedback

---

## 📊 Example Workflow

```bash
# Create input
echo "AAPL rose 5% to $150 in Q2" > raw.txt
echo "Patient prescribed 500 mg Paracetamol twice daily" >> raw.txt

# Tag with both domains
nersdk tag --in raw.txt --out labeled.jsonl --domains ner_sdk.domains.finance ner_sdk.domains.medical

# Inspect domains
nersdk domains list
nersdk domains info --domains ner_sdk.domains.finance ner_sdk.domains.medical

# Validate packs
nersdk doctor
```

---

## 🧭 Roadmap

| Feature                         | Status  |
| ------------------------------- | ------- |
| `nersdk scaffold domain <name>` | Planned |
| spaCy / HF adapters             | Planned |
| Evaluation metrics module       | Planned |
| `nersdk doctor --list` alias    | Planned |
| Multi-language tokenization     | Planned |

---

## ✅ Summary

| Goal               | Modify                          |
| ------------------ | ------------------------------- |
| Add entity         | `patterns.yaml`                 |
| New domain         | `src/ner_sdk/domains/<domain>/` |
| Add rule logic     | `hooks.py`                      |
| Extend engine      | `labeler.py` / `resolve.py`     |
| Add CLI command    | `cli.py`                        |
| Add tests          | `tests/`                        |
| Verify environment | `nersdk doctor`                 |
| List domains       | `nersdk domains list/info`      |

---

*Document maintained by NER-SDK Core Team — feel free to extend or contribute new domain packs.*

