"""Text statistics utility."""

import sys
import re
from collections import Counter


# Common English stop words to exclude from top-words results.
_STOP_WORDS = {
    "a", "an", "the", "and", "or", "but", "is", "in", "on",
    "at", "to", "of", "for", "by", "as", "it", "be", "with",
    "that", "this", "was", "are", "were", "has", "have", "had",
}


def word_count(text):
    """Return the number of words in text."""
    return len(text.split())


def char_count(text):
    """Return the number of non-whitespace characters in text."""
    return len(text.replace(" ", "").replace("\n", "").replace("\t", ""))


def word_frequency(text):
    """Return a Counter mapping each word to its frequency.

    Words are normalized to lowercase and stripped of punctuation so that
    'The', 'the', and 'THE' all count as the same word.
    """
    words = re.findall(r"[a-zA-Z']+", text.lower())
    return Counter(words)


def top_words(text, n=5):
    """Return the n most common words and their counts.

    Stop words (e.g. 'the', 'a', 'is') are filtered out so the results
    highlight meaningful vocabulary.
    """
    freq = word_frequency(text)
    filtered = Counter({w: c for w, c in freq.items() if w not in _STOP_WORDS})
    return filtered.most_common(n)


def sentence_count(text):
    """Return the number of sentences in text.

    A sentence is delimited by '.', '!', or '?'.
    Returns 0 for empty or unpunctuated text.
    """
    if not text:
        return 0
    return len(re.findall(r'[.!?]', text))


def average_word_length(text):
    """Return the average length of words in text.

    Returns 0.0 if there are no words.
    """
    words = text.split()
    if not words:
        return 0.0
    return sum(len(w) for w in words) / len(words)


def report(text):
    """Print a summary report for the given text."""
    avg = average_word_length(text)
    print(f"Word count      : {word_count(text)}")
    print(f"Char count      : {char_count(text)}")
    print(f"Sentence count  : {sentence_count(text)}")
    print(f"Avg word length : {avg:.2f}")
    print(f"Top 5 words     : {top_words(text)}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python stats.py '<text>'")
        sys.exit(1)
    report(" ".join(sys.argv[1:]))
