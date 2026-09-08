"""Everything this plugin ships as prose passes its own checker, strictly. If a rule is worth giving
every session, the plugin's own words follow it."""
import pytest
import wlah_check as wc
from conftest import ROOT

PROSE = ["README.md", "style/card.md", "style/rules.md", "presets/terse.md", "presets/letter.md", "presets/resume.md",
         "CLAUDE.md", "skills/wlah/SKILL.md"]

@pytest.mark.parametrize("path", PROSE)
def test_our_own_prose_is_natural(path):
    r = wc.check((ROOT / path).read_text(encoding="utf-8"), strict=True, with_unslop=False)
    assert r["grade"] == "NATURAL", (path, [(f["line"], f["tell"], f["text"]) for f in r["findings"]])
