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
from main import parse_args


class TestParseArgsRequired:
    def test_no_arguments_exits(self):
        """Edge case: calling with no args must fail — file is required."""
        with pytest.raises(SystemExit):
            parse_args([])


class TestParseArgsDefaults:
    def test_file_is_stored(self):
        """Nominal: the positional file path is stored on args.file."""
        args = parse_args(["transcript.txt"])
        assert args.file == "transcript.txt"

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
