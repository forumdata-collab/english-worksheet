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
- **Light tracing guides** (描紅) in practice cells
- **Speech**: US or UK English pronunciation per letter/word/sentence
- **A4 print / PDF export** with print-size options (1.5–2.6cm)
- **Dictation mode** (hide guides, readings as cues)
- Settings persisted in localStorage

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
├── strokes_font.js     # Generated letter stroke paths (mask-reveal animation)
├── fonts/              # Self-hosted Andika + Playwrite woff2
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

## License

MIT. Fonts: Andika & Playwrite are licensed under the SIL Open Font License 1.1.