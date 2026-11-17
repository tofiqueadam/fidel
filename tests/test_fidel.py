import random
import unicodedata

import pytest

import fidel
from fidel._tables import SYLLABLES


# ------------------------------------------------------------------ numerals
KNOWN = {
    1: "፩", 9: "፱", 10: "፲", 11: "፲፩", 99: "፺፱", 100: "፻", 101: "፻፩", 123: "፻፳፫",
    200: "፪፻", 1000: "፲፻", 2016: "፳፻፲፮", 10_000: "፼", 10_100: "፼፻", 20_000: "፪፼",
    123_456: "፲፪፼፴፬፻፶፮", 1_000_000: "፻፼", 1_010_000: "፻፩፼", 100_000_000: "፼፼",
}


@pytest.mark.parametrize("n,s", KNOWN.items())
def test_known_numerals(n, s):
    assert fidel.to_ethiopic(n) == s
    assert fidel.from_ethiopic(s) == n


def test_numeral_roundtrip_dense():
    for n in range(1, 120_000):
        assert fidel.from_ethiopic(fidel.to_ethiopic(n)) == n


def test_numeral_roundtrip_large():
    rng = random.Random(7)
    for _ in range(5000):
        n = rng.randint(1, 10**24)
        assert fidel.from_ethiopic(fidel.to_ethiopic(n)) == n


@pytest.mark.parametrize("bad", [0, -5])
def test_numeral_rejects_non_positive(bad):
    with pytest.raises(ValueError):
        fidel.to_ethiopic(bad)


@pytest.mark.parametrize("bad", ["", "abc", "፲፲፲፲፲፲፲፲፲፲፲", "፻፻"])
def test_numeral_rejects_garbage(bad):
    with pytest.raises(ValueError):
        fidel.from_ethiopic(bad)


def test_replace_numerals():
    assert fidel.replace_numerals("በ፳፻፲፮ ዓ.ም.") == "በ2016 ዓ.ም."


# ------------------------------------------------------------------- script
def test_table_matches_unicode_names():
    for ch, s in SYLLABLES.items():
        name = unicodedata.name(ch)
        assert name.startswith("ETHIOPIC SYLLABLE"), name
        assert fidel.compose(s.base, s.order, s.kind) == ch


def test_syllable_parts():
    s = fidel.syllable("ቋ")
    assert (s.base, s.kind, s.vowel) == ("ቀ", "labio", "wa")
    s = fidel.syllable("ም")
    assert (s.base, s.order, s.vowel) == ("መ", 6, "ə")
    assert fidel.syllable("a") is None


def test_row_and_split():
    assert "".join(fidel.row("ለ")) == "ለሉሊላሌልሎሏ"
    assert "".join(fidel.row("ቀ")) == "ቀቁቂቃቄቅቆቇቈቊቋቌቍ"
    assert [s.char for s in fidel.split("ሰላም!")] == ["ሰ", "ላ", "ም"]


def test_is_ethiopic():
    assert fidel.is_ethiopic("ሀ") and fidel.is_ethiopic("።") and fidel.is_ethiopic("፲")
    assert not fidel.is_ethiopic("a") and not fidel.is_ethiopic("ሀሀ")


# ------------------------------------------------------------ transliteration
@pytest.mark.parametrize("fid,lat", [
    ("ሰላም", "selam"), ("ኢትዮጵያ", "'ityoPya"), ("አበበ", "'ebebe"), ("ቋንቋ", "qWanqWa"),
    ("ሏ", "lWa"), ("ጸሐይ", "SeHey"), ("ዕሥራ", "`I`sra"),
])
def test_romanize(fid, lat):
    assert fidel.romanize(fid) == lat
    assert fidel.to_fidel(lat) == fid


def test_bare_vowels_use_glottal_row():
    assert fidel.to_fidel("ebebe") == fidel.to_fidel("'ebebe") == "አበበ"
    assert fidel.to_fidel("abebe") == "ኣበበ"


def test_romanize_roundtrip_random():
    chars = list(SYLLABLES) + list("፡።፣፤፧ ")
    rng = random.Random(1)
    for _ in range(3000):
        s = "".join(rng.choice(chars) for _ in range(rng.randint(1, 12)))
        assert fidel.to_fidel(fidel.romanize(s)) == s, s


def test_ascii_punct():
    assert fidel.romanize("ሰላም፡ዓለም።", ascii_punct=True) == "selam `alem."


# -------------------------------------------------------------- normalization
@pytest.mark.parametrize("src,out", [
    ("ሐይለ ሥላሴ", "ሀይለ ስላሴ"),
    ("ዐይን", "አይን"),
    ("ፀሐይ", "ጸሀይ"),
    ("ቱዋ ኩዋ", "ቷ ኳ"),
    ("ሰላም፡፡", "ሰላም።"),
    ("  ሰላም   ነህ  ", "ሰላም ነህ"),
])
def test_normalize_standard(src, out):
    assert fidel.normalize(src) == out


def test_normalize_levels():
    assert fidel.normalize("ሐ ሃ", "light") == "ሐ ሃ"
    assert fidel.normalize("ሓ ኻ", "standard") == "ሃ ኻ"
    assert fidel.normalize("ሓ ኻ ኣ ዓ ሰላም፡ዓለም", "aggressive") == "ሀ ሀ አ አ ሰላም አለም"


def test_normalize_is_idempotent():
    rng = random.Random(3)
    chars = list(SYLLABLES) + [" ", "፡", "።"]
    for level in fidel.LEVELS:
        for _ in range(500):
            s = "".join(rng.choice(chars) for _ in range(rng.randint(1, 20)))
            once = fidel.normalize(s, level)
            assert fidel.normalize(once, level) == once


def test_normalize_bad_level():
    with pytest.raises(ValueError):
        fidel.normalize("x", "extreme")


# ---------------------------------------------------------------- tokenizing
def test_sentences():
    assert fidel.sentences("ሰላም ነህ? ደህና ነኝ። አመሰግናለሁ") == ["ሰላም ነህ?", "ደህና ነኝ።", "አመሰግናለሁ"]


def test_words():
    assert fidel.words("ሰላም፡ዓለም፣ በ፳፻፲፮ 3.5 ok።") == ["ሰላም", "ዓለም", "፣", "በ", "፳፻፲፮", "3.5", "ok", "።"]
    assert fidel.words("ሰላም፣ ዓለም።", punct=False) == ["ሰላም", "ዓለም"]
