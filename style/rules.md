# The rules behind the card

`style/card.md` is what every session sees. This file is the longer version: where each rule came from, what it looks like when broken, and what to write instead. `/wlah` reads it when rewriting. You can read it when you disagree with a finding.

## Where the rules come from

Three sources, in order of weight.

1. Drafts a real reader rejected. The owner's cover letters in 2026 passed every automated check and still came back as "feels very robotic/AI, it would not pull me in". The reader named one sentence as the tell: `That is a program I have built before, not inherited`. Most of the shape rules below were written by looking at what that draft did and doing the opposite.
2. Wikipedia's [Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing), kept by the editors who clean machine text out of articles. The word list and the contrast patterns start there.
3. The [unslop](https://github.com/theclaymethod/unslop) project's catalogue of phrases and document shapes. When unslop is installed, `/wlah check` runs its scanners as well and shows what they say.

Nothing here is copied from either source. The rules are rewritten in plain words with our own examples.

## Words

The checker's list is in `scripts/wlah_check.py`. The short version: if a word shows up in a marketing page and nowhere in speech, do not write it. `Leverage` is `use`. `Robust` is `works when the input is bad`. `Journey` is what a train takes. `Delve` is a word nobody says out loud.

Intensifiers get the same treatment. `Significantly reduced` says less than `cut from 40 minutes to 9`. If there is no number, the adverb is hiding that.

Connectives that open a paragraph (`Furthermore`, `Moreover`, `Additionally`) are scaffolding. A paragraph that needs them is two paragraphs.

## Shapes

Before and after, all from real drafts.

Contrast for effect.
Before: `That is a program I have built before, not inherited.`
After: `I built the same program at Cetera in 2023.`

The participial tail.
Before: `Migrated 25 servers to AWS, ensuring uptime and reducing costs.`
After: `Migrated 25 servers to AWS. Uptime went from 99.2% to 99.9% and hosting costs fell by $180k a year.`

Three for rhythm.
Before: `A comprehensive, scalable, and robust migration strategy.`
After: `A migration plan that survived the second data centre.`

Throat clearing.
Before: `As a senior engineer with a passion for reliability, I led the migration.`
After: `I led the migration.`

Hedge, then claim.
Before: `While the timeline was challenging, we ultimately delivered on time.`
After: `We delivered on time. The timeline was six weeks shorter than the estimate.`

A question that answers itself.
Before: `Why does this matter? Because uptime is revenue.`
After: `Uptime is revenue.`

The label bullet.
Before: `- **Performance:** the new index cut query time in half.`
After: `- The new index cut query time in half.`

## Rhythm

Machines write sentences of the same length. People do not. The checker measures how much sentence lengths vary across the piece, and eight or more sentences with almost no variation is a finding on its own. The fix is one short sentence per paragraph. Five words. Then a long one that carries the detail the short one set up.

The same goes for openings. Three sentences in a row starting with `I` in a letter, or three bullets in a row starting with `Led`, read as a template.

## Pulse

Cutting the tells is half the job. Text with every tell removed can still read as nobody home: no opinion, every point given equal weight, every difficulty smoothed over. So:

- Say what you think. `The second option is better because it needs no server` beats `both options have merit`.
- Let two things matter more than the rest. In a list of six achievements, two get a number and a sentence, four get a line.
- Say the messy part. The thing that did not work is often the most useful sentence in a report.
- Write to one reader, in the register they use. If they say `stuff`, do not upgrade it to `components`.

## Grades

`/wlah check` counts findings per 300 words and gives one grade:

| Grade | Findings per 300 words | Meaning |
|---|---|---|
| NATURAL | 0 or 1 | Send it. |
| ADEQUATE | 2 or 3 | Fix the named lines, then send. |
| STILTED | 4 or more, or flat rhythm | Rewrite the piece, not the lines. |

`--strict` counts every em dash and semicolon and passes only NATURAL. Use it for anything published: a README, a letter, a post.

## Thresholds by kind

| Tell | General prose, per 300 words | Letter, per 300 words | Resume, per 5 bullets |
|---|---|---|---|
| Em dash | 1 | 1 | 1 |
| Semicolon | 1 | 1 | 1 |
| Three in a row | 1 | 1 | 1 |
| Sentences starting with I, in a row | any | 2 | none (no I) |
| Colon then a list | 1 | 0 | 2 per resume |
| Ellipsis | 0 | 0 | 0 |

## The self-audit

The last step of any rewrite is two questions, in this order:

1. What makes this obviously written by a machine?
2. Fix that.

Then read it once as the person receiving it. That reading catches what no list does.
