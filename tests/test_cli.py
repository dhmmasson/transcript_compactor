# Tests for main.py CLI argument parsing — scaffold step
#
# These tests cover:
#   - parse_args() exists and returns a Namespace
#   - Positional 'file' argument is required (no args → SystemExit)
#   - All phase flags are False by default
#   - Each flag can be set individually
#   - --all flag is parsed (expansion to individual flags done in main())
#   - --strip-timestamps is independent (not part of --all)
#   - -o / --output stores the path
#   - --stats flag is parsed
#   - --freq-threshold parsed as float, defaults to 0.02
#
# All tests are RED at this point: parse_args does not exist in main.py yet.

import pytest
from main import parse_args, main


class TestParseArgsRequired:
    def test_no_arguments_exits(self):
        """Edge case: calling with no args must fail — file is required."""
        with pytest.raises(SystemExit):
            parse_args([])


class TestParseArgsDefaults:
    def test_file_is_stored(self):
        """Nominal: the positional file path is stored on args.file as a one-element list."""
        args = parse_args(["transcript.txt"])
        assert args.file == ["transcript.txt"]

    def test_blacklist_disabled_by_default(self):
        """--blacklist is off unless explicitly passed."""
        args = parse_args(["transcript.txt"])
        assert args.blacklist is False

    def test_frequency_disabled_by_default(self):
        """--frequency is off unless explicitly passed."""
        args = parse_args(["transcript.txt"])
        assert args.frequency is False

    def test_nlp_disabled_by_default(self):
        """--nlp is off unless explicitly passed."""
        args = parse_args(["transcript.txt"])
        assert args.nlp is False

    def test_all_disabled_by_default(self):
        """--all is off unless explicitly passed."""
        args = parse_args(["transcript.txt"])
        assert args.all is False

    def test_strip_timestamps_disabled_by_default(self):
        """--strip-timestamps is off by default and independent of --all."""
        args = parse_args(["transcript.txt"])
        assert args.strip_timestamps is False

    def test_stats_disabled_by_default(self):
        """--stats is off by default."""
        args = parse_args(["transcript.txt"])
        assert args.stats is False

    def test_output_is_none_by_default(self):
        """-o/--output defaults to None (means stdout)."""
        args = parse_args(["transcript.txt"])
        assert args.output is None

    def test_freq_threshold_default_is_0_02(self):
        """--freq-threshold defaults to 0.02."""
        args = parse_args(["transcript.txt"])
        assert args.freq_threshold == 0.02


class TestParseArgsFlags:
    def test_blacklist_flag(self):
        """--blacklist sets args.blacklist to True."""
        args = parse_args(["transcript.txt", "--blacklist"])
        assert args.blacklist is True

    def test_frequency_flag(self):
        """--frequency sets args.frequency to True."""
        args = parse_args(["transcript.txt", "--frequency"])
        assert args.frequency is True

    def test_nlp_flag(self):
        """--nlp sets args.nlp to True."""
        args = parse_args(["transcript.txt", "--nlp"])
        assert args.nlp is True

    def test_all_flag(self):
        """--all sets args.all to True."""
        args = parse_args(["transcript.txt", "--all"])
        assert args.all is True

    def test_strip_timestamps_flag(self):
        """--strip-timestamps sets args.strip_timestamps to True."""
        args = parse_args(["transcript.txt", "--strip-timestamps"])
        assert args.strip_timestamps is True

    def test_stats_flag(self):
        """--stats sets args.stats to True."""
        args = parse_args(["transcript.txt", "--stats"])
        assert args.stats is True

    def test_output_short_flag(self):
        """-o stores the output path."""
        args = parse_args(["transcript.txt", "-o", "out.txt"])
        assert args.output == "out.txt"

    def test_output_long_flag(self):
        """--output stores the output path."""
        args = parse_args(["transcript.txt", "--output", "out.txt"])
        assert args.output == "out.txt"

    def test_freq_threshold_custom_value(self):
        """--freq-threshold parses the float value."""
        args = parse_args(["transcript.txt", "--freq-threshold", "0.05"])
        assert args.freq_threshold == 0.05

    def test_multiple_flags_combined(self):
        """Multiple flags can be combined freely."""
        args = parse_args(["transcript.txt", "--blacklist", "--frequency", "--stats"])
        assert args.blacklist is True
        assert args.frequency is True
        assert args.stats is True
        assert args.nlp is False


class TestParseArgsMultipleFiles:
    def test_single_file_stored_as_list(self):
        """Nominal: a single file path is stored as a one-element list."""
        args = parse_args(["transcript.txt"])
        assert args.file == ["transcript.txt"]

    def test_multiple_files_stored_as_list(self):
        """Nominal: multiple positional paths are stored in order."""
        args = parse_args(["file1.txt", "file2.txt", "file3.txt"])
        assert args.file == ["file1.txt", "file2.txt", "file3.txt"]

    def test_folder_path_stored_as_list(self):
        """Nominal: a folder path is accepted — expansion to .txt files is main()'s job."""
        args = parse_args(["transcripts/"])
        assert args.file == ["transcripts/"]


class TestMainBehavior:
    def test_missing_file_exits_with_error(self, tmp_path):
        """Edge case: non-existent input file must exit with a non-zero code."""
        nonexistent = str(tmp_path / "no_such_file.txt")
        with pytest.raises(SystemExit) as exc_info:
            main([nonexistent])
        assert exc_info.value.code != 0

    def test_output_written_to_stdout(self, tmp_path, capsys):
        """Nominal: no -o flag → result written to stdout."""
        input_file = tmp_path / "input.txt"
        input_file.write_text("Hello world.")
        main([str(input_file)])
        captured = capsys.readouterr()
        assert "Hello world." in captured.out

    def test_output_written_to_file(self, tmp_path):
        """Nominal: -o flag writes result to the specified file."""
        input_file = tmp_path / "input.txt"
        input_file.write_text("Hello world.")
        output_file = tmp_path / "out.txt"
        main([str(input_file), "-o", str(output_file)])
        assert output_file.read_text() == "Hello world."

    def test_output_directory_is_created(self, tmp_path):
        """Edge case: missing parent directories for -o are created automatically."""
        input_file = tmp_path / "input.txt"
        input_file.write_text("Hello world.")
        output_file = tmp_path / "nested" / "dir" / "out.txt"
        main([str(input_file), "-o", str(output_file)])
        assert output_file.exists()

    def test_output_same_as_input_exits_with_error(self, tmp_path):
        """Safety: output path equal to input path must error to prevent data loss."""
        input_file = tmp_path / "input.txt"
        input_file.write_text("Hello world.")
        with pytest.raises(SystemExit) as exc_info:
            main([str(input_file), "-o", str(input_file)])
        assert exc_info.value.code != 0

    def test_existing_output_file_is_overwritten(self, tmp_path):
        """Nominal: existing output file is overwritten silently."""
        input_file = tmp_path / "input.txt"
        input_file.write_text("New content.")
        output_file = tmp_path / "out.txt"
        output_file.write_text("Old content.")
        main([str(input_file), "-o", str(output_file)])
        assert output_file.read_text() == "New content."

    def test_all_flag_enables_all_phases_in_main(self, tmp_path, capsys):
        """Coverage: --all sets blacklist/frequency/nlp inside main()."""
        input_file = tmp_path / "input.txt"
        input_file.write_text("The cat.")
        main([str(input_file), "--all"])
        captured = capsys.readouterr()
        # blacklist is active → "The" removed
        assert "cat." in captured.out

    def test_directory_input_expands_txt_files(self, tmp_path, capsys):
        """Coverage: passing a directory globs all .txt files inside it."""
        sub = tmp_path / "transcripts"
        sub.mkdir()
        (sub / "a.txt").write_text("Hello.")
        (sub / "b.txt").write_text("World.")
        (sub / "c.csv").write_text("Ignored.")  # non-txt
        main([str(sub)])
        captured = capsys.readouterr()
        assert "Hello." in captured.out
        assert "World." in captured.out
        assert "Ignored." not in captured.out
