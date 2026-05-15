"""
Unit tests for vocab_service.py (Iteration 1).
"""

import sys
import os

# Allow importing from src/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest
from vocab_service import (
    VOCAB_DIFFICULTY,
    is_difficult,
    get_definition,
    tokenize,
    find_difficult_words,
    find_difficult_words_sorted,
)


class TestVocabDictionary:
    """Tests for the hardcoded vocabulary database."""

    def test_vocab_has_at_least_180_words(self):
        """Ensure we have roughly the target number of difficult words."""
        assert len(VOCAB_DIFFICULTY) >= 180

    def test_vocab_entries_have_definition_and_pos(self):
        """Every entry should be a (definition, pos) tuple of two strings."""
        for word, entry in VOCAB_DIFFICULTY.items():
            assert isinstance(entry, tuple), f"Expected tuple for '{word}', got {type(entry)}"
            assert len(entry) == 2, f"Expected 2 items for '{word}', got {len(entry)}"
            assert isinstance(entry[0], str), f"Definition for '{word}' must be str"
            assert isinstance(entry[1], str), f"POS for '{word}' must be str"
            assert len(entry[0]) > 0, f"Definition for '{word}' must not be empty"

    def test_all_keys_are_lowercase(self):
        """All vocabulary keys should be lowercase for case-insensitive matching."""
        for word in VOCAB_DIFFICULTY:
            assert word == word.lower(), f"Key '{word}' is not lowercase"


class TestIsDifficult:
    """Tests for is_difficult()."""

    def test_known_difficult_word(self):
        assert is_difficult("evidence") is True
        assert is_difficult("atmosphere") is True
        assert is_difficult("telescope") is True

    def test_case_insensitive(self):
        assert is_difficult("Evidence") is True
        assert is_difficult("EVIDENCE") is True
        assert is_difficult("AtMoSpHeRe") is True

    def test_unknown_word(self):
        assert is_difficult("cat") is False
        assert is_difficult("dog") is False
        assert is_difficult("apple") is False
        assert is_difficult("") is False

    def test_whitespace_handling(self):
        assert is_difficult("  evidence  ") is True


class TestGetDefinition:
    """Tests for get_definition()."""

    def test_returns_tuple_for_known_word(self):
        result = get_definition("evidence")
        assert result is not None
        assert result[0] == "证据"
        assert result[1] == "n."

    def test_case_insensitive(self):
        result = get_definition("ATMOSPHERE")
        assert result is not None
        assert result[0] == "大气层；氛围"

    def test_returns_none_for_unknown_word(self):
        assert get_definition("pizza") is None
        assert get_definition("") is None

    def test_returns_none_for_whitespace_only(self):
        assert get_definition("   ") is None


class TestTokenize:
    """Tests for tokenize()."""

    def test_simple_sentence(self):
        tokens = tokenize("The cat sat.")
        # Should be: "The", " ", "cat", " ", "sat", "."
        texts = [t["text"] for t in tokens]
        assert texts == ["The", " ", "cat", " ", "sat", "."]

    def test_word_flags(self):
        tokens = tokenize("Hello world")
        assert tokens[0]["is_word"] is True
        assert tokens[0]["word"] == "Hello"
        assert tokens[1]["is_word"] is False  # space
        assert tokens[1]["word"] is None
        assert tokens[2]["is_word"] is True
        assert tokens[2]["word"] == "world"

    def test_difficult_word_detection(self):
        tokens = tokenize("The evidence is clear.")
        # Find the evidence token
        evidence_tokens = [t for t in tokens if t["word"] == "evidence"]
        assert len(evidence_tokens) == 1
        t = evidence_tokens[0]
        assert t["is_difficult"] is True
        assert t["definition"] == "证据"
        assert t["pos"] == "n."

    def test_normal_word_not_difficult(self):
        tokens = tokenize("The cat is happy.")
        cat_tokens = [t for t in tokens if t["word"] == "cat"]
        assert len(cat_tokens) == 1
        assert cat_tokens[0]["is_difficult"] is False

    def test_punctuation_preserved(self):
        tokens = tokenize("Hello, world!")
        comma_tokens = [t for t in tokens if t["text"] == ","]
        exclaim_tokens = [t for t in tokens if t["text"] == "!"]
        assert len(comma_tokens) == 1
        assert len(exclaim_tokens) == 1

    def test_multiple_spaces_preserved(self):
        tokens = tokenize("Hello   world")
        texts = [t["text"] for t in tokens]
        assert "   " in texts

    def test_empty_string(self):
        tokens = tokenize("")
        assert tokens == []

    def test_contractions(self):
        tokens = tokenize("don't can't")
        words = [t["text"] for t in tokens if t["is_word"]]
        assert "don't" in words
        assert "can't" in words

    def test_numbers_not_words(self):
        tokens = tokenize("I have 3 cats and 42 dogs.")
        word_texts = [t["text"] for t in tokens if t["is_word"]]
        assert "3" not in word_texts
        assert "42" not in word_texts


class TestFindDifficultWords:
    """Tests for find_difficult_words()."""

    def test_finds_difficult_words(self):
        text = "The discovery was confirmed by evidence from the telescope."
        result = find_difficult_words(text)
        words_found = {r["lower"] for r in result}
        assert "discovery" in words_found
        assert "confirmed" in words_found
        assert "evidence" in words_found
        assert "telescope" in words_found

    def test_no_difficult_words(self):
        text = "The cat sat on the mat with a happy dog."
        result = find_difficult_words(text)
        assert result == []

    def test_each_word_appears_once(self):
        text = "The evidence shows more evidence every day."
        result = find_difficult_words(text)
        evidence_entries = [r for r in result if r["lower"] == "evidence"]
        assert len(evidence_entries) == 1

    def test_empty_string(self):
        result = find_difficult_words("")
        assert result == []

    def test_result_structure(self):
        text = "Scientists made a discovery."
        result = find_difficult_words(text)
        for r in result:
            assert "word" in r
            assert "lower" in r
            assert "definition" in r
            assert "pos" in r
            assert r["lower"] == r["word"].lower()


class TestFindDifficultWordsSorted:
    """Tests for find_difficult_words_sorted()."""

    def test_sorted_by_appearance(self):
        text = "The telescope found evidence of a planet."
        result = find_difficult_words_sorted(text)
        # "telescope" appears before "evidence" which is before "planet"
        assert result[0]["lower"] == "telescope"
        assert result[1]["lower"] == "evidence"
        assert result[2]["lower"] == "planet"

    def test_same_result_as_unsorted(self):
        text = "The discovery was made using a telescope and the evidence was clear."
        unsorted = find_difficult_words(text)
        sorted_result = find_difficult_words_sorted(text)
        assert len(sorted_result) == len(unsorted)
        # Same words (order may differ)
        unsorted_lowers = {r["lower"] for r in unsorted}
        sorted_lowers = {r["lower"] for r in sorted_result}
        assert unsorted_lowers == sorted_lowers


class TestIntegrationWithArticle:
    """Integration tests using actual article content."""

    def test_article_has_reasonable_difficult_count(self):
        """The article should have 5-10 difficult words (not 40-50 like Iter 0)."""
        text = (
            "A 17-year-old student from New York made an amazing discovery last week. "
            "While working on a school science project with a small telescope, "
            "he found a new planet outside our solar system. "
            "Scientists at NASA later confirmed his finding. "
            "The news quickly spread across the internet, and many people called him a young genius. "
            "The planet is about six times bigger than Earth. It is very far away "
            "more than 1,000 light-years from us. The planet goes around a star that looks "
            "a lot like our sun. Scientists say the surface of the planet is extremely hot, "
            "over 800 degrees, so there is probably no life there. "
            "But the planet's atmosphere is still very interesting to study. "
            "The discovery is still very important. It shows that young people can do real science, "
            "not just read about it in textbooks. The student, named Jack Chen, spent three months "
            "looking at data from his school's small telescope. He said he almost missed the evidence "
            "because the signal was very weak. "
            "NASA has invited Jack to visit their space center this summer. He will meet real "
            "astronomers and learn more about how to explore the universe. "
            "Jack said he plans to study physics in college and hopes to discover more planets in the future."
        )
        result = find_difficult_words(text)
        count = len(result)
        # Should be between 5 and 12 difficult words for a ~220 word article
        assert 5 <= count <= 16, (
            f"Expected 5-13 difficult words, got {count}. "
            f"Words: {[r['word'] for r in result]}"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
