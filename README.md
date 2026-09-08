# wlah

Write like a human. A Claude Code plugin that makes every session on your machine write plainly by default, lets a project turn that off or pick a style, and gives you `/wlah` to rewrite or grade a piece of text.

## What it does

Claude's default prose has a recognisable shape: em dashes, `not X, but Y`, three adjectives in a row, a sentence that trails off into `, ensuring...`, and a word list (`leverage`, `robust`, `delve`, `journey`) nobody says out loud. Readers spot it in one paragraph. This plugin puts a short style card in front of every session so the first draft avoids that shape, and ships a checker that grades what still slips through.

Before:

> Spearheaded a comprehensive, scalable, and robust cloud migration strategy — resulting in significantly improved uptime and dramatically reduced operational costs.

After:

> Migrated 25 servers to AWS. Uptime went from 99.2% to 99.9%. Cut hosting costs by $180k a year.

## Install

```
claude plugin marketplace add Popschlock/wlah
claude plugin install wlah@wlah
```

Restart Claude Code. From then on every session starts with the style card loaded, and the first line of that context tells you it is on.

## Use

`/wlah <text or file>` rewrites in the style. It shows what it found, then the final text, then the grade.

`/wlah check <file>` grades a file and lists each finding with its line. Add `--kind letter` or `--kind resume` for those forms, and `--strict` for anything you will publish.

`/wlah voice` reads samples of your own writing and records how you write in the project, so rewrites match you instead of a generic plain style.

The checker also runs on its own, with nothing but Python 3:

```
python scripts/wlah_check.py draft.md --strict
```

## Turn it off, or pick a style

Put a `.wlah` file at the project root. Its first line is the style:

```
off
```

or `terse` (chat and commit messages), `letter` (cover letters and outreach), `resume`, or `default`. A `wlah: off` line in the project's CLAUDE.md does the same as `off`.

Anything under a `## Voice` heading in that file is added to the card, so a project can carry notes on how its owner writes. `/wlah voice` writes that section for you.

## Grades

| Grade | Findings per 300 words |
|---|---|
| NATURAL | 0 or 1 |
| ADEQUATE | 2 or 3 |
| STILTED | 4 or more, or every sentence the same length |

The checker exits 0 on NATURAL or ADEQUATE and 1 on STILTED, so it works as a gate in a script. With `--strict`, only NATURAL passes.

## Where the rules come from

The card is in `style/card.md` and the reasons behind it, with before and after examples, in `style/rules.md`. The patterns come from drafts a real reader rejected, from Wikipedia's [Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing), and from the [unslop](https://github.com/theclaymethod/unslop) project's catalogue. Nothing is copied from either. If you install unslop as well, `/wlah` uses its scanners for a second opinion and its rewrite flow on long documents.

## Requirements

Python 3 on PATH as `python` or `python3`. The checker and the hook use the standard library only. Tests need pytest: `python -m pytest tests/`.

MIT.
