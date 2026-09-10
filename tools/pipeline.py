"""Font glyph -> pen centreline strokes (skeleton graph, pruned + merged + ordered).

Input : /tmp/glyphs/raw.json  (browser-rendered glyph rasters, identical rasterisation
        to what the app draws, so paths and the reference text line up exactly)
Output: /tmp/glyphs/paths.json  {style: {char: [[ [x,y], ... ], ...]}}  in em units,
        y-down, baseline at y=0, glyph origin (pen start x) at x=0.
"""
import base64, io, json, math
import numpy as np
from PIL import Image
from skimage.morphology import skeletonize

EM = 400  # px em used when the browser rasterised the glyphs
PRUNE_F = 0.13   # dead-end spur pruning threshold, as a fraction of min(h,w)
NB = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]


def mask_of(entry):
    im = Image.open(io.BytesIO(base64.b64decode(entry['data'])))
    if im.mode == 'RGBA':
        a = np.array(im)[:, :, 3]          # canvas draws black-on-transparent -> use alpha
    else:
        a = np.array(im.convert('L'))
    return a > 100, entry['ox'], entry['oy']


def neighbours(sk, y, x):
    h, w = sk.shape
    out = []
    for dy, dx in NB:
        ny, nx = y + dy, x + dx
        if 0 <= ny < h and 0 <= nx < w and sk[ny, nx]:
            out.append((ny, nx))
    return out


def cluster_nodes(pix, deg, radius=3):
    """Junction pixels come in clumps (adjacent pixels all degree>=3). Collapse
    each clump into ONE graph node, else the graph fills with 2px stub edges and
    no stroke merging can ever fire."""
    nodepx = sorted(p for p, d in deg.items() if d != 2)
    parent = {p: p for p in nodepx}

    def find(p):
        while parent[p] != p:
            parent[p] = parent[parent[p]]
            p = parent[p]
        return p

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    for i, p in enumerate(nodepx):
        for q in nodepx[i + 1:]:
            if abs(p[0] - q[0]) <= radius and abs(p[1] - q[1]) <= radius:
                union(p, q)
    groups = {}
    for p in nodepx:
        groups.setdefault(find(p), []).append(p)
    pixel_to_node = {}
    centroids = []
    for gi, (root, members) in enumerate(sorted(groups.items())):
        for m in members:
            pixel_to_node[m] = gi
        cy = sum(m[0] for m in members) / len(members)
        cx = sum(m[1] for m in members) / len(members)
        centroids.append((cy, cx))
    return pixel_to_node, centroids


def build_graph(sk):
    """-> centroids, edges [(nodeA, nodeB, [pixel path])] with junction clumps merged."""
    ys, xs = np.nonzero(sk)
    pix = set(zip(ys.tolist(), xs.tolist()))
    deg = {p: len(neighbours(sk, *p)) for p in pix}
    pixel_to_node, centroids = cluster_nodes(pix, deg)
    if not centroids:                                   # pure loop, no junction px
        pixel_to_node = {next(iter(pix)): 0}
        centroids = [next(iter(pix))]

    edges = []
    visited = set()
    for start in list(pixel_to_node):
        for q in neighbours(sk, *start):
            if q in pixel_to_node:
                continue                             # inside a clump
            if (start, q) in visited:
                continue
            path = [start, q]
            visited.add((start, q))
            prev, cur = start, q
            while cur not in pixel_to_node:
                nxt = [n for n in neighbours(sk, *cur) if n != prev]
                if not nxt:
                    break
                prev, cur = cur, nxt[0]
                path.append(cur)
            if cur in pixel_to_node:
                visited.add((path[-1], path[-2]))
                visited.add((path[-2], path[-1]))
            edges.append([pixel_to_node[start], pixel_to_node.get(cur), path])
    return centroids, edges


def prune(edges, min_len):
    """Drop short dead-end spurs; repeat because pruning creates new dead ends."""
    while True:
        deg = {}
        for a, b, p in edges:
            deg[a] = deg.get(a, 0) + 1
            deg[b] = deg.get(b, 0) + 1
        drop = [i for i, (a, b, p) in enumerate(edges)
                if len(p) < min_len and (deg[a] == 1 or deg[b] == 1) and a != b]
        if not drop:
            break
        for i in reversed(drop):
            edges.pop(i)
    return edges


def direction(path, from_end, k=12):
    k = min(k, len(path) - 1)
    if from_end == 'start':
        (y0, x0), (y1, x1) = path[0], path[k]
    else:
        (y0, x0), (y1, x1) = path[-1], path[-1 - k]
    v = np.array([x1 - x0, y1 - y0], float)
    n = np.linalg.norm(v)
    return v / n if n else v


def merge_through_junctions(edges, cos_thresh=0.55):
    """Fuse edges that continue each other through a junction. Handles degree 3
    (stem passing a branch, e.g. B's stem) and degree 4 (X crossing)."""
    changed = True
    while changed:
        changed = False
        deg = {}
        for a, b, p in edges:
            deg[a] = deg.get(a, 0) + 1
            deg[b] = deg.get(b, 0) + 1
        for nid, d in sorted(deg.items()):
            if d < 2 or d > 4 or d % 2 != 0 and d != 3:
                if d != 3:
                    continue
            inc = [i for i, (a, b, p) in enumerate(edges) if a == nid or b == nid]
            if len(inc) < 2:
                continue
            # for each incident edge, its out-going direction when leaving nid
            info = []
            for i in inc:
                a, b, p = edges[i]
                outpath = p if a == nid else p[::-1]        # starts at nid
                info.append((i, outpath, direction(outpath, 'start')))
            best, bestdot = None, -2.0
            for ii in range(len(info)):
                for jj in range(ii + 1, len(info)):
                    i, pi, vi = info[ii]
                    j, pj, vj = info[jj]
                    dot = -float(vi.dot(vj))                 # want opposite directions
                    if dot > bestdot:
                        bestdot, best = dot, (i, j)
            if best is None or bestdot < cos_thresh:
                continue
            i, j = best
            ai, bi, pi = edges[i]
            aj, bj, pj = edges[j]
            # p1 must END at nid, p2 must START at nid
            p1 = pi if bi == nid else pi[::-1]
            p2 = pj if aj == nid else pj[::-1]
            newpath = p1 + p2[1:]
            new_start = ai if bi == nid else bi
            new_end = bj if aj == nid else aj
            edges = [e for k, e in enumerate(edges) if k not in (i, j)]
            edges.append([new_start, new_end, newpath])
            changed = True
            break
    return edges


def a1_ends_at(a, b, nid):
    """True when the edge's path ends at nid (path runs a -> b)."""
    return b == nid


def is_loop(pts, tol=6):
    (y0, x0), (y1, x1) = pts[0], pts[-1]
    return abs(y0 - y1) <= tol and abs(x0 - x1) <= tol and len(pts) > 8


def simplify(pts, eps=2.2):
    """RDP, but closed loops are cut in half first (the straight chord
    degenerate case would otherwise collapse the whole loop to 2 points)."""
    if is_loop(pts):
        mid = len(pts) // 2
        a = rdp(pts[:mid + 1], eps)
        b = rdp(pts[mid:], eps)
        return a[:-1] + b
    return rdp(pts, eps)


def spike_free(path, min_len):
    return len(path) >= min_len


def rdp(points, eps):
    if len(points) < 3:
        return points
    (y0, x0), (y1, x1) = points[0], points[-1]
    dmax, idx = 0.0, 0
    for i in range(1, len(points) - 1):
        y, x = points[i]
        num = abs((y1 - y0) * x - (x1 - x0) * y + x1 * y0 - y1 * x0)
        den = math.hypot(y1 - y0, x1 - x0) or 1e-9
        d = num / den
        if d > dmax:
            dmax, idx = d, i
    if dmax > eps:
        return rdp(points[:idx + 1], eps)[:-1] + rdp(points[idx:], eps)
    return [points[0], points[-1]]


def order_strokes(strokes, oy, oh):
    """Heuristic writing order: topmost start first, then leftmost; normalise
    each stroke's direction (vertical: top->down, horizontal: left->right)."""
    norm = []
    for pts in strokes:
        (ya, xa), (yb, xb) = pts[0], pts[-1]
        dy, dx = yb - ya, xb - xa
        if abs(dy) >= abs(dx):
            if dy < 0:
                pts = pts[::-1]
        else:
            if dx < 0:
                pts = pts[::-1]
        norm.append(pts)
    norm.sort(key=lambda p: (round((p[0][0] - oy) / (oh * 0.16)), p[0][1]))
    return norm


def loop_path(sk):
    """Closed skeleton with no junction at all (letter 'o'): walk the cycle once,
    then start it at the top-right (where a pen naturally begins an 'o')."""
    ys, xs = np.nonzero(sk)
    start = (int(ys[0]), int(xs[0]))
    path, prev, cur = [start], None, start
    while True:
        nxt = [n for n in neighbours(sk, *cur) if n != prev and n not in path]
        if not nxt:
            break
        prev, cur = cur, nxt[0]
        path.append(cur)
    if len(path) < 8:
        return None
    top = min(range(len(path)), key=lambda i: (path[i][0], -path[i][1]))
    path = path[top:] + path[:top]
    # go leftwards from the top (visually anticlockwise)
    if len(path) > 2 and path[1][1] > path[0][1]:
        path = [path[0]] + path[:0:-1]
    path.append(path[0])
    return path


def component_strokes(mask, prune_f):
    """Skeletonise ONE connected blob and return its strokes in pixel coords."""
    from scipy import ndimage
    ys, xs = np.nonzero(mask)
    if len(ys) < 4:
        return []
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    sub = mask[y0:y1 + 1, x0:x1 + 1]
    sk = skeletonize(sub)
    if sk.sum() < 2:
        return []
    h, w = sk.shape
    dys, dxs = np.nonzero(sk)
    deg = {(int(y), int(x)): len(neighbours(sk, int(y), int(x))) for y, x in zip(dys, dxs)}
    out = []
    if all(d == 2 for d in deg.values()):
        lp = loop_path(sk)
        if lp:
            out.append(simplify(lp, 2.0))
    else:
        centroids, edges = build_graph(sk)
        edges = [e for e in edges if spike_free(e[2], 3)]
        edges = prune(edges, max(3, int(min(h, w) * prune_f)))
        edges = merge_through_junctions(edges)
        edges = [e for e in edges if len(e[2]) >= max(3, int(min(h, w) * prune_f * 0.8))]
        for a, b, p in edges:
            pts = simplify(p, 2.2)
            if len(pts) >= 2:
                out.append(pts)
    if not out:
        # a round blob (i/j dot) skeletons to a handful of pixels and yields no
        # path at all -> fall back to a short segment through it so the stroke
        # mask still covers the dot
        dyy, dxx = np.nonzero(sub)
        top = (int(dyy.min()), int(dxx[dyy.argmin()]))
        bot = (int(dyy.max()), int(dxx[dyy.argmax()]))
        if top != bot:
            out.append([top, bot])
    return [[(int(y) + y0, int(x) + x0) for (y, x) in st] for st in out]


def process(entry, style, ch):
    m, ox, oy = mask_of(entry)
    if m.sum() < 6:
        return None
    from scipy import ndimage
    labels, n = ndimage.label(m, structure=np.ones((3, 3)))
    h, w = m.shape
    total = int(m.sum())
    groups = []           # (is_dot, strokes_px)
    for lab in range(1, n + 1):
        comp = labels == lab
        area = int(comp.sum())
        if area < 12:
            continue
        strokes = component_strokes(comp, PRUNE_F)
        # i/j dot: small, round, and much smaller than the main body
        is_dot = area < 0.35 * total      # i/j dot: separate blob, written last
        groups.append((is_dot, strokes))
    if not groups:
        return None
    body = [s for d, g in groups if not d for s in g]
    dots = [s for d, g in groups if d for s in g]
    if not body and not dots:
        return None
    body = order_strokes(body, oy, h) if body else []
    # a dot (letter i / j) is always written last
    dots = sorted(dots, key=lambda p: (p[0][0], p[0][1]))
    strokes = body + dots
    em_strokes = []
    for pts in strokes:
        em = [((x / EM) + ox, (y / EM) + oy) for (y, x) in pts]
        em = [(round(x, 4), round(y, 4)) for x, y in em]
        em_strokes.append(em)
    return em_strokes


if __name__ == '__main__':
    raw = json.load(open('/tmp/glyphs/raw.json'))
    out = {'print': {}, 'cursive': {}}
    fails = []
    for key, entry in raw.items():
        style, ch = key.split('_', 1)
        style = 'print' if style == 'print' else 'cursive'
        try:
            r = process(entry, style, ch)
        except Exception as e:
            r, err = None, e
            fails.append((key, repr(e)))
        if r:
            out[style][ch] = r
        elif not any(f[0] == key for f in fails):
            fails.append((key, 'no strokes'))
    json.dump(out, open('/tmp/glyphs/paths.json', 'w'))
    print('print letters:', len(out['print']), '| cursive letters:', len(out['cursive']))
    print('failures:', len(fails))
    for k, e in fails[:15]:
        print('  ', k, e)
    for ch in 'aeoBgWxX':
        if ch in out['print']:
            print(f"  print {ch}: {len(out['print'][ch])} strokes, "
                  f"pts={[len(s) for s in out['print'][ch]]}")
