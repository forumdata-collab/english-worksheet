# Stroke-path tooling

`strokes_font.js` is generated — do not hand-edit it. It drives the Show modal by
masking the real font glyph with the pen's centreline strokes.

## Why it exists

The Show animation must agree with the letterform behind it. Hand-drawn stroke data
never could: it used a different baseline, a lowercase x-height 1.9x too small, and
its own letterform. So the visible ink is now the font glyph itself, revealed
through a mask of centreline paths derived from those same glyphs.

## Regenerating after a font change

1. **Rasterise the glyphs in the browser** (identical rasterisation to the page,
   including Playwrite's `calt` shaping). In the app's tab run the `grab()` loop —
   see "Capture" below — and save the JSON to `/tmp/glyphs/raw.json`.
   Each entry: `{data: <base64 PNG>, w, h, ox, oy}` where `ox/oy` is the crop
   origin in em units relative to (glyph centre, baseline).
   Two traps that silently produce garbage:
   - `document.fonts.ready` resolves immediately when no font has been *requested*
     yet, so the canvas would draw a **fallback** font. You must `await
     document.fonts.load('400px "EduPre"', CHARS)` for every family first, then
     assert `document.fonts.check(...)` before drawing. (A whole metric table was
     wrong once because of this.)
   - Keys must be a **flat** dict `{"print_A": …, "curs_a": …}`: `pipeline.py` splits
     on the first `_`, and `finalcheck.py` wants the prefixes `print_` / `curs_`
     (not `cursive_`).
2. `python3 tools/pipeline.py` — skeletonise, prune spurs, clump junction pixels,
   merge collinear edges, simplify, order → `/tmp/glyphs/paths.json`
   (`PRUNE_F = 0.13` is the current default and passes the coverage gate.)
3. `python3 tools/group.py` — group segments into teaching strokes so the red
   numbers show the school stroke count → `/tmp/glyphs/grouped.json`
   (edit `IDEAL_PRINT` / `IDEAL_CURSIVE` to change the expected counts).
4. `python3 tools/emit.py` — smooth (Catmull-Rom → cubic Bézier) and write
   `/tmp/glyphs/strokes_font.js`. `WIDTH_EM = 0.30` (0.20em left 6 letters below
   99.9%; 0.30em brings every print letter to 100% and the worst cursive letter to
   99.8%). Copy the result into the project root.
5. `python3 tools/finalcheck.py` — **must** report ~100% mask coverage. It reads the
   stroke width from the emitted file (not a hard-coded constant), so verification
   always matches what ships. Anything below ~99.9% means part of the glyph would
   never be revealed: raise `WIDTH_EM` in `emit.py` (and re-run step 4).

### Two print datasets live in one file

`strokes_font.js` holds `print` (Andika → 4-line grid), `print_pre`
(Edu AU VIC WA NT Pre → Sky·Grass·Mud when *Pre* is the selected caoni font) and
`cursive` (Playwrite). `strokeDataKey()` in `index.html` picks between them; the
Show modal's glyph font and cap ratio switch with it (`EduPre` cap 0.92 vs Andika
0.72). To regenerate only the Pre set: capture the rasters with
`FAM = { print: 'EduPre', cursive: 'Playwrite' }`, run steps 2–4, then take the
emitted `print` block and store it as `print_pre` in the repo file (keep the other
two blocks untouched — that is what `/tmp/engtest/merge_strokes.py` does).

Dependencies: `numpy scikit-image scipy pillow fonttools` (a venv is fine).

## Capture snippet (browser)

```js
const EM = 400, CW = 700, CH = 700, BASE = 480, CX = 350;
const c = document.createElement('canvas'); c.width = CW; c.height = CH;
const ctx = c.getContext('2d');
const grab = (ch, fam) => {
  ctx.clearRect(0, 0, CW, CH);
  ctx.font = EM + 'px "' + fam + '"';
  ctx.textAlign = 'center'; ctx.textBaseline = 'alphabetic'; ctx.fillStyle = '#000';
  ctx.fillText(ch, CX, BASE);
  const d = ctx.getImageData(0, 0, CW, CH).data;
  let x0 = 1e9, y0 = 1e9, x1 = -1e9, y1 = -1e9;
  for (let y = 0; y < CH; y++) for (let x = 0; x < CW; x++)
    if (d[(y * CW + x) * 4 + 3] > 40) { if (x < x0) x0 = x; if (x > x1) x1 = x; if (y < y0) y0 = y; if (y > y1) y1 = y; }
  // crop + pad, then read the ALPHA channel (the canvas is black-on-transparent,
  // so convert('L') would give all zeros)
  ...
};
```

## Coordinate contract with index.html

Both the glyph text and the mask live in the same `<g>`:

```
<g transform="translate(50,65) scale(FS)">
  <text x="0" y="0" font-size="1" text-anchor="middle">  <- watermark and ink
  <path d="..." stroke-width="0.20">                     <- mask strokes (em units)
```

so `x=0` is the glyph centre and `y=0` the baseline for both. That is what makes
"strokes always match the watermark" structural rather than a tuning exercise.
`FS = 46 / capRatio` (`capRatio` = 0.72 Andika print, 1.02 Playwrite cursive).
