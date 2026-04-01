# Tests for compactor/pipeline.py — scaffold step
#
# These tests cover:
#   - PipelineConfig defaults (all phases disabled, correct threshold default)
#   - run_pipeline pass-through behaviour (no phases enabled → text unchanged)
#   - Edge cases: empty string, multiline input
#
# All tests are RED at this point: compactor.pipeline does not exist yet.

from compactor.pipeline import PipelineConfig, run_pipeline


class TestPipelineConfig:
    def test_all_phases_disabled_by_default(self):
        """Nominal: a fresh PipelineConfig has every phase flag set to False."""
        config = PipelineConfig()
        assert config.blacklist is False
        assert config.frequency is False
        assert config.nlp is False
        assert config.strip_timestamps is False
        assert config.stats is False

    def test_freq_threshold_default_is_0_02(self):
        """Default frequency threshold is 0.02 (2 % of total tokens)."""
        config = PipelineConfig()
        assert config.freq_threshold == 0.02

    def test_individual_flags_can_be_set_independently(self):
        """Each flag can be toggled without affecting the others."""
        config = PipelineConfig(blacklist=True)
        assert config.blacklist is True
        assert config.frequency is False
        assert config.nlp is False


class TestRunPipeline:
    def test_returns_text_unchanged_when_no_phases_enabled(self):
        """Nominal: with no phases active the output equals the input exactly."""
        config = PipelineConfig()
        text = "Many people have dreamed of summiting the highest mountains."
        result = run_pipeline(text, config)
        assert result == text

    def test_returns_a_string(self):
        """run_pipeline always returns a str, never None or another type."""
        config = PipelineConfig()
        result = run_pipeline("some text", config)
        assert isinstance(result, str)

    def test_handles_empty_string(self):
        """Edge case: empty input should return empty output without error."""
        config = PipelineConfig()
        result = run_pipeline("", config)
        assert result == ""

    def test_handles_multiline_text(self):
        """Edge case: newlines and multiple paragraphs are preserved as-is."""
        config = PipelineConfig()
        text = "Line one.\nLine two.\n\nParagraph two."
        result = run_pipeline(text, config)
        assert result == text


class TestRunPipelineBlacklistIntegration:
    def test_applies_blacklist_when_enabled(self):
        """Nominal: blacklist-enabled pipeline removes configured stopwords/fillers."""
        config = PipelineConfig(blacklist=True)
        text = "This is the basic idea of the technique."
        result = run_pipeline(text, config)
        assert result == "basic idea technique."

    def test_keeps_pass_through_when_blacklist_disabled(self):
        """Nominal: disabling blacklist keeps existing pass-through behavior."""
        config = PipelineConfig(blacklist=False)
        text = "This is the basic idea of the technique."
        result = run_pipeline(text, config)
        assert result == text
