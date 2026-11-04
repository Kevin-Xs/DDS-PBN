# Bridge PBN replay page — Render Web Service

Open the replay page from a public URL, pick a PBN file from a
dropdown in the first tab, and replay it — no upload step needed.
Everything else is unchanged from the replay page: four-tab
view (match summary, single-match replay, same-board comparison,
X-IMP ranking),
Par contract line, double-dummy table in
N / S / E / W order, per-card +n / = / −n badges, and the
first-tab DDS service setting.

## 本次更新 2026-11-04 — DreamlandCup_R2 + Par 定约修正 + 比赛列表获胜队红粗 (this version)

- **本包的比赛文件换成 R2**：`pbn/` 里现在只有 `DreamlandCup_R2.pbn` + `DreamlandCup_R2.lin`，`pbn/default.txt` 只有一行 `DreamlandCup_R2.pbn`（仍是单行，不用写两行，LIN 由同名自动推导）。
  R2 PBN：640 条记录，20 副，16 场比赛，32 支队，MD5 `691259118c57e9163bb4bd28c884eb8c`。
  R2 LIN：USEBIO XML，32 支队，MD5 `98a1035d89fa0b6b7dd4d1d8bec9847d`。
  旧的 `DreamlandCup_R1.pbn` / `DreamlandCup_R1.lin` 已从本包 `pbn/` 里删掉（不是删 Render 服务，只是换文件）；如果你仓库里还留着 R1 文件，推本包时一并删掉，否则下拉框里会出现 R1 和 R2 两个文件。
- **Par 定约修正（标准 Par 逻辑）**：Par 定约计算重写——从文件 `DoubleDummyTricks` + 局况出发推演叫牌，牺牲定约一律按加倍后的罚分评估（对手对宕定约在加倍优于放过/再叫时必然加倍），不再出现“某个定约不加倍罚分恰好等于 Par 分数”就被选中的错误。
  本包验证：R2 第 1 副（3♠X 北家，9 墩，NS 530，双方无局，`DoubleDummyTricks` `4953149531846ab847ab`，`OptimumScore` NS -300）Par 行是 **NS -300 · 5♠ N X / 5♠ S X**，不是 5♥。Par 分数仍取文件 `OptimumScore`，没有改动。
- **比赛列表（第一个 tab 的第一个列表，仅此表）**：获胜队（IMP 赢得比对手多的一方）队名**红色粗体**（`winner` 类，只限定在 `table.match-table` 内，平局两队都不加红）；
  IMP 和 VP 两列**不加颜色**（去掉原来 IMP 按胜负染绿/红的逻辑），格式改为空格分开，例如 **92 : 25**、**19.99 : 0.01**。数值、排序、VP 排名、其他 tab 和牌桌均未改动；tab2 的比赛头仍用原来的紧凑格式。
- **VP 排名（R2 有真实 C/O，不再是全 0）**：逻辑与 R1 包相同，但 R2 LIN 里 32 支队**全部**有 `CARRY_FORWARD`，所以 C/O 列显示真实数值，总 VP = C/O + 本轮（本轮 = LIN `TOTAL_SCORE`，C/O = LIN `CARRY_FORWARD`，即 R1 的本轮 VP）。
  本地核对（LIN CF + TOTAL）：老友 18.91 + 20.00 = 38.91 第 1，上海老克勒 19.25 + 18.73 = 37.98 第 2，乔家大院一队 14.01 + 18.63 = 32.64，枫雪桥缘 20.00 + 12.30 = 32.30，A Team 15.11 + 16.52 = 31.63，美加乐 12.30 + 19.99 = 32.29（按总 VP 排序在枫雪桥缘之后、A Team 之前，见页面实际行序）。
  注意：R2 比赛列表里的 VP（例如美加乐对休城十月天 19.99 : 0.01）是本轮 VP，不是总 VP；总 VP 只在 VP 排名里。
- **服务器没有回归**：`server.py` 仍是 R1 包那版（已能 serving 辅助 LIN 文件 `*.lin` / `*.lin.xml`，`/api/pbn-list` 只列 `*.pbn` + 验证过的 `default` / `default_requested`，`/health`、`CORS *`、遍历/`default.txt` 400、不存在 404、从不 serving `server.py`/`Dockerfile`/`render.yaml`）。R2 文件名不需要服务器改动，但已有服务仍需把本包的 `index.html` + `server.py` + `pbn/` 文件 + `default.txt` 一起推上去。
- **每周更新（换文件不用重新打包页面）**：把新一对同名文件（例如 `DreamlandCup_R3.pbn` + `DreamlandCup_R3.lin`）放进 `pbn/`，把 `pbn/default.txt` 改成新的 PBN 文件名，push 即可；页面和服务器不用改。PBN 和 LIN 必须同名（只差扩展名），否则页面按同名找不到 LIN，就会回退到 PBN 计算。

## 本次更新 2026-11-03 — VP排名 + 同名 LIN 自动查找 (this version)

- **VP排名**：第一 tab 比赛列表下方新增 “VP排名” 列表，按总 VP 降序、并列共享名次（1,1,3…）。
  列：排名、队伍、C/O、本轮、总 VP。C/O 列**始终显示**，LIN 里没有 `CARRY_FORWARD` 的队伍（第一轮正常情况）按 **0.00** 计，总 VP = C/O + 本轮，不留空、不显示 —、不警告。
  本轮那一列的表头就是 **“本轮”** 两个字，不带括号和轮次（如不再显示“本轮（第一轮）”）。
- **手动传 LIN 的入口已删除**：页面上不再有“补充 LIN 文件”按钮。VP 排名的 LIN 改为**按 PBN 文件名自动找**：
  载入 PBN 后，页面依次向服务器同一 `/pbn/` 路径请求同名 `.lin`、再同名 `.lin.xml`、再旧命名（去掉 `_full` 加 `_lin.xml`），
  找到第一个能解析出 `PARTICIPANTS` 的就用它的 `TOTAL_SCORE`（本轮）和 `CARRY_FORWARD`（C/O）；
  找不到任何一个就回退到 PBN 自己按 IMP→WBF 换算的 VP、C/O 0.00，并只注明“未找到同名 LIN 文件，VP 按 PBN 计算”。
  本包的例子：`DreamlandCup_R1.pbn` → `DreamlandCup_R1.lin`（内容是 USEBIO XML，扩展名是 `.lin`）。
- **`default.txt` 仍是单行 PBN，不用写两行**：`pbn/default.txt` 只有一行 `DreamlandCup_R1.pbn`。
  LIN 不用列在 `default.txt` 里，也不用出现在下拉框里——它由 PBN 同名自动推导。
- **服务器改动（已有服务必须同时推 `index.html` + `server.py` + `pbn/` 文件 + `default.txt`）**：
  `/api/pbn-list` 仍只列 `*.pbn`（按文件名排序，含 `default` / `default_requested`）；
  `/pbn/<name>` 现在除了 `*.pbn`，还可 serving 辅助 LIN 文件 `*.lin` / `*.lin.xml`（仅作 VP 排名补充，**不列入下拉框**）；
  遍历、分隔符、绝对路径、隐藏文件仍拒绝，`default.txt` 本身请求 `/pbn/default.txt` 仍是 400，不存在的文件是 404。
  `server.py` / `Dockerfile` / `render.yaml` / `.dockerignore` 仍不对外 serving。
- **本周 / 每周更新（换文件不用重新打包页面）**：把新一对同名文件（例如 `DreamlandCup_R2.pbn` + `DreamlandCup_R2.lin`）
  放进 `pbn/`，把 `pbn/default.txt` 改成新的 PBN 文件名，push 即可；页面和服务器不用改。
  旧文件不用时从 `pbn/` 里删掉再 push，否则它仍会出现在下拉框里。
  注意：PBN 和 LIN 必须**同名**（只差扩展名），否则页面按同名找不到 LIN，就会回退到 PBN 计算。
- 本包的 PBN 已是修正版：`DreamlandCup_R1.pbn`（640 条记录，16 场比赛，32 支队，第 2 副 Table 15 的东家已由 `???` 修正为 Xinshan Zhao，
  MD5 见下文），不再是旧的 `2610273252192026DreamlandCup_full.pbn`。LIN 是 `DreamlandCup_R1.lin`（32 支队，无 `CARRY_FORWARD`，
  所以 VP 排名 C/O 全是 0.00，总 VP = 本轮 `TOTAL_SCORE`：友为先 / 枫雪桥缘 20.00 并列第 1，下一名是第 3）。

## 更新已有部署 (update an existing deployment)

**If you already have a Render service from the previous version
of this package, do NOT delete it and do NOT create a new one.**

**⚠️ This update is different from the usual one: replacing
`index.html` alone is NOT enough this time.** This version changes
`server.py` (it must now serve `*.lin` / `*.lin.xml` as supplementary
files) and replaces the `pbn/` contents with the new same-stem pair.
So for an existing service, push together: `index.html` **and**
`server.py` **and** the new `pbn/` files (`DreamlandCup_R2.pbn`,
`DreamlandCup_R2.lin`, `pbn/default.txt`), and remove the old
`DreamlandCup_R1.pbn` / `DreamlandCup_R1.lin` from `pbn/` if they are
still there. The page alone will not break on an old server — it falls
back to the first file — but auto-LIN lookup will 404 on the old
server (it rejects `.lin`), so VP ranking will fall back to PBN VP. The page alone will not
break on an old server — it falls back to the first file — but
the marker will not work until `server.py` is updated.
Render auto-redeploys the **same service, with the same URL**,
once it sees the new commit.

For later updates that do not touch `server.py`, the old rule
applies again: replace only `index.html` and push, keeping
your existing `pbn/` folder exactly as it is — including any
PBN file you renamed there — and do not touch `server.py`,
`Dockerfile`, or `render.yaml` unless you changed them on
purpose.

Do NOT delete the separate DDS service `https://dds-jt98.onrender.com` — it is a different service from this page service, and deleting it breaks the per-card badges (the built-in WASM fallback may be incomplete).

If you have **not** created a service yet, ignore this section
and follow **“Deploy to Render (free)”** below, which is the
full first-time setup.

## 默认文件（default.txt）(choose which PBN file opens by default)

When several `.pbn` files sit in `pbn/`, the page no longer
has to open the alphabetically first one. Create (or edit)
`pbn/default.txt` with **one line: the exact PBN filename to
auto-load**, for example:

```
DreamlandCup_R1.pbn
```

How it works and what to remember:

- (a) To set the default, write that one line into
  `pbn/default.txt` and push. The dropdown still lists every
  `.pbn` file in filename order, and the marked file is
  pre-selected and auto-loaded on open; picking another file
  in the dropdown and clicking “载入所选文件” still works as
  before.
- (b) To change the default later, you only need to edit
  `default.txt` and push — **no page rebuild, no `index.html`
  or `server.py` change**. The new default takes effect on the
  next Render deploy.
- (c) Deleting `default.txt` reverts to the old behaviour:
  the first file alphabetically is auto-loaded.
- (d) If the marker names a file that is not in `pbn/`, the
  page warns in the status line (“default.txt 指定的默认文件
  … 未找到”) and loads the first file instead — it never
  shows a blank page.
- (e) For an **existing** deployed service, this update
  requires pushing the new `index.html` **and** the new
  `server.py`, plus adding `pbn/default.txt` — replacing
  `index.html` alone is NOT enough this time, because the
  server must return the `default` field (the page alone
  falls back to the first file if the server is old, so it
  will not break, but the marker will not work until
  `server.py` is updated).
- (f) GitHub web tip: navigate **inside** the `pbn/` folder
  first, then create `default.txt` there. If you create it
  from the repo root, it lands in the repo root and will be
  ignored — the server only reads `pbn/default.txt`.
- Parsing is tolerant: UTF-8 with optional BOM, the first
  non-empty line that does not start with `#`, surrounding
  whitespace stripped, and a missing `.pbn` suffix is added
  for matching (so `b` matches `b.pbn`). `default.txt`
  itself never appears in the dropdown, and
  `/pbn/default.txt` is rejected (400).
- Keep your existing `pbn/*.pbn` files. Do NOT delete or
  recreate the page service, and do NOT delete the separate
  DDS service `https://dds-jt98.onrender.com`.

**本次更新 (what is new in this version, vs the previous Render package):**
- 本次重新打包 (2026-11-01, 针对上一个 zip 被反馈缺少 default.txt): index.html / server.py 内容与上一版相同（index.html 是从最新 artifact 导出重新 transplant 默认感知选择器，server.py 未变），但 zip 改为真实文件而非符号链接，解压后 pbn/default.txt 一定存在（内容为 2610273252192026DreamlandCup_full.pbn）；已有服务仍按上文三件套（index.html + server.py + pbn/default.txt）推送。
- 本次更新 (2026-11-01, vs 上一版 Render 包): 新增默认文件标记 `pbn/default.txt`: 第一 tab 的下拉仍按文件名顺序列出所有 `.pbn` 文件, 但打开页面时自动载入 `default.txt` 里指定的那一个 (预选中并载入); 改默认以后只需改 `default.txt` 并 push, 不用改页面; 删掉 `default.txt` 就回到按文件名第一个自动载入; 标记指向不存在的文件时页面提示并回退到第一个文件。注意: 已有服务这次必须同时推新 `index.html` 和新 `server.py` 并加上 `pbn/default.txt`, 只换 `index.html` 不够 (旧服务器没有 `default` 字段时页面会回退到第一个文件, 不会坏, 但标记不起作用)。
- 本次更新 (2026-11-01, vs 上一版 Render 包): 新增第四个 tab “X-IMP排名” (排在 “同牌比较” 之后): 覆盖当前载入的整个 PBN 文件的全部牌、全部桌, 复用 “同牌比较” 的 X-IMP 口径 (Score 标签取 NS 原始分, EW x 记负, 不用 ScoreIMP; 每桌 X-IMP = 与其他有得分桌的分差按标准 IMP 表换算求和 ÷ (桌数 − 1), 坐 EW 的一对取相反数; 单桌 / 无得分副不计入), Pair 按无序两人组合合并 (名字去 # 后缀, 坐 NS / EW 都算同一对), 每对的平均 X-IMP = X-IMP 总和 ÷ 计入副数, 按平均从高到低排名; 队伍按坐向确定且一致时才显示, 否则留空; 顶部标题行与其他 tab 一样用 PBN 文件名 (去掉 .pbn 后缀), 未载入文件时只提示去第一页上传。
- 本次更新 (2026-11-01, vs v1 Render package): 同牌比较新增 “X-IMP” 列 (Score 列之后): 对同一副牌, 本桌 NS 原始分与每一其他桌得分的差值按标准 IMP 表逐一换算、求和, 再除以 (有得分的桌数 − 1), 显示带正负号的两位小数; 只有一桌或无有效得分时显示 —, 且缺得分的行不参与其他桌的计算; 排序仍按 NS 原始分从高到低。
- 第一 tab 比赛表去掉最后一列 “看牌面”: 表只剩主队 / 客队 / 副数 / IMP / VP 五列, 整行可点击 (回车也可) 进入第二页, 与原来点 “看牌面” 效果相同。
- 第二 tab 比赛头部的 “赛事:” 值改为 PBN 文件名 (去掉 .pbn 后缀, 例如 2610273252192026DreamlandCup_full (1).pbn 显示为 2610273252192026DreamlandCup_full (1)), 不再用 Event 标签的赛事名; “来自文件:” 行保留。
- 第三 tab “同牌比较” 顶部新增一行, 显示与第一 tab 标题相同的 PBN 文件名 (去掉 .pbn 后缀, 含场次计数); 未载入文件时仍只提示去第一页上传, 不显示文件名。
- 以下为此前已包含的 post-v1 内容 (本次仍在内):
- Third tab “同牌比较” (same-board comparison): a board-number row
  (distinct board numbers, ascending, default first board), a table of
  that board's results at all tables sorted by NS raw Score from the
  Score tag (NS x = +x, EW x = −x, ScoreIMP ignored, no IMP-table
  conversion, no datum/average), and clicking a row opens that table's
  own replay below the table.
- Team names split per side in that table: the NS pair shows only the
  NS side's team underneath it, the EW pair shows only the EW side's
  team (Room indicator kept after the EW team); Open NS = Home team /
  EW = Visit team, Closed NS = Visit team / EW = Home team, from
  HomeTeam / VisitTeam and Room. Records with no team tags show no
  team line.
- Tab renames: tab 1 “比赛汇总 选PBN”, tab 2 “单场比赛 打牌过程”,
  tab 3 “同牌比较” (unchanged).
- Still included from v1: first-tab title shows the loaded PBN filename
  without the `.pbn` suffix (for example
  `2610273252192026DreamlandCup_full` instead of “队名列表”),
  falling back to “队名列表” when nothing is loaded. Everything
  else — the PBN selector, Par, DDS settings,
  and badges — is unchanged.

## What is in this folder

| File | What it is |
| --- | --- |
| `index.html` | The replay page (single file, ~1.6 MB). It does **not** embed any PBN: it loads PBNs over HTTP from `/pbn/`, so adding a file later does not require rebuilding this page. |
| `pbn/` | PBN + supplementary LIN files served by the service. This version: `DreamlandCup_R2.pbn` (2026 Dreamland Cup R2, 640 records, 20 boards, 16 matches, 32 teams) + `DreamlandCup_R2.lin` (USEBIO XML, 32 teams, all with CARRY_FORWARD) + `default.txt` (single line: `DreamlandCup_R2.pbn`). Only `*.pbn` appears in the dropdown; `*.lin` is fetched automatically by same stem and never listed. |
| `server.py` | Python standard library only, no third-party packages. Serves `index.html`, `GET /api/pbn-list`, `GET /pbn/<name>`, and `GET /health`. Binds `0.0.0.0:$PORT` (default 10000). |
| `Dockerfile` | Python 3.12 slim, copies the files above, runs `server.py`. |
| `render.yaml` | Render Blueprint: Web Service, Docker, Free plan, health check `/health`. |
| `.dockerignore` | Keeps caches and the zip out of the Docker build. |

## How the file selector works

On page load the first tab's **“Render 上的牌局文件”** dropdown calls
`GET /api/pbn-list` on the same origin. The server lists only `*.pbn`
files directly inside `pbn/` (sorted by filename, hidden files
excluded) and returns each file's name, size, and URL. Because the
page starts with no file loaded, the first file in the list is
auto-loaded once at startup; picking another file in the dropdown
and pressing **“载入所选文件”** fetches it and feeds it into the
page's existing PBN loader, so it **replaces** the current data —
it is never appended to it. Uploading a file or pasting PBN text
still works the same way and also replaces the data.

## Deploy to Render (free)

**Do not upload the zip itself to GitHub.** The zip is only for
downloading this package conveniently. Render needs the individual
files at the repo root.

1. Download and unzip `bridge-pbn-render.zip` (or copy this folder).
2. Create an empty GitHub repo (do not initialise it with a README,
   or delete that README afterwards) — e.g. `bridge-pbn`.
3. Upload **these files at the repo root**, not nested in a
   `bridge-pbn-render/` subfolder, otherwise Render will not find
   `Dockerfile` / `render.yaml` at the root:
   `index.html`, `server.py`, `Dockerfile`, `render.yaml`,
   `.dockerignore`, and the `pbn/` folder with its `.pbn` file(s).
4. In Render: **New → Web Service → pick that repo**. Render
   detects `render.yaml` and pre-fills: Environment Docker,
   Plan Free, Health Check Path `/health`. Create the service.
5. Wait for the first deploy to finish, then open the service URL.
   Check `https://<your-service>.onrender.com/health` returns
   `{"ready": true}`, and `/api/pbn-list` lists `DreamlandCup_R2.pbn` (and only that `.pbn`; the `.lin` is not listed).
6. Open the service URL itself: the first tab should show the
   PBN dropdown with the Dreamland Cup file already loaded.

If you create the service by hand instead of from the Blueprint,
use the same values: Environment Docker, Plan Free, Health Check
Path `/health`.

## Add a new PBN file later (now as a same-stem PBN + LIN pair)

Drop a `.pbn` file **together with its same-stem LIN file** into the `pbn/` folder and push to GitHub.
Example: `DreamlandCup_R2.pbn` + `DreamlandCup_R2.lin` (same stem, only the extension differs).
Render redeploys, and the PBN appears automatically in the dropdown — no page rebuild, no manifest edit, no code change.
The LIN is then found automatically by stem for VP ranking and never appears in the dropdown.
If you also want the new file to open by default, edit `pbn/default.txt` to that new PBN name and push in the same commit.
File names must be plain file names (no subfolders, no `..`, no spaces needed
but allowed — they are URL-encoded in the list).

To remove a file, delete it (and its LIN pair, if any) from `pbn/` and push again.

GitHub web rename warning: the rename field is the **full path** (`pbn/old.pbn`); replacing it with just `new.pbn`
moves the file to the repo root, where the server will not list it. Always keep the `pbn/` prefix when renaming
(e.g. rename to `pbn/new-name.pbn`), then verify the root has no `.pbn` and `/api/pbn-list` lists the file.

## Free-plan sleep — please read this first

A free Render Web Service **sleeps after 15 minutes idle**.
The first open after sleep takes about **a minute to wake up**;
after that it responds normally. This is a free-tier limit, not a
bug in this service. If the page is opened while the service is
still waking, the dropdown may briefly report that the file list
could not be read — wait for the service to wake, then reload the
page. Upload / paste still works even before the list loads.

## DDS badges are a separate service

The per-card badges do **not** come from this service. They use
the DDS service address in the page's first-tab **“DDS 服务设置”**,
which defaults to `https://dds-jt98.onrender.com` (a separate
Render service, also free, so it can also be asleep on first use).
Anyone who receives this page can change that address in the
first tab to their own DDS service; that setting lasts for the
current opening only and is not written into any file.

The built-in WASM fallback in the exported page is unchanged from
the base export: its worker asset (`assets/dds-worker.js`) was
unresolved at export time, so the fallback may be incomplete in
the standalone page, while the DDS-service path is unaffected.

## Run it locally (optional check)

```sh
cd bridge-pbn-render
PORT=18099 python3 server.py
```

Then open `http://127.0.0.1:18099/`, check `/api/pbn-list`,
and check `/health` returns `{"ready": true}`.
