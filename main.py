import argparse
import sys
from pathlib import Path
from typing import Iterable

from compactor.pipeline import PipelineConfig, run_pipeline


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Compact a YouTube transcript for LLM use."
    )
    parser.add_argument(
        "file",
        nargs="+",
        help="Path to transcript .txt file(s) or a folder containing .txt files.",
    )
    parser.add_argument(
        "--blacklist", action="store_true", help="Enable Phase 1: blacklist filter."
    )
    parser.add_argument(
        "--frequency", action="store_true", help="Enable Phase 2: frequency analysis."
    )
    parser.add_argument(
        "--nlp", action="store_true", help="Enable Phase 3: NLP filter."
    )
    parser.add_argument("--all", action="store_true", help="Enable all phases.")
    parser.add_argument(
        "--strip-timestamps",
        dest="strip_timestamps",
        action="store_true",
        help="Strip timestamp markers (standalone, not part of --all).",
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Print token counts before/after each phase.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=None,
        help="Write result to file (default: stdout).",
    )
    parser.add_argument(
        "--freq-threshold",
        dest="freq_threshold",
        type=float,
        default=0.02,
        help="Frequency threshold for Phase 2 (default: 0.02).",
    )
    return parser.parse_args(argv)


def _resolve_input_files(paths: Iterable[str]) -> list[Path]:
    resolved: list[Path] = []
    for p in paths:
        path = Path(p)
        if path.is_dir():
            resolved.extend(sorted(path.glob("*.txt")))
        else:
            resolved.append(path)
    return resolved


def _validate_input_files(input_files: list[Path]) -> None:
    if not input_files:
        print(
            "Error: no .txt input files found from the provided path(s)",
            file=sys.stderr,
        )
        sys.exit(1)

    for input_file in input_files:
        if not input_file.exists():
            print(f"Error: file not found: {input_file}", file=sys.stderr)
            sys.exit(1)


def _validate_output_not_input(output_path: Path, input_files: list[Path]) -> None:
    resolved_output = output_path.resolve()
    for input_file in input_files:
        if input_file.resolve() == resolved_output:
            print(
                f"Error: output path is the same as input: {input_file}",
                file=sys.stderr,
            )
            sys.exit(2)


def main(argv=None):
    args = parse_args(argv)

    if args.all:
        args.blacklist = True
        args.frequency = True
        args.nlp = True

    input_files = _resolve_input_files(args.file)

    _validate_input_files(input_files)

    if args.output is not None:
        _validate_output_not_input(Path(args.output), input_files)

    config = PipelineConfig(
        blacklist=args.blacklist,
        frequency=args.frequency,
        nlp=args.nlp,
        strip_timestamps=args.strip_timestamps,
        stats=args.stats,
        freq_threshold=args.freq_threshold,
    )

    results = []
    for input_file in input_files:
        text = input_file.read_text(encoding="utf-8")
        results.append(run_pipeline(text, config))

    output = "\n".join(results)

    if args.output is not None:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(output, encoding="utf-8")
    else:
        print(output)


if __name__ == "__main__":
    main()
