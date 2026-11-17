"""Command-line interface: ``fidel <command> [text]`` (reads stdin when text is omitted)."""
from __future__ import annotations

import argparse
import sys

from . import LEVELS, __version__, from_ethiopic, normalize, romanize, row, sentences, split, to_ethiopic, to_fidel, words


def _text(args) -> str:
    return " ".join(args.text) if args.text else sys.stdin.read()


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="fidel", description="Tools for Amharic and Ge'ez-script text.")
    p.add_argument("--version", action="version", version=f"fidel {__version__}")
    sub = p.add_subparsers(dest="cmd", required=True)

    n = sub.add_parser("normalize", help="fold homophones, fix punctuation and spacing")
    n.add_argument("--level", choices=LEVELS, default="standard")
    r = sub.add_parser("romanize", help="Ge'ez → SERA-style Latin")
    r.add_argument("--ascii-punct", action="store_true")
    sub.add_parser("fidelize", help="SERA-style Latin → Ge'ez")
    sub.add_parser("sentences", help="one sentence per line")
    sub.add_parser("words", help="one token per line")
    sub.add_parser("split", help="consonant + vowel for each character")
    sub.add_parser("num", help="convert between Ethiopic and Arabic numerals")
    sub.add_parser("row", help="print the full row for a character")
    for sp in sub.choices.values():
        sp.add_argument("text", nargs="*")

    a = p.parse_args(argv)
    t = _text(a).strip("\n")
    if a.cmd == "normalize":
        print(normalize(t, a.level))
    elif a.cmd == "romanize":
        print(romanize(t, ascii_punct=a.ascii_punct))
    elif a.cmd == "fidelize":
        print(to_fidel(t))
    elif a.cmd == "sentences":
        print("\n".join(sentences(t)))
    elif a.cmd == "words":
        print("\n".join(words(t)))
    elif a.cmd == "split":
        for s in split(t):
            print(f"{s.char}  {s.base} + {s.vowel:<3}  order {s.order}  {s.kind}")
    elif a.cmd == "num":
        for tok in t.split():
            print(to_ethiopic(int(tok)) if tok.isdigit() and tok.isascii() else from_ethiopic(tok))
    elif a.cmd == "row":
        print(" ".join(row(t.strip()[0])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
