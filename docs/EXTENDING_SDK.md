📄 **`docs/EXTENDING_SDK.md`**

---

# 🔧 Extending the NER-SDK

> **Goal:** Provide practical, safe recipes for extending the SDK — so contributors can innovate **without breaking existing functionality**.

---

## 🧭 Guiding Principles

1. **Never edit `core/` logic unless you’re fixing or improving general behavior.**  
   (Domains and hooks should solve 95% of customization.)

2. **Follow the declarative-first approach:**  
   - Add or change behavior via `patterns.yaml`  
   - Only use Python hooks when absolutely necessary.

3. **One domain = one responsibility.**  
   - Finance rules live in `domains/finance/`  
   - Medical rules live in `domains/medical/`  
   - No cross-domain imports.

4. **Every change must pass:**
   ```bash
   pytest -q
   nersdk doctor
````

---

## 🪄 1. Add a New CLI Command

Example: You want to add `nersdk validate` that checks YAML syntax.

### Step-by-Step

1. **Open** `src/ner_sdk/cli.py`

2. **Create the handler:**

   ```python
   def _cmd_validate(args: argparse.Namespace) -> int:
       from .loader import load_pack
       ok = True
       for name in args.domains or ["ner_sdk.domains.finance"]:
           try:
               load_pack(name)
               print(f"✅ {name} valid")
           except Exception as e:
               ok = False
               print(f"❌ {name} failed: {e}")
       return 0 if ok else 1
   ```

3. **Register it in `build_parser()`:**

   ```python
   p_val = sub.add_parser("validate", help="Validate YAMLs and hooks for domain packs.")
   p_val.add_argument("--domains", nargs="*", default=[], help="Domains to validate.")
   p_val.set_defaults(func=_cmd_validate)
   ```

4. **Test it:**

   ```bash
   nersdk validate --domains ner_sdk.domains.finance
   ```

✅ That’s all. Every CLI command is just a function + parser registration.

---

## 🧩 2. Add a New Domain Pack

### Folder Template

```
src/ner_sdk/domains/<domain>/
├─ patterns.yaml
├─ hooks.py   (optional)
└─ __init__.py
```

### YAML Template

```yaml
entities:
  - name: ENTITY_LABEL
    kind: regex-token
    pattern: "<regex>"
  - name: PHRASE_ENTITY
    kind: phrase
    phrases:
      - "keyword 1"
      - "keyword 2"
```

### Hook Template (optional)

```python
def custom_match(tokens):
    spans = []
    # tokens = ["word1", "word2", ...]
    for i in range(len(tokens)-1):
        if tokens[i].lower() == "special" and tokens[i+1].lower() == "case":
            spans.append({"start": i, "end": i+2, "label": "SPECIAL_CASE"})
    return spans
```

### Register in `pyproject.toml`

```toml
[tool.setuptools.package-data]
"ner_sdk.domains.<domain>" = ["patterns.yaml"]
```

### Test and Verify

```bash
pip install -e .
nersdk doctor --domains ner_sdk.domains.<domain>
nersdk domains list
```

---

## ⚗️ 3. Add a Hybrid (ML + Rule) Domain

Sometimes a domain benefits from both **regex rules** and **machine-learned predictions**
(e.g., product names or medical entities that can’t be captured with patterns).

### Example: `domains/biomedical/`

1. **`patterns.yaml`** — keeps the high-precision rules.

2. **`hooks.py`** — load an ML model to propose additional spans:

   ```python
   from transformers import pipeline
   _model = pipeline("ner", model="dslim/bert-base-NER")

   def custom_match(tokens):
       text = " ".join(tokens)
       results = _model(text)
       spans = []
       for r in results:
           spans.append({"start": r["index"]-1, "end": r["index"], "label": r["entity_group"]})
       return spans
   ```

3. Run `nersdk doctor` — it will still pass because the hook is callable.

> ⚠️ Avoid heavy imports in top-level scope.
> Lazy-load ML models inside `custom_match()` to keep CLI startup fast.

---

## 🧩 4. Add or Modify Core Rules

When to modify the core:

* To improve tokenization
* To adjust span conflict resolution
* To add a new matching strategy globally

### Example: Add Numeric Range Detection

1. Edit `labeler.py`

   ```python
   if re.fullmatch(r"\d+\s?-\s?\d+", tok):
       labels[i] = "B-RANGE"
   ```

2. Add test under `tests/`.

3. Run:

   ```bash
   pytest -q
   ```

---

## 🧠 5. Integrate spaCy or Hugging Face (Adapters)

NER-SDK can cooperate with existing NLP frameworks.

### spaCy Adapter (optional add-on)

Create a module `src/ner_sdk/adapters/spacy_adapter.py`:

```python
import spacy

def spacy_to_sdk(doc):
    return [{"start": ent.start, "end": ent.end, "label": ent.label_} for ent in doc.ents]

def run_spacy(text, model="en_core_web_sm"):
    nlp = spacy.load(model)
    doc = nlp(text)
    return spacy_to_sdk(doc)
```

### Hugging Face Adapter

```python
from transformers import pipeline
ner_pipe = pipeline("ner", model="dslim/bert-base-NER")

def hf_to_sdk(results):
    return [{"start": r["index"]-1, "end": r["index"], "label": r["entity_group"]} for r in results]

def run_hf(text):
    return hf_to_sdk(ner_pipe(text))
```

Adapters can be combined with domain rules inside `custom_match()` functions.

---

## 🧩 6. Extend the Resolver Logic

By default, `resolve.py` prefers:

* longer spans
* higher domain priority

You can override it by subclassing or replacing the function.

```python
def merge_spans(spans):
    # Example: prefer finance over all others
    spans.sort(key=lambda x: (x["label"] != "MONEY", -len(x["label"])))
    return spans
```

Replace in `labeler.py` if needed.

---

## 🔍 7. Add Automated Tests

Always accompany new code with unit tests.

### Example: `tests/test_medical_pack.py`

```python
from ner_sdk.labeler import generate_ner_labels

def test_drug_and_dosage():
    s = "500 mg Paracetamol twice daily"
    labels = generate_ner_labels(s, domains=["ner_sdk.domains.medical"])
    assert "B-DOSAGE" in labels
    assert "B-FREQUENCY" in labels
```

Run tests locally before pushing:

```bash
pytest -q
```

---

## ⚙️ 8. Versioning & Contribution Workflow

| Action      | Command                             |
| ----------- | ----------------------------------- |
| Format code | `black src/ tests/`                 |
| Run tests   | `pytest -q`                         |
| Check packs | `nersdk doctor`                     |
| Commit      | `git commit -m "Add <domain> pack"` |
| Tag release | `git tag v1.1.0`                    |

### Pull Request Checklist

* [ ] All tests pass
* [ ] `nersdk doctor` reports healthy
* [ ] New files documented in `DEVELOPER_GUIDE.md`
* [ ] New entity labels added to tests

---

## 📘 9. Common Anti-Patterns (Don’t Do)

❌ Hardcoding patterns inside Python
✅ Always use `patterns.yaml`

❌ Mixing multiple domains in one folder
✅ Each domain = one subpackage

❌ Importing `ner_sdk.domains.<other_domain>` inside a hook
✅ Keep hooks self-contained

❌ Heavy ML imports at top level
✅ Lazy-load inside `custom_match()`

---

## 🧩 10. Suggested Extension Ideas

| Idea                 | Description                                 |
| -------------------- | ------------------------------------------- |
| `legal` domain       | Detect “Section 5 of IPC”, “Act 1956”, etc. |
| `ecommerce` domain   | Detect SKU, product names, discount %       |
| `geography` domain   | Detect countries, cities, lat/long patterns |
| `biomedical` domain  | Integrate BioBERT for gene/protein entities |
| `socialmedia` domain | Detect hashtags, mentions, URLs             |

---

## 🧭 Summary

| Extension Type | Edit Files                  | Run Commands    |
| -------------- | --------------------------- | --------------- |
| CLI Command    | `cli.py`                    | `nersdk --help` |
| New Domain     | `domains/<domain>/`         | `nersdk doctor` |
| Core Rule      | `labeler.py` / `resolve.py` | `pytest -q`     |
| Hybrid ML      | `hooks.py` + adapters       | `nersdk tag`    |
| Resolver       | `resolve.py`                | `pytest -q`     |
| Test           | `tests/`                    | `pytest`        |

---

### 💬 Contribution Philosophy

> Every domain should be self-contained, documented, and testable in isolation.

By following this guide, external developers can safely:

* Add new knowledge domains
* Extend the CLI
* Integrate third-party models
* Maintain 100% backward compatibility

---

*Maintained by the NER-SDK Core Team — contributions welcome via pull requests!*
