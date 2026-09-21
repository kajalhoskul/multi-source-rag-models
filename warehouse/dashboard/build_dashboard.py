"""Builds a single self-contained HTML analytics dashboard by querying the
dbt marts directly out of the DuckDB warehouse file.

Usage:
    python build_dashboard.py
"""
import os

import duckdb
import plotly.graph_objects as go
from plotly.offline import plot

BASE_DIR = os.path.join(os.path.dirname(__file__), "..")
DB_PATH = os.path.join(BASE_DIR, "warehouse.duckdb")
OUT_PATH = os.path.join(os.path.dirname(__file__), "dashboard.html")

# Colors from the validated reference palette (references/palette.md):
# fixed categorical order, sequential blue ramp for magnitude/heatmaps.
INK_PRIMARY = "#0b0b0b"
INK_SECONDARY = "#52514e"
INK_MUTED = "#898781"
GRIDLINE = "#e1e0d9"
SURFACE = "#fcfcfb"
CATEGORICAL = ["#2a78d6", "#eb6834", "#1baf7a"]  # blue, orange, aqua
SEQUENTIAL_BLUE = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#1c5cab", "#0d366b"]

BASE_LAYOUT = dict(
    paper_bgcolor=SURFACE,
    plot_bgcolor=SURFACE,
    font=dict(family="system-ui, -apple-system, Segoe UI, sans-serif", color=INK_PRIMARY, size=13),
    margin=dict(l=60, r=30, t=60, b=50),
    hoverlabel=dict(bgcolor="white", font_size=12),
)
AXIS_STYLE = dict(
    gridcolor=GRIDLINE,
    zerolinecolor=GRIDLINE,
    linecolor=INK_MUTED,
    tickfont=dict(color=INK_SECONDARY),
)


def fig_total_revenue_trend(con):
    rows = con.execute("""
        select year_month, sum(net_revenue) as revenue
        from main_analytics.mart_monthly_revenue
        group by 1 order by 1
    """).fetchall()
    months = [r[0] for r in rows]
    revenue = [r[1] for r in rows]

    fig = go.Figure(go.Scatter(
        x=months, y=revenue, mode="lines+markers",
        line=dict(color=CATEGORICAL[0], width=2, shape="spline", smoothing=0.3),
        marker=dict(size=7, color=CATEGORICAL[0]),
        hovertemplate="%{x}<br>$%{y:,.0f}<extra></extra>",
    ))
    fig.update_layout(
        **BASE_LAYOUT,
        title="Total Net Revenue by Month",
        xaxis=dict(title=None, **AXIS_STYLE),
        yaxis=dict(title="Net revenue ($)", tickprefix="$", separatethousands=True, **AXIS_STYLE),
        showlegend=False,
        height=380,
    )
    return fig


def fig_revenue_by_channel(con):
    rows = con.execute("""
        select year_month, channel, net_revenue
        from main_analytics.mart_monthly_revenue
        order by channel, year_month
    """).fetchall()

    by_channel = {}
    for month, channel, revenue in rows:
        by_channel.setdefault(channel, {"x": [], "y": []})
        by_channel[channel]["x"].append(month)
        by_channel[channel]["y"].append(revenue)

    fig = go.Figure()
    for i, (channel, series) in enumerate(sorted(by_channel.items())):
        color = CATEGORICAL[i % len(CATEGORICAL)]
        fig.add_trace(go.Scatter(
            x=series["x"], y=series["y"], mode="lines+markers", name=channel,
            line=dict(color=color, width=2),
            marker=dict(size=6, color=color),
            hovertemplate="%{x}<br>" + channel + ": $%{y:,.0f}<extra></extra>",
        ))
    fig.update_layout(
        **BASE_LAYOUT,
        title="Net Revenue by Channel",
        xaxis=dict(title=None, **AXIS_STYLE),
        yaxis=dict(title="Net revenue ($)", tickprefix="$", separatethousands=True, **AXIS_STYLE),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        hovermode="x unified",
        height=380,
    )
    return fig


def fig_rfm_segments(con):
    rows = con.execute("""
        select rfm_segment, count(*) as customers
        from main_analytics.mart_rfm_segments
        group by 1 order by 2 desc
    """).fetchall()
    segments = [r[0] for r in rows]
    counts = [r[1] for r in rows]

    fig = go.Figure(go.Bar(
        x=segments, y=counts,
        marker=dict(color=CATEGORICAL[0]),
        text=counts, textposition="outside",
        hovertemplate="%{x}: %{y} customers<extra></extra>",
    ))
    fig.update_layout(
        **BASE_LAYOUT,
        title="Customers by RFM Segment",
        xaxis=dict(title=None, **AXIS_STYLE),
        yaxis=dict(title="Customers", **AXIS_STYLE),
        showlegend=False,
        height=400,
    )
    return fig


def fig_cohort_retention(con):
    rows = con.execute("""
        select cohort_month, months_since_signup, retention_pct
        from main_analytics.mart_cohort_retention
        where months_since_signup between 0 and 11
        order by cohort_month, months_since_signup
    """).fetchall()

    cohorts = sorted({r[0] for r in rows})
    max_month = max(r[1] for r in rows)
    z = [[None] * (max_month + 1) for _ in cohorts]
    cohort_index = {c: i for i, c in enumerate(cohorts)}
    for cohort_month, month_n, pct in rows:
        z[cohort_index[cohort_month]][month_n] = pct

    fig = go.Figure(go.Heatmap(
        z=z,
        x=[f"M{m}" for m in range(max_month + 1)],
        y=cohorts,
        colorscale=[[i / (len(SEQUENTIAL_BLUE) - 1), c] for i, c in enumerate(SEQUENTIAL_BLUE)],
        hovertemplate="Cohort %{y}, %{x}<br>Retention: %{z}%<extra></extra>",
        colorbar=dict(title="Retention %", ticksuffix="%"),
    ))
    fig.update_layout(
        **BASE_LAYOUT,
        title="Monthly Cohort Retention (% of cohort active each month since signup)",
        xaxis=dict(title="Months since signup", **AXIS_STYLE),
        yaxis=dict(title="Signup cohort", autorange="reversed", **AXIS_STYLE),
        height=420,
    )
    return fig


def main():
    con = duckdb.connect(DB_PATH, read_only=True)

    figures = [
        fig_total_revenue_trend(con),
        fig_revenue_by_channel(con),
        fig_rfm_segments(con),
        fig_cohort_retention(con),
    ]
    con.close()

    divs = []
    for i, fig in enumerate(figures):
        # Embed plotly.js inline (on the first figure only) so the dashboard
        # is a single fully offline-viewable file with no CDN dependency.
        divs.append(plot(fig, include_plotlyjs=(i == 0), output_type="div"))

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Retail Analytics Dashboard</title>
<style>
  body {{
    background: #f9f9f7;
    font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
    color: {INK_PRIMARY};
    margin: 0;
    padding: 32px;
  }}
  h1 {{ font-size: 22px; margin-bottom: 4px; }}
  p.subtitle {{ color: {INK_SECONDARY}; margin-top: 0; margin-bottom: 28px; }}
  .card {{
    background: {SURFACE};
    border: 1px solid rgba(11,11,11,0.10);
    border-radius: 8px;
    padding: 12px;
    margin-bottom: 24px;
    max-width: 1000px;
  }}
</style>
</head>
<body>
  <h1>Retail Analytics Dashboard</h1>
  <p class="subtitle">Generated from the retail_warehouse dbt marts (DuckDB).</p>
  <div class="card">{divs[0]}</div>
  <div class="card">{divs[1]}</div>
  <div class="card">{divs[2]}</div>
  <div class="card">{divs[3]}</div>
</body>
</html>
"""

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Wrote dashboard -> {OUT_PATH}")


if __name__ == "__main__":
    main()
