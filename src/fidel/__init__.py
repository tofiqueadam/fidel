"""fidel — a small, dependency-free toolkit for Amharic and Ge'ez-script text."""
from .normalize import LEVELS, normalize
from .numerals import from_ethiopic, replace_numerals, to_ethiopic
from .script import compose, is_ethiopic, row, split, syllable
from .tokenize import sentences, words
from .translit import romanize, to_fidel

__all__ = [
    "LEVELS", "compose", "from_ethiopic", "is_ethiopic", "normalize", "replace_numerals",
    "romanize", "row", "sentences", "split", "syllable", "to_ethiopic", "to_fidel", "words",
]
__version__ = "0.2.0"
