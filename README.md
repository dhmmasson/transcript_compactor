# transcript_compactor

Compact YouTube transcript text for LLM-oriented downstream use.

The project is being built iteratively. Current behavior is intentionally conservative: Phase 1 removes only a small exact-match blacklist of common determiners.

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
