<p align="center">
  <a href="https://github.com/voroninsergei/triz-ai-patent-assistant/actions/workflows/ci.yml">
    <img src="https://github.com/voroninsergei/triz-ai-patent-assistant/actions/workflows/ci.yml/badge.svg" alt="CI Status" />
  </a>
  <a href="https://voroninsergei.github.io/triz-ai-patent-assistant/">
    <img src="https://img.shields.io/badge/docs-online-brightgreen" alt="Docs" />
  </a>
  <a href="https://pypi.org/project/triz-ai-patent-assistant/">
    <img src="https://img.shields.io/pypi/v/triz-ai-patent-assistant.svg" alt="PyPI Version" />
  </a>
  <a href="https://github.com/voroninsergei/triz-ai-patent-assistant/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/license-MIT-yellow" alt="License: MIT" />
  </a>
</p>

# TRIZ‑AI Patent Assistant

> **AI‑assisted toolkit for generating, validating and analysing patent claims using TRIZ methodology.**

---

## ✨ Features

- **Formula Generator** – creates patent claims from brief invention ideas.  
- **Prompt Enhancer** – refines claims and suggests non‑obvious improvements.  
- **Novelty / Patentability checks** (basic heuristics, extensible).  
- **Streamlit demo** & MkDocs documentation.

---

## 🚀 Installation

```bash
pip install triz-ai-patent-assistant
```

Install the development version:

```bash
pip install git+https://github.com/voroninsergei/triz-ai-patent-assistant.git
```

> Requires **Python 3.8+**.

---

## 🏁 Quick start

```python
from triz_ai.generate_formula import generate_formula

idea = "Устройство для подачи топлива с насосом"
print(generate_formula(idea))
```

Run the web demo:

```bash
streamlit run triz_ai/streamlit_app.py
```

See full API reference in the [📚 Documentation](https://voroninsergei.github.io/triz-ai-patent-assistant/).

---

## 🛠️  Development

1. **Clone** the repo & create virtual env.  
2. `pip install -e .[dev]` – installs testing/formatting tools.  
3. Run tests locally:
   ```bash
   pytest -q
   ```
4. Lint & format code:
   ```bash
   ruff check triz_ai && ruff format triz_ai
   ```

### Conventional commits
We follow the [Conventional Commits](https://www.conventionalcommits.org/) spec – this feeds the auto‑release workflow.

---

## 🤝 Contributing & Community

| 🙋 Что сделать            | Как                                                                              |
|---------------------------|----------------------------------------------------------------------------------|
| Сообщить об ошибке        | Откройте [Issue](https://github.com/voroninsergei/triz-ai-patent-assistant/issues) |
| Предложить улучшение      | Создайте Issue → Pull Request                                                     |
| Чат/вопросы               | Раздел **Discussions** в репозитории                                             |

Пожалуйста, читайте [CONTRIBUTING.md](CONTRIBUTING.md) и соблюдайте [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

---

## 📜 License

Distributed under the **MIT License** – see the [LICENSE](LICENSE) file for details.
