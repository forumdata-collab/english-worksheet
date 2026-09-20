import base64, io, json, re
import numpy as np
from PIL import Image, ImageDraw

EM = 400
raw = json.load(open('/tmp/glyphs/raw.json'))
paths = json.load(open('/tmp/glyphs/paths.json'))
# 用 emit 實際寫入嘅筆寬（唔好硬編，否則驗證同出貨唔一致）
_src = open('/tmp/glyphs/strokes_font.js').read()
WIDTH_EM = float(re.search(r'STROKE_WIDTH_EM = ([\d.]+)', _src).group(1)) if 'STROKE_WIDTH_EM' in _src else 0.20


def glyph(key):
    im = Image.open(io.BytesIO(base64.b64decode(raw[key]['data'])))
    if im.mode == 'RGBA':
        return np.array(im)[:, :, 3] > 100
    return np.array(im.convert('L')) > 100


worst = []
for style, pref in (('print', 'print'), ('cursive', 'curs')):
    for ch, strokes in paths[style].items():
        e = raw[f'{pref}_{ch}']
        m = glyph(f'{pref}_{ch}')
        h, w = m.shape
        img = Image.new('L', (w, h), 0)
        d = ImageDraw.Draw(img)
        lw = max(2, round(WIDTH_EM * EM))
        r = lw / 2
        for st in strokes:
            pts = [((x - e['ox']) * EM, (y - e['oy']) * EM) for x, y in st]
            if len(pts) >= 2:
                d.line(pts, fill=255, width=lw, joint='curve')
            for px, py in pts:
                d.ellipse([px - r, py - r, px + r, py + r], fill=255)
        covered = np.logical_and(m, np.array(img) > 100)
        cov = covered.sum() / m.sum()
        worst.append((float(cov), f'{style} {ch}'))

worst.sort()
print(f'worst 8 coverage (mask width {WIDTH_EM}em, final paths):')
for c, n in worst[:8]:
    print(f'   {n:12s} {c*100:.3f}%')
print(f'letters below 99.9%: {sum(1 for c, _ in worst if c < 0.999)} / {len(worst)}')
