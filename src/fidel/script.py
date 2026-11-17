"""Decompose and compose Ge'ez characters."""
from __future__ import annotations

import re

from ._tables import COMPOSE, LETTER_RANGES, SYLLABLES, Syllable

_ETHIOPIC = re.compile(f"[{LETTER_RANGES}፠-፼]")


def is_ethiopic(ch: str) -> bool:
    """True for any Ethiopic letter, punctuation mark or numeral."""
    return len(ch) == 1 and bool(_ETHIOPIC.match(ch))


def syllable(ch: str) -> Syllable | None:
    """Decompose one character, or ``None`` if it is not a supported syllable.

    >>> s = syllable("ሏ")
    >>> s.base, s.vowel
    ('ለ', 'wa')
    """
    return SYLLABLES.get(ch)


def split(text: str) -> list[Syllable]:
    """Decompose every supported syllable in ``text``, skipping everything else."""
    return [s for ch in text if (s := SYLLABLES.get(ch))]


def compose(base: str, order: int, kind: str = "plain") -> str:
    """Build a character from its row base and vowel order (1..7).

    >>> compose("ለ", 4)
    'ላ'
    >>> compose("ቀ", 4, kind="labio")
    'ቋ'
    """
    s = SYLLABLES.get(base)
    if s is None:
        raise ValueError(f"{base!r} is not a supported Ge'ez character")
    if kind == "wa":
        order = 4
    elif kind == "oa":
        order = 7
    try:
        return COMPOSE[(s.row, order, kind)]
    except KeyError:
        raise ValueError(f"no {kind} form of order {order} in the {s.base} row") from None


def row(base: str) -> list[str]:
    """All characters in a consonant row, plain orders first.

    >>> "".join(row("ለ"))
    'ለሉሊላሌልሎሏ'
    """
    s = SYLLABLES.get(base)
    if s is None:
        raise ValueError(f"{base!r} is not a supported Ge'ez character")
    kinds = {"plain": 0, "wa": 1, "oa": 1, "labio": 2}
    members = [x for x in SYLLABLES.values() if x.row == s.row]
    return [x.char for x in sorted(members, key=lambda x: (kinds[x.kind], x.order))]
