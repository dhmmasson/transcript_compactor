# Phase 1 - Blacklist Filter

## Selection

Feature selected from plan: **Step 2 / Phase 1 - blacklist filter**.

Goal: reduce transcript token count with simple, deterministic rules that are cheap to run (stdlib only), while preserving core semantic content for LLM input.

## Research

### Transcript observations

Dataset inspected: `transcripts/transcript1.txt`.

Quick token stats (lowercased, regex tokenization):
- Total tokens: 5403
- Unique tokens: 1117
- Top words are common function words: `the`, `to`, `and`, `a`, `of`, `we`, `that`, `in`, `is`, `it`

This supports a first-pass blacklist approach with stopwords and filler-like terms.

### Phrase-pattern experiment

The sample transcript includes outro/CTA style lines:
- "If you liked the video, you can click the like button, and if you want to see more, consider subscribing."
- "Till next time."

No sponsor segment appears in this specific sample, but sponsor phrases are still part of required feature scope.

### Product decisions captured

From user decisions for this phase:
1. Intro/outro/sponsor matching removes **only matched words**, not whole sentences.
2. Matching is **case-insensitive**.
3. Output text should **normalize whitespace/punctuation artifacts** after removals.

## Hypothesis

Phase 1 is a single, simple operation: **remove every token that appears in a blacklist**.

- The blacklist is one flat list of words. No categories, no "fillers", no regex.
- Matching is **case-insensitive, exact token** (split on whitespace). `the` matches `The` and `THE` but not `them`.
- Default fallback blacklist (when no file is provided):
  `the`, `a`, `an`, `of`, `to`, `and`, `in`, `is`, `it`, `that`, `for`, `on`, `with`, `as`, `at`, `by`, `from`, `be`, `are`, `was`, `were`
- Blacklist source resolution order:
  1. user-provided blacklist file parameter (`blacklist_file=`),
  2. local `blacklist.txt` in the current working directory,
  3. fallback default list above.
- If the user wants filler words removed, they add them to their blacklist file. That's a user decision, not a code feature.
- Normalize whitespace after removals (collapse multiple spaces).

### Example Sentences and Expected Results

Default fallback blacklist:
`the`, `a`, `an`, `of`, `to`, `and`, `in`, `is`, `it`, `that`, `for`, `on`, `with`, `as`, `at`, `by`, `from`, `be`, `are`, `was`, `were`

| # | Input | Output | Why |
|---|---|---|---|
| 1 | `This is the basic idea of the technique.` | `This basic idea technique.` | removes `is`, `the` ×2, `of` |
| 2 | `If you liked the video, click the like button and subscribe.` | `If you liked video, click like button subscribe.` | removes `the` ×2, `and`. `liked` ≠ `like` so both stay. `like` is NOT in the default blacklist. |
| 3 | `The idea of the method is clear.` | `idea method clear.` | removes `The`, `of`, `the`, `is` |
| 4 | `Erosion gradients generate branching gullies.` | `Erosion gradients generate branching gullies.` | no default blacklist words present — nothing removed |
| 5 | `Well, this is, like, basically, a test.` | `Well, this like, basically, test.` | removes `is,` → normalizes; removes `a`. `well`, `like`, `basically` are NOT in default blacklist so they stay |
| 6 | (custom file containing `erosion` + `gradients`) `Erosion gradients generate branching gullies.` | `generate branching gullies.` | custom file overrides defaults |

## Planned tests (RED)

1. Nominal: removes default blacklist words from a sentence (example 1).
2. Nominal: case-insensitive matching — uppercase/mixed-case blacklist words are removed (example 3).
3. Nominal: words NOT in the blacklist are preserved, including near-matches like `liked` vs `like` (example 2).
4. Edge: no blacklist words in input — text unchanged (example 4).
5. Edge: whitespace normalized after removals (example 5).
6. Edge: empty input returns empty output.
7. Nominal: custom blacklist file overrides defaults (example 6).
8. Edge: local `blacklist.txt` fallback when no parameter given.
9. Edge: built-in default list used when no file exists at all.
10. Pipeline integration: `blacklist=True` applies the filter.
11. Pipeline integration: `blacklist=False` is pass-through.

## Implementation Plan

### `compactor/blacklist.py` — single module, three functions

**Constants**:
- `DEFAULT_BLACKLIST`: a `frozenset` of 7 determiners: `the, a, an, this, that, those, these`.
- `PUNCT_PRIORITY`: a dict mapping punctuation characters to integer priority:
  `{',': 0, ';': 1, '.': 2, '!': 3, '?': 4}`. Higher number wins when merging.

**`_load_blacklist(blacklist_file: str | None) -> set[str]`** (private, unchanged):
1. If `blacklist_file` is provided and exists → read it, return `set` of lowercased non-empty lines.
2. Else if `blacklist.txt` exists in `Path.cwd()` → read it, same format.
3. Else → return `set(DEFAULT_BLACKLIST)`.
- File format: one word per line, UTF-8. Blank lines and leading/trailing whitespace ignored.

**`_extract_trailing_punct(token: str) -> tuple[str, str]`** (private, new):
- If the last character of `token` is in `PUNCT_PRIORITY`, return `(token[:-1], token[-1])`.
- Otherwise return `(token, "")`.
- Handles the single trailing punctuation character that matters for merging.

**`apply_blacklist(text: str, blacklist_file: str | None = None) -> str`** (public, rewritten):

Algorithm — three phases:

**Phase A — Classify tokens**:
1. If `text` is empty, return `""`.
2. Split `text` on whitespace (`str.split()`).
3. For each token, call `_extract_trailing_punct` → `(word, punct)`.
4. Classify: if `word.lower()` is in the blacklist and `word` is non-empty → mark as removed.
5. Store as list of `(word, punct, is_kept)`.

**Phase B — Build result with punctuation merging**:
1. Walk through classified tokens.
2. **Removed token**: if it has trailing punct, accumulate into a `pending_puncts` list.
3. **Kept token**: if `pending_puncts` is non-empty:
   - If there is a previous kept token in results:
     - Collect the previous token's trailing punct + all `pending_puncts`.
     - Pick the highest-priority punctuation mark (using `PUNCT_PRIORITY`).
     - Replace the previous token's trailing punct with the winner.
   - If there is no previous kept token (removal at start of text):
     - Pick the highest-priority punct from `pending_puncts`.
     - Insert a standalone punctuation token `("", best_punct)` before the current word.
   - Clear `pending_puncts`.
   - Append the current `(word, punct)` to results.
4. After the loop, if `pending_puncts` remains (removals at end of text):
   - Merge with the last kept token's trailing punct, same priority rule.

**Phase C — Reconstruct**:
1. Join `word + punct` for each result tuple with single spaces.
2. Return the string.

### Traced examples

| Input | Tokens (word, punct, kept) | Pending | Result tokens | Output |
|---|---|---|---|---|
| `cat the.` | (cat,,✓) (the,.,✗) | [.] at end → merge to cat. | [(cat,.)] | `cat.` |
| `cat, the; dog` | (cat,,,✓) (the,;,✗) (dog,,✓) | [;] → merge with , → ; | [(cat,;)(dog,)] | `cat; dog` |
| `cat, the a. dog` | (cat,,,✓) (the,,✗) (a,.,✗) | [.] → merge with , → . | [(cat,.)(dog,)] | `cat. dog` |
| `cat, the; a. this! dog` | (cat,,,✓) (the,;,✗) (a,.,✗) (this,!,✗) (dog,,✓) | [;,.!] → merge with , → ! | [(cat,!)(dog,)] | `cat! dog` |
| `the, cat dog` | (the,,,✗) (cat,,✓) (dog,,✓) | [,] → no prev → standalone | [(,,)(cat,)(dog,)] | `, cat dog` |
| `cat, an dog.` | (cat,,,✓) (an,,✗) (dog,.,✓) | [] (an has no punct) | [(cat,,)(dog,.)] | `cat, dog.` |

### `compactor/pipeline.py` — wire the blacklist phase (already done)

The pipeline already calls `apply_blacklist` when `config.blacklist` is True.
Only `blacklist.py` needs changes.

### No changes to `main.py`
CLI already passes `blacklist=True/False` into `PipelineConfig`. No `--blacklist-file` CLI flag yet (planned for later cycle per plan.md).
