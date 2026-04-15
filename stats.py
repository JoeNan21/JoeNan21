"""Text statistics utility."""

import sys
import re
from collections import Counter


def word_count(text):
    """Return the number of words in text."""
    return len(text.split())


def char_count(text):
    """Return the number of non-whitespace characters in text."""
    return len(text.replace(" ", "").replace("\n", "").replace("\t", ""))


def word_frequency(text):
    """Return a Counter mapping each word to its frequency.

    TODO: Normalize words to lowercase and strip punctuation before counting.
    """
    words = text.split()
    return Counter(words)


def top_words(text, n=5):
    """Return the n most common words and their counts.

    TODO: Filter out common stop words (e.g. 'the', 'a', 'is', 'in', 'of')
          before returning results so the output is more meaningful.
    """
    freq = word_frequency(text)
    return freq.most_common(n)


def sentence_count(text):
    """Return the number of sentences in text.

    TODO: Implement this function. A sentence ends with '.', '!', or '?'.
          Return 0 for empty text.
    """
    pass


def average_word_length(text):
    """Return the average length of words in text.

    TODO: Implement this function. Return 0.0 if there are no words.
    """
    pass


def report(text):
    """Print a summary report for the given text."""
    print(f"Word count      : {word_count(text)}")
    print(f"Char count      : {char_count(text)}")
    print(f"Sentence count  : {sentence_count(text)}")
    print(f"Avg word length : {average_word_length(text):.2f}" if average_word_length(text) is not None else "Avg word length : N/A")
    print(f"Top 5 words     : {top_words(text)}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python stats.py '<text>'")
        sys.exit(1)
    report(" ".join(sys.argv[1:]))
