# Tests for compactor/blacklist.py — Phase 1 RED tests
#
# Phase 1 is one operation: remove every token that appears in a blacklist.
# No filler categories, no regex patterns — just a flat word list.

from compactor.blacklist import apply_blacklist


class TestApplyBlacklist:
    def test_removes_default_blacklist_words_from_sentence(self):
        """Nominal (example 1): default stopwords are removed, meaning words stay."""
        # Arrange
        text = "This is the basic idea of the technique."

        # Act
        result = apply_blacklist(text)

        # Assert
        assert result == "This basic idea technique."

    def test_case_insensitive_matching(self):
        """Nominal (example 3): uppercase blacklist words are removed too."""
        # Arrange
        text = "The idea of the method is clear."

        # Act
        result = apply_blacklist(text)

        # Assert
        assert result == "idea method clear."

    def test_preserves_words_not_in_blacklist(self):
        """Nominal (example 2): near-matches like 'liked' vs 'like' both stay."""
        # Arrange
        text = "If you liked the video, click the like button and subscribe."

        # Act
        result = apply_blacklist(text)

        # Assert
        assert result == "If you liked video, click like button subscribe."

    def test_no_blacklist_words_present_unchanged(self):
        """Edge (example 4): text with no blacklist words passes through unchanged."""
        # Arrange
        text = "Erosion gradients generate branching gullies."

        # Act
        result = apply_blacklist(text)

        # Assert
        assert result == "Erosion gradients generate branching gullies."

    def test_normalizes_whitespace_after_removals(self):
        """Edge (example 5): extra spaces from removed tokens are collapsed."""
        # Arrange
        text = "Well, this is, like, basically, a test."

        # Act
        result = apply_blacklist(text)

        # Assert
        assert result == "Well, this like, basically, test."

    def test_empty_input_returns_empty_output(self):
        """Edge: empty input remains empty without errors."""
        # Arrange
        text = ""

        # Act
        result = apply_blacklist(text)

        # Assert
        assert result == ""

    def test_uses_custom_blacklist_file(self, tmp_path):
        """Nominal (example 6): explicit blacklist file overrides defaults."""
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

        # Assert
        assert result == "idea method clear."
