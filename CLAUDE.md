# wlah, for whoever builds on it

The plugin is small on purpose. `style/card.md` is the product: every session sees it, so every line in it must earn its place. `scripts/wlah_check.py` is stdlib Python and the only code. The hook reads files and exits 0 whatever happens.

Rules for changes:

- Anything shipped as prose (the card, the presets, the README, `style/rules.md`) passes `python scripts/wlah_check.py --strict <file>` at NATURAL. `tests/test_readme.py` pins that.
- A new tell goes into the checker with a fixture that fails before the change and passes after it.
- Both manifests carry the same version, and `tests/test_package.py` pins the number. Bump all three together: the plugin cache is keyed by version.
- `python -m pytest tests/` must pass.
- Pushing to GitHub is the owner's word, never automatic.
