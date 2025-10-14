# 🧠 NER-SDK — Modular Named Entity Recognition Framework

> **NER-SDK** is an open, pluggable framework for rule-based Named Entity Recognition (NER).  
> Build, extend, and deploy custom NER domains — *finance, medical, legal, or your own* — without writing complex ML pipelines.

---

<p align="center">
  <img src="https://img.shields.io/badge/python-3.9%2B-blue" />
  <img src="https://img.shields.io/github/license/yourusername/ner-sdk" />
  <img src="https://img.shields.io/github/actions/workflow/status/yourusername/ner-sdk/tests.yml?label=tests" />
  <img src="https://img.shields.io/badge/docs-available-brightgreen" />
</p>

---

## ✨ Features

- 🔹 **Pluggable Domains** – add `finance`, `medical`, `legal`, or custom NER packs in minutes  
- 🔹 **Declarative Rules** – define entities in simple YAML, not code  
- 🔹 **Optional Hooks** – write Python logic only when needed  
- 🔹 **CLI Ready** – tag, validate, list, and inspect directly from the command line  
- 🔹 **Extensible Architecture** – hybrid ML + rule integration via adapters  
- 🔹 **Developer-Friendly** – fully documented and unit-tested  

---

## 🧱 Project Layout

```

ner-sdk/
├─ src/ner_sdk/
│  ├─ core/                  # tokenization + resolver logic
│  ├─ domains/               # pluggable domain packs
│  │  ├─ finance/
│  │  ├─ medical/
│  │  └─ ...
│  ├─ labeler.py             # BIO tagging logic
│  ├─ loader.py              # domain pack loader
│  ├─ cli.py                 # command-line entrypoints
│  └─ io_utils.py            # JSON/JSONL helpers
└─ docs/                     # developer and architecture docs

````

---

## 🚀 Quick Start

### 1️⃣ Install (development mode)

```bash
git clone https://github.com/<your-username>/ner-sdk.git
cd ner-sdk
pip install -e .
````

### 2️⃣ Verify setup

```bash
nersdk doctor
```

Expected output:

```
🔍 Checking pack: ner_sdk.domains.finance
  ✅ patterns.yaml found (4 entity patterns)
  ✅ hooks.py found and custom_match callable loaded
✅ All domain packs look healthy!
```

### 3️⃣ Tag your text

Create `raw.txt`:

```text
AAPL rose 5% to $150 in Q2
Patient prescribed 500 mg Paracetamol twice daily
```

Run:

```bash
nersdk tag --in raw.txt --out labeled.jsonl --domains ner_sdk.domains.finance ner_sdk.domains.medical
```

Output (`labeled.jsonl`):

```json
{"text": "AAPL rose 5% to $150 in Q2", "labels": "O O B-PERCENT O B-MONEY O B-DATE_Q"}
{"text": "Patient prescribed 500 mg Paracetamol twice daily", "labels": "O O B-DOSAGE O B-DRUG O B-FREQUENCY"}
```

---

## 🧩 Available CLI Commands

| Command               | Description                                     |
| --------------------- | ----------------------------------------------- |
| `nersdk tag`          | Label input texts with one or more domain packs |
| `nersdk doctor`       | Validate domain pack health                     |
| `nersdk domains list` | List all built-in domains                       |
| `nersdk domains info` | Show detailed info per domain                   |
| `nersdk roundtrip`    | Convert between JSON and JSONL formats          |

---

## 🧰 Example Domain: Finance

**`src/ner_sdk/domains/finance/patterns.yaml`**

```yaml
entities:
  - name: MONEY
    kind: regex-token
    pattern: "^[\\$€£]\\d+(?:\\.\\d{1,2})?$"
  - name: PERCENT
    kind: regex-token
    pattern: "^\\d+(\\.\\d+)?%$"
  - name: TICKER
    kind: regex-token
    pattern: "^[A-Z]{1,5}$"
  - name: DATE_Q
    kind: regex-token
    pattern: "^(Q[1-4])$"
```

---

## 🧠 Architecture Snapshot

```
CLI Layer (nersdk tag / doctor / domains)
        │
        ▼
Labeler → Loader → Resolver
        │        │
        ▼        ▼
   Domain Packs  Core Utils
     (YAML + hooks)
```

* Each **domain pack** is self-contained.
* Loader dynamically imports and merges multiple domains.
* Labeler unifies regex, phrase, and hook-based entities.

👉 Full details in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

---

## 📘 Developer Documentation

| Topic                                        | File                                               |
| -------------------------------------------- | -------------------------------------------------- |
| Developer guide (how to add domains/rules)   | [docs/DEVELOPER_GUIDE.md](docs/DEVELOPER_GUIDE.md) |
| Architecture internals                       | [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)       |
| Extension recipes (CLI, hybrid ML, adapters) | [docs/EXTENDING_SDK.md](docs/EXTENDING_SDK.md)     |
| Contribution process                         | [CONTRIBUTING.md](CONTRIBUTING.md)                 |

---

## 💡 Example: Add Your Own Domain

```bash
# 1. Create folder
mkdir -p src/ner_sdk/domains/legal

# 2. Add YAML
echo "entities:\n  - name: LAW_SECTION\n    kind: regex-token\n    pattern: '^[A-Z]+\\s?\\d{1,3}[A-Z]?$'" > src/ner_sdk/domains/legal/patterns.yaml

# 3. Verify
nersdk doctor --domains ner_sdk.domains.legal
```

---

## 🧪 Run Tests

```bash
pytest -q
```

---

## 🤝 Contributing

Contributions are welcome!
Please read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request.

You can:

* Add new domain packs
* Extend CLI features
* Improve docs or examples
* Add test coverage

---

## 🛡️ License

[MIT License](LICENSE)

---

## 🌟 Acknowledgements

Inspired by:

* [spaCy](https://spacy.io)
* [Hugging Face Transformers](https://huggingface.co)
* [John Snow Labs Spark NLP](https://nlp.johnsnowlabs.com)

NER-SDK bridges rule-based and declarative NLP with modularity and openness.
*Built for developers who want clarity, speed, and control.*

---

### 🧩 Let’s build domain-smart NER together.

```
pip install -e .
nersdk doctor
nersdk domains list
```

---

```

---

✅ **Summary:**
- Clean project intro + usage example
- Direct links to `DEVELOPER_GUIDE.md`, `ARCHITECTURE.md`, `EXTENDING_SDK.md`, and `CONTRIBUTING.md`
- Markdown table layout and diagram optimized for GitHub
- Lightweight and readable on mobile


