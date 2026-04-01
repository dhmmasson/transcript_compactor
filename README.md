# transcript_compactor

transcript_compactor is a tool to compact YouTube transcript text for LLM-oriented workflows. The goal is to reduce transcript size to save tokens while retaining essential content.

This project explores techniques to minimize text length without significant quality loss, including:

- Removing common function words (e.g., the, a, this, that) — testing whether these contribute meaningfully to LLM understanding.
- Filtering out high-frequency words to reduce redundancy.
- Eliminating [[weasel words]] and passive constructions using shell scripts.
- Randomly removing words, inspired by techniques in machine learning where portions of input data (e.g., image patches) are masked during training.

The project is experimental and intended to find the optimal balance between token efficiency and semantic fidelity.

The project is being built iteratively. Current behavior is intentionally conservative: Phase 1 removes only a small exact-match blacklist of common determiners. This is also a test of the development process with AI-generated code and tests, commit discipline, and documentation practices. You can check the [plan](plan.md) for details on the development process and upcoming features as well as the commits for a step-by-step history of the implementation.

## Current Features

- CLI entry point in `main.py`
- Single file, multiple file, or folder input
- Safe output handling with directory creation and overwrite guards
- Phase 1 blacklist filter via `--blacklist`
- Custom blacklist file support at the module level (`apply_blacklist(..., blacklist_file=...)`)

## Phase 1 Blacklist

Built-in fallback blacklist:

```text
the
a
an
this
that
those
these
```

Behavior:

- Exact token match only
- Case-insensitive
- Punctuation is preserved unless removals create adjacent punctuation, in which case the highest-priority punctuation survives: `,` < `;` < `.` < `!` < `?`

## Development

This project uses [uv](https://docs.astral.sh/uv/) for dependency management and execution.

```sh
uv run main.py transcripts/transcript1.txt --blacklist
uv run main.py transcripts/transcript1.txt transcripts/clean.txt --blacklist
uv run main.py transcripts/ --blacklist -o out/
uv run pytest
uv run pytest --cov=compactor --cov=main --cov-report=term-missing -q
```

## Roadmap

- Planned CLI support for `--blacklist-file PATH`
- Phase 2: frequency analysis
- Phase 3: NLP-based filtering
- Packaging: hatchling build backend and console script

## License

MIT
