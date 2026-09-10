"""Group skeleton segments into TEACHING strokes.

The mask reveal needs every skeleton segment (that's what guarantees coverage),
but the red numbers must show the school stroke sequence. So: keep all segments,
group them, and number the groups.

Grouping = repeatedly merge the pair of groups whose join is the most
continuous (closest endpoints + most collinear), until the group count reaches
the target from the teaching table. If the segmentation is too coarse
(too few groups, e.g. Andika's one-piece 'a') the longest group is split at its
sharpest corner.
"""
import json

IDEAL_PRINT = dict(
    a=2, b=2, c=1, d=2, e=2, f=2, g=2, h=2, i=2, j=2, k=3, l=1, m=3, n=2,
    o=1, p=2, q=2, r=2, s=1, t=2, u=2, v=1, w=1, x=2, y=2, z=1,
    A=3, B=3, C=1, D=2, E=4, F=3, G=1, H=3, I=3, J=1, K=3, L=2, M=4, N=3,
    O=1, P=2, Q=2, R=3, S=1, T=2, U=1, V=1, W=4, X=2, Y=3, Z=3,
)

# Cursive (Playwrite) is written in one flowing motion; only i/j add a dot and
# a few letters double back. Counts here are deliberately small.
IDEAL_CURSIVE = dict(
    a=1, b=1, c=1, d=1, e=1, f=2, g=1, h=1, i=2, j=2, k=2, l=1, m=1, n=1, o=1,
    p=1, q=1, r=1, s=1, t=2, u=1, v=1, w=1, x=2, y=1, z=1,
    A=1, B=1, C=1, D=1, E=1, F=2, G=1, H=1, I=1, J=1, K=2, L=1, M=1, N=1, O=1,
    P=1, Q=2, R=1, S=1, T=1, U=1, V=1, W=1, X=2, Y=1, Z=1,
)


def _dist(a, b):
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5


def _dir_pts(pts, from_start, k=6):
    k = min(k, len(pts) - 1)
    if from_start:
        (x0, y0), (x1, y1) = pts[0], pts[k]
    else:
        (x0, y0), (x1, y1) = pts[-1], pts[-1 - k]
    dx, dy = x1 - x0, y1 - y0
    n = (dx * dx + dy * dy) ** 0.5 or 1e-9
    return (dx / n, dy / n)


def _join_score(g1, g2, strokes):
    """Lower = better continuation between two groups."""
    best = None
    for i in g1:
        for j in g2:
            p, q = strokes[i], strokes[j]
            for a_end in (0, 1):          # 0 = p's tail, 1 = p's head
                for b_end in (0, 1):
                    pa = p[-1] if a_end else p[0]
                    qb = q[0] if b_end else q[-1]
                    d = _dist(pa, qb)
                    if d > 0.22:          # too far apart to be one motion
                        continue
                    va = _dir_pts(p, not a_end)
                    vb = _dir_pts(q, not b_end)
                    # want va leaving the join and vb continuing in the same direction
                    cos = -(va[0] * vb[0] + va[1] * vb[1])
                    s = d + 0.35 * (1 - cos)
                    if best is None or s < best:
                        best = s
    return best if best is not None else 9.9


def _group_len(g, strokes):
    return sum(_len(strokes[i]) for i in g)


def _len(pts):
    t = 0.0
    for k in range(len(pts) - 1):
        t += _dist(pts[k], pts[k + 1])
    return t


def _sharpest_split(pts):
    """Index of the corner where a one-piece glyph is really two strokes.
    Falls back to the arc-length midpoint when the curve has no sharp corner
    (still reveals as one continuous pen motion, just numbered as two)."""
    if len(pts) < 5:
        return None
    best, bi = -2.0, None
    for i in range(2, len(pts) - 2):
        v1 = (pts[i][0] - pts[i - 2][0], pts[i][1] - pts[i - 2][1])
        v2 = (pts[i + 2][0] - pts[i][0], pts[i + 2][1] - pts[i][1])
        n1 = (v1[0] ** 2 + v1[1] ** 2) ** 0.5 or 1e-9
        n2 = (v2[0] ** 2 + v2[1] ** 2) ** 0.5 or 1e-9
        cos = (v1[0] * v2[0] + v1[1] * v2[1]) / (n1 * n2)
        if cos < best:
            best, bi = cos, i
    if bi is not None and best < 0.85:
        return bi
    # no usable corner -> cut at the half-way point of the arc
    half, acc = _len(pts) / 2.0, 0.0
    for i in range(len(pts) - 1):
        acc += _dist(pts[i], pts[i + 1])
        if acc >= half:
            return i + 1
    return None


def group(strokes, target):
    groups = [[i] for i in range(len(strokes))]
    guard = 0
    while len(groups) > target and guard < 200:
        guard += 1
        best, pair = None, None
        for gi in range(len(groups)):
            for gj in range(gi + 1, len(groups)):
                s = _join_score(groups[gi], groups[gj], strokes)
                if best is None or s < best:
                    best, pair = s, (gi, gj)
        gi, gj = pair
        groups[gi] = groups[gi] + groups[gj]
        groups.pop(gj)
    guard = 0
    while len(groups) < target and guard < 60:
        guard += 1
        gi = max(range(len(groups)), key=lambda i: _group_len(groups[i], strokes))
        g = groups[gi]
        # split the longest single path in this group at its sharpest corner
        cand = [i for i in g if len(strokes[i]) >= 6]
        if not cand:
            break
        li = max(cand, key=lambda i: _len(strokes[i]))
        cut = _sharpest_split(strokes[li])
        if cut is None:
            break
        a, b = strokes[li][:cut + 1], strokes[li][cut:]
        strokes[li] = a
        strokes.insert(li + 1, b)
        groups = [[i if i <= li else i + 1 for i in gg] for gg in groups]
        groups.insert(gi + 1, [li + 1])
    return groups, strokes


if __name__ == '__main__':
    paths = json.load(open('/tmp/glyphs/paths.json'))
    out = {'print': {}, 'cursive': {}}
    for style, ideal in (('print', IDEAL_PRINT), ('cursive', IDEAL_CURSIVE)):
        for ch, strokes in paths[style].items():
            target = ideal.get(ch, len(strokes))
            groups, strokes2 = group([list(map(tuple, s)) for s in strokes], target)
            # flatten: each group becomes a list of segments in reveal order
            out[style][ch] = [[list(map(list, strokes2[i])) for i in g] for g in groups]
    json.dump(out, open('/tmp/glyphs/grouped.json', 'w'))

    bad = []
    for style, ideal in (('print', IDEAL_PRINT), ('cursive', IDEAL_CURSIVE)):
        for ch, g in out[style].items():
            if len(g) != ideal[ch]:
                bad.append(f'{style} {ch}: {len(g)} != {ideal[ch]}')
    print('letters whose group count != target:', len(bad))
    for b in bad[:10]:
        print('  ', b)
    tot = sum(len(g) for g in out['print'].values())
    print('print groups total:', tot, '| all letters present:', len(out['print']), len(out['cursive']))
