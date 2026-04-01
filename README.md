# transcript_compactor

A Python project for compacting and processing transcripts.

## Roadmap Snapshot

- Phase 1 (blacklist): customizable blacklist source via `--blacklist-file`.
- Default blacklist resolution will be:
	1. `--blacklist-file PATH`
	2. local `blacklist.txt`
	3. built-in fallback words (`the`, `a`, `an`, `of`, `to`, `and`, ...).
- Phase 2: frequency analysis.
- Phase 3: NLP-based filtering.

## Version

v0.0.1

## Dependency Management

This project uses [uv](https://github.com/astral-sh/uv) for dependency management. Install uv with:

```sh
pip install uv
```

## License

MIT
