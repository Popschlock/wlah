#!/usr/bin/env python3
"""wlah_check: grade a piece of writing for the marks of machine-written text.

Usage:
    python wlah_check.py <file.md|.txt|->  [--kind general|letter|resume] [--strict] [--json]

Reads the file (or stdin for "-"), skips code fences, inline code, block quotes, links and
front matter, then looks for the tells: the banned words, the sentence shapes machines lean
on, and flat rhythm. Prints each finding with the text around it, then one grade:

    NATURAL   0 or 1 tells per 300 words
    ADEQUATE  2 or 3
    STILTED   4 or more, or the rhythm test failed

Exit 0 on NATURAL or ADEQUATE, 1 on STILTED. With --strict, any em dash or semicolon is a
finding on its own and anything but NATURAL exits 1. A finding is something to rewrite, not
a warning to leave in.

The word list and the shapes come from Wikipedia's "Signs of AI writing", from the owner's
own rejected drafts (ResumeCreator, 2026), and from the unslop project's catalogue. When the
unslop skill is installed, its scanners run too and their output is shown, unscored.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

# Words and stock phrases a person rarely writes on purpose (case-insensitive, whole-word).
GENERAL = [
    "leverage", "leveraged", "leveraging", "synergy", "synergize", "cutting-edge", "robust",
    "seamless", "seamlessly", "delve", "delving", "deep dive", "landscape", "journey", "tapestry",
    "testament", "elevate", "empower", "empowering", "streamline", "streamlined", "holistic",
    "game-changer", "game changer", "unlock", "unleash", "navigate", "navigating", "foster",
    "fostering", "facilitate", "comprehensive", "pivotal", "crucial role", "vital role", "key role",
    "utilize", "utilizing", "innovative", "transformative", "revolutionary", "groundbreaking",
    "multifaceted", "myriad", "plethora", "paradigm", "realm", "beacon", "symphony", "vibrant",
    "meticulous", "meticulously", "intricate", "underscore", "underscores", "showcase",
    "showcasing", "bolster", "bolstered", "garner", "resonate", "serves as", "stands as",
    "stands out", "boasts", "exemplifies", "renowned", "in the heart of", "diverse array",
    "valuable insights", "it is important to note", "it's important to note", "it is worth noting",
    "generally speaking", "to some extent", "from a broader perspective", "in today's",
    "in an era", "in a world where", "at its core", "imagine a world", "demystify",
    "setting the stage", "highlights the importance", "reflects broader", "commitment to excellence",
    "furthermore", "moreover", "additionally", "in conclusion", "in summary", "to summarize",
    "let's dive in", "let's explore", "let's break this down", "here's the thing",
    "here's what you need to know", "let me be clear", "make no mistake", "full stop",
    "let that sink in", "i hope this helps", "certainly!", "great question",
    "experts agree", "experts argue", "studies show", "research shows", "it is widely known",
    "many believe", "some critics argue", "observers have cited",
    "significantly", "dramatically", "greatly", "substantially", "effectively", "successfully",
    "passionate about", "results-driven", "proven track record", "spearheaded", "harnessing",
    "endeavor", "poised", "cornerstone", "intersection", "unwavering", "enduring",
]

LETTER = [
    "i am writing to", "i'm writing to", "express my interest", "i am excited", "i'm excited",
    "thrilled", "i believe i would be", "perfect fit", "ideal candidate", "hit the ground running",
    "value-add", "bring to the table", "thank you for your consideration",
    "look forward to the opportunity", "would love the opportunity", "eager to",
    "wealth of experience", "track record", "skill set", "fast-paced", "team player",
    "go above and beyond", "not only", "to whom it may concern", "dear hiring manager",
]

RESUME = [
    "responsible for", "tasked with", "duties included", "seasoned", "adept", "dynamic",
    "results-oriented", "detail-oriented", "self-starter", "go-getter", "think outside the box",
]

# Sentence shapes. (regex, label, multiline)
PATTERNS = [
    (r"\bnot\b[^.;:!?]{1,60},\s*(but|it is|it's|it needs|rather)\b", "'not X, but Y' contrast", False),
    (r"\bnot\b[^.;:!?]{1,60}\brather than\b", "'not X rather than Y' contrast", False),
    (r"\b(is|was|were|are)\b[^.;:!?]{1,40}\bnot\s+[a-z]+ed\b", "'X, not Y-ed' contrast", False),
    (r"\bnot only\b[^.!?]{1,80}\bbut (also )?\b", "'not only X but also Y'", False),
    (r"\bfrom \w+ to \w+ to \w+\b", "'from X to Y to Z' run", False),
    (r",\s*(ensuring|highlighting|underscoring|reflecting|demonstrating|showcasing|enabling|allowing|"
     r"resulting|driving|leading|delivering|supporting|contributing|fostering|paving)\b[^.!?]*[.!?]",
     "participial tail (a sentence that trails into ', -ing ...')", False),
    (r"\b(\w+), (\w+),? and (\w+)\b(?![^.!?]*\d)", "three single words in a row for rhythm", False),
    (r"\bwhile\b[^.!?]{1,60},\s*(ultimately|in the end)\b", "hedge then claim ('while X, ultimately Y')", False),
    (r"^(In|As|With|Given|Whether|When it comes to)\b[^.!?]{0,80},\s", "front-loaded opener", True),
    (r"^(Significantly|Dramatically|Effectively|Successfully|Efficiently|Proactively) \w+ed\b",
     "adverb before the verb (say the number instead)", True),
    (r"\bthat is (the kind of|exactly the kind of)\b", "'that is the kind of' framing", False),
    (r"\?\s+(Because|The answer|It's simple|Simple)\b", "a question answered by its own next word", False),
    (r"^\s*[-*] \*\*[^*]{1,40}:\*\* ", "a bullet built as 'Label: sentence'", True),
    (r"\.{3}|…", "ellipsis", False),
]

EM_DASH = re.compile(r"—|–|(?<=\w) - (?=\w)|\s--\s")
SEMICOLON = re.compile(r";(?!\))")


def strip_markup(text: str) -> str:
    """Drop what is not prose: front matter, code fences, inline code, block quotes, link targets,
    images, HTML tags and markdown tables' rule rows. Line count is kept so line numbers still match."""
    lines = text.split("\n")
    if lines and lines[0].strip() == "---":
        end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
        if end is not None:
            for i in range(0, end + 1): lines[i] = ""
    out, fence = [], False
    for l in lines:
        s = l.strip()
        if s.startswith("```") or s.startswith("~~~"):
            fence = not fence; out.append(""); continue
        if fence or s.startswith(">") or re.match(r"^\|?\s*:?-{3,}", s):
            out.append(""); continue
        l = re.sub(r"`[^`]*`", " ", l)
        l = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", l)
        l = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", l)
        l = re.sub(r"<[^>]+>", " ", l)
        l = re.sub(r"https?://\S+", " ", l)
        out.append(l)
    return "\n".join(out)


def line_of(text: str, pos: int) -> int: return text.count("\n", 0, pos) + 1


def context(text: str, start: int, end: int, pad: int = 28) -> str:
    return re.sub(r"\s+", " ", text[max(0, start - pad):end + pad]).strip()


def scan(text: str, kind: str = "general", strict: bool = False) -> list[dict]:
    words = GENERAL + (LETTER if kind == "letter" else []) + (RESUME if kind == "resume" else [])
    if kind == "resume": words = [w for w in words if w != "not only"]
    low = text.lower(); found = []
    for term in words:
        for m in re.finditer(r"(?<![\w-])" + re.escape(term) + r"(?![\w-])", low):
            found.append({"line": line_of(text, m.start()), "tell": f"word: {term}", "text": context(text, m.start(), m.end())})
    for pat, label, multi in PATTERNS:
        for m in re.finditer(pat, text, re.I | (re.M if multi else 0)):
            found.append({"line": line_of(text, m.start()), "tell": label, "text": context(text, m.start(), m.end())})
    n_words = max(1, len(text.split()))
    per300 = 300.0 / max(n_words, 300)
    dashes = [m for m in EM_DASH.finditer(text)]; semis = [m for m in SEMICOLON.finditer(text)]
    if strict or len(dashes) * per300 > 1:
        for m in (dashes if strict else dashes[1:]):
            found.append({"line": line_of(text, m.start()), "tell": "em dash", "text": context(text, m.start(), m.end())})
    if strict or len(semis) * per300 > 1:
        for m in (semis if strict else semis[1:]):
            found.append({"line": line_of(text, m.start()), "tell": "semicolon", "text": context(text, m.start(), m.end())})
    found.sort(key=lambda f: f["line"])
    return found


def sentences(text: str) -> list[str]:
    flat = re.sub(r"\s+", " ", text)
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", flat) if len(s.split()) > 2]


def rhythm(text: str) -> dict:
    """Sentence count, mean length, and how much the lengths vary. Eight or more sentences whose
    lengths barely differ (variation under 0.35) is a tell in itself."""
    sents = sentences(text)
    if not sents: return {"sentences": 0, "mean": 0.0, "variation": 0.0, "flat": False, "i_runs": 0}
    lens = [len(s.split()) for s in sents]; mean = sum(lens) / len(lens)
    var = sum((x - mean) ** 2 for x in lens) / len(lens); cv = (var ** 0.5) / mean if mean else 0.0
    run = best = 0
    for s in sents:
        run = run + 1 if re.match(r"^I\b", s) else 0; best = max(best, run)
    return {"sentences": len(sents), "mean": round(mean, 1), "variation": round(cv, 2),
            "flat": len(sents) >= 8 and cv < 0.35, "i_runs": best}


def grade(findings: list[dict], rh: dict, n_words: int, strict: bool) -> str:
    rate = len(findings) * 300.0 / max(n_words, 300)
    if rh["flat"] or rate >= 4: return "STILTED"
    if rate >= 2: return "ADEQUATE"
    return "NATURAL"


def unslop_scripts() -> Path | None:
    for base in (Path.home() / ".claude" / "skills" / "unslop", Path.home() / "dev" / "unslop"):
        if (base / "scripts" / "banned_phrase_scan.py").is_file(): return base / "scripts"
    return None


def run_unslop(text: str) -> list[str]:
    """The unslop scanners, when that skill is installed. Their lines are shown, not scored: the
    two catalogues overlap, and a double count would be a false grade."""
    d = unslop_scripts(); out = []
    if not d: return out
    for name in ("banned_phrase_scan.py", "structure_scan.py"):
        try:
            r = subprocess.run([sys.executable, str(d / name)], input=text, capture_output=True, text=True, timeout=30)
            lines = [l for l in (r.stdout or "").splitlines() if l.strip()]
            out.extend(f"{name}: {l}" for l in lines[:20])
        except Exception as e:
            out.append(f"{name}: could not run ({e})")
    return out


def check(text: str, kind: str = "general", strict: bool = False, with_unslop: bool = True) -> dict:
    prose = strip_markup(text)
    findings = scan(prose, kind, strict); rh = rhythm(prose)
    if rh["flat"]:
        findings.append({"line": 0, "tell": "rhythm: sentence lengths barely vary", "text": f"{rh['sentences']} sentences, variation {rh['variation']}"})
    if kind == "letter" and rh["i_runs"] > 2:
        findings.append({"line": 0, "tell": f"rhythm: {rh['i_runs']} sentences in a row start with I", "text": ""})
    n_words = len(prose.split())
    g = grade(findings, rh, n_words, strict)
    return {"grade": g, "words": n_words, "findings": findings, "rhythm": rh,
            "unslop": run_unslop(prose) if with_unslop else [],
            "exit": 1 if g == "STILTED" or (strict and g != "NATURAL") else 0}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="wlah_check")
    ap.add_argument("path", help="a file, or - for stdin")
    ap.add_argument("--kind", default="general", choices=["general", "letter", "resume"])
    ap.add_argument("--strict", action="store_true", help="any em dash or semicolon is a finding; only NATURAL exits 0")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--no-unslop", action="store_true")
    a = ap.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        try: sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception: pass
    text = sys.stdin.read() if a.path == "-" else Path(a.path).read_text(encoding="utf-8", errors="replace")
    r = check(text, a.kind, a.strict, not a.no_unslop)
    if a.json:
        print(json.dumps(r, ensure_ascii=False, indent=1)); return r["exit"]
    rh = r["rhythm"]
    print(f"wlah_check: {r['grade']}, {len(r['findings'])} finding(s) in {r['words']} words, "
          f"{rh['sentences']} sentences, mean {rh['mean']} words, variation {rh['variation']}")
    for f in r["findings"]:
        where = f"line {f['line']}: " if f["line"] else ""
        print(f"- {where}{f['tell']}" + (f"  ...{f['text']}..." if f["text"] else ""))
    if r["unslop"]:
        print("unslop says (not scored):")
        for l in r["unslop"]: print(f"  {l}")
    return r["exit"]


if __name__ == "__main__":
    sys.exit(main())
