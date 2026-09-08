#!/usr/bin/env python3
"""SessionStart hook: put the writing style in front of every session on this machine.

Prints style/card.md (or a preset the project chose) as context, with one line first saying it is on
and how to turn it off. Reads files only, exits 0 always, and prints nothing when the project opted out.

A project chooses in a `.wlah` file at its root:

    off                      nothing is injected
    terse | letter | resume  that preset replaces the card
    default                  the card (same as no file)

    ## Voice                 everything under this heading is appended, so a project can carry the
    ...                      owner's own voice notes (what they say, what they never say)

A `wlah: off` line anywhere in the project's CLAUDE.md does the same as `off`.
"""
import json, os, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRESETS = {"terse", "letter", "resume"}


def read(p):
    try: return Path(p).read_text(encoding="utf-8", errors="replace")
    except OSError: return ""


def project_choice(root):
    """-> (mode, voice): mode is 'off', 'default' or a preset name; voice is the text under '## Voice'."""
    claude = read(root / "CLAUDE.md")
    if re.search(r"^\s*wlah:\s*off\s*$", claude, re.I | re.M): return "off", ""
    text = read(root / ".wlah")
    if not text: return "default", ""
    head, _, voice = text.partition("## Voice")
    mode = next((l.strip().lower() for l in head.split("\n") if l.strip() and not l.strip().startswith("#")), "default")
    mode = re.sub(r"^style:\s*", "", mode)
    if mode not in PRESETS and mode != "off": mode = "default"
    return mode, voice.strip()


def compose(mode, voice):
    body = read(ROOT / "presets" / f"{mode}.md") if mode in PRESETS else read(ROOT / "style" / "card.md")
    if not body: return ""
    head = (f"wlah: writing like a human is on (style: {mode}). A project turns it off with a `.wlah` file "
            "containing `off`, or picks a style with `terse`, `letter` or `resume`. Check a draft with `/wlah check <file>`.")
    out = head + "\n\n" + body.strip() + "\n"
    if voice: out += "\n## This project's voice\n\n" + voice + "\n"
    return out


def main():
    if hasattr(sys.stdout, "reconfigure"):
        try: sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception: pass
    cwd = None
    try:
        raw = sys.stdin.read()
        cwd = json.loads(raw).get("cwd") if raw.strip() else None
    except Exception:
        pass
    try:
        root = Path(cwd or os.getcwd()).resolve()
        mode, voice = project_choice(root)
        if mode == "off": return 0
        text = compose(mode, voice)
        if text: print(text)
    except Exception as e:
        print(f"wlah: could not load the style ({e})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
