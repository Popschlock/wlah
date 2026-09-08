import json, subprocess, sys, time
from conftest import ROOT

HOOK = ROOT / "hooks" / "session-start.py"

def run(cwd):
    t0 = time.time()
    r = subprocess.run([sys.executable, str(HOOK)], input=json.dumps({"cwd": str(cwd)}), capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 0, r.stderr
    return r.stdout, time.time() - t0

def test_default_prints_the_card_with_the_off_switch_first(project):
    out, secs = run(project)
    assert out.startswith("wlah: writing like a human is on (style: default)")
    assert "# Write like a human" in out and "Cut on sight" in out and "`off`" in out
    assert secs < 1.5

def test_off_file_prints_nothing(project):
    (project / ".wlah").write_text("off\n", encoding="utf-8")
    assert run(project)[0] == ""

def test_claude_md_line_turns_it_off(project):
    (project / "CLAUDE.md").write_text("# p\n\nwlah: off\n", encoding="utf-8")
    assert run(project)[0] == ""

def test_a_preset_replaces_the_card(project):
    (project / ".wlah").write_text("terse\n", encoding="utf-8")
    out = run(project)[0]
    assert "(style: terse)" in out and "# Write like a human, terse" in out and "Cut on sight" not in out
    (project / ".wlah").write_text("style: letter\n", encoding="utf-8")
    assert "# Write like a human, letters" in run(project)[0]

def test_unknown_style_falls_back_to_the_card(project):
    (project / ".wlah").write_text("shouty\n", encoding="utf-8")
    out = run(project)[0]
    assert "(style: default)" in out and "Cut on sight" in out

def test_voice_section_is_appended(project):
    (project / ".wlah").write_text("default\n\n## Voice\n\nShort sentences. Says 'stuff'. Never says 'utilize'.\n", encoding="utf-8")
    out = run(project)[0]
    assert out.rstrip().endswith("Never says 'utilize'.") and "## This project's voice" in out

def test_bad_payload_still_exits_zero_and_prints_the_card(project):
    r = subprocess.run([sys.executable, str(HOOK)], input="not json", capture_output=True, text=True, encoding="utf-8", cwd=str(project))
    assert r.returncode == 0 and "Write like a human" in r.stdout
