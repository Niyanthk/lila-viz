# LILA BLACK — Player Journey Visualization Tool

> A web-based tool for Level Designers to explore player behavior across LILA BLACK's 3 maps using 5 days of production telemetry data.

🔗 **Live Demo:** [your-deployed-url.streamlit.app](https://your-app.streamlit.app)

---

## What It Does

| Feature | Description |
|---|---|
| 🗺️ **Player Paths** | Renders human and bot movement paths on the minimap with correct world-to-pixel coordinate mapping |
| 🔥 **Heatmaps** | Overlay kill zones, death zones, loot hotspots, storm death clusters, and traffic density |
| ⏯️ **Match Playback** | Timeline scrubber to watch any individual match unfold event-by-event |
| 📊 **Stats Dashboard** | Event breakdowns, daily volume, kill sources, top player leaderboard |
| 🎛️ **Filters** | Filter by map, date, match, player type (human/bot), and event type |

---

## Tech Stack

| Layer | Choice | Why |
|---|---|---|
| **Frontend + App** | Streamlit | Fastest path to a shareable browser tool; no JS required; excellent Plotly integration |
| **Data Parsing** | PyArrow + Pandas | Native Parquet support, fast columnar reads, handles bytes decoding cleanly |
| **Visualization** | Plotly | Interactive scatter/heatmap/line charts with minimap image overlay support |
| **Image** | Pillow | Minimap PNG/JPG loading and resizing to 1024×1024 |
| **Heatmap smoothing** | SciPy (gaussian_filter) | Makes heatmaps readable without sharp binning artifacts |
| **Hosting** | Streamlit Community Cloud | Free, Git-connected, one-click deploy |

---

## Setup (Local)

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/lila-viz.git
cd lila-viz

# 2. Place the data
# Copy the player_data/ folder (with subfolders February_10 through February_14
# AND the minimaps/ subfolder) into the root of this repo.
# Final structure:
# lila-viz/
# ├── app.py
# ├── requirements.txt
# ├── ARCHITECTURE.md
# ├── INSIGHTS.md
# └── player_data/
#     ├── February_10/ ... February_14/
#     ├── minimaps/
#     └── README.md

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run
streamlit run app.py
```

Open http://localhost:8501 in your browser.

---

## Deployment (Streamlit Community Cloud)

1. Push this repo (with player_data/) to GitHub
2. Go to https://share.streamlit.io
3. Click "New app" → select your repo → set `app.py` as the main file
4. Click Deploy

> ⚠️ If `player_data/` is too large for GitHub (>100MB), use [Git LFS](https://git-lfs.github.com/) or host the data on S3/GCS and modify `load_all_data()` to fetch from remote.

---

## Environment Variables

None required for the base setup. If you move data to cloud storage, add:

```
DATA_BUCKET=s3://your-bucket/player_data
```

And update the `DATA_DIR` path in `app.py`.

---

## Folder Structure

```
lila-viz/
├── app.py              ← Main Streamlit application
├── requirements.txt    ← Python dependencies
├── README.md           ← This file
├── ARCHITECTURE.md     ← System design decisions
├── INSIGHTS.md         ← 3 data insights for Level Designers
└── player_data/        ← Telemetry data (not committed if using LFS)
    ├── February_10/
    ├── February_11/
    ├── February_12/
    ├── February_13/
    ├── February_14/
    ├── minimaps/
    └── README.md
```
