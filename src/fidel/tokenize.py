"""Sentence and word segmentation for Ge'ez-script text."""
from __future__ import annotations

import re

from ._tables import LETTER_RANGES

# A sentence ends at ። ፧ ? ! ፨, or at ፡፡ (two word separators), which many
# writers type in place of ።.
_SENT_END = re.compile(r"(?:[።፧?!፨]|፡{2,})+")
_L = f"[{LETTER_RANGES}]"
_TOKEN = re.compile(
    rf"{_L}{{1,2}}(?:\.{_L}{{1,2}})+\.?"  # dotted abbreviations: ዓ.ም. ዓ.ዓ. አ.አ.ዩ
    rf"|{_L}{{1,2}}/{_L}+"        # slashed abbreviations: ት/ቤት ዶ/ር ወ/ሮ
    rf"|{_L}+"                    # Ge'ez words
    r"|[፩-፼]+"          # Ethiopic numerals
    r"|[0-9]+(?:[.,][0-9]+)*"     # Arabic numbers
    r"|[^\W\d_]+"                 # other-script words
    r"|[^\s፡]"               # any single punctuation mark, except the ፡ word separator
)


def sentences(text: str) -> list[str]:
    """Split text into sentences, keeping the final punctuation.

    >>> sentences("ሰላም ነህ? ደህና ነኝ።")
    ['ሰላም ነህ?', 'ደህና ነኝ።']
    >>> sentences("ደህና ነኝ፡፡ አመሰግናለሁ")
    ['ደህና ነኝ፡፡', 'አመሰግናለሁ']
    """
    out, start = [], 0
    for m in _SENT_END.finditer(text):
        s = text[start:m.end()].strip()
        if s:
            out.append(s)
        start = m.end()
    tail = text[start:].strip()
    if tail:
        out.append(tail)
    return out


def words(text: str, *, punct: bool = True) -> list[str]:
    """Split text into tokens. ``፡`` and whitespace separate words.

    Common abbreviations stay whole: dotted ones such as ``ዓ.ም.`` and slashed
    ones such as ``ት/ቤት`` (school) or ``ዶ/ር`` (Dr.).

    >>> words("ሰላም፡ዓለም።")
    ['ሰላም', 'ዓለም', '።']
    """
    toks = _TOKEN.findall(text)
    if punct:
        return toks
    return [t for t in toks if t[0].isalnum()]
