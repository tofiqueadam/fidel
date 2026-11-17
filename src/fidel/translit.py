"""SERA-style transliteration between Ge'ez script and Latin.

The scheme follows the conventions of SERA (System for Ethiopic
Representation in ASCII): seven vowels ``e u i a E I o``, capitals for
ejectives and extra consonants (``T C P S``), a backtick for the
historical homophones (`` `s `h `S ` ``), and ``'`` for the glottal row.
It is lossless: ``to_fidel(romanize(x)) == x`` for supported text.
"""
from __future__ import annotations

from ._tables import SYLLABLES, VOWELS

PUNCT = {"፡": ":", "።": "::", "፣": ",", "፤": ";", "፥": "-:", "፦": ":-", "፧": "?", "፨": "|"}
ASCII_PUNCT = {"፡": " ", "።": ".", "፣": ",", "፤": ";", "፥": ":", "፦": ":", "፧": "?", "፨": "¶"}


def _latin(s, explicit_sixth: bool) -> str:
    if s.kind == "wa":
        return s.consonant + "Wa"
    if s.kind == "oa":
        return s.consonant + "oa"
    v = VOWELS[s.order - 1]
    if s.kind == "labio":
        return s.consonant + "W" + v
    if s.order == 6 and not explicit_sixth:
        return s.consonant
    return s.consonant + v


def romanize(text: str, *, ascii_punct: bool = False, explicit_sixth: bool = False) -> str:
    """Transliterate Ge'ez script to Latin.

    >>> romanize("ሰላም")
    'selam'
    >>> romanize("ኢትዮጵያ")
    "'ityoPya"
    """
    punct = ASCII_PUNCT if ascii_punct else PUNCT
    out = []
    for ch in text:
        s = SYLLABLES.get(ch)
        if s is None:
            out.append(punct.get(ch, ch))
            continue
        # a bare pharyngeal ` would fuse with a following s/h/S, so keep its vowel
        out.append(_latin(s, explicit_sixth or (s.order == 6 and s.consonant == "`")))
    return "".join(out)


def _reverse() -> dict[str, str]:
    rev = {}
    for ch, s in SYLLABLES.items():
        rev[_latin(s, explicit_sixth=True)] = ch
        if s.kind == "plain" and s.order == 6:
            rev.setdefault(s.consonant, ch)
    for ch, lat in PUNCT.items():
        rev[lat] = ch
    return rev


_REV = _reverse()
_MAXLEN = max(map(len, _REV))
_VOWEL_START = set("euiaEIo")


def to_fidel(latin: str) -> str:
    """Transliterate SERA-style Latin back to Ge'ez script.

    A vowel with no consonant in front of it is written on the glottal row,
    so ``ebebe`` and ``'ebebe`` both give ``አበበ`` (in SERA the
    vowel of አ is ``e``; ``a`` is the 4th order, ኣ).

    >>> to_fidel("selam")
    'ሰላም'
    """
    out, i, n = [], 0, len(latin)
    while i < n:
        if latin[i] in _VOWEL_START:
            # a bare vowel: try it on the glottal row
            for size in range(min(_MAXLEN - 1, n - i), 0, -1):
                if (ch := _REV.get("'" + latin[i:i + size])):
                    out.append(ch)
                    i += size
                    break
            else:  # pragma: no cover - every vowel exists on the glottal row
                out.append(latin[i])
                i += 1
            continue
        for size in range(min(_MAXLEN, n - i), 0, -1):
            if (ch := _REV.get(latin[i:i + size])):
                out.append(ch)
                i += size
                break
        else:
            out.append(latin[i])
            i += 1
    return "".join(out)
