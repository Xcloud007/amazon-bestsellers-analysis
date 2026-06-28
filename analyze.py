"""
Amazon Bestsellers Analysis
----------------------------
Reads bestsellers.csv and generates a self-contained interactive HTML report.
Usage: python analyze.py
       python analyze.py --csv path/to/your_file.csv
"""

import argparse
import json
import os
import sys
import webbrowser
from pathlib import Path

import pandas as pd


# ── CLI ──────────────────────────────────────────────────────────────────────

def parse_args():
    parser = argparse.ArgumentParser(description="Amazon Bestsellers Analysis")
    parser.add_argument(
        "--csv",
        default="bestsellers.csv",
        help="Path to the CSV file (default: bestsellers.csv)",
    )
    parser.add_argument(
        "--out",
        default="report.html",
        help="Output HTML file name (default: report.html)",
    )
    return parser.parse_args()


# ── DATA LOADING & CLEANING ──────────────────────────────────────────────────

def load_data(path: str) -> pd.DataFrame:
    if not Path(path).exists():
        print(f"[ERROR] File not found: {path}")
        sys.exit(1)

    df = pd.read_csv(path)

    # Normalise column names: strip whitespace, title-case
    df.columns = df.columns.str.strip()

    required = {"Name", "Author", "User Rating", "Reviews", "Price", "Year", "Genre"}
    missing = required - set(df.columns)
    if missing:
        print(f"[ERROR] Missing columns in CSV: {missing}")
        sys.exit(1)

    df["User Rating"] = pd.to_numeric(df["User Rating"], errors="coerce")
    df["Reviews"]     = pd.to_numeric(df["Reviews"],     errors="coerce")
    df["Price"]       = pd.to_numeric(df["Price"],       errors="coerce")
    df["Year"]        = pd.to_numeric(df["Year"],        errors="coerce").astype("Int64")
    df = df.dropna(subset=["User Rating", "Reviews", "Price", "Year"])
    return df


# ── ANALYSIS ─────────────────────────────────────────────────────────────────

def run_analysis(df: pd.DataFrame) -> dict:
    # Top 10 by reviews
    top_by_reviews = (
        df.nlargest(10, "Reviews")[["Name", "Author", "Reviews", "User Rating", "Genre"]]
        .reset_index(drop=True)
    )

    # Top 10 by rating (min 1000 reviews to filter noise)
    top_by_rating = (
        df[df["Reviews"] >= 1000]
        .nlargest(10, "User Rating")[["Name", "Author", "User Rating", "Reviews", "Genre"]]
        .reset_index(drop=True)
    )

    # Genre distribution
    genre_counts = df["Genre"].value_counts().reset_index()
    genre_counts.columns = ["Genre", "Count"]

    # Average rating by genre
    avg_rating_genre = (
        df.groupby("Genre")["User Rating"]
        .mean()
        .round(2)
        .reset_index()
        .rename(columns={"User Rating": "Avg Rating"})
    )

    # Books per year
    books_per_year = (
        df.groupby("Year")
        .size()
        .reset_index(name="Count")
        .sort_values("Year")
    )

    # Average price by genre
    avg_price_genre = (
        df.groupby("Genre")["Price"]
        .mean()
        .round(2)
        .reset_index()
        .rename(columns={"Price": "Avg Price ($)"})
    )

    # Most frequent authors
    top_authors = (
        df["Author"]
        .value_counts()
        .head(10)
        .reset_index()
    )
    top_authors.columns = ["Author", "Books"]

    # Rating distribution buckets
    bins   = [0, 3.5, 4.0, 4.5, 4.8, 5.0]
    labels = ["< 3.5", "3.5–4.0", "4.0–4.5", "4.5–4.8", "4.8–5.0"]
    df["Rating Bucket"] = pd.cut(df["User Rating"], bins=bins, labels=labels, right=True)
    rating_dist = (
        df["Rating Bucket"]
        .value_counts()
        .reindex(labels)
        .fillna(0)
        .reset_index()
    )
    rating_dist.columns = ["Rating Range", "Count"]

    # Summary stats
    summary = {
        "total_books"   : int(len(df)),
        "unique_authors": int(df["Author"].nunique()),
        "avg_rating"    : round(float(df["User Rating"].mean()), 2),
        "avg_price"     : round(float(df["Price"].mean()), 2),
        "avg_reviews"   : int(df["Reviews"].mean()),
        "year_range"    : f"{int(df['Year'].min())} – {int(df['Year'].max())}",
        "fiction_count" : int((df["Genre"] == "Fiction").sum()),
        "nonfiction_count": int((df["Genre"] == "Non Fiction").sum()),
    }

    return {
        "summary"          : summary,
        "top_by_reviews"   : top_by_reviews.to_dict(orient="records"),
        "top_by_rating"    : top_by_rating.to_dict(orient="records"),
        "genre_counts"     : genre_counts.to_dict(orient="records"),
        "avg_rating_genre" : avg_rating_genre.to_dict(orient="records"),
        "books_per_year"   : books_per_year.to_dict(orient="records"),
        "avg_price_genre"  : avg_price_genre.to_dict(orient="records"),
        "top_authors"      : top_authors.to_dict(orient="records"),
        "rating_dist"      : rating_dist.to_dict(orient="records"),
    }


# ── HTML REPORT ──────────────────────────────────────────────────────────────

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Amazon Bestsellers Analysis</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
  :root {
    --bg: #0d1117; --surface: #161b22; --surface2: #21262d;
    --border: #30363d; --text: #e6edf3; --muted: #8b949e;
    --purple: #8b5cf6; --violet: #7c3aed; --indigo: #6366f1;
    --blue: #3b82f6; --green: #22c55e; --amber: #f59e0b;
    --radius: 12px;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    background: var(--bg); color: var(--text);
    font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
    font-size: 14px; line-height: 1.6;
  }

  /* ── HEADER ── */
  header {
    background: linear-gradient(135deg, #1a0a2e 0%, #16213e 50%, #0d1117 100%);
    border-bottom: 1px solid var(--border);
    padding: 40px 32px 32px;
    text-align: center;
  }
  header h1 { font-size: 2rem; font-weight: 700; letter-spacing: -0.5px; }
  header h1 span { color: var(--purple); }
  header p  { color: var(--muted); margin-top: 6px; font-size: 0.95rem; }

  /* ── LAYOUT ── */
  main { max-width: 1280px; margin: 0 auto; padding: 32px 24px 64px; }

  section { margin-bottom: 40px; }
  section h2 {
    font-size: 1rem; font-weight: 600; text-transform: uppercase;
    letter-spacing: 0.08em; color: var(--purple);
    margin-bottom: 16px; padding-bottom: 8px;
    border-bottom: 1px solid var(--border);
  }

  /* ── STAT CARDS ── */
  .stat-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
    gap: 16px;
  }
  .stat-card {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: var(--radius); padding: 20px 16px; text-align: center;
    transition: border-color .2s;
  }
  .stat-card:hover { border-color: var(--purple); }
  .stat-card .val  { font-size: 1.8rem; font-weight: 700; color: var(--purple); }
  .stat-card .lbl  { font-size: 0.78rem; color: var(--muted); margin-top: 4px; text-transform: uppercase; letter-spacing: .05em; }

  /* ── CHART GRID ── */
  .chart-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(440px, 1fr));
    gap: 20px;
  }
  .chart-card {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: var(--radius); padding: 24px;
  }
  .chart-card h3 {
    font-size: 0.88rem; font-weight: 600; color: var(--muted);
    text-transform: uppercase; letter-spacing: .06em; margin-bottom: 18px;
  }
  .chart-wrap { position: relative; height: 260px; }

  /* ── TABLE ── */
  .tbl-wrap { overflow-x: auto; border-radius: var(--radius); border: 1px solid var(--border); }
  table { width: 100%; border-collapse: collapse; }
  thead th {
    background: var(--surface2); color: var(--muted);
    font-size: 0.78rem; text-transform: uppercase; letter-spacing: .06em;
    padding: 12px 16px; text-align: left; font-weight: 600;
    border-bottom: 1px solid var(--border);
  }
  tbody tr { border-bottom: 1px solid var(--border); transition: background .15s; }
  tbody tr:last-child { border-bottom: none; }
  tbody tr:hover { background: var(--surface2); }
  tbody td { padding: 12px 16px; color: var(--text); }
  .rank { color: var(--purple); font-weight: 700; }
  .badge {
    display: inline-block; padding: 2px 10px; border-radius: 20px;
    font-size: 0.75rem; font-weight: 600;
  }
  .badge-fiction    { background: #1e1b4b; color: #a5b4fc; }
  .badge-nonfiction { background: #14532d; color: #86efac; }
  .stars { color: var(--amber); }

  /* ── TABS ── */
  .tab-bar { display: flex; gap: 4px; margin-bottom: 20px; }
  .tab-btn {
    padding: 8px 18px; border-radius: 8px; border: 1px solid var(--border);
    background: transparent; color: var(--muted); cursor: pointer;
    font-size: 0.85rem; font-weight: 500; transition: all .2s;
  }
  .tab-btn.active, .tab-btn:hover {
    background: var(--purple); color: #fff; border-color: var(--purple);
  }
  .tab-panel { display: none; }
  .tab-panel.active { display: block; }
</style>
</head>
<body>

<header>
  <h1>Amazon <span>Bestsellers</span> Analysis</h1>
  <p>Interactive data report &nbsp;·&nbsp; Powered by Python + Pandas</p>
</header>

<main>

  <!-- SUMMARY STATS -->
  <section>
    <h2>Overview</h2>
    <div class="stat-grid" id="stat-grid"></div>
  </section>

  <!-- CHARTS -->
  <section>
    <h2>Visual Insights</h2>
    <div class="chart-grid">
      <div class="chart-card">
        <h3>Genre Distribution</h3>
        <div class="chart-wrap"><canvas id="genreChart"></canvas></div>
      </div>
      <div class="chart-card">
        <h3>Books Per Year</h3>
        <div class="chart-wrap"><canvas id="yearChart"></canvas></div>
      </div>
      <div class="chart-card">
        <h3>Rating Distribution</h3>
        <div class="chart-wrap"><canvas id="ratingDistChart"></canvas></div>
      </div>
      <div class="chart-card">
        <h3>Avg Price by Genre</h3>
        <div class="chart-wrap"><canvas id="priceChart"></canvas></div>
      </div>
      <div class="chart-card">
        <h3>Top Authors by Books</h3>
        <div class="chart-wrap"><canvas id="authorChart"></canvas></div>
      </div>
      <div class="chart-card">
        <h3>Avg Rating by Genre</h3>
        <div class="chart-wrap"><canvas id="ratingGenreChart"></canvas></div>
      </div>
    </div>
  </section>

  <!-- TABLES -->
  <section>
    <h2>Rankings</h2>
    <div class="tab-bar">
      <button class="tab-btn active" onclick="switchTab('reviews')">Top by Reviews</button>
      <button class="tab-btn"        onclick="switchTab('rating')">Top by Rating</button>
    </div>

    <div id="tab-reviews" class="tab-panel active">
      <div class="tbl-wrap">
        <table>
          <thead><tr>
            <th>#</th><th>Book</th><th>Author</th>
            <th>Reviews</th><th>Rating</th><th>Genre</th>
          </tr></thead>
          <tbody id="tbody-reviews"></tbody>
        </table>
      </div>
    </div>

    <div id="tab-rating" class="tab-panel">
      <div class="tbl-wrap">
        <table>
          <thead><tr>
            <th>#</th><th>Book</th><th>Author</th>
            <th>Rating</th><th>Reviews</th><th>Genre</th>
          </tr></thead>
          <tbody id="tbody-rating"></tbody>
        </table>
      </div>
    </div>
  </section>

</main>

<script>
const DATA = __DATA_PLACEHOLDER__;

const PURPLE  = '#8b5cf6';
const VIOLET  = '#7c3aed';
const INDIGO  = '#6366f1';
const BLUE    = '#3b82f6';
const GREEN   = '#22c55e';
const AMBER   = '#f59e0b';
const MUTED   = '#8b949e';
const SURFACE = '#161b22';

Chart.defaults.color           = MUTED;
Chart.defaults.borderColor     = '#30363d';
Chart.defaults.font.family     = "'Segoe UI', system-ui, sans-serif";

function gradientH(ctx, c1, c2) {
  const g = ctx.createLinearGradient(0, 0, ctx.canvas.width, 0);
  g.addColorStop(0, c1); g.addColorStop(1, c2);
  return g;
}

// ── Stat Cards ──────────────────────────────────────────────────
const s = DATA.summary;
const stats = [
  { val: s.total_books,          lbl: 'Total Books'    },
  { val: s.unique_authors,       lbl: 'Unique Authors' },
  { val: s.avg_rating,           lbl: 'Avg Rating'     },
  { val: '$' + s.avg_price,      lbl: 'Avg Price'      },
  { val: s.avg_reviews.toLocaleString(), lbl: 'Avg Reviews' },
  { val: s.year_range,           lbl: 'Year Range'     },
  { val: s.fiction_count,        lbl: 'Fiction'        },
  { val: s.nonfiction_count,     lbl: 'Non-Fiction'    },
];
const grid = document.getElementById('stat-grid');
stats.forEach(st => {
  grid.innerHTML += `<div class="stat-card"><div class="val">${st.val}</div><div class="lbl">${st.lbl}</div></div>`;
});

// ── Genre Donut ──────────────────────────────────────────────────
new Chart(document.getElementById('genreChart'), {
  type: 'doughnut',
  data: {
    labels:   DATA.genre_counts.map(d => d.Genre),
    datasets: [{ data: DATA.genre_counts.map(d => d.Count),
      backgroundColor: [PURPLE, INDIGO, BLUE, GREEN],
      borderColor: '#0d1117', borderWidth: 3,
    }],
  },
  options: {
    responsive: true, maintainAspectRatio: false,
    plugins: { legend: { position: 'bottom', labels: { padding: 16, boxWidth: 12 } } },
    cutout: '62%',
  }
});

// ── Books per Year Line ──────────────────────────────────────────
new Chart(document.getElementById('yearChart'), {
  type: 'line',
  data: {
    labels:   DATA.books_per_year.map(d => d.Year),
    datasets: [{
      label: 'Books on List',
      data:  DATA.books_per_year.map(d => d.Count),
      borderColor: PURPLE, backgroundColor: 'rgba(139,92,246,0.15)',
      borderWidth: 2.5, pointRadius: 4, pointBackgroundColor: PURPLE,
      fill: true, tension: 0.35,
    }],
  },
  options: {
    responsive: true, maintainAspectRatio: false,
    plugins: { legend: { display: false } },
    scales: {
      x: { grid: { color: '#21262d' } },
      y: { grid: { color: '#21262d' }, beginAtZero: true, ticks: { stepSize: 1 } },
    },
  }
});

// ── Rating Distribution Bar ──────────────────────────────────────
new Chart(document.getElementById('ratingDistChart'), {
  type: 'bar',
  data: {
    labels:   DATA.rating_dist.map(d => d['Rating Range']),
    datasets: [{
      label: 'Books',
      data:  DATA.rating_dist.map(d => d.Count),
      backgroundColor: [INDIGO, BLUE, PURPLE, VIOLET, AMBER],
      borderRadius: 6, borderSkipped: false,
    }],
  },
  options: {
    responsive: true, maintainAspectRatio: false,
    plugins: { legend: { display: false } },
    scales: {
      x: { grid: { display: false } },
      y: { grid: { color: '#21262d' }, beginAtZero: true, ticks: { stepSize: 1 } },
    },
  }
});

// ── Avg Price by Genre ───────────────────────────────────────────
new Chart(document.getElementById('priceChart'), {
  type: 'bar',
  data: {
    labels:   DATA.avg_price_genre.map(d => d.Genre),
    datasets: [{
      label: 'Avg Price ($)',
      data:  DATA.avg_price_genre.map(d => d['Avg Price ($)']),
      backgroundColor: [GREEN, BLUE], borderRadius: 6, borderSkipped: false,
    }],
  },
  options: {
    responsive: true, maintainAspectRatio: false,
    plugins: { legend: { display: false } },
    scales: {
      x: { grid: { display: false } },
      y: { grid: { color: '#21262d' }, beginAtZero: true,
           ticks: { callback: v => '$' + v } },
    },
  }
});

// ── Top Authors Horizontal Bar ────────────────────────────────────
new Chart(document.getElementById('authorChart'), {
  type: 'bar',
  data: {
    labels:   DATA.top_authors.map(d => d.Author),
    datasets: [{
      label: 'Books',
      data:  DATA.top_authors.map(d => d.Books),
      backgroundColor: PURPLE, borderRadius: 4, borderSkipped: false,
    }],
  },
  options: {
    indexAxis: 'y',
    responsive: true, maintainAspectRatio: false,
    plugins: { legend: { display: false } },
    scales: {
      x: { grid: { color: '#21262d' }, beginAtZero: true, ticks: { stepSize: 1 } },
      y: { grid: { display: false }, ticks: { font: { size: 11 } } },
    },
  }
});

// ── Avg Rating by Genre ───────────────────────────────────────────
new Chart(document.getElementById('ratingGenreChart'), {
  type: 'bar',
  data: {
    labels:   DATA.avg_rating_genre.map(d => d.Genre),
    datasets: [{
      label: 'Avg Rating',
      data:  DATA.avg_rating_genre.map(d => d['Avg Rating']),
      backgroundColor: [AMBER, INDIGO], borderRadius: 6, borderSkipped: false,
    }],
  },
  options: {
    responsive: true, maintainAspectRatio: false,
    plugins: { legend: { display: false } },
    scales: {
      x: { grid: { display: false } },
      y: { grid: { color: '#21262d' }, min: 3.5, max: 5.0 },
    },
  }
});

// ── Tables ────────────────────────────────────────────────────────
function badgeHtml(genre) {
  return genre === 'Fiction'
    ? `<span class="badge badge-fiction">Fiction</span>`
    : `<span class="badge badge-nonfiction">Non Fiction</span>`;
}

DATA.top_by_reviews.forEach((b, i) => {
  document.getElementById('tbody-reviews').innerHTML += `
    <tr>
      <td class="rank">#${i+1}</td>
      <td>${b.Name}</td>
      <td style="color:var(--muted)">${b.Author}</td>
      <td>${Number(b.Reviews).toLocaleString()}</td>
      <td class="stars">★ ${b['User Rating']}</td>
      <td>${badgeHtml(b.Genre)}</td>
    </tr>`;
});

DATA.top_by_rating.forEach((b, i) => {
  document.getElementById('tbody-rating').innerHTML += `
    <tr>
      <td class="rank">#${i+1}</td>
      <td>${b.Name}</td>
      <td style="color:var(--muted)">${b.Author}</td>
      <td class="stars">★ ${b['User Rating']}</td>
      <td>${Number(b.Reviews).toLocaleString()}</td>
      <td>${badgeHtml(b.Genre)}</td>
    </tr>`;
});

// ── Tabs ──────────────────────────────────────────────────────────
function switchTab(name) {
  document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.getElementById('tab-' + name).classList.add('active');
  event.target.classList.add('active');
}
</script>
</body>
</html>
"""


def build_html(data: dict) -> str:
    return HTML_TEMPLATE.replace(
        "__DATA_PLACEHOLDER__", json.dumps(data, default=str)
    )


# ── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    args = parse_args()

    print(f"[1/3] Loading data from '{args.csv}' ...")
    df = load_data(args.csv)
    print(f"      {len(df)} records loaded.")

    print("[2/3] Running analysis ...")
    data = run_analysis(df)
    s    = data["summary"]
    print(f"      Books: {s['total_books']}  |  Authors: {s['unique_authors']}"
          f"  |  Avg Rating: {s['avg_rating']}  |  Avg Price: ${s['avg_price']}")

    print(f"[3/3] Writing report to '{args.out}' ...")
    html = build_html(data)
    out_path = Path(args.out)
    out_path.write_text(html, encoding="utf-8")

    abs_path = out_path.resolve()
    print(f"\n✓  Report ready → {abs_path}")
    print("   Opening in browser ...")
    webbrowser.open(f"file://{abs_path}")


if __name__ == "__main__":
    main()
