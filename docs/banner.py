#!/usr/bin/env python3
"""Draw the README banner: the syllabary as a drafting-sheet matrix. Run from repo root."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from fidel import romanize, syllable  # noqa: E402

THEMES = {
    "light": dict(bg="#F4F1EA", ink="#17171B", muted="#6E6A62", faint="#DDD7CA", grid="#E8E3D7", accent="#E4572E"),
    "dark": dict(bg="#0E1217", ink="#ECE7DC", muted="#8B9099", faint="#262C35", grid="#161B22", accent="#FF6B3D"),
}
SANS = "Inter, 'Segoe UI', -apple-system, Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace"
ETH = "'Noto Sans Ethiopic', Nyala, Ebrima, Kefa, 'Abyssinica SIL', sans-serif"
ROWS = "ሀለመረሰቀበ"
ORDERS = "ä u i a e ə o".split()
TOUR = [(0, 0), (1, 3), (3, 5), (4, 2), (5, 6), (6, 1), (2, 4), (4, 0)]  # (row, order) cells visited


def banner(p):
    W, H = 1200, 420
    cell, gx, gy = 41, 846, 92
    o = [f'<rect width="{W}" height="{H}" fill="{p["bg"]}"/>',
         f'<defs><pattern id="g" width="20" height="20" patternUnits="userSpaceOnUse"><path d="M20 0H0V20" fill="none" stroke="{p["grid"]}"/></pattern></defs>',
         f'<rect x="20" y="20" width="1160" height="380" fill="url(#g)" stroke="{p["ink"]}" stroke-width="1.5"/>',
         f'<text x="64" y="84" font-family="{MONO}" font-size="12" letter-spacing="2.5" fill="{p["accent"]}">◆ OPEN SOURCE · PYTHON ≥ 3.10 · ZERO DEPENDENCIES</text>',
         f'<text x="58" y="190" font-family="{SANS}" font-size="112" font-weight="800" letter-spacing="-5" fill="{p["ink"]}">fidel</text>',
         f'<text x="322" y="188" font-family="{ETH}" font-size="56" font-weight="700" fill="{p["accent"]}">ፊደል</text>',
         f'<rect x="64" y="214" width="56" height="4" fill="{p["accent"]}"/>',
         f'<text x="64" y="258" font-family="{SANS}" font-size="24" font-weight="500" fill="{p["ink"]}">A toolkit for Amharic &amp; Ge\'ez-script text.</text>',
         f'<text x="64" y="292" font-family="{MONO}" font-size="14" fill="{p["muted"]}">normalize · tokenize · transliterate · Ethiopic numerals</text>']
    # matrix header + cells
    for j, v in enumerate(ORDERS):
        o.append(f'<text x="{gx + j*cell + cell/2}" y="{gy - 14}" text-anchor="middle" font-family="{MONO}" font-size="12" fill="{p["muted"]}">{v}</text>')
    for i, base in enumerate(ROWS):
        s = syllable(base)
        o.append(f'<text x="{gx - 16}" y="{gy + i*cell + 25}" text-anchor="end" font-family="{MONO}" font-size="12" fill="{p["muted"]}">{s.consonant}</text>')
        for j in range(7):
            ch = chr(s.row + j)
            o.append(f'<rect x="{gx + j*cell}" y="{gy + i*cell}" width="{cell}" height="{cell}" fill="{p["bg"]}" stroke="{p["faint"]}"/>'
                     f'<text x="{gx + j*cell + cell/2}" y="{gy + i*cell + 28}" text-anchor="middle" font-family="{ETH}" font-size="20" fill="{p["ink"]}">{ch}</text>')
    o.append(f'<rect x="{gx}" y="{gy}" width="{7*cell}" height="{len(ROWS)*cell}" fill="none" stroke="{p["ink"]}" stroke-width="1.5"/>')
    # moving highlight + synced readout
    n, dur = len(TOUR), 1.6 * len(TOUR)
    xs = ";".join(str(gx + c*cell) for _, c in TOUR)
    ys = ";".join(str(gy + r*cell) for r, _ in TOUR)
    o.append(f'<rect width="{cell}" height="{cell}" fill="{p["accent"]}" fill-opacity=".14" stroke="{p["accent"]}" stroke-width="2">'
             f'<animate attributeName="x" values="{xs}" dur="{dur}s" calcMode="discrete" repeatCount="indefinite"/>'
             f'<animate attributeName="y" values="{ys}" dur="{dur}s" calcMode="discrete" repeatCount="indefinite"/></rect>')
    for k, (r, c) in enumerate(TOUR):
        ch = chr(syllable(ROWS[r]).row + c)
        s = syllable(ch)
        vis = ";".join("1" if m == k else "0" for m in range(n))
        o.append(f'<g opacity="{1 if k == 0 else 0}"><animate attributeName="opacity" values="{vis}" dur="{dur}s" calcMode="discrete" repeatCount="indefinite"/>'
                 f'<text x="64" y="356" font-family="{MONO}" font-size="15" fill="{p["muted"]}">&gt;&gt;&gt; split("<tspan font-family="{ETH}" fill="{p["ink"]}">{ch}</tspan>")'
                 f'<tspan fill="{p["accent"]}">  →  {s.base} + {s.vowel}</tspan><tspan>   romanize → </tspan><tspan fill="{p["ink"]}">{romanize(ch, explicit_sixth=True)}</tspan></text></g>')
    body = "".join(o)
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="fidel — a toolkit for Amharic and Ge\'ez-script text"><title>fidel</title>{body}</svg>\n'


for name, pal in THEMES.items():
    (Path(__file__).parent / f"banner-{name}.svg").write_text(banner(pal))
