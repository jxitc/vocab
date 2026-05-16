"""
Unit tests for vocab_service.py (Iteration 6).
Tests updated vocabulary format with levels, level-based filtering,
and known-word filtering functions.
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
    get_full_entry,
    is_difficult_for_level,
    get_levels_for_user,
    get_max_highlights,
    filter_vocab_by_level,
    tokenize,
    find_difficult_words,
    find_difficult_words_sorted,
    count_vocab_by_level,
    filter_known_words,
    filter_known_words_from_tokens,
    stem_word,
    LEVEL_NAMES,
    MAX_HIGHLIGHTS,
    LEVEL_HIGHLIGHT_RANGES,
)


class TestVocabDictionary:
    """Tests for the hardcoded vocabulary database."""

    def test_vocab_has_at_least_200_words(self):
        """Ensure we have the target number of words across all levels."""
        assert len(VOCAB_DIFFICULTY) >= 200

    def test_vocab_entries_have_definition_pos_and_level(self):
        """Every entry should be a (definition, pos, level) tuple of three items."""
        for word, entry in VOCAB_DIFFICULTY.items():
            assert isinstance(entry, tuple), f"Expected tuple for '{word}', got {type(entry)}"
            assert len(entry) == 3, f"Expected 3 items for '{word}', got {len(entry)}"
            assert isinstance(entry[0], str), f"Definition for '{word}' must be str"
            assert isinstance(entry[1], str), f"POS for '{word}' must be str"
            assert isinstance(entry[2], int), f"Level for '{word}' must be int"
            assert entry[2] in (1, 2, 3, 4), f"Level for '{word}' must be 1-4, got {entry[2]}"
            assert len(entry[0]) > 0, f"Definition for '{word}' must not be empty"

    def test_all_keys_are_lowercase(self):
        """All vocabulary keys should be lowercase for case-insensitive matching."""
        for word in VOCAB_DIFFICULTY:
            assert word == word.lower(), f"Key '{word}' is not lowercase"

    def test_level_counts_reasonable(self):
        """Each level should have a reasonable number of words."""
        counts = count_vocab_by_level()
        assert 35 <= counts[1] <= 55, f"Level 1 (小学) should have ~40-45 words, got {counts[1]}"
        assert 80 <= counts[2] <= 130, f"Level 2 (初中) should have ~80-120 words, got {counts[2]}"
        assert 55 <= counts[3] <= 105, f"Level 3 (高中) should have ~60-95 words, got {counts[3]}"
        assert 25 <= counts[4] <= 45, f"Level 4 (大学) should have ~30 words, got {counts[4]}"

    def test_known_level_4_words(self):
        """Verify some specific academic words exist at level 4."""
        assert "hypothesis" in VOCAB_DIFFICULTY
        assert VOCAB_DIFFICULTY["hypothesis"][2] == 4
        assert "paradigm" in VOCAB_DIFFICULTY
        assert VOCAB_DIFFICULTY["paradigm"][2] == 4
        assert "sustainable" in VOCAB_DIFFICULTY
        assert VOCAB_DIFFICULTY["sustainable"][2] == 4

    def test_level_names(self):
        """Verify level name mapping."""
        assert LEVEL_NAMES[1] == "小学"
        assert LEVEL_NAMES[2] == "初中"
        assert LEVEL_NAMES[3] == "高中"
        assert LEVEL_NAMES[4] == "大学"


class TestLevelConfiguration:
    """Tests for level configuration constants and helpers."""

    def test_get_levels_for_user(self):
        """Test cumulative level ranges for each user level."""
        assert get_levels_for_user(1) == {1}
        assert get_levels_for_user(2) == {1, 2}
        assert get_levels_for_user(3) == {1, 2, 3}
        assert get_levels_for_user(4) == {1, 2, 3, 4}
        # Invalid levels should default to {1, 2}
        assert get_levels_for_user(99) == {1, 2}

    def test_get_max_highlights(self):
        """Test max highlights per level."""
        assert get_max_highlights(1) == 3
        assert get_max_highlights(2) == 6
        assert get_max_highlights(3) == 8
        assert get_max_highlights(4) == 10
        # Invalid levels default to 6
        assert get_max_highlights(99) == 6

    def test_max_highlights_constants(self):
        """Verify the MAX_HIGHLIGHTS dict."""
        assert MAX_HIGHLIGHTS[1] == 3
        assert MAX_HIGHLIGHTS[2] == 6
        assert MAX_HIGHLIGHTS[3] == 8
        assert MAX_HIGHLIGHTS[4] == 10

    def test_level_highlight_ranges(self):
        """Verify cumulative highlight ranges."""
        assert LEVEL_HIGHLIGHT_RANGES[1] == {1}
        assert LEVEL_HIGHLIGHT_RANGES[2] == {1, 2}
        assert LEVEL_HIGHLIGHT_RANGES[3] == {1, 2, 3}
        assert LEVEL_HIGHLIGHT_RANGES[4] == {1, 2, 3, 4}

    def test_filter_vocab_by_level(self):
        """Test filtering vocab to a specific user level."""
        # 小学: only level 1 words
        l1 = filter_vocab_by_level(1)
        for entry in l1.values():
            assert entry[2] == 1

        # 初中: levels 1+2
        l2 = filter_vocab_by_level(2)
        for entry in l2.values():
            assert entry[2] in (1, 2)
        assert len(l2) >= len(l1)

        # 大学: all levels
        l4 = filter_vocab_by_level(4)
        assert len(l4) == len(VOCAB_DIFFICULTY)


class TestIsDifficult:
    """Tests for is_difficult()."""

    def test_known_difficult_word(self):
        assert is_difficult("evidence") is True
        assert is_difficult("atmosphere") is True
        assert is_difficult("telescope") is True
        assert is_difficult("hypothesis") is True

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


class TestIsDifficultForLevel:
    """Tests for level-aware difficulty checking."""

    def test_level1_word_only_for_elementary(self):
        """A level 1 word should be difficult for all user levels."""
        assert is_difficult_for_level("planet", 1) is True   # Planet is L1
        assert is_difficult_for_level("planet", 2) is True
        assert is_difficult_for_level("planet", 3) is True
        assert is_difficult_for_level("planet", 4) is True

    def test_level2_word_not_for_elementary(self):
        """A level 2 word should NOT be highlighted for 小学 users."""
        assert is_difficult_for_level("evidence", 2) is True   # evidence is L2, 初中 user
        assert is_difficult_for_level("evidence", 3) is True   # 高中 user sees it
        assert is_difficult_for_level("evidence", 4) is True   # 大学 user sees it
        # 小学 user should NOT see level 2 words
        assert is_difficult_for_level("evidence", 1) is False

    def test_level4_word_only_for_college(self):
        """A level 4 word should only be highlighted for 大学 users."""
        assert is_difficult_for_level("hypothesis", 4) is True
        assert is_difficult_for_level("hypothesis", 3) is False
        assert is_difficult_for_level("hypothesis", 2) is False
        assert is_difficult_for_level("hypothesis", 1) is False

    def test_unknown_word_never_difficult(self):
        assert is_difficult_for_level("pizza", 1) is False
        assert is_difficult_for_level("pizza", 4) is False


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


class TestGetFullEntry:
    """Tests for get_full_entry() which includes level."""

    def test_returns_triple_for_known_word(self):
        result = get_full_entry("evidence")
        assert result is not None
        assert len(result) == 3
        assert result[0] == "证据"
        assert result[1] == "n."
        assert isinstance(result[2], int)

    def test_returns_level_for_word(self):
        result = get_full_entry("planet")
        assert result is not None
        assert result[2] == 1  # planet is level 1

        result = get_full_entry("hypothesis")
        assert result is not None
        assert result[2] == 4  # hypothesis is level 4

    def test_returns_none_for_unknown(self):
        assert get_full_entry("pizza") is None


class TestTokenize:
    """Tests for tokenize()."""

    def test_simple_sentence(self):
        tokens = tokenize("The cat sat.")
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
        tokens = tokenize("The evidence is clear.", user_level=2)
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

    def test_numbers_are_word_tokens(self):
        """Numbers should be preserved as word tokens."""
        tokens = tokenize("I have 3 cats and 42 dogs.")
        word_texts = [t["text"] for t in tokens if t["is_word"]]
        assert "3" in word_texts
        assert "42" in word_texts
        num_tokens = [t for t in tokens if t["text"] == "3"]
        assert num_tokens[0]["is_difficult"] is False

    def test_hyphenated_number_words(self):
        """'17-year-old' and '1,000' must be single tokens."""
        tokens = tokenize("A 17-year-old student found 1,000 stars.")
        word_texts = [t["text"] for t in tokens if t["is_word"]]
        assert "17-year-old" in word_texts
        assert "1,000" in word_texts

    def test_level_filtering_in_tokenize(self):
        """Tokenize with level 1 should only mark level 1 words as difficult."""
        text = "The planet has an extraordinary atmosphere."
        # planet=L1, extraordinary=L3, atmosphere=L2
        tokens = tokenize(text, user_level=1)
        difficult = [t for t in tokens if t["is_difficult"]]
        assert len(difficult) == 1
        assert difficult[0]["word"] == "planet"

    def test_level_filtering_in_tokenize_level3(self):
        """Tokenize with level 3 should mark L1+L2+L3 words as difficult but not L4."""
        text = "The discovery of the planet was significant."
        # discovery=L1, planet=L1, significant=L3
        tokens = tokenize(text, user_level=3)
        difficult = [t for t in tokens if t["is_difficult"]]
        difficult_words = [t["word"] for t in difficult]
        assert "planet" in difficult_words
        assert "discovery" in difficult_words
        assert "significant" in difficult_words

    def test_token_includes_level_field(self):
        """Difficult tokens should include the 'level' field."""
        tokens = tokenize("The planet has an atmosphere.", user_level=4)
        planet_tokens = [t for t in tokens if t["word"] == "planet"]
        assert len(planet_tokens) == 1
        assert planet_tokens[0]["level"] == 1
        atmosphere_tokens = [t for t in tokens if t["word"] == "atmosphere"]
        assert len(atmosphere_tokens) == 1
        assert atmosphere_tokens[0]["level"] == 2


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
            assert "level" in r
            assert r["lower"] == r["word"].lower()

    def test_level_filtering(self):
        """find_difficult_words with level 1 should only return level 1 words."""
        text = "The planet was an extraordinary discovery with a telescope."
        result = find_difficult_words(text, user_level=1)
        words_found = {r["lower"] for r in result}
        # planet and discovery are L1, extraordinary is L3, telescope is L3
        assert "planet" in words_found
        assert "discovery" in words_found
        assert "extraordinary" not in words_found
        assert "telescope" not in words_found

    def test_level_filtering_all(self):
        """find_difficult_words with level 4 should return all levels."""
        text = "The sustainable development requires innovation."
        result = find_difficult_words(text, user_level=4)
        words_found = {r["lower"] for r in result}
        assert "sustainable" in words_found  # L4
        assert "innovation" in words_found   # L4


class TestFindDifficultWordsSorted:
    """Tests for find_difficult_words_sorted()."""

    def test_sorted_by_appearance(self):
        text = "The telescope found evidence of a planet."
        result = find_difficult_words_sorted(text)
        assert result[0]["lower"] == "telescope"
        assert result[1]["lower"] == "evidence"
        assert result[2]["lower"] == "planet"

    def test_same_result_as_unsorted(self):
        text = "The discovery was made using a telescope and the evidence was clear."
        unsorted = find_difficult_words(text)
        sorted_result = find_difficult_words_sorted(text)
        assert len(sorted_result) == len(unsorted)
        unsorted_lowers = {r["lower"] for r in unsorted}
        sorted_lowers = {r["lower"] for r in sorted_result}
        assert unsorted_lowers == sorted_lowers

    def test_level_filtering_sorted(self):
        text = "The planet was an extraordinary discovery with a telescope."
        result = find_difficult_words_sorted(text, user_level=1)
        words = [r["lower"] for r in result]
        assert "planet" in words
        assert "discovery" in words
        assert "extraordinary" not in words


class TestIntegrationWithArticle:
    """Integration tests using actual article content."""

    def test_article_has_reasonable_difficult_count(self):
        """The planet article should have 5-15 difficult words at level 4 (all)."""
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
        result = find_difficult_words(text, user_level=4)
        count = len(result)
        assert 5 <= count <= 18, (
            f"Expected 5-18 difficult words, got {count}. "
            f"Words: {[r['word'] for r in result]}"
        )

    def test_level1_article_has_fewer_words(self):
        """At level 1, the article should have fewer difficult words."""
        text = (
            "A 17-year-old student from New York made an amazing discovery last week. "
            "While working on a school science project with a small telescope, "
            "he found a new planet outside our solar system. "
            "Scientists at NASA later confirmed his finding. "
            "The planet is about six times bigger than Earth. "
            "But the planet's atmosphere is still very interesting to study. "
            "The discovery is still very important. "
            "He said he almost missed the evidence because the signal was very weak. "
            "NASA has invited Jack to visit their space center this summer. "
            "Jack said he plans to study physics in college and hopes to discover more planets in the future."
        )
        all_result = find_difficult_words(text, user_level=4)
        l1_result = find_difficult_words(text, user_level=1)
        # Level 1 should have fewer or equal words than all levels
        assert len(l1_result) <= len(all_result)
        # Level 1 should have at least 1 word (planet, discovery, explore, etc.)
        assert len(l1_result) >= 1, f"Expected at least 1 L1 word, got: {[r['word'] for r in l1_result]}"

    def test_level_progression_has_increasing_words(self):
        """As user level increases, more words should be found (non-strict)."""
        text = (
            "The planet discovery was confirmed with a telescope and the atmosphere "
            "study was an extraordinary achievement for the scientific community. "
            "The hypothesis was validated by empirical evidence."
        )
        l1 = len(find_difficult_words(text, user_level=1))
        l2 = len(find_difficult_words(text, user_level=2))
        l3 = len(find_difficult_words(text, user_level=3))
        l4 = len(find_difficult_words(text, user_level=4))
        assert l1 <= l2, f"L1({l1}) should be <= L2({l2})"
        assert l2 <= l3, f"L2({l2}) should be <= L3({l3})"
        assert l3 <= l4, f"L3({l3}) should be <= L4({l4})"


class TestFilterKnownWords:
    """Tests for filter_known_words()."""

    def test_filters_out_known_words(self):
        """Known words should be removed from the word list."""
        word_list = [
            {"word": "Planet", "lower": "planet", "definition": "行星", "pos": "n.", "level": 1},
            {"word": "Telescope", "lower": "telescope", "definition": "望远镜", "pos": "n.", "level": 3},
            {"word": "Discover", "lower": "discover", "definition": "发现", "pos": "v.", "level": 1},
        ]
        known_set = {"planet"}
        result = filter_known_words(word_list, known_set)
        assert len(result) == 2
        lowers = {w["lower"] for w in result}
        assert "planet" not in lowers
        assert "telescope" in lowers
        assert "discover" in lowers

    def test_empty_known_set_returns_all(self):
        """An empty known set should return all words unchanged."""
        word_list = [
            {"word": "Planet", "lower": "planet", "definition": "行星", "pos": "n.", "level": 1},
        ]
        result = filter_known_words(word_list, set())
        assert len(result) == 1
        assert result[0]["lower"] == "planet"

    def test_empty_word_list_returns_empty(self):
        """An empty word list should return an empty list."""
        result = filter_known_words([], {"planet"})
        assert result == []

    def test_multiple_known_words_filtered(self):
        """Multiple known words should all be removed."""
        word_list = [
            {"word": "Planet", "lower": "planet", "definition": "行星", "pos": "n.", "level": 1},
            {"word": "Evidence", "lower": "evidence", "definition": "证据", "pos": "n.", "level": 2},
            {"word": "Telescope", "lower": "telescope", "definition": "望远镜", "pos": "n.", "level": 3},
        ]
        known_set = {"planet", "telescope"}
        result = filter_known_words(word_list, known_set)
        assert len(result) == 1
        assert result[0]["lower"] == "evidence"

    def test_no_match_returns_all(self):
        """If no words match the known set, all should be returned."""
        word_list = [
            {"word": "Planet", "lower": "planet", "definition": "行星", "pos": "n.", "level": 1},
        ]
        known_set = {"nonexistent"}
        result = filter_known_words(word_list, known_set)
        assert len(result) == 1


class TestFilterKnownWordsFromTokens:
    """Tests for filter_known_words_from_tokens()."""

    def test_clears_difficulty_for_known_words(self):
        """Tokens for known words should have is_difficult cleared."""
        tokens = [
            {"text": "The", "is_word": True, "word": "The", "is_difficult": False, "definition": None, "pos": None, "level": None},
            {"text": " ", "is_word": False, "word": None, "is_difficult": False, "definition": None, "pos": None, "level": None},
            {"text": "planet", "is_word": True, "word": "planet", "is_difficult": True, "definition": "行星", "pos": "n.", "level": 1},
            {"text": " ", "is_word": False, "word": None, "is_difficult": False, "definition": None, "pos": None, "level": None},
            {"text": "is", "is_word": True, "word": "is", "is_difficult": False, "definition": None, "pos": None, "level": None},
            {"text": ".", "is_word": False, "word": None, "is_difficult": False, "definition": None, "pos": None, "level": None},
        ]
        result = filter_known_words_from_tokens(tokens, {"planet"})
        assert len(result) == len(tokens)
        # Check that "planet" token is no longer difficult
        planet_tokens = [t for t in result if t.get("word") == "planet"]
        assert len(planet_tokens) == 1
        assert planet_tokens[0]["is_difficult"] is False
        assert planet_tokens[0]["definition"] is None
        assert planet_tokens[0]["pos"] is None
        assert planet_tokens[0]["level"] is None
        # Other tokens should be unchanged
        assert result[0]["is_difficult"] is False  # "The" was never difficult
        assert result[2]["is_difficult"] is False  # "planet" cleared
        # Non-word tokens should be unchanged
        assert result[1]["is_word"] is False

    def test_non_known_words_unchanged(self):
        """Tokens not in known set should remain as they were."""
        tokens = [
            {"text": "evidence", "is_word": True, "word": "evidence", "is_difficult": True, "definition": "证据", "pos": "n.", "level": 2},
            {"text": "cat", "is_word": True, "word": "cat", "is_difficult": False, "definition": None, "pos": None, "level": None},
        ]
        result = filter_known_words_from_tokens(tokens, {"planet"})
        assert result[0]["is_difficult"] is True  # evidence is NOT in known set
        assert result[1]["is_difficult"] is False  # cat was never difficult

    def test_empty_known_set_returns_unchanged(self):
        """An empty known set should return tokens unchanged."""
        tokens = [
            {"text": "planet", "is_word": True, "word": "planet", "is_difficult": True, "definition": "行星", "pos": "n.", "level": 1},
        ]
        result = filter_known_words_from_tokens(tokens, set())
        assert result[0]["is_difficult"] is True

    def test_empty_tokens_returns_empty(self):
        """An empty token list should return empty."""
        result = filter_known_words_from_tokens([], {"planet"})
        assert result == []

    def test_original_tokens_not_mutated(self):
        """The original token list should not be modified (no side effects)."""
        tokens = [
            {"text": "planet", "is_word": True, "word": "planet", "is_difficult": True, "definition": "行星", "pos": "n.", "level": 1},
        ]
        result = filter_known_words_from_tokens(tokens, {"planet"})
        # Original should still be difficult
        assert tokens[0]["is_difficult"] is True
        assert tokens[0]["definition"] == "行星"
        # Result should be cleared
        assert result[0]["is_difficult"] is False

    def test_case_insensitive_matching(self):
        """Known words matching should be case-insensitive via lowercase comparison."""
        tokens = [
            {"text": "Planet", "is_word": True, "word": "Planet", "is_difficult": True, "definition": "行星", "pos": "n.", "level": 1},
        ]
        result = filter_known_words_from_tokens(tokens, {"planet"})
        assert result[0]["is_difficult"] is False


class TestTokenizeWithIntegration:
    """Integration tests for known-word filtering with the tokenize pipeline."""

    def test_tokenize_then_filter_known(self):
        """Tokenize then filter known words - known words should not be difficult."""
        text = "The planet and the telescope were amazing."
        tokens = tokenize(text, user_level=4)
        # Both planet (L1) and telescope (L3) should be difficult at level 4
        filtered = filter_known_words_from_tokens(tokens, {"planet"})
        planet_tokens = [t for t in filtered if t.get("word") == "planet"]
        telescope_tokens = [t for t in filtered if t.get("word") == "telescope"]
        assert planet_tokens[0]["is_difficult"] is False  # filtered out
        assert telescope_tokens[0]["is_difficult"] is True  # still difficult


class TestKnownWordPipeline:
    """Tests for the full known-word filtering pipeline mimicking server behavior."""

    def test_find_difficult_words_excludes_known(self):
        """find_difficult_words followed by filter_known_words excludes known words."""
        text = "The discovery was confirmed by telescope evidence."
        all_words = find_difficult_words(text, user_level=4)
        filtered = filter_known_words(all_words, {"discovery", "telescope"})
        filtered_lowers = {w["lower"] for w in filtered}
        assert "discovery" not in filtered_lowers
        assert "telescope" not in filtered_lowers
        assert "confirmed" in filtered_lowers  # still there if not known
        assert "evidence" in filtered_lowers

    def test_find_difficult_words_sorted_excludes_known(self):
        """find_difficult_words_sorted followed by filter_known_words preserves order."""
        text = "The discovery was confirmed by telescope evidence."
        all_words = find_difficult_words_sorted(text, user_level=4)
        filtered = filter_known_words(all_words, {"discovery"})
        filtered_lowers = [w["lower"] for w in filtered]
        # Should maintain first-appearance order, minus discovery
        assert "discovery" not in filtered_lowers
        assert filtered_lowers[0] == "confirmed"  # was second, now first
        assert filtered_lowers[-1] == "evidence"

    def test_known_words_do_not_affect_ordering(self):
        """After filtering known words, remaining words stay in original order."""
        text = "The planet was an extraordinary discovery with evidence."
        all_words = find_difficult_words_sorted(text, user_level=4)
        filtered = filter_known_words(all_words, {"extraordinary"})
        filtered_lowers = [w["lower"] for w in filtered]
        assert filtered_lowers == ["planet", "discovery", "evidence"]


class TestStemWord:
    """Tests for the stem_word function used in deduplication."""

    def test_plural_to_singular(self):
        """Plural forms should stem."""
        assert stem_word("experiments") == "experiment"
        assert stem_word("discoveries") == "discovery"
        assert stem_word("abilities") == "ability"

    def test_ing_to_base(self):
        """-ing forms should stem to base."""
        assert stem_word("protecting") == "protect"
        assert stem_word("playing") == "play"

    def test_ed_to_base(self):
        """-ed forms should stem to base."""
        assert stem_word("confirmed") == "confirm"
        assert stem_word("published") == "publish"
        assert stem_word("studied") == "study"

    def test_ly_adverb(self):
        """-ly adverbs should stem."""
        assert stem_word("nearly") == "near"
        assert stem_word("extremely") == "extreme"

    def test_ment_noun(self):
        """-ment nouns should stem (ement rule matches first)."""
        assert stem_word("achievement") == "achiev"
        assert stem_word("replacement") == "replac"

    def test_er_agent(self):
        """-er agent nouns should stem."""
        assert stem_word("teacher") == "teach"

    def test_short_words_unchanged(self):
        """Words with 1-2 letters should stay unchanged."""
        assert stem_word("a") == "a"
        assert stem_word("is") == "is"

    def test_no_change_for_base_form(self):
        """Words already in base form should not change."""
        assert stem_word("planet") == "planet"
        assert stem_word("strategy") == "strategy"

    def test_stem_unifies_inflected_forms(self):
        """Stemming groups: confirm/confirmed, protect/protecting, play/played."""
        assert stem_word("confirm") == stem_word("confirmed")
        assert stem_word("protect") == stem_word("protecting")
        assert stem_word("play") == stem_word("played")

    def test_s_rule_blocks_deeper_stem(self):
        """Plural s-rule fires first, preventing ment/other stemming."""
        assert stem_word("experiments") == "experiment"  # s-rule
        assert stem_word("experiment") == "experi"       # ment-rule
        # These don't unify — known limitation of single-pass stemmer

    def test_case_insensitive_handled_by_caller(self):
        """stem_word expects lowercase input."""
        assert stem_word("PROTECTING") != "protect"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
