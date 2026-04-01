#!/usr/bin/env python3
"""Generate YAML test cases for blacklist removal.

Builds nonsensical sentences from combinations of:
- whitelisted words (should survive)
- blacklisted words (should be removed)
- punctuation marks (with priority rules for adjacent cleanup)

The punctuation priority order (lowest → highest):
  , < ; < . < ! < ?
When two punctuation marks become adjacent after a blacklisted word is
removed, the lower-priority mark is dropped.

Usage:
    python tests/generate_blacklist_cases.py > tests/blacklist_cases.yaml
"""

import itertools
import yaml

WHITE = ["cat", "dog", "run", "big"]
BLACK = ["the", "a", "an", "this", "that"]

# Priority: lowest index = lowest priority = removed first when adjacent
PUNCT_PRIORITY = [",", ";", ".", "!", "?"]


def priority(p: str) -> int:
    return PUNCT_PRIORITY.index(p)


def make_token(word: str, trailing_punct: str = "") -> str:
    return word + trailing_punct


def resolve_adjacent_punct(left: str, right: str) -> str:
    """When two punctuation marks are adjacent, keep the higher-priority one."""
    if priority(left) < priority(right):
        return right
    return left


# ── Case generators ──────────────────────────────────────────────────────

cases: list[dict] = []


def add(rationale: str, input_text: str, output: str):
    cases.append({"rationale": rationale, "input": input_text, "output": output})


# ── 1. Basic removal (no punctuation complications) ─────────────────────

add(
    rationale="Single blacklisted word between two white words is removed",
    input_text="cat the dog",
    output="cat dog",
)

add(
    rationale="Multiple blacklisted words removed, white words kept",
    input_text="the cat a dog an run",
    output="cat dog run",
)

add(
    rationale="Case-insensitive: uppercase blacklisted word removed",
    input_text="The cat A dog",
    output="cat dog",
)

add(
    rationale="No blacklisted words — input unchanged",
    input_text="cat dog run big",
    output="cat dog run big",
)

add(
    rationale="All words blacklisted — result is empty",
    input_text="the a an this that",
    output="",
)

add(
    rationale="Empty input — empty output",
    input_text="",
    output="",
)

# ── 2. Punctuation preserved on removed words ───────────────────────────

add(
    rationale="Trailing period on blacklisted word at end → period attaches to previous word",
    input_text="cat the.",
    output="cat.",
)

add(
    rationale="Trailing comma on blacklisted word in middle → comma attaches to previous word",
    input_text="cat the, dog",
    output="cat, dog",
)

add(
    rationale="Blacklisted word with trailing punctuation at start → punctuation kept on next word",
    input_text="the, cat dog",
    output=", cat dog",
)

# ── 3. Adjacent punctuation cleanup with priority ───────────────────────

# Generate all pairs of punctuation marks that can become adjacent
for left_p, right_p in itertools.combinations(PUNCT_PRIORITY, 2):
    # Sentence: "white<left_p> black<right_p> white"
    # After removal of black: "white<left_p> <right_p> white"
    # Adjacent cleanup: keep higher priority
    survivor = resolve_adjacent_punct(left_p, right_p)
    inp = f"cat{left_p} the{right_p} dog"
    out = f"cat{survivor} dog"
    add(
        rationale=(
            f"Adjacent '{left_p}' and '{right_p}' after removal → "
            f"keep '{survivor}' (higher priority)"
        ),
        input_text=inp,
        output=out,
    )

# Same-punctuation adjacent → collapse to one
for p in PUNCT_PRIORITY:
    inp = f"cat{p} the{p} dog"
    out = f"cat{p} dog"
    add(
        rationale=f"Two adjacent '{p}' after removal → collapse to one '{p}'",
        input_text=inp,
        output=out,
    )

# ── 4. Multiple removals in sequence ────────────────────────────────────

add(
    rationale="Two consecutive blacklisted words removed, punctuation from each merges",
    input_text="cat, the a. dog",
    output="cat. dog",
)

add(
    rationale="Blacklisted word between two punctuated white words — no adjacent punct",
    input_text="cat, an dog.",
    output="cat, dog.",
)

add(
    rationale="Three consecutive blacklisted words with mixed punctuation",
    input_text="cat, the; a. this! dog",
    output="cat! dog",
)

# ── 5. Non-adjacent punctuation stays untouched ─────────────────────────

add(
    rationale="Non-adjacent punctuation marks are both preserved",
    input_text="cat, dog. run",
    output="cat, dog. run",
)

add(
    rationale="Blacklisted word removed between non-adjacent puncts — no merge needed",
    input_text="cat, dog the run.",
    output="cat, dog run.",
)


# ── Output ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(yaml.dump(cases, default_flow_style=False, allow_unicode=True, sort_keys=False))
