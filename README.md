# English Word Practice ✏️

Handwriting worksheet generator for English learners — **print & cursive**, **uppercase & lowercase**, **word, sentence & copybook practice**, printable to A4.

## Features

- **Four practice modes**
  - Letters — single-letter grids with uppercase / lowercase / both
  - Words — whole-word practice lines
  - Copybook — letter-by-letter guided writing
  - 淨句子 (sentences-only) — full sentence practice without letter breakdown
- **Two handwriting styles**
  - Print (正寫) — Andika (SIL), standard school print form
  - Cursive (草寫) — Playwrite USA Trad
  - Or both, side by side
- **✍️ Show** — animated stroke guidance using **mask-reveal animation**: each letter's handwriting strokes are rendered from the font's own glyph skeletons, so the animation matches the reference letterform exactly (103 letters, ≥99.8% coverage)
- **Four-line handwriting grid** (top, dashed midline, baseline, descender) — inline SVG so it prints reliably
- **Sky·Grass·Mud guide** (天草泥) — optional three-band background drawn from the bundled artwork (`caoni-bg.jpg`), or a colours-only variant. **The font is selectable in this mode** (`Edu AU VIC WA NT Pre` by default, `Playwrite US Modern` = closest to the original even thirds at 30.7/36.5/32.8, or `Andika`); the 4-line *standard* mode always stays on Andika. Everything else is **derived from the chosen font's metrics** (`CAONI_FONTS` table: ascender / x-height / descender / cap / t / `k`): band boundaries (`caoniGeo()`), letter size (the whole glyph block fills the cell), baseline, and the cap & t multipliers (`asc/cap`, `asc/tAsc`). So print capitals reach the top frame (ink top ≈0.1% with Pre, ≈1.3% with Andika), lowercase ascenders b/d/f/h/k/l (and t, stretched to match h) touch the top, the lowercase bodies fill the grass band, and the g/y/p/q tails reach the bottom (≈99%). The artwork is *not* sliced: `caoniArtPlacement()` computes a y/height offset that puts the artwork's own two lines (measured at 32.91% / 65.60%) exactly on the band boundaries, so switching fonts needs no re-cutting. The cursive template is untouched (Playwrite's proportions already suit the original even thirds). On a long word/sentence line the artwork stays at the same scale as the letter cells and **tiles horizontally** (mirror-alternating) instead of stretching. Optional **dotted tracing** (`Edu AU VIC WA NT Dots`, Pre only) is available for tracing practice.
- **Light tracing guides** (描紅) in practice cells
- **Long text wraps**: word/sentence practice lines are measured at render time and split at word boundaries onto as many guide rows as needed (an over-long single word breaks character-wise), so nothing spills past the grid
- **Speech**: US or UK English pronunciation per letter/word/sentence
- **A4 print / PDF export** with print-size options (1.5–2.6cm)
- **Dictation mode** (hide guides, readings as cues)
- Settings persisted in localStorage
- **Bilingual menu** (English + 中文) — labels, option values, buttons and hints all show both languages

## Tech

- Single-file vanilla JS app (`index.html`), no build step
- Self-hosted OFL fonts: [Andika](https://fonts.google.com/specimen/Andika) (print) & [Playwrite USA Trad](https://fonts.google.com/specimen/Playwrite+USA) (cursive) — zero CDN dependency
- Four-line guides are inline SVG strokes (CSS backgrounds don't print)
- Web Speech API for pronunciation (en-US / en-GB)
- `tools/` — the stroke-generation pipeline (font glyph → skeleton → teaching strokes → `strokes_font.js`)

## Project structure

```
english-worksheet/
├── index.html          # Single-page app (UI + logic + styles)
├── caoni-bg.jpg        # Sky·grass·mud artwork — ONE file for both templates; the print band
│                       #   boundaries are hit by re-positioning/scaling it (caoniArtPlacement)
├── strokes_font.js     # Generated stroke paths, 4 datasets: print (Andika), print_pre
│                       #   (EduPre), print_pwusm (Playwrite US Modern) and cursive (Playwrite)
├── fonts/              # hand.css + the 6 woff2 actually used: Andika, EduPre, EduDots, PWUSM,
│                       #   Playwrite 400/700 (unused candidates were pruned)
├── tools/              # Stroke-generation pipeline (Python)
├── CHANGELOG.md        # Version history
└── LICENSE             # MIT
```

## Run

The app is static — no build step, no server dependency:

```bash
git clone https://github.com/forumdata-collab/english-worksheet.git
cd english-worksheet
python3 -m http.server 8080
# → http://localhost:8080
```

Or open `index.html` directly in a browser.

## Code health (2026-09-19 audit)

- **Regression suite, 68 checks** (headless chromium + real `change` events, results read via `--dump-dom`): all four sections × case × style · 5 guide styles + Sky·Grass·Mud tile aspect · `practice=0` · long-sentence / no-space-word wrapping · cells-per-row font scaling · dictation mode · stroke modal · localStorage · horizontal overflow · JS errors · caoni font switch (all three fonts: size fills the cell, family applied, CSS vars written) · dotted tracing · options-panel layout logic (4 decision axes, data-when conditional rows, collapse, presets, reset, label/id pairing) · Show-modal font/data switch (caoni+Pre → EduPre letterform + print_pre skeleton; fonts without a skeleton fall back to Andika). Print layout is tested separately by forcing the `@media print` rules on at A4 width: no overflow, and by a real `--print-to-pdf` + text-extraction check that the options panel and the on-sheet buttons (🔊 / ✍) never print.
- **Fixed smells**: Divergent Change + Long Method (`renderWorksheet` 175 lines → orchestrator + 4 section builders) · Duplicated Code (word/sentence rows → `lineBlockHtml`) · Speculative Generality (unused params) · Dead Code (CSS left over from the removed "Advanced" panel).
- **Accepted by design**: single `index.html`, no build step (Large Class is the deliberate trade-off); `splitToFitLine()` 4 params; cross-file duplication with chineseword — the two sites are separate deployments, and shared helpers are deliberately small (`jsArg`, guide SVG).

## License

MIT. Fonts: Andika & Playwrite are licensed under the SIL Open Font License 1.1.