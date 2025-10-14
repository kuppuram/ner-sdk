🧠 NER-SDK Developer Guide
1. Overview

NER-SDK is a lightweight, modular framework for rule-based Named Entity Recognition (NER).
It provides:

🔹 Core rule engine (tokenizer, BIO label builder)

🔹 Domain packs (finance, medical, …) that supply YAML patterns and Python hooks

🔹 CLI tools (nersdk tag, nersdk doctor, nersdk domains list/info)

🔹 Pluggable loader to add new domains without editing core code

The SDK is structured for easy extension by domain experts — each new domain can bring its own patterns, hooks, and test sets.

2. Folder Structure
ner-sdk/
├─ pyproject.toml
├─ README.md
├─ src/
│  └─ ner_sdk/
│     ├─ core/                  # low-level tokenizer & BIO utilities
│     ├─ domains/               # domain packs live here
│     │  ├─ finance/
│     │  │  ├─ patterns.yaml
│     │  │  ├─ hooks.py
│     │  │  └─ __init__.py
│     │  ├─ medical/
│     │  │  ├─ patterns.yaml
│     │  │  ├─ hooks.py
│     │  │  └─ __init__.py
│     │  └─ __init__.py
│     ├─ labeler.py             # generates BIO labels
│     ├─ loader.py              # loads domain packs
│     ├─ resolve.py             # merges overlapping matches
│     ├─ io_utils.py            # JSON/JSONL read/write
│     ├─ cli.py                 # CLI command definitions
│     └─ __init__.py
└─ tests/
   └─ test_finance_pack.py

3. Core Concepts
3.1 Domain Pack

A domain pack is a mini-module containing:

patterns.yaml — declarative regex or phrase rules

hooks.py — optional procedural logic (custom_match())

__init__.py — marks it as a Python subpackage

Each pack corresponds to a domain like finance, medical, or legal.

Example usage:

nersdk tag --in raw.txt --out tagged.jsonl --domains ner_sdk.domains.finance ner_sdk.domains.medical

3.2 YAML Pattern Schema

Each pattern entry has:

Field	Type	Description
name	str	Label for the entity (e.g. MONEY, ICD10)
kind	str	Matching mode: regex-token or phrase
pattern	str	Regex expression (if kind=regex-token)
phrases	list[str]	Static list of strings (if kind=phrase)
case_insensitive	bool	Optional flag for matching
Example (finance)
entities:
  - name: MONEY
    kind: regex-token
    pattern: "^[\\$€£]\\d+(?:\\.\\d{1,2})?$"
  - name: PERCENT
    kind: regex-token
    pattern: "^\\d+(\\.\\d+)?%$"

Example (medical)
entities:
  - name: DRUG
    kind: regex-token
    case_insensitive: true
    pattern: "^(aspirin|metformin|ibuprofen)$"

3.3 Hook Function

hooks.py may optionally define:

def custom_match(tokens: list[str]) -> list[dict]:
    # return spans like {"start": 2, "end": 4, "label": "FREQUENCY"}
    ...


Used for logic that regex/phrases can’t express easily (e.g. cross-token patterns).

4. How It Works

nersdk labeler.generate_ner_labels(text, domains=...)

Tokenizes text into words.

Loads domain packs via loader.load_pack().

Matches tokens against YAML regexes and phrases.

Applies any custom_match() hooks.

Combines overlaps (using resolve.py).

Outputs BIO tag string.

nersdk tag CLI command

Reads lines from input file.

Calls bulk_tag() for each.

Writes JSON/JSONL dataset.

nersdk doctor

Validates pack structure, syntax, and callable hooks.

nersdk domains list/info

Lists built-in domains and entity counts.

5. Adding a New Domain Pack
Step 1. Create folder
src/ner_sdk/domains/legal/

Step 2. Add patterns.yaml
entities:
  - name: LAW_SECTION
    kind: regex-token
    pattern: "^[A-Z]+\\s?\\d{1,3}[A-Z]?$"
  - name: CASE_ID
    kind: regex-token
    pattern: "^(?:No\\.|Case)\\s?\\d{4}/\\d{2,4}$"

Step 3. Optional hooks.py
def custom_match(tokens):
    # detect "Section 5 of IPC"
    spans = []
    for i in range(len(tokens) - 2):
        if tokens[i].lower() == "section" and tokens[i+2].lower() == "ipc":
            spans.append({"start": i, "end": i+3, "label": "LAW_SECTION"})
    return spans

Step 4. Add __init__.py

(empty file)

Step 5. Update pyproject.toml
[tool.setuptools.package-data]
"ner_sdk.domains.legal" = ["patterns.yaml"]

Step 6. Reinstall in editable mode
pip install -e .

Step 7. Validate
nersdk doctor --domains ner_sdk.domains.legal

6. Adding New Core Rules

To modify tokenization or BIO assembly logic:

Edit src/ner_sdk/core/tokenize.py or src/ner_sdk/labeler.py

Ensure it outputs a flat list of tokens and BIO tags.

Add new regex categories or scoring heuristics there.

Always run unit tests after adding new rules.

7. Testing

All tests live under tests/.

Run:

pytest -q


Example:

def test_money_percent_ticker():
    s = "AAPL rose 5% to $150 in Q2"
    labels = generate_ner_labels(s, domains=["ner_sdk.domains.finance"])
    assert "B-PERCENT" in labels

8. CLI Reference
Command	Description
nersdk tag --in raw.txt --out tagged.jsonl --domains …	Tag text lines with NER labels
nersdk doctor [--domains …]	Validate domain packs
nersdk domains list	List available built-in domains
nersdk domains info --domains …	Show entity and hook info
nersdk roundtrip --in file --out file	Convert JSON↔JSONL
9. Internals: Loader Workflow

load_pack(name_or_path)

Detects whether name_or_path is a Python module (ner_sdk.domains.finance) or a path (./packs/finance).

Reads patterns.yaml and validates it.

Dynamically imports hooks.py (if present) and extracts custom_match.

Returns a DomainPack dataclass:

class DomainPack:
    name: str
    base: Path
    patterns: list[dict]
    hook_fn: Optional[Callable]

10. Extending the CLI (for advanced users)

To add new commands:

Define _cmd_<name>(args) at module level in cli.py.

Register it in build_parser() with set_defaults(func=_cmd_<name>).

Follow existing style for consistency and auto-help.

11. Tips

✅ Keep each domain self-contained — no cross-imports.

✅ Include patterns.yaml in pyproject.toml package-data.

✅ Use nersdk doctor after any changes.

✅ Write at least one pytest per new entity type.

✅ Prefer regex over procedural hooks when possible (faster).

12. Example End-to-End Workflow
# create raw input file
echo "AAPL rose 5% to $150 in Q2" > raw.txt
echo "Patient prescribed 500 mg Paracetamol twice daily" >> raw.txt

# tag with finance + medical
nersdk tag --in raw.txt --out tagged.jsonl --domains ner_sdk.domains.finance ner_sdk.domains.medical

# view entities
nersdk domains list
nersdk domains info --domains ner_sdk.domains.finance ner_sdk.domains.medical

# verify setup
nersdk doctor

13. Future Roadmap

 Add nersdk scaffold domain <name> → auto-generate new domain pack

 Add nersdk doctor --list alias

 Optional adapters: nersdk.spacy_adapter() / nersdk.hf_adapter()

 Add metrics module for precision/recall on labeled data

 Support language-specific tokenization

🏁 Summary
Area	Extend by
New entities	Edit patterns.yaml
New domain	Create subfolder under domains/
New rule logic	Add in hooks.py
New core behavior	Modify labeler.py / resolve.py
Test & validate	pytest, nersdk doctor
Inspect domains	nersdk domains list/info