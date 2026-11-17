"""Amharic text normalization.

Amharic writes several sounds with more than one row of the syllabary
(ሀ/ሐ/ኀ, ሰ/ሠ, አ/ዐ, ጸ/ፀ). For search, deduplication and model training
it is usually better to fold them together. Three levels are offered:

``light``      Unicode NFC, ``፡፡`` → ``።``, whitespace cleanup.
``standard``   + homophone rows folded, spelled-out labials joined (ሉዋ → ሏ).
``aggressive`` + ኸ folded, 1st/4th order of ሀ and አ merged (ሃ → ሀ, ኣ → አ),
               and the ``፡`` word separator turned into a space.
"""
from __future__ import annotations

import re
import unicodedata

from ._tables import COMPOSE, SYLLABLES

LEVELS = ("light", "standard", "aggressive")

_HOMOPHONES = {0x1210: 0x1200, 0x1280: 0x1200, 0x1220: 0x1230, 0x12D0: 0x12A0, 0x1340: 0x1338}
_AGGRESSIVE_ROWS = {0x12B8: 0x1200}
_ORDER_MERGE = {0x1200, 0x12A0}  # rows whose 1st and 4th orders sound the same


def _fold_map(rows: dict[int, int], merge_orders: bool) -> dict[int, str]:
    table = {}
    for ch, s in SYLLABLES.items():
        target_row = rows.get(s.row, s.row)
        order = s.order
        if merge_orders and target_row in _ORDER_MERGE and s.kind == "plain" and order == 4:
            order = 1
        if (target_row, order) == (s.row, s.order):
            continue
        if (target := COMPOSE.get((target_row, order, s.kind))):
            table[ord(ch)] = target
    return table


_STANDARD = _fold_map(_HOMOPHONES, merge_orders=False)
_AGGRESSIVE = _fold_map(_HOMOPHONES | _AGGRESSIVE_ROWS, merge_orders=True)
_LABIAL = re.compile("([" + "".join(c for c, s in SYLLABLES.items() if s.kind == "plain" and s.order == 2) + "])ዋ")
_SPACES = re.compile(r"[ \t ​]+")


def _join_labial(m: re.Match) -> str:
    s = SYLLABLES[m.group(1)]
    return (COMPOSE.get((s.row, 4, "labio")) or COMPOSE.get((s.row, 4, "wa")) or m.group(0))


def normalize(text: str, level: str = "standard") -> str:
    """Normalize Amharic text.

    >>> normalize("ሐይለ ሥላሴ")
    'ሀይለ ስላሴ'
    >>> normalize("ቱዋ")
    'ቷ'
    """
    if level not in LEVELS:
        raise ValueError(f"level must be one of {LEVELS}")
    text = unicodedata.normalize("NFC", text)
    text = text.replace("፡፡", "።")
    if level != "light":
        text = text.translate(_AGGRESSIVE if level == "aggressive" else _STANDARD)
        text = _LABIAL.sub(_join_labial, text)
    if level == "aggressive":
        text = text.replace("፡", " ")
    text = _SPACES.sub(" ", text)
    return "\n".join(line.strip() for line in text.split("\n"))
