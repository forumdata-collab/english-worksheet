"""paths.json -> strokes_font.js  (smoothed SVG path data, em units, baseline y=0)

Coordinate contract with the app:
  <text x="50" y="BASELINE" text-anchor="middle" font-size="FS">  <- watermark + ink
  <g transform="translate(50,BASELINE) scale(FS)">              <- mask strokes
Both use the glyph's own centre-x as x=0 and the baseline as y=0, so the masked
reveal lines up with the text EXACTLY by construction.
"""
import json

PRUNE_F = 0.05
WIDTH_EM = 0.20


def catmull_rom(pts, closed=False):
    """Polyline -> smooth cubic path (Catmull-Rom tangents)."""
    P = list(pts)
    if closed and len(P) > 2:
        core = P[:-1]
        n = len(core)
        d = f'M {core[0][0]:.4f} {core[0][1]:.4f}'
        for i in range(n):
            p0 = core[(i - 1) % n] if i > 0 else core[(i - 1) % n]
            p1 = core[i]
            p2 = core[(i + 1) % n]
            p3 = core[(i + 2) % n]
            c1 = (p1[0] + (p2[0] - p0[0]) / 6.0, p1[1] + (p2[1] - p0[1]) / 6.0)
            c2 = (p2[0] - (p3[0] - p1[0]) / 6.0, p2[1] - (p3[1] - p1[1]) / 6.0)
            d += f' C {c1[0]:.4f} {c1[1]:.4f} {c2[0]:.4f} {c2[1]:.4f} {p2[0]:.4f} {p2[1]:.4f}'
        return d
    if len(P) == 2:
        return f'M {P[0][0]:.4f} {P[0][1]:.4f} L {P[1][0]:.4f} {P[1][1]:.4f}'
    n = len(P)
    d = f'M {P[0][0]:.4f} {P[0][1]:.4f}'
    tang = []
    for i in range(n):
        if i == 0:
            t = (P[1][0] - P[0][0], P[1][1] - P[0][1])
        elif i == n - 1:
            t = (P[n - 1][0] - P[n - 2][0], P[n - 1][1] - P[n - 2][1])
        else:
            t = ((P[i + 1][0] - P[i - 1][0]) / 2.0, (P[i + 1][1] - P[i - 1][1]) / 2.0)
        tang.append(t)
    for i in range(n - 1):
        p1, p2 = P[i], P[i + 1]
        c1 = (p1[0] + tang[i][0] / 3.0, p1[1] + tang[i][1] / 3.0)
        c2 = (p2[0] - tang[i + 1][0] / 3.0, p2[1] - tang[i + 1][1] / 3.0)
        d += f' C {c1[0]:.4f} {c1[1]:.4f} {c2[0]:.4f} {c2[1]:.4f} {p2[0]:.4f} {p2[1]:.4f}'
    return d


def is_closed(pts, tol=0.012):
    (x0, y0), (x1, y1) = pts[0], pts[-1]
    return abs(x0 - x1) < tol and abs(y0 - y1) < tol and len(pts) > 4


if __name__ == '__main__':
    paths = json.load(open('/tmp/glyphs/grouped.json'))
    out = {}
    total = 0
    for style in ('print', 'cursive'):
        out[style] = {}
        for ch, groups in paths[style].items():
            gg = []
            for grp in groups:
                ds = []
                for st in grp:
                    pts = [tuple(p) for p in st]
                    closed = is_closed(pts) and len(pts) > 8
                    if closed:
                        pts = pts + [pts[0]]
                    ds.append(catmull_rom(pts, closed))
                gg.append(ds)
                total += 1
            out[style][ch] = gg
    js = ('// Generated from the real font glyphs by /tmp/glyphs/pipeline.py + emit.py.\n'
          '// Centreline pen paths in em units: x=0 is the glyph centre, y=0 is the baseline\n'
          '// (y grows downwards). Used as a MASK over the font glyph, so the revealed shape\n'
          '// is exactly the font letterform - the paths only decide the writing order.\n'
          '// Shape: letter -> [ stroke, ... ] ; each stroke -> [ segmentPathData, ... ]\n'
          '// (one stroke may need several skeleton segments to guarantee full coverage).\n'
          f'const STROKE_WIDTH_EM = {WIDTH_EM};\n'
          'const LETTER_PATHS = ' + json.dumps(out, ensure_ascii=False) + ';\n')
    open('/tmp/glyphs/strokes_font.js', 'w').write(js)
    print('letters:', len(out['print']), '+', len(out['cursive']), '| strokes total:', total)
    print('file bytes:', len(js))
    for ch in 'aoBiFW':
        g = out['print'][ch]
        print(f'  {ch}: {len(g)} strokes, segments {[len(x) for x in g]}')
