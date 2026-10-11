# 🤝 Contributing to Z.Dip

We welcome contributions from the community! Whether you want to add support for a new streaming service, reinforce existing protocol extractors, enhance cloud storage integrations, or fix a bug, here is how you can help.

---

## 🛠️ Development Setup

1. **Fork and clone the repository:**
   ```bash
   git clone https://github.com/mayankreseracher/Z.Dip.git
   cd Z.Dip
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies in editable mode:**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   pip install -e .
   ```

4. **Run the test suite:**
   ```bash
   pytest tests/ -v
   ```

---

## 🧩 Adding a New Protocol Extractor

1. Inherit from `BaseProtocolExtractor` in `zdip/protocols/base.py`.
2. Register your class using `@register_protocol`.
3. Implement `can_handle(url)` and `extract(url, options)`.
4. Add unit tests in `tests/test_protocols.py`.
5. Submit a pull request!

---

## 📜 Pull Request Guidelines

- Ensure all existing unit tests in `tests/` pass.
- Write clear commit messages using the Conventional Commits format (`feat: ...`, `fix: ...`, `docs: ...`).
- Never commit private secrets or API keys (respect our zero-knowledge policy).

Thank you for helping make Z.Dip faster, more private, and universal!
