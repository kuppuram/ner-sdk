# ner-sdk

Rule-based NER labeler + IO helpers (JSON / JSONL) with a simple CLI.

## Install (local dev)

```bash
pip install -e .

pip install pytest

pip install pyyaml

nersdk doctor

nersdk doctor --domains ./packs/medical ner_sdk.domains.finance

# run tests
pytest -q

# tag with core only
nersdk tag --in raw.txt --out out.jsonl

# tag with finance domain (built-in)
nersdk tag --in raw.txt --out out.json --domains ner_sdk.domains.finance

nersdk doctor --domains ner_sdk.domains.finance ner_sdk.domains.medical
nersdk doctor --domains ner_sdk.domains.medical ner_sdk.domains.medical

nersdk domains list
nersdk domains info --domains ner_sdk.domains.finance ner_sdk.domains.medical
nersdk tag --in raw.txt --out labeled.jsonl --domains ner_sdk.domains.finance ner_sdk.domains.medical
