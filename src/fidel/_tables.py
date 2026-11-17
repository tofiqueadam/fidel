"""The Ethiopic syllabary as data.

Every Ge'ez character is a consonant row combined with a vowel order. Unicode
lays rows out on an 8-code-point grid, so the table below only names the row
bases; everything else is derived and cross-checked against Python's Unicode
database at import time, so a wrong code point fails loudly instead of
silently mis-transliterating.
"""
from __future__ import annotations

import unicodedata
from dataclasses import dataclass

# SERA-style Latin for the 7 vowel orders, and a readable IPA-ish rendering.
VOWELS = ("e", "u", "i", "a", "E", "I", "o")
IPA = ("ä", "u", "i", "a", "e", "ə", "o")

# row base -> (SERA-style consonant, Unicode name of the base character)
ROWS: dict[int, tuple[str, str]] = {
    0x1200: ("h", "HA"),      0x1208: ("l", "LA"),      0x1210: ("H", "HHA"),
    0x1218: ("m", "MA"),      0x1220: ("`s", "SZA"),    0x1228: ("r", "RA"),
    0x1230: ("s", "SA"),      0x1238: ("x", "SHA"),     0x1240: ("q", "QA"),
    0x1260: ("b", "BA"),      0x1268: ("v", "VA"),      0x1270: ("t", "TA"),
    0x1278: ("c", "CA"),      0x1280: ("`h", "XA"),     0x1290: ("n", "NA"),
    0x1298: ("N", "NYA"),     0x12A0: ("'", "GLOTTAL A"), 0x12A8: ("k", "KA"),
    0x12B8: ("K", "KXA"),     0x12C8: ("w", "WA"),      0x12D0: ("`", "PHARYNGEAL A"),
    0x12D8: ("z", "ZA"),      0x12E0: ("Z", "ZHA"),     0x12E8: ("y", "YA"),
    0x12F0: ("d", "DA"),      0x1300: ("j", "JA"),      0x1308: ("g", "GA"),
    0x1320: ("T", "THA"),     0x1328: ("C", "CHA"),     0x1330: ("P", "PHA"),
    0x1338: ("S", "TSA"),     0x1340: ("`S", "TZA"),    0x1348: ("f", "FA"),
    0x1350: ("p", "PA"),
}

# labiovelar row base -> plain row base it belongs to
LABIO_ROWS: dict[int, int] = {
    0x1248: 0x1240,  # ቈ  q
    0x1288: 0x1280,  # ኈ  `h
    0x12B0: 0x12A8,  # ኰ  k
    0x12C0: 0x12B8,  # ዀ  K
    0x1310: 0x1308,  # ጐ  g
}


@dataclass(frozen=True)
class Syllable:
    """One Ge'ez character, decomposed."""

    char: str
    row: int          # code point of the plain row base (e.g. ለ for ሏ)
    consonant: str    # SERA-style consonant
    order: int        # 1..7 vowel order
    kind: str         # "plain" | "wa" | "oa" | "labio"

    @property
    def vowel(self) -> str:
        if self.kind == "wa":
            return "wa"
        if self.kind == "oa":
            return "oa"
        v = IPA[self.order - 1]
        return "w" + v if self.kind == "labio" else v

    @property
    def base(self) -> str:
        return chr(self.row)


def _name(cp: int) -> str:
    return unicodedata.name(chr(cp), "")


def _build() -> dict[str, Syllable]:
    table: dict[str, Syllable] = {}
    for base, (lat, nm) in ROWS.items():
        expected = f"ETHIOPIC SYLLABLE {nm}"
        if _name(base) != expected:  # pragma: no cover - guards the data above
            raise RuntimeError(f"U+{base:04X} is {_name(base)!r}, expected {expected!r}")
        for k in range(7):
            if _name(base + k):
                table[chr(base + k)] = Syllable(chr(base + k), base, lat, k + 1, "plain")
        eighth = _name(base + 7)
        if eighth.endswith("WA"):
            table[chr(base + 7)] = Syllable(chr(base + 7), base, lat, 4, "wa")
        elif eighth.endswith("OA"):
            table[chr(base + 7)] = Syllable(chr(base + 7), base, lat, 7, "oa")
    for lbase, plain in LABIO_ROWS.items():
        for k in (0, 2, 3, 4, 5):
            if not _name(lbase + k):  # pragma: no cover
                raise RuntimeError(f"missing labiovelar U+{lbase + k:04X}")
            table[chr(lbase + k)] = Syllable(chr(lbase + k), plain, ROWS[plain][0], k + 1, "labio")
    return table


SYLLABLES: dict[str, Syllable] = _build()

# (row, order, kind) -> character, for composing
COMPOSE: dict[tuple[int, int, str], str] = {(s.row, s.order, s.kind): c for c, s in SYLLABLES.items()}

# Ethiopic letters across all four Unicode blocks (punctuation and numerals excluded).
LETTER_RANGES = "ሀ-ፚᎀ-᎙ⶀ-ⷞꬁ-ꬮ"
