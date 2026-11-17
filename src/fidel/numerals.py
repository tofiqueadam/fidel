"""Ethiopic numerals ⇄ integers.

Ethiopic numerals are additive within a pair of decimal digits and use two
multipliers: ፻ (100) and ፼ (10 000). A number is read as base-100 groups,
most significant first, where odd groups are followed by ፻ and even groups
by ፼. ``፩`` is dropped before ፻, and before ፼ when it leads the number.
"""
from __future__ import annotations

import re

ONES = "፩፪፫፬፭፮፯፰፱"
TENS = "፲፳፴፵፶፷፸፹፺"
HUNDRED, MYRIAD = "፻", "፼"
_VALUE = {c: i + 1 for i, c in enumerate(ONES)} | {c: 10 * (i + 1) for i, c in enumerate(TENS)}
NUMERAL_RUN = re.compile("[፩-፼]+")


def _pair(n: int) -> str:
    return (TENS[n // 10 - 1] if n >= 10 else "") + (ONES[n % 10 - 1] if n % 10 else "")


def to_ethiopic(n: int) -> str:
    """Write a positive integer in Ethiopic numerals.

    >>> to_ethiopic(2016)
    '፳፻፲፮'
    >>> to_ethiopic(123456)
    '፲፪፼፴፬፻፶፮'
    """
    if isinstance(n, bool) or not isinstance(n, int):
        raise TypeError("expected an int")
    if n < 1:
        raise ValueError("Ethiopic numerals have no zero or negatives")
    groups = []
    while n:
        n, r = divmod(n, 100)
        groups.append(r)
    out = []
    top = len(groups) - 1
    for i in range(top, -1, -1):
        g = groups[i]
        if i == 0:
            out.append(_pair(g))
        elif i % 2:  # followed by ፻
            if g:
                out.append(("" if g == 1 else _pair(g)) + HUNDRED)
        else:  # followed by ፼, always written once something precedes it
            out.append(("" if g == 1 and i == top else _pair(g)) + MYRIAD)
    return "".join(out)


def _hundreds(s: str, leading: bool) -> int:
    if HUNDRED in s:
        left, right = s.split(HUNDRED, 1)
        if HUNDRED in right:
            raise ValueError(f"misplaced ፻ in {s!r}")
        return (_digits(left) if left else 1) * 100 + _digits(right)
    if not s:
        return 1 if leading else 0
    return _digits(s)


def _digits(s: str) -> int:
    total = 0
    for c in s:
        if c not in _VALUE:
            raise ValueError(f"{c!r} is not an Ethiopic digit")
        total += _VALUE[c]
    if total > 99:
        raise ValueError(f"{s!r} is not a valid digit pair")
    return total


def from_ethiopic(s: str) -> int:
    """Read Ethiopic numerals back into an integer.

    >>> from_ethiopic("፻፼")
    1000000
    """
    s = s.strip()
    if not s or not NUMERAL_RUN.fullmatch(s):
        raise ValueError(f"{s!r} is not an Ethiopic numeral")
    parts = s.split(MYRIAD)
    total = 0
    for i, part in enumerate(parts):
        total = total * 10_000 + _hundreds(part, leading=(i == 0 and len(parts) > 1))
    return total


def replace_numerals(text: str) -> str:
    """Rewrite every Ethiopic numeral in ``text`` with Arabic digits."""
    return NUMERAL_RUN.sub(lambda m: str(from_ethiopic(m.group())), text)
