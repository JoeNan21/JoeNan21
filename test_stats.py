"""Tests for stats.py"""

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


def test_char_count():
    assert char_count("hello world") == 10
    assert char_count("") == 0


def test_word_frequency_normalized():
    freq = word_frequency("The the THE cat")
    # After normalization all three 'the' variants should collapse
    assert freq["the"] == 3
    assert freq["cat"] == 1


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


def test_average_word_length():
    assert average_word_length("hi bye") == 3.0
    assert average_word_length("") == 0.0
