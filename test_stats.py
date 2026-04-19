"""Tests for stats.py"""

from collections import Counter
from stats import (
    word_count,
    char_count,
    word_frequency,
    top_words,
    sentence_count,
    average_word_length,
)


def test_word_count():
    assert word_count("hello world") == 2
    assert word_count("") == 0


def test_word_count_ignores_punctuation():
    assert word_count("Hello, world.") == 2
    assert word_count("it's great!") == 2


def test_char_count():
    assert char_count("hello world") == 10
    assert char_count("") == 0


def test_char_count_handles_all_whitespace():
    # carriage return and newline should both be excluded
    assert char_count("ab\r\ncd") == 4
    assert char_count("a\tb") == 2


def test_word_frequency_normalized():
    freq = word_frequency("The the THE cat")
    assert freq["the"] == 3
    assert freq["cat"] == 1


def test_word_frequency_empty():
    assert word_frequency("") == Counter()


def test_word_frequency_contraction():
    freq = word_frequency("it's great")
    assert freq["it's"] == 1
    assert freq["great"] == 1


def test_word_frequency_no_bare_apostrophes():
    freq = word_frequency("it's a ''quoted'' word")
    assert "'" not in freq
    assert "''" not in freq


def test_top_words_filters_stopwords():
    text = "the cat sat on the mat the mat is flat"
    results = top_words(text, n=3)
    words = [w for w, _ in results]
    assert "the" not in words
    assert "is" not in words
    assert "on" not in words


def test_sentence_count():
    assert sentence_count("Hello world. How are you? I am fine!") == 3
    assert sentence_count("No punctuation here") == 0
    assert sentence_count("") == 0


def test_sentence_count_adjacent_punctuation():
    # '?!' is one boundary, not two
    assert sentence_count("Really?!") == 1
    # ellipsis + question mark = two boundaries
    assert sentence_count("Wait... ok?") == 2


def test_average_word_length():
    assert average_word_length("hi bye") == 2.5
    assert average_word_length("") == 0.0


def test_average_word_length_ignores_punctuation():
    # "Hi" = 2, "bye" = 3 — trailing punctuation excluded
    assert average_word_length("Hi, bye.") == 2.5
