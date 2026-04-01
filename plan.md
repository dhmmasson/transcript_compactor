# transcript_compactor — Implementation Plan

## Goal

CLI tool that takes a YouTube transcript (plain text) and compresses it for LLM use.
Compression is additive: opt-in flags, all off by default, `--all` as the power-user shorthand.
Run via `uv run main.py` during development, installable via `uv tool install .` once packaged.

## Step Checklist

- [x] Step 1: Scaffold `compactor/` package + pipeline skeleton + CLI
- [ ] Step 2: Phase 1 — blacklist filter
- [ ] Step 3: Phase 2 — frequency analysis
- [ ] Step 4: Phase 3 — NLP filter (spacy)
- [ ] Step 5: Packaging (hatchling, console script, uv build)

---

## File Structure

```
transcript_compactor/
├── main.py                        ← CLI entry point, main() function
├── compactor/
│   ├── __init__.py
│   ├── pipeline.py                ← chains selected filters, collects stats
│   ├── blacklist.py               ← Phase 1
│   ├── frequency.py               ← Phase 2
│   ├── nlp_filter.py              ← Phase 3
│   └── data/
│       ├── stopwords.txt          ← articles, copulas, prepositions
│       └── fillers.txt            ← "um", "uh", "like", "you know" …
├── tests/
│   ├── test_blacklist.py
│   ├── test_frequency.py
│   ├── test_nlp_filter.py
│   └── test_pipeline.py
├── transcripts/
│   └── transcript1.txt            ← sample transcript for manual testing
├── pyproject.toml
├── README.md
└── LICENSE
```

---

## CLI Interface

All flags are opt-in. No flag disables another.

| Flag | Description |
|---|---|
| `file [file ...]` | one or more `.txt` files **or** a folder path |
| `--blacklist` | Phase 1: stopwords + fillers + sponsor/intro removal |
| `--blacklist-file PATH` | custom blacklist words file (one word/line), used by `--blacklist` |
| `--frequency` | Phase 2: high-frequency token removal |
| `--freq-threshold FLOAT` | cutoff for Phase 2 (default: `0.02`) |
| `--nlp` | Phase 3: spaCy POS-based filtering |
| `--all` | enables blacklist + frequency + nlp |
| `--strip-timestamps` | strip `[00:12]` / `00:12` markers (standalone, not in `--all`) |
| `-o / --output` | write result to file instead of stdout |
| `--stats` | print token counts before/after each phase |

### Multiple files and folder input

`file` uses `nargs='+'` so one or more paths are accepted. When a folder is given,
`main()` expands it to all `.txt` files in that top-level folder (non-recursive).
`main()` normalises all inputs to a list of `Path` objects early — single-file and
multi-file cases share the same loop.

**Output strategy with multiple inputs** (not yet implemented, architecture note):
- Single input + `-o file` → write to that file
- Single input, no `-o` → stdout
- Multiple inputs + no `-o` → stdout, files separated by a header line
- Multiple inputs + `-o path` → `-o` must point to a **folder**; each output is
  written alongside its input using the same filename

---

## Input / Output Edge Cases

Handled in `main()` before the pipeline runs:

| Situation | Behaviour |
|---|---|
| Input file does not exist | `sys.exit(1)` with an error message |
| Input is a folder | expand to `*.txt` in that folder (non-recursive) |
| `-o` directory does not exist | create all missing parent directories |
| `-o` points to the same path as the input | `sys.exit(1)` — prevents data loss |
| `-o` points to an existing file | overwrite silently |

---

## Phase 1 — Blacklist (stdlib, no new deps)

**Module**: `compactor/blacklist.py`

1. Token-level removal using a customizable blacklist source
    - Resolution order:
       1. `--blacklist-file PATH` (CLI override)
       2. local `blacklist.txt` in working directory
       3. built-in fallback defaults
    - Built-in fallback defaults (explicit):
       `the`, `a`, `an`, `of`, `to`, `and`, `in`, `is`, `it`, `that`, `for`, `on`, `with`, `as`, `at`, `by`, `from`, `be`, `are`, `was`, `were`
2. Token-level removal using `data/fillers.txt` ("um", "uh", "like", "you know", "basically"…)
3. Sentence-level regex filter: sponsor / intro / outro patterns
   - "sponsored by", "use code", "promo code"
   - "hello everyone", "welcome back", "in today's video"
   - "don't forget to like", "hit the subscribe button", "see you in the next"
4. Optional timestamp stripping via `--strip-timestamps` (`[00:12]`, `0:12`, `00:12:34` patterns)

### Phase 1 architecture notes

- Blacklist file format: UTF-8 text, one word or phrase per line; empty lines and `#` comments ignored.
- Matching remains case-insensitive.
- Tests must read the active blacklist source so behavior validates against the real loaded list.
- A later validation task will ensure default blacklist coverage remains sufficient.

---

## Phase 2 — Frequency Analysis (stdlib, no new deps)

**Module**: `compactor/frequency.py`

1. Tokenize the full transcript (lowercase, strip punctuation)
2. Build a frequency map
3. Drop tokens whose frequency exceeds `--freq-threshold` fraction of total tokens
   - These are transcript-specific noise words (e.g. a speaker repeating "right" constantly)
4. `--stats` reports which tokens were dropped and their frequency

---

## Phase 3 — NLP Filter (adds `spacy` dependency)

**Module**: `compactor/nlp_filter.py`

1. POS-tag with spaCy `en_core_web_sm`
2. Drop `ADV` tokens that don't anchor meaning ("really", "very", "quite", "just")
3. Drop discourse markers ("so", "well", "now", "right", "okay")
4. Drop weak `ADJ` (configurable)
5. Dependency added at this phase only: `uv add spacy`

---

## Pipeline

**Module**: `compactor/pipeline.py`

- Receives the transcript text and a config object (which phases are enabled + params)
- Runs enabled phases in order: 1 → 2 → 3
- Returns the compacted text
- Optionally reports per-phase token reduction (for `--stats`)

---

## Packaging

- `[build-system]` using hatchling in `pyproject.toml`
- `[project.scripts]`: `transcript-compactor = "main:main"`
- `uv build` → `dist/`
- `uv tool install .` → installable locally

---

## Delivery Order (Iterative, TDD)

Each step follows the RESEARCH → TEST → DOCUMENT → IMPLEMENT → IMPROVE → SUMMARIZE cycle.

| Step | Scope | New deps |
|---|---|---|
| 1 | Scaffold: `compactor/` package, `pipeline.py` skeleton, CLI in `main.py` | — |
| 2 | Phase 1: blacklist + data files + sentence-level filter | — |
| 3 | Phase 2: frequency analysis | — |
| 4 | Phase 3: NLP filter | `spacy` |
| 5 | Packaging: build-system, console script, `uv build` validation | hatchling |

---

## Open Questions / Notes

- Input assumed UTF-8 plain text, one paragraph per line (typical YouTube export)
- Sentences are preserved as units; token removal is within sentences
- `--strip-timestamps` is standalone and excluded from `--all` (clipper handles this by default)
- Phase 3 model: `en_core_web_sm` (small, fast); upgrade to `en_core_web_md` if accuracy is insufficient
