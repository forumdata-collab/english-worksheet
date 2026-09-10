# English Word Practice ✏️

Handwriting worksheet generator for English learners — **print & cursive**, **uppercase & lowercase**, **word & sentence practice**, printable to A4.

Live: https://engword.we1co.me

## Features

- **Three practice levels**
  - Letters — single-letter grids with uppercase/lowercase
  - Words — whole-word practice lines
  - Sentences — full sentence practice
- **Two handwriting styles**
  - Print (正寫) — Kalam font
  - Cursive (草寫) — Caveat font
  - Or both, side by side
- **Uppercase / Lowercase / Both** toggle
- **Four-line handwriting grid** (top, dashed midline, baseline, descender) — rendered as inline SVG so it prints reliably
- **Light tracing guides** (描紅) in practice cells
- **Speech**: US or UK English pronunciation per letter/word/sentence
- **A4 print / PDF export** with print-size options (1.5–2.6cm)
- Dictation mode (hide guides, readings as cues)
- Settings persisted in localStorage

## Tech

- Single-file vanilla JS app (`index.html`), no build step
- Self-hosted OFL fonts: [Kalam](https://fonts.google.com/specimen/Kalam) (print) & [Caveat](https://fonts.google.com/specimen/Caveat) (cursive) — zero CDN dependency
- Four-line guides are inline SVG strokes (CSS backgrounds don't print)
- Web Speech API for pronunciation (en-US / en-GB)

## Deploy

```bash
wrangler pages deploy . --project-name=engword-we1co --branch=main
```

## License

MIT. Fonts: Kalam & Caveat are SIL Open Font License 1.1.
