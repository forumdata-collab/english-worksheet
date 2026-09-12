# Changelog

## 2026-09-11 — v1.1

- **Mask-reveal stroke animation**: handwriting strokes now derived from the font's own glyph skeletons (`strokes_font.js`, generated via `tools/` pipeline) — the Show animation matches the reference letterform exactly
- **✍️ Show** available on Words, Copybook and 淨句子 blocks too (not just Letters)
- **淨句子 mode**: sentences-only practice section
- **Standard print font**: Andika (SIL) replaces Kalam for 正寫 — standard school print form; Playwrite USA Trad replaces Caveat for cursive
- Baseline re-calibrated for the new fonts (cell / word / sentence × print / cursive)

## 2026-09-10 — v1.0

- Initial release: letters / words / sentences practice
- Print & cursive handwriting styles (self-hosted OFL)
- Uppercase & lowercase practice grids
- Four-line guides (inline SVG, print-safe)
- US/UK pronunciation via Web Speech API
- A4 print with size options, dictation mode, localStorage settings
