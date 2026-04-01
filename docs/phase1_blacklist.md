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

### `compactor/blacklist.py` — single module, two functions

**Constants**:
- `DEFAULT_BLACKLIST`: a `frozenset` containing the 21 default words listed in the hypothesis.

**`_load_blacklist(blacklist_file: str | None) -> set[str]`** (private):
1. If `blacklist_file` is provided and exists → read it, return `set` of lowercased non-empty lines.
2. Else if `blacklist.txt` exists in `Path.cwd()` → read it, same format.
3. Else → return `DEFAULT_BLACKLIST`.
- File format: one word per line, UTF-8. Blank lines and leading/trailing whitespace ignored.

**`apply_blacklist(text: str, blacklist_file: str | None = None) -> str`** (public):
1. Call `_load_blacklist(blacklist_file)` to get the word set.
2. If `text` is empty, return `""` immediately.
3. Split `text` on whitespace (`str.split()`).
4. For each token:
   - Strip punctuation from the token to get bare word (e.g. `"is,"` → `"is"`).
   - Compare bare word (lowercased) against the blacklist set.
   - If match → drop the entire token (including its punctuation).
   - If no match → keep the token as-is.
5. Join surviving tokens with single space.
6. Return result.

**Punctuation handling detail** (critical for test correctness):
- Example 5: `"is,"` → bare word `"is"` matches → entire token `"is,"` is removed.
- This means `"Well, this is, like, basically, a test."` → remove `"is,"` and `"a"` → `"Well, this like, basically, test."` ✓
- Punctuation stripping uses `str.strip(string.punctuation)` for the comparison only; the original token (with punctuation) is what gets kept or dropped.

### `compactor/pipeline.py` — wire the blacklist phase

Replace the pass-through scaffold with:
```python
def run_pipeline(text: str, config: PipelineConfig) -> str:
    if config.blacklist:
        text = apply_blacklist(text)
    return text
```

Import `apply_blacklist` from `compactor.blacklist`.

### No changes to `main.py`
CLI already passes `blacklist=True/False` into `PipelineConfig`. No `--blacklist-file` CLI flag yet (planned for later cycle per plan.md).
