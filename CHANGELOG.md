# Changelog

## 2026-09-19 — v1.6

### Fixed
- **Cells-per-row 模式下字級冇跟格仔**：perRow=4 格仔 216px 但字級仍固定 61.44px（比例 0.285，應為 0.64），基線亦對唔上四線格。改用 container query（`--cell-font: 64cqw`），螢幕同列印都跟格仔比例（實測 0.62–0.63）。

### Changed（Code Smells 修正）
- **Divergent Change + Long Method**：`renderWorksheet()` 175 行（包辦 letters / words / sentences + header + 格大小 + 格線樣式）拆成 orchestrator（~25 行）+ `letterSectionHtml()` / `wordSectionHtml()` / `sentenceSectionHtml()` + `applyCellSizes()` / `applyGuideStyle()` / `applyHeader()`。
- **Duplicated Code**：詞語行同句子行原本逐行近乎重複（只差塊 class、行高、字級比例、layer class）→ 合併為 `lineBlockHtml(o, ctx, cfg)`，兩邊各一個薄 wrapper。
- **Speculative Generality**：移除 `animateSvgBox()` 未用嘅 `box` 參數；清走「Advanced」摺疊層移除後遺留嘅 `.advance-collapse` / `.collapse-wrap` 死 CSS。
- `jsArg()` 統一處理 inline onclick 嘅字串轉義（原本 `.replace(/'/g, …)` 散落 4 處）。

### Notes
- 回歸測試套件 **35 項**（letters/words/copybook/sentences × case × style、5 款格線 + 天草泥比例、practice=0、長句／無空格長字斷行、perRow 字級、默書版、筆順 modal、localStorage、溢出、JS error）。全綠。
- 列印版面測試（`@media print` → `@media all` @794px）：無溢出，列印格 var 2.2cm。

## 2026-09-19 — v1.5

- **Options apply immediately**: changing any control in the options panel now regenerates the worksheet itself (250ms debounce, `bindAutoRegenerate()`) instead of waiting for another **Generate** click — the same change was made on chineseword after a "the option has no effect" report. It only runs once a worksheet exists and the input is non-empty.

## 2026-09-19 — v1.4

- **Fixed — long sentences / words did not wrap and spilled out of the guide box**: the word/sentence glyphs are `white-space: nowrap` at a fixed font size, so any text wider than the line (e.g. a full sentence) overflowed instead of continuing on the next row — measured 259px past the line edge for the glyph layer, 349px past the container for the whole block. Text is now measured with a canvas at the **font actually in use** and split at word boundaries onto as many rows as needed (practice rows cycle through the chunks in order); a single over-long word with no spaces falls back to character-level breaks. The fit is computed from the live line width with a margin covering the narrower A4 print layout, and recomputed after `document.fonts.ready`.

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
