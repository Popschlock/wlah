import json
from conftest import ROOT

def test_both_manifests_carry_the_same_version():
    """The plugin cache is keyed by version: a bump in one file and not the other serves stale code."""
    plugin = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
    market = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
    entries = market["plugins"]
    assert len(entries) == 1 and entries[0]["version"] == plugin["version"] == "0.1.0"
    assert entries[0]["description"] == plugin["description"]

def test_the_shipped_tree_is_complete():
    for p in ("skills/wlah/SKILL.md", "hooks/hooks.json", "hooks/session-start.py", "scripts/wlah_check.py",
              "style/card.md", "style/rules.md", "presets/terse.md", "presets/letter.md", "presets/resume.md",
              "README.md", "LICENSE", ".claudeignore"):
        assert (ROOT / p).is_file(), p

def test_the_hook_falls_back_from_python3_to_python():
    hooks = json.loads((ROOT / "hooks" / "hooks.json").read_text(encoding="utf-8"))
    cmd = hooks["hooks"]["SessionStart"][0]["hooks"][0]["command"]
    assert "python3" in cmd and "|| python" in cmd and "session-start.py" in cmd
    assert hooks["hooks"]["SessionStart"][0]["matcher"] == "startup|clear|compact"

def test_the_skill_names_its_three_verbs():
    text = (ROOT / "skills" / "wlah" / "SKILL.md").read_text(encoding="utf-8")
    assert text.startswith("---\nname: wlah\n")
    for verb in ("## /wlah <text or file>", "## /wlah check", "## /wlah voice"): assert verb in text
