# Bridge PBN replay page — Render Web Service

Open the replay page from a public URL, pick a PBN file from a
dropdown in the first tab, and replay it — no upload step needed.
Everything else is unchanged from the replay page: three-tab
view (match summary, single-match replay, same-board comparison),
Par contract line, double-dummy table in
N / S / E / W order, per-card +n / = / −n badges, and the
first-tab DDS service setting.

## 更新已有部署 (update an existing deployment)

**If you already have a Render service from the previous version
of this package, do NOT delete it and do NOT create a new one.**

You only need to replace `index.html` in your GitHub repo and
push. Keep your existing `pbn/` folder exactly as it is —
including any PBN file you renamed there — and do not touch
`server.py`, `Dockerfile`, or `render.yaml` unless you changed
them on purpose. Render auto-redeploys the **same service, with
the same URL**, once it sees the new commit.

If you have **not** created a service yet, ignore this section
and follow **“Deploy to Render (free)”** below, which is the
full first-time setup.

**本次更新 (what is new in this version, vs the previous Render package):**
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
| `pbn/` | PBN files served by the service. Initially one file: `2610273252192026DreamlandCup_full.pbn` (2026 Dreamland Cup, 640 records, 16 matches, 32 teams). |
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
   `{"ready": true}`, and `/api/pbn-list` lists the Dreamland Cup file.
6. Open the service URL itself: the first tab should show the
   PBN dropdown with the Dreamland Cup file already loaded.

If you create the service by hand instead of from the Blueprint,
use the same values: Environment Docker, Plan Free, Health Check
Path `/health`.

## Add a new PBN file later

Just drop a `.pbn` file into the `pbn/` folder and push to GitHub.
Render redeploys, and the file appears automatically in the dropdown
— no page rebuild, no manifest edit, no code change. File names
must be plain file names (no subfolders, no `..`, no spaces needed
but allowed — they are URL-encoded in the list).

To remove a file, delete it from `pbn/` and push again.

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
