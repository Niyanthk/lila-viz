# ARCHITECTURE.md

## What I Built and Why

### Tech Stack

| Component | Choice | Rationale |
|---|---|---|
| App framework | **Streamlit** | Fastest path to a browser-accessible tool for non-data-scientists (Level Designers). No frontend build step, native Python, one command to run. Plotly integration is excellent. |
| Data pipeline | **PyArrow + Pandas** | PyArrow has native Parquet support with zero config, handles the bytes-encoded `event` column cleanly, and Pandas makes filtering/grouping ergonomic for this dataset size (~89K rows). |
| Visualization | **Plotly (go + express)** | Interactive out of the box — Level Designers can hover, zoom, and isolate traces. Supports image overlays (minimap) as a base layer on scatter plots. |
| Heatmaps | **NumPy histogram2d + SciPy gaussian_filter** | 2D histogram gives an accurate density grid; Gaussian smoothing makes the output readable without sharp edges that misrepresent sparse areas. |
| Image handling | **Pillow** | Reliable PNG/JPG loading and resize to consistent 1024×1024 coordinate space. |
| Hosting | **Streamlit Community Cloud** | Free, Git-connected, no DevOps. One-click deploy from GitHub. |

---

## Data Flow

```
player_data/February_XX/*.nakama-0
         │
         ▼
  PyArrow pq.read_table()          ← reads Parquet (no extension, but valid format)
         │
         ▼
  pd.concat() all files            ← ~89K rows, ~1,243 files across 5 days
         │
         ▼
  Decode event bytes → string      ← event column stored as b'Position' etc.
         │
         ▼
  Classify is_bot                  ← numeric user_id = bot, UUID = human
         │
         ▼
  world_to_pixel(x, z, map_id)     ← apply coordinate transform per row (see below)
         │
         ▼
  Streamlit session_state cache    ← @st.cache_data prevents reload on filter change
         │
         ▼
  Sidebar filters (map/date/match/player_type/event)
         │
         ▼
  Plotly figures rendered          ← minimap as layout_image base layer
         │
         ▼
  Browser (shareable URL)
```

---

## Coordinate Mapping — The Tricky Part

The README provides this formula:

```
u = (x - origin_x) / scale
v = (z - origin_z) / scale

pixel_x = u * 1024
pixel_y = (1 - v) * 1024   ← Y is FLIPPED (image origin top-left)
```

**Key insight:** The 3D game engine uses a right-handed coordinate system where Z increases "upward" on the map, but image pixel coordinates increase downward from the top-left. The `(1 - v)` flip is critical — without it, the entire map is mirrored vertically.

**Also:** `y` in the data is *elevation*, not a map axis. For 2D plotting, only `x` and `z` are used.

**Per-map config applied:**

| Map | Scale | Origin X | Origin Z |
|---|---|---|---|
| AmbroseValley | 900 | -370 | -473 |
| GrandRift | 581 | -290 | -290 |
| Lockdown | 1000 | -500 | -500 |

Coordinates are computed at load time using `.apply()` per row and stored as `px`, `py` columns — this avoids recomputing on every render.

---

## Assumptions Made

| Situation | Assumption | Reasoning |
|---|---|---|
| `ts` column values appear to be relative match time (epoch near 1970-01-21) | Treated as milliseconds elapsed within match, not wall-clock time | README states "time elapsed within match" |
| Some files contain very few rows (< 5 events) | Included — likely early-exit players or bots that died quickly | Short journeys are still valid data for death zone analysis |
| `map_id` values exactly match the config keys (case-sensitive) | Assumed consistent — confirmed by sampling files | No normalization applied |
| February 14 is partial | Included in all-dates view but labeled correctly | README notes this explicitly |

---

## Major Tradeoffs

| Decision | What I Considered | What I Chose | Why |
|---|---|---|---|
| Streamlit vs React | React would give more custom control; Streamlit is faster to ship | Streamlit | Assignment is 5 days; React would eat 2 days on boilerplate alone |
| Load all data vs lazy load | Lazy load reduces startup time; all-in-memory enables fast filtering | All in memory with `@st.cache_data` | 89K rows × 10 columns ≈ ~15MB in RAM — trivially small |
| Heatmap: KDE vs histogram | KDE is more statistically correct; histogram is faster and simpler | histogram2d + gaussian_filter | Visually equivalent for Level Designer use; faster to compute |
| Coordinate transform: per-row apply vs vectorized | Vectorized is faster; per-row is readable and maintainable | per-row apply at load time, cached | Speed is irrelevant post-cache; readability helps maintainability |
| Path rendering: all users vs sampled | All users can clutter map; sampling loses data | All users, with low opacity | Level Designers need to see ALL paths to identify under-used zones |
