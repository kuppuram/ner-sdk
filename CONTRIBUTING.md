# 🤝 Contributing to NER-SDK

Welcome! 🎉  
Thank you for considering contributing to **NER-SDK**, an open, modular rule-based Named Entity Recognition framework.

Our goal is to make domain-specific NER **extensible, safe, and developer-friendly**.  
This guide explains how to set up your environment, follow the standards, and submit high-quality pull requests.

---

## 🧱 Table of Contents
1. [Setup](#-setup)
2. [Branching Model](#-branching-model)
3. [Coding Standards](#-coding-standards)
4. [Testing & Validation](#-testing--validation)
5. [Commit & PR Guidelines](#-commit--pr-guidelines)
6. [Adding Domains](#-adding-domains)
7. [Adding CLI Commands](#-adding-cli-commands)
8. [Code of Conduct](#-code-of-conduct)

---

## 🧩 Setup

```bash
# 1. Fork and clone the repo
git clone https://github.com/<your-user>/ner-sdk.git
cd ner-sdk

# 2. Create a virtual environment
python -m venv env
source env/bin/activate  # or on Windows: env\Scripts\activate

# 3. Install in editable mode
pip install -e .[dev]

# 4. Run the basic checks
pytest -q
nersdk doctor
````

---

## 🌿 Branching Model

We follow a **GitHub Flow** style:

| Branch                 | Purpose                             |
| ---------------------- | ----------------------------------- |
| `main`                 | Stable, released versions           |
| `develop`              | Next release (default for new work) |
| `feature/<short-name>` | New feature or enhancement          |
| `fix/<short-name>`     | Bug fix or hotfix                   |
| `docs/<short-name>`    | Documentation updates               |

### Example:

```bash
git checkout -b feature/add-legal-domain develop
```

When done, push and open a Pull Request into `develop`.

---

## 🧠 Coding Standards

| Area         | Guideline                                                                                                |
| ------------ | -------------------------------------------------------------------------------------------------------- |
| **Language** | Python 3.9+                                                                                              |
| **Style**    | [PEP 8](https://peps.python.org/pep-0008/) + [Black](https://github.com/psf/black) (`black src/ tests/`) |
| **Imports**  | Absolute imports only                                                                                    |
| **Typing**   | Use type hints everywhere                                                                                |
| **Docs**     | Each public function must have a short docstring                                                         |
| **Commits**  | Use conventional format (`feat:`, `fix:`, `docs:`, `refactor:`, etc.)                                    |

---

## 🧪 Testing & Validation

Before submitting any PR:

```bash
pytest -q              # All tests must pass
nersdk doctor          # All domain packs must load correctly
nersdk domains list    # Should list all expected packs
black --check src/     # Code formatted
```

If you add new functionality:

* Include unit tests in `tests/`
* Ensure coverage for new entity types, CLI commands, or core logic

---

## 🧰 Commit & PR Guidelines

**Commit Messages**

* Keep them atomic and descriptive.
* Use conventional prefixes:

  * `feat:` → new feature
  * `fix:` → bug fix
  * `docs:` → documentation change
  * `test:` → test addition or fix
  * `refactor:` → code restructuring
  * `chore:` → dependency or setup change

**Example:**

```
feat: add medical domain with ICD10 and dosage detection
```

**Pull Requests**

* PRs should target the `develop` branch.
* Include a short description of:

  * What you changed
  * Why you changed it
  * Any tests or commands to reproduce

---

## 🧩 Adding Domains

Follow the quick-start steps in [DEVELOPER_GUIDE.md](docs/DEVELOPER_GUIDE.md):

1. Create folder: `src/ner_sdk/domains/<domain>/`
2. Add:

   * `patterns.yaml`
   * optional `hooks.py`
   * blank `__init__.py`
3. Register your YAML in `pyproject.toml`
4. Verify via:

   ```bash
   nersdk doctor --domains ner_sdk.domains.<domain>
   ```
5. Add at least one test case.

> **Pro tip:** Run `nersdk domains list` — your domain should appear automatically.

---

## ⚙️ Adding CLI Commands

To add a new CLI command:

1. Define `_cmd_<name>(args)` in `src/ner_sdk/cli.py`
2. Register it in `build_parser()`
   Example:

   ```python
   p_val = sub.add_parser("validate", help="Validate YAML and hooks")
   p_val.set_defaults(func=_cmd_validate)
   ```
3. Test it:

   ```bash
   nersdk validate --domains ner_sdk.domains.finance
   ```

---

## 🧱 Documentation Updates

Docs live under the `/docs/` folder:

* `DEVELOPER_GUIDE.md` → how to build & extend
* `ARCHITECTURE.md` → module relationships
* `EXTENDING_SDK.md` → recipes for extending safely

If you add or rename modules, **update these docs** accordingly.

---

## Code of Conduct

All contributors are expected to:

* Be respectful and collaborative
* Use inclusive, constructive language
* Respect maintainers’ review decisions

Harassment, hate speech, or toxic behavior will result in permanent bans.

---

## ✅ Summary Checklist (Before PR)

| Check                        | Command             |
| ---------------------------- | ------------------- |
| Code formatted               | `black src/ tests/` |
| Tests pass                   | `pytest -q`         |
| Domain packs healthy         | `nersdk doctor`     |
| Docs updated                 | `docs/`             |
| Commit message clean         | `feat: ...`         |
| Branch created off `develop` | ✅                   |
| PR opened into `develop`     | ✅                   |

---

### 💬 Questions?

Open a [GitHub Issue](../../issues) for:

* Bug reports 🐞
* Feature suggestions 💡
* Documentation improvements 📘

---

*Maintained by the NER-SDK Core Team.
Let’s build a robust, extensible, and community-driven NER platform together! 🤝*


---

✅ **Summary:**
- This file belongs in your repo root (`CONTRIBUTING.md`).
- GitHub automatically displays it in the **Pull Request → “Contributing”** tab.
- It connects directly to your other docs (`docs/DEVELOPER_GUIDE.md`, `docs/ARCHITECTURE.md`, and `docs/EXTENDING_SDK.md`).

