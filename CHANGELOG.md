# Changelog

## 2026-09-19 — v1.3

- **Fixed — Sky·Grass·Mud picture distorted on word/sentence lines**: the guide SVG uses `preserveAspectRatio="none"` so one viewBox unit is wider than it is tall on a long line, which stretched the artwork horizontally (up to ~12× on a full-width word line). The artwork is now drawn at a **fixed 3:1 pixel aspect** (same scale as the square letter cells) and **tiled horizontally** — alternate tiles mirrored so seams read as part of the picture — which keeps every mode in scale. Tiles are re-fitted on resize, before print and after print.
- **Bilingual UI** (English + 中文): every option label, option value, quick button, print-bar button, modal button, toast, hint and worksheet section title now shows both languages — previously some were English-only, some bilingual and some Chinese-only (淨句子).
- **Options panel re-organised** into three self-contained sections: 📐 **Layout 版面** (rows · guide style · cells per row · screen/print cell size) · 📝 **Content 內容** (style · case · section · tracing guide · dedupe) · 📄 **Page 頁面** (title · name · accent · show header). The collapsed "⚙️ Advanced" layer is gone — every control is visible in one pass.

## 2026-09-19 — v1.2

- **Sky·Grass·Mud guide** (天草泥): optional three-band background — 天 sky (light blue) / 草 grass (light green) / 泥 mud (light brown) — drawn from the bundled artwork `caoni-bg.jpg` (sliced 3× across a practice row so one asset reassembles the full picture), plus a **colours-only** variant
- Band boundaries follow the **font metrics, not the drawn grid lines**: sky ends at the x-height line (31.5%) and mud starts at the baseline (65%), so capitals sit on the mud, lower-case bodies stay in the grass, and only g/y/q/p tails reach into the mud
- In guide mode the dashed midline moves onto the band boundary; guide/tracing colours adjusted for the coloured background

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
