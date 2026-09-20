# Changelog

## 2026-09-20 — v1.14

### Changed — 選項面板排版邏輯重構（用戶要求「深度整理」，全做）
**問題**：16 個選項分 3 個 section，但依賴關係被切斷（「格線樣式」在 Layout、「天草泥字體／點點描紅」在 Content）；全站只有 1 條條件邏輯，其餘選項永遠顯示（即使零作用）；三個選項都叫「style／字體」；grid 用 `auto-fill` 排出參差行。

**改法**：
- **4 個決策軸，順序跟工作流**：📝 Content 內容（練咩）→ 🖍 Guides 格線（點顯示）→ 📐 Layout 版面 → 📄 Page 頁面；`optGuideStyle` 由 Layout 搬入 Guides，同天草泥子選項一組
- **`data-when` 條件顯示機制**：`data-when="guide=caoni|caoni-color"` / `section=letters` → 天草泥字體＋點點描紅只在相關格線模式出現；大小寫／字母去重／每行格數只在 letters 範圍出現（7 個條件節點）
- **控件統一**：「label 左、控件右」一行（checkbox 同樣放右邊，靠 `label for` 仍可 click）；刪掉 inline `style="flex:0 0 auto"` hack
- **Grid 改明確 3 欄**（≤900px 2 欄、≤640px 1 欄）；text 輸入用 `.wide` 佔 2 欄
- **改名去歧義**：`Style 字體` → `Letter style 字體類型`；`Guide style` → `Grid style 格線樣式`；`Print cell size` → `Print cell size 印刷格`（縮短）；`Accent 口音` → `語音口音 Accent`（移到 Page 最尾，因為佢係語音設定）
- **每個 section 加灰字副題**（一句講清決策軸）
- **可及性**：16 個 label 全部加 `for`／關聯到現有 id（回歸測試會驗）
- **新增面板工具列**：🧸 幼稚園 · 🎒 小一 · 🖍 天草泥 三個 preset ＋ ↺ Reset 重設
- **Section 可摺疊**（狀態存 `engOptSections`；預設全開）

### Verify
- 回歸 **58 → 68 項**：+10 項面板測試（4 個決策軸及順序、7 條 data-when 顯示／隱藏、摺疊／展開、preset 生效、重設回預設、16 個 label for 全部指到現有 id）
- 所有選項 id 保持不變（JS、localStorage、測試都靠 id）→ 舊功能 58 項零回歸

## 2026-09-20 — v1.13

### Added
- **天草泥第三隻字體：Playwrite US Modern**（選項 `天草泥字體`）。掃完 Google Fonts **全部 357 個 Handwriting 家族**之後，佢係唯一比 Edu Pre 更貼 1/3 而又用得嘅：三區 **30.7 / 36.5 / 32.8（偏離 1/3 只 6.3）**，Pre 係 8.9、Andika 31.9。（真正最貼嘅係 Hurricane / Pinyon Script / Ingrid Darling 等書法字，偏離 2.0，但唔可能做 copybook。）實測：大楷頂 **0.36–2.35%**、h 頂 0.53%、t 頂 0.65%、身頂 30.74%（貼天空/草線）、g 尾 **99.49%**、零溢出。
- Playwrite 係 cursive 家族 → 當印刷體用要 **`font-feature-settings:'calt' 0`**（唔連筆）。已加 `--caoni-print-feat` CSS var，由字體表嘅 `caltOff` 控制。
- metric 全部**喺 app 內實測反推**（calt 關之後同字檔 bbox 差好遠）：asc 0.9404 · xh 0.5309 · desc 0.4550 · cap 0.9380 · tAsc 0.7353 · k 0.0485。

### Notes
- **PWUSM 有自己一套筆順數據**（`print_pwusm`，52 字母 · `group.py` 報 0 隻唔符目標 · `finalcheck` 全部 100% 覆蓋）。
  ⚠️ 之前寫「canvas 捉唔到 calt 關嘅字形」係**錯嘅假設**：單一個字冇相鄰字母，calt 唔會觸發，所以 canvas 捉到嘅就係 unjoined 字形（實測同 app 渲染差 <1.3%：h 0.9525 vs 0.9404、a 0.52 vs 0.531、g 尾完全一樣）→ 唔使改 DOM 擷取。
- modal 嘅字形亦要 `calt 0`（`strokeFeat()`）—— 否則 SVG text 會用連筆字形，同 unjoined 遮罩唔夾。
- 字體表加 `dataKey`：有自己數據就用自己一套（EduPre → `print_pre`、PWUSM → `print_pwusm`），冇就整套回落 Andika（字形/遮罩一致 > 同工作紙一致）。
- 保留一個已知小問題：word-line（0.75×）情境下小楷升部會凸出頂線約 2–3%（Pre 都一樣，屬 sub-scale hinting 差異）；主要嘅 letters 格（大楷頂 0.02–0.93%）冇事。
- 回歸 **52 → 58 項**（+3 隻字體字級/字體/--cg-base、+2 PWUSM modal 字形/dataKey/calt、+1 print_pwusm 筆數）。

## 2026-09-20 — v1.12

### Fixed
- **Pre 版筆順筆數（背景 pipeline log 揭發）**：`print_pre`（Edu AU VIC WA NT Pre）有 5 隻字嘅教學筆數唔符目標 —— E 3≠4、F 2≠3、Y 2≠3（Andika 版 0 隻唔符，即係我自己新加嘅數據嘅問題）。根因係 `group.py` 嘅拆筆規則：
  - `_sharpest_split()` 只處理 ≥5 點嘅骨架 → 短骨架（3–4 點，例如 F 嘅「頂橫＋長脊」）永遠拆唔到，直接 break；
  - 後備「弧長一半」切點會 `return None`（轉角兩點太近，cos 係噪音）→ E 拆完一次就停。
  修法：短骨架用 ±1 window；後備改成**揀最接近弧長一半、兩邊都 ≥2 點**嘅切點（唔再 return None）；同時守住退化片段（1 點）唔可以交去 `emit.py`（Catmull-Rom 會 IndexError）。重跑後：**E=4、F=3、Y=3**，`group.py` 報 0 隻唔符目標，其他 51 隻 + 全部 cursive 一個都冇動（逐字 diff 過）。
- **目標筆數要跟字形，唔係跟字母**：Edu Pre 嘅大寫 `I` 係**純直筆**（逐行量墨跡闊度：全高 22–24px 等闊，上下 1/3 冇加闊）→ 1 筆才對；`L` 一筆過。Andika 嘅 `I` 有上下橫 → 3 筆。新增 `IDEAL_PRINT_BY_FONT` + `GROUP_FONT=<字體>` 環境變數，唔指定就沿用原表（Andika 數據完全不受影響）。

### Verify
- 回歸 **52/52**（新增 4 項：`print_pre` 52 隻齊、E4/F3/Y3/I1/L1 跟字形、Andika I3/L2 不變、每隻字都有筆劃）。
- `finalcheck.py`：print 52 隻 **100%** 遮罩覆蓋；最差 cursive I 99.81%（1/104 <99.9%）。
- 筆劃總數 print 102 → **105**；`STROKE_WIDTH_EM` 0.30。

## 2026-09-20 — v1.11

### Fixed
- **`fonts/hand.css` 漏咗 Andika `@font-face`**（v1.10 換字體時誤刪，回滾只做咗 index.html）→ 四線格模式一直靜靜用系統 fallback 字體渲染。已補回兩個 weight（400/700）＋ 加註警告。**同時推翻 v1.10 對 Andika 嘅「metric 修正」**：當時量到嘅 0.696 / 0.475 / 0.221 / 0.666 / 0.566 其實係 fallback 嘅數字，真 Andika 係 **0.800 / 0.520 / 0.240 / 0.720 / 0.650**（k 亦由 0.156 返 0.085）—— 即係原本 canvas 掃描冇錯，錯嘅係我以為佢錯。
- 補返字體後實測：caoni + Andika 大楷頂 **1.09%**、h 2.33%、t 0.49%、g 尾 **98.17%**、基線 76.3%（同 v1.9 設計一致）。

### Added
- **Pre 版筆順骨架數據**：`strokes_font.js` 現在有第三組 `print_pre`（52 字母，由 Edu AU VIC WA NT Pre 真實字形重跑 `tools/pipeline.py → group.py → emit.py`）。Show modal 用 `strokeDataKey()` 自動揀：**天草泥 + Pre → `print_pre` + EduPre 字形 + cap ratio 0.92**；四線格 → `print` + Andika + 0.72。之前動畫用 Andika 筆形去遮 Pre 字，字形唔夾。
- 遮罩筆寬 `STROKE_WIDTH_EM` 0.20 → **0.30**：`finalcheck.py` 由 6 隻 <99.9%（最差 cursive I 98.15%）改善到 **print 全部 100%、最差 cursive I 99.81%**。`finalcheck.py` 改為讀 emit 實際寫入嘅筆寬，唔再硬編 0.20（否則驗證同出貨唔一致）。

### Removed
- **清走 26 個未用嘅候選字體／字型源檔**（caveat、kalam、handlee、neucha、patrick_hand、gochi_hand、short_stack、coming_soon、edu 各州變體、eduqld、andika.ttf 等，約 1.8MB）→ `fonts/` 只剩實際引用嘅 5 個：andika-400、edupre-400、edudots-400、playwrite-400、playwrite-700（＋hand.css）。備份喺 `/tmp/engword_fonts_backup/`。

### Notes
- Arial 實測（Linux 上 `Arial` 由 Liberation Sans 代，兩者 metric 兼容）：升部 0.73 · x-height 0.54 · 尾 0.21 · cap 0.69 · t 0.65 → **1.35 : 1 : 0.39 → 三區 20/57/22**，比 Andika（27/50/23）離 1/3 更遠。用同一套填滿格機制係可以做到「大楷貼頂、尾貼底」，但代價係草區佔 57%、原圖要縱向拉 1.7 倍；加上 Arial 係 Monotype 商業字體（公開站自 host 有授權問題）、`l` 同 `I` 幾乎分唔開（維基百科明講），唔適合做 copybook 字體。

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
