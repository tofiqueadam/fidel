"""Sentence and word segmentation for Ge'ez-script text."""
from __future__ import annotations

import re

from ._tables import LETTER_RANGES

_SENT_END = "።፧?!፨"
_SENTENCE = re.compile(rf"[^{_SENT_END}]+[{_SENT_END}]*|[{_SENT_END}]+")
_TOKEN = re.compile(
    rf"[{LETTER_RANGES}]+"        # Ge'ez words
    r"|[፩-፼]+"          # Ethiopic numerals
    r"|[0-9]+(?:[.,][0-9]+)*"     # Arabic numbers
    r"|[^\W\d_]+"                 # other-script words
    r"|[^\s፡]"               # any single punctuation mark, except the ፡ word separator
)


def sentences(text: str) -> list[str]:
    """Split text into sentences, keeping the final punctuation.

    >>> sentences("ሰላም ነህ? ደህና ነኝ።")
    ['ሰላም ነህ?', 'ደህና ነኝ።']
    """
    return [s.strip() for s in _SENTENCE.findall(text) if s.strip()]


def words(text: str, *, punct: bool = True) -> list[str]:
    """Split text into tokens. ``፡`` and whitespace separate words.

    >>> words("ሰላም፡ዓለም።")
    ['ሰላም', 'ዓለም', '።']
    """
    toks = _TOKEN.findall(text)
    if punct:
        return toks
    return [t for t in toks if t[0].isalnum()]
