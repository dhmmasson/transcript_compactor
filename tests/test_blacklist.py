# Tests for compactor/blacklist.py — Phase 1 blacklist behavior
#
# Phase 1 is one operation: remove every token that appears in a blacklist.
# No filler categories, no regex patterns — just a flat word list.
#
# Default blacklist: the, a, an, this, that, those, these (determiners only).
# Punctuation rule: when a word is removed, its attached punctuation is
# preserved. Adjacent punctuation marks are then cleaned up (remove in
# priority order: comma < semicolon < period < ! < ?).
#
# Test cases for blacklist removal + punctuation are generated from
# tests/generate_blacklist_cases.py → tests/blacklist_cases.yaml
# The YAML is the source of truth for expected I/O.

from pathlib import Path

import pytest
import yaml

from compactor.blacklist import apply_blacklist

CASES_PATH = Path(__file__).parent / "blacklist_cases.yaml"


def _load_cases() -> list[dict]:
    return yaml.safe_load(CASES_PATH.read_text(encoding="utf-8"))


def _case_ids() -> list[str]:
    """Short test IDs from rationale (first 60 chars)."""
    return [c["rationale"][:60] for c in _load_cases()]


class TestApplyBlacklistFromYAML:
    """All blacklist removal + punctuation cases loaded from YAML."""

    @pytest.mark.parametrize("case", _load_cases(), ids=_case_ids())
    def test_blacklist_case(self, case, tmp_path, monkeypatch):
        # Ensure no local blacklist.txt interferes — run from empty dir
        monkeypatch.chdir(tmp_path)

        result = apply_blacklist(case["input"])

        assert result == case["output"], (
            f"\nRationale: {case['rationale']}\n"
            f"  Input:    {case['input']!r}\n"
            f"  Expected: {case['output']!r}\n"
            f"  Got:      {result!r}"
        )


class TestApplyBlacklistSource:
    def test_uses_custom_blacklist_file(self, tmp_path):
        """Nominal: explicit blacklist file overrides defaults."""
        # Arrange
        custom_blacklist = tmp_path / "custom_blacklist.txt"
        custom_blacklist.write_text("erosion\ngradients\n", encoding="utf-8")
        text = "Erosion gradients generate branching gullies."

        # Act
        result = apply_blacklist(text, blacklist_file=str(custom_blacklist))

        # Assert
        assert result == "generate branching gullies."

    def test_uses_local_blacklist_txt_fallback(self, tmp_path, monkeypatch):
        """Edge: local blacklist.txt in cwd is used when no parameter given."""
        # Arrange
        local_blacklist = tmp_path / "blacklist.txt"
        local_blacklist.write_text("branching\n", encoding="utf-8")
        monkeypatch.chdir(tmp_path)
        text = "Erosion gradients generate branching gullies."

        # Act
        result = apply_blacklist(text)

        # Assert
        assert result == "Erosion gradients generate gullies."

    def test_uses_fallback_defaults_when_no_file_exists(self, tmp_path, monkeypatch):
        """Edge: built-in default list used when no file source exists at all."""
        # Arrange
        monkeypatch.chdir(tmp_path)
        text = "The idea of the method is clear."

        # Act
        result = apply_blacklist(text)

        # Assert — only "The" and "the" removed (determiners); "of", "is" stay
        assert result == "idea of method is clear."


class TestApplyBlacklistMultiline:
    def test_preserves_line_breaks_while_removing_blacklisted_words(self, tmp_path, monkeypatch):
        """Line boundaries should stay intact for transcript readability."""
        # Arrange
        monkeypatch.chdir(tmp_path)
        text = "The cat\nand the dog"

        # Act
        result = apply_blacklist(text)

        # Assert
        assert result == "cat\nand dog"

    def test_preserves_blank_lines_after_removals(self, tmp_path, monkeypatch):
        """Paragraph boundaries (empty lines) should be preserved."""
        # Arrange
        monkeypatch.chdir(tmp_path)
        text = "the cat\n\nthis dog"

        # Act
        result = apply_blacklist(text)

        # Assert
        assert result == "cat\n\ndog"

    def test_does_not_merge_punctuation_across_lines(self, tmp_path, monkeypatch):
        """Punctuation rules apply within a line; line breaks are not collapsed."""
        # Arrange
        monkeypatch.chdir(tmp_path)
        text = "cat,\nthe dog."

        # Act
        result = apply_blacklist(text)

        # Assert
        assert result == "cat,\ndog."
