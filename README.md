# wlah

wlah (write like a human) is a Claude Code plugin that makes every session on your machine write the way a person would, without you asking each time. It loads a short style card at the start of every session, lets any project turn that off or choose a different style, and gives you a `/wlah` command to rewrite a draft or grade a file for the marks of machine writing.

Claude's default prose has a recognisable shape: em dashes, `not X, but Y`, three adjectives in a row, sentences that trail off into `, ensuring...`, and a word list (`leverage`, `robust`, `delve`, `journey`) that nobody says out loud. Readers spot it within a paragraph. The card keeps the first draft clear of that shape, and the checker catches what still slips through.

Before:

> Spearheaded a comprehensive, scalable, and robust cloud migration strategy — resulting in significantly improved uptime and dramatically reduced operational costs.

After:

> Migrated 25 servers to AWS. Uptime went from 99.2% to 99.9%. Cut hosting costs by $180k a year.

## Getting Started

Install the plugin from GitHub and restart Claude Code:

```
claude plugin marketplace add Popschlock/wlah
claude plugin install wlah@wlah
```

From then on, every session starts with the style card loaded, and the first line of that context tells you it is on and how to turn it off. You do not need to do anything else for ordinary replies, commit messages and documents to follow it.

To rewrite something, run `/wlah` followed by the text or a file path, such as `/wlah docs/README.md`. It shows what it found, then the final text, then the grade. To grade a file without changing it, run `/wlah check docs/README.md`, and add `--kind letter` or `--kind resume` for those forms or `--strict` for anything you are about to publish. To record how you write so rewrites match you rather than a generic plain style, run `/wlah voice` and paste two or three samples of your own writing.

The checker also runs on its own with nothing but Python 3, so you can use it as a gate in a script:

```
python scripts/wlah_check.py draft.md --strict
```

## Turning It Off or Choosing a Style

Put a `.wlah` file at the root of a project. Its first line is the style, so a file containing `off` turns the card off for that project, and `terse` (chat and commit messages), `letter` (cover letters and outreach), `resume` or `default` picks a preset. A `wlah: off` line in the project's CLAUDE.md does the same as `off`.

Anything under a `## Voice` heading in that file is added to the card, so a project can carry notes on how its owner writes. `/wlah voice` writes that section for you.

## Grades

| Grade | Findings per 300 words |
|---|---|
| NATURAL | 0 or 1 |
| ADEQUATE | 2 or 3 |
| STILTED | 4 or more, or every sentence the same length |

The checker exits 0 on NATURAL or ADEQUATE and 1 on STILTED. With `--strict`, only NATURAL passes and every em dash and semicolon counts as a finding.

## Where the Rules Come From

The card is `style/card.md`, and `style/rules.md` explains each rule with before and after examples. The patterns come from drafts a real reader rejected, from Wikipedia's [Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing), and from the [unslop](https://github.com/theclaymethod/unslop) project's catalogue. Nothing is copied from either source. If you install unslop as well, `/wlah` uses its scanners for a second opinion and its rewrite flow on long documents.

## Requirements

Python 3 on PATH as `python` or `python3`. The checker and the hook use only the standard library, and the tests need pytest (`python -m pytest tests/`).

MIT.
