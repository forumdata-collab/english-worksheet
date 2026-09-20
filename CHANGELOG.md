# Changelog

## 2026-09-20 — v1.10

### Added
- **天草泥模式可選字體**（選項 `天草泥字體 Caoni font`）：預設 **Edu AU VIC WA NT Pre**（澳洲學校手寫體，OFL），亦可揀返 **Andika**。**四線格（standard）模式一律照舊用 Andika，唔受影響。**
- **三區比例／字級／基線全部由所選字體嘅 metric 自動調節**（用戶要求「系統自行調節」）：每隻字體只需一張 metric 表（升部 / x-height / 尾 / 大楷 / t / k），`caoniGeo()` 就會計出字級、基線、天空/草/泥界線；大楷倍數 = asc/cap、t 倍數 = asc/tAsc 亦係推導出嚟，冇硬編數字。
  - **Pre**：升部 0.9395 · x-height 0.506 · 尾 0.434 · cap 0.930 · t 0.818 → 三區 **32.0 / 36.1 / 31.9**（≈ 原圖 1/3）、字級 0.713 格高、基線 68.0%
  - **Andika**：0.696 / 0.475 / 0.221 / 0.666 / 0.566 → 三區 **24.9 / 50.2 / 24.9**（草區天生闊，就係佢比例問題）
- **點點描紅**（選項 `Dotted tracing`）：天草泥模式 + Pre 時，描紅字改用 **Edu AU VIC WA NT Dots**（同 Pre 同形嘅點點版，CSS 配 EduPre fallback 補標點）；揀 Andika 時選項自動變灰（冇點點孿生兄弟）。

### Changed
- **唔再切片**：v1.9 用 `caoni-sky/grass/mud.jpg` 三條切片；v1.10 改回**一張原圖 + 一個計出嚟嘅 y/height 位移縮放**，令原圖內部嗰兩條線（實測 32.91% / 65.60%）啱啱落喺所選字體嘅天空/草、草/泥界線上（`caoniArtPlacement()`）。少三個檔案，而且換字體唔使再切圖。
- **metric 表重做**：舊表嘅 Andika 數字（0.80 / 0.52 / 0.24 / 0.72 / 0.65）係用 bare canvas 掃描攞到嘅，偏大 7–15%，令三個色帶整體錯位。新表一律**喺 app 內用實際渲染量 inkTop/inkBot ÷ font-size** 得出（連 `k` = 有效基線偏移比都要實測：Andika 0.156、Pre 0.082，唔等於 nominal descent —— 受 line-height 影響）。
- `--cg-*`（字級倍數 / 基線係數 / k）改由 JS 寫 CSS var，色帶同 margin 公式跟住字體走。
- 0.5× 行（句子 / copybook）嘅大楷加返 `--caoni-cap-adj5`（Pre 0.975）補償圓頭 overshoot。

### Verify
- 兩隻字體都達到用戶三準則：**大楷頂 0.10%（Pre）/ 1.29%（Andika）**、h 頂 0.08% / 0.14%、t 頂 0.07% / 0.26%、**g 尾底 99.03% / 99.09%**、小楷身頂貼天空/草界線（31.33% / 24.09%）。
- 回歸套件 **44 項全綠**（新增：兩隻字體各自字級填滿格、字體實際套用、`--cg-base` 有寫入、點點描紅 class 同 EduDots 生效 / Andika 唔生效）。
- 11 個情境（全大寫長句 × md/lg/sm × perRow × 圖案／純色）**零橫向溢出**；大楷頂喺 −0.49% ~ +1.95%。
- 未做：`strokes_font.js`（Show 筆順動畫骨架）仍然係 Andika 版，所以天草泥 + Pre 時筆順動畫嘅字形同工作紙唔一致 —— 要為 Pre 重跑 `tools/` pipeline。

## 2026-09-20 — v1.9

### Changed
- **天草泥模式：字母填滿成格**（用戶：「小楷也是 h、t 頭盡量掂頂，g、y、q、p 等盡量貼底」）。原本色帶用原圖三等分（各 33%），但 Andika 嘅升部只有 x-height 嘅 55%、尾只有 47% —— 即係話無論字級點調，h 頭都停喺 13.8%（離上框 13.8%）、尾停喺 80%（離底 20%）。所以改成**跟字體真實 metric 重排三區**：
  - **print 模板**：字級 **0.942 格高**（成塊字 升部0.80 + 尾0.24 = 1.04em 啱啱填滿，上下各留 1%）· 基線 **76.4%** · 天空 **27.4%** / 草 **49.0%** / 泥 **23.6%**
  - 原圖**切片**成 `caoni-sky/grass/mud.jpg` 三條帶，各自按新界線擺位（天空壓扁 ~0.85×、草拉伸 ~1.45×、泥壓扁 ~0.7× 縱向）
  - **大楷 ×1.10**（實測校正 → cap 頂 ~1%，貼上框）· **小楷 t ×1.218**（t 0.65em → 頭同 h 0.79em 並齊）· 小楷升部（b/d/f/h/k/l）自然頂到 1.6%
  - 實測：大楷頂 **1.0%**（圓形大楷 G/O/C/S −0.03~−1.4%，係字體本身 overshoot）· h 頂 2.35% · t 頂 1.17% · x-height 頂 27.35% · g 尾底 **98.2%**（列印 97.8%）
  - **cursive 完全不變**：Playwrite metric（升部 1.02 / x-height 0.52 / 尾 0.52）本身啱原圖三等分，所以沿用舊界線（31.5 / 65）同舊字級 —— 零回歸風險
- **格線**：天草泥模式下頂線/底線會橫穿字母 → 只畫天空/草、草/泥兩條界線（同色帶界線重叠）。
- 實作：`caoniGeo(st)`（由 metric 表推字級/基線/界線）· `caoniBands()` + `caoniBandTiles()`（逐帶切片平鋪）· `glyphSpansHtml()` 逐隻大楷/t 包 span（CSS 用 `--cg-fs/--cg-mb/--caoni-cap/--caoni-t` 統一算）。margin 公式一律「原本嗰條 margin − 0.085·(放大咗嘅字級 − 原字級)」保住基線（同行基線差 ≤0.3px）。W 喺正方格會縮返入格（1.016em > 格內 0.90em）。

### Notes
- 驗證：回歸套件 **37 項全綠**（新增 perRow × standard/caoni 兩組字級比例斷言）；11 個情境（全大寫長句 × md/lg/sm × perRow × 圖案／純色）**零橫向溢出**；列印版面（`@media print` → `@media all` @794px）無溢出、大楷頂 1.4%（圓形 0.2%）、h 頂 1.6%、g 尾 97.8%。

## 2026-09-20 — v1.8

### Changed
- **天草泥模式：print 大楷改為頂到上外框**（用戶：「大楷高度尚未到貼外框」）。之前大楷同小楷一樣字級，cap-ink 頂離上框 18.5%（浮喺天空色帶中間）。現在 print 大楷放大 **×1.366**（`--caoni-cap`，JS 常數寫入 CSS var），只放大字級**唔推高整隻字** —— 同時用 `margin_cap = margin0 − 0.111·fs₀·(cap−1)` 修正 `margin-bottom`，所以**基線照樣鎖死**（實測同一格／行內大楷 vs 小楷基線差 0.02px，列印 0.7px）。大楷 cap-ink 頂：螢幕 **18.5% → 0.85%**、A4 列印 **0.79%**。
- **只影響 caoni / caoni-color 兩種 print 格線**：小楷唔動（x-height 仍 32%，留喺草區、唔踩上天空）；cursive 唔動（Playwrite cap 本身 1.02em 已經貼頂）；standard / dashed / blank 完全唔受影響。
- 實作：`glyphSpansHtml()` 把每隻大寫字母包成 `span.caoni-cap`（其餘連續字元合成一段）。空格轉 `&nbsp;` —— 實測 flex item 嘅前導空格會被丟棄（`span(" cat")` 少 17px，字會黏埋）。`splitToFitLine()` 嘅量度跟住放大字級（逐字加總），否則大寫長句會爆出格。

### Notes
- 驗證（headless chromium，探針量真基線 + canvas 量 ink）：35 項回歸測試全綠（同改動前一致）；全大寫長句 × md/lg/sm × perRow × 圖案／純色 共 11 個組合**零橫向溢出**；列印版面測試（`@media print` → `@media all` @794px）無溢出、大楷貼框。
- 已知：句子行大楷 cap-ink 頂 ≈2.3%（因為句子行自身基線比格仔低 ~1px，係原有校準，兩者都係貼住框）。

## 2026-09-19 — v1.7

### Changed
- **Footer 改為正式 "Sources & credits 資料來源與聲明" 區塊**（雙語）：Typefaces 字體 / Sky·Grass·Mud 天草泥 / Disclaimer 聲明 三項，取代原本一行 `Fonts: … · Made with ✏️`。標籤欄用 `grid-template-columns: max-content 1fr` + `.wsf-row { display: contents }` 令跨行自動對齊（長標籤如 "Sky·Grass·Mud 天草泥" 唔會推歪內文）。
- **加入天草泥來源**：the three-band visual-cue concept comes from the「天草泥格線印章教材套」teaching set by the occupational therapy team at 協康會 Heep Hong Society.
- **聲明**：unofficial teaching aid, not affiliated with/endorsed by the above organisations; third-party names and materials remain the property of their owners.

## 2026-09-19 — v1.6
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
