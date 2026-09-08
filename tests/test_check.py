import json
import wlah_check as wc
from conftest import FIX

def read(name): return (FIX / name).read_text(encoding="utf-8")

def test_the_rejected_draft_is_stilted():
    r = wc.check(read("bad.md"), with_unslop=False)
    tells = {f["tell"] for f in r["findings"]}
    assert r["grade"] == "STILTED" and r["exit"] == 1 and len(r["findings"]) >= 12
    for t in ("word: spearheaded", "word: leverage", "word: furthermore", "'not X, but Y' contrast",
              "'X, not Y-ed' contrast", "participial tail (a sentence that trails into ', -ing ...')",
              "three single words in a row for rhythm", "a question answered by its own next word"):
        assert any(t in x for x in tells), t
    strict = {f["tell"] for f in wc.check(read("bad.md"), strict=True, with_unslop=False)["findings"]}
    assert "semicolon" in strict and "em dash" in strict  # one of each sits under the loose ceiling for 170 words

def test_the_plain_rewrite_is_natural():
    r = wc.check(read("good.md"), with_unslop=False)
    assert r["grade"] == "NATURAL" and r["exit"] == 0, r["findings"]

def test_flat_rhythm_is_a_finding_on_its_own():
    text = " ".join("The team shipped the feature on Monday morning." for _ in range(10))
    r = wc.check(text, with_unslop=False)
    assert r["rhythm"]["flat"] and r["grade"] == "STILTED"
    assert any(f["tell"].startswith("rhythm") for f in r["findings"])

def test_code_quotes_and_links_are_not_prose():
    text = ("Plain sentence here.\n\n```\nleverage the robust synergy — delve; deep dive\n```\n\n"
            "> quoted: we must leverage the landscape\n\nUse `leverage` as a name. See [the docs](https://x.y/journey).\n")
    r = wc.check(text, with_unslop=False)
    assert r["findings"] == [], r["findings"]

def test_strict_counts_every_dash_and_semicolon_and_passes_only_natural():
    text = "One idea per sentence — and then another; then a third.\n"
    loose = wc.check(text, with_unslop=False); strict = wc.check(text, strict=True, with_unslop=False)
    assert not any(f["tell"] in ("em dash", "semicolon") for f in loose["findings"])  # one of each per 300 words is allowed
    assert {f["tell"] for f in strict["findings"]} >= {"em dash", "semicolon"} and strict["exit"] == 1

def test_the_density_threshold_scales_with_length():
    text = ("Short sentence. " * 40) + "Here — and there — and everywhere — again — and again.\n"
    r = wc.check(text, with_unslop=False)
    assert sum(f["tell"] == "em dash" for f in r["findings"]) == 3  # four dashes in 300 words: three over the one allowed

def test_kinds_add_their_own_words():
    letter = "I am writing to express my interest in the role. I am excited. Thank you for your consideration."
    assert any("i am writing to" in f["tell"] for f in wc.check(letter, "letter", with_unslop=False)["findings"])
    assert not any("i am writing to" in f["tell"] for f in wc.check(letter, "general", with_unslop=False)["findings"])
    resume = "Responsible for overseeing the team. Tasked with managing budgets."
    assert len([f for f in wc.check(resume, "resume", with_unslop=False)["findings"] if f["tell"].startswith("word:")]) == 2

def test_letter_flags_a_run_of_i_openers():
    text = "I led the migration. I wrote the plan. I ran the cutover. I stayed late.\n"
    r = wc.check(text, "letter", with_unslop=False)
    assert any("start with I" in f["tell"] for f in r["findings"])

def test_findings_carry_line_numbers_and_json_output(capsys, tmp_path):
    p = tmp_path / "d.md"; p.write_text("Fine line.\n\nWe will leverage this.\n", encoding="utf-8")
    assert wc.main([str(p), "--json", "--no-unslop"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["grade"] == "NATURAL" and out["findings"][0]["line"] == 3 and out["findings"][0]["tell"] == "word: leverage"

def test_cli_reads_stdin_and_prints_a_grade_line(capsys, monkeypatch):
    import io
    monkeypatch.setattr("sys.stdin", io.StringIO("A plain sentence that says one thing.\n"))
    assert wc.main(["-", "--no-unslop"]) == 0
    assert capsys.readouterr().out.startswith("wlah_check: NATURAL, 0 finding(s)")

def test_front_matter_is_skipped():
    text = "---\ndescription: leverage the robust landscape\n---\n\nA plain line.\n"
    assert wc.check(text, with_unslop=False)["findings"] == []
