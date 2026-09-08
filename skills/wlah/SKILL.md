---
name: wlah
description: Write like a human. Rewrites a draft so it reads as one person wrote it for another, grades a file for the marks of machine writing, or records a project's voice. Use when the user types /wlah <text or file>, /wlah check <file> [--kind letter|resume] [--strict], or /wlah voice.
---

# /wlah

`WLAH` = `python "${CLAUDE_PLUGIN_ROOT}/scripts/wlah_check.py"`. The style is `${CLAUDE_PLUGIN_ROOT}/style/card.md`, the reasons and examples behind it are `${CLAUDE_PLUGIN_ROOT}/style/rules.md`, and the presets are under `${CLAUDE_PLUGIN_ROOT}/presets/`. Read the card first if this session has not seen it. If the project has a `.wlah` file, its style line picks the preset and anything under `## Voice` describes how this owner writes: match it.

## /wlah <text or file>  (rewrite)

The argument is a path or the text itself. Keep every fact, number, name, quotation, code span and the meaning. Change the writing, not the claims.

1. Run `WLAH <file> --no-unslop` (write pasted text to a scratch file first) and keep its findings: they name the lines to fix.
2. If the unslop skill is installed (`~/.claude/skills/unslop`) and the text is over about 400 words, run `/unslop rewrite` on it first and take its output as the draft. Otherwise draft the rewrite yourself against the card and the preset.
3. Audit the draft with the two questions from the card: what makes this obviously written by a machine, and fix that. Write the answers as three to six short bullets.
4. Rewrite once more from those bullets. Run `WLAH` on the result. Not NATURAL means one more pass on the named lines, never a third.
5. Show, in this order: the audit bullets, then the final text, then the checker's grade line. For a file, write the final text back to the file and say so. Nothing else.

## /wlah check <file> [--kind letter|resume] [--strict]

Run `WLAH <file>` with the flags given. Print its output as it is. Then, in two or three sentences, say which findings matter most and what one change would fix the most of them. `--strict` is for anything that will be published.

## /wlah voice

Build the project's `.wlah` file from samples of the owner's own writing. Ask for two or three samples (pasted, or paths) if none were given. Read them and write, under `## Voice`, six to ten lines of what this person does: sentence length, favourite words, words they never use, how they open, how they close, how formal, first or third person. Quote one short phrase of theirs as the example of each. Keep the file's first line as the style (`default` unless they say otherwise). Show the file and where it was written. If the unslop skill is installed, `/unslop teach` can build a fuller profile: say so, once.
