"""Text statistics utility."""

import sys
import re
from collections import Counter


_STOP_WORDS = {
    "a", "an", "the", "and", "or", "but", "is", "in", "on",
    "at", "to", "of", "for", "by", "as", "it", "be", "with",
    "that", "this", "was", "are", "were", "has", "have", "had",
}


def _tokenize(text):
    # Lowercase alphabetic runs; internal apostrophes preserved (e.g. "it's").
    return re.findall(r"[a-zA-Z]+(?:'[a-zA-Z]+)*", text.lower())


def word_count(text):
    """Return the number of words in text."""
    return len(_tokenize(text))


def char_count(text):
    """Return the number of non-whitespace characters in text."""
    return sum(1 for ch in text if not ch.isspace())


def word_frequency(text):
    """Return a Counter mapping each word to its frequency."""
    return Counter(_tokenize(text))


def top_words(text, n=5):
    """Return the n most common non-stop words and their counts."""
    freq = word_frequency(text)
    filtered = Counter({w: c for w, c in freq.items() if w not in _STOP_WORDS})
    return filtered.most_common(n)


def sentence_count(text):
    """Return the number of sentences in text.

    A sentence boundary is one or more consecutive '.', '!', or '?' characters,
    so 'Really?!' and '...' each count as one boundary.
    Returns 0 for empty or unpunctuated text.
    """
    if not text:
        return 0
    return len(re.findall(r'[.!?]+', text))


def average_word_length(text):
    """Return the average length of words in text.

    Uses the same tokenisation as word_frequency so punctuation is excluded.
    Returns 0.0 if there are no words.
    """
    words = _tokenize(text)
    if not words:
        return 0.0
    return sum(len(w) for w in words) / len(words)


def report(text, n=5):
    """Print a summary report for the given text."""
    print(f"Word count      : {word_count(text)}")
    print(f"Char count      : {char_count(text)}")
    print(f"Sentence count  : {sentence_count(text)}")
    print(f"Avg word length : {average_word_length(text):.2f}")
    print(f"Top {n} words     : {top_words(text, n)}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python stats.py '<text>'")
        sys.exit(1)
    report(" ".join(sys.argv[1:]))
