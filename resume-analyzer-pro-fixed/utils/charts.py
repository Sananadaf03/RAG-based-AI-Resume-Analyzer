# ============================================================
# utils/charts.py
# Visualization: Plotly Charts for Analysis Results
# ============================================================

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# ── Brand colors
BG = "rgba(0,0,0,0)"          # Transparent background
ACCENT = "#7c3aed"
SUCCESS = "#22c55e"
WARNING = "#f59e0b"
DANGER = "#ef4444"
INFO = "#3b82f6"
MUTED = "#6b7280"
GRID_COLOR = "rgba(255,255,255,0.08)"
FONT = "DM Sans"


def _base_layout(**kwargs) -> dict:
    return dict(
        paper_bgcolor=BG,
        plot_bgcolor=BG,
        font=dict(family=FONT, color="white"),
        margin=dict(l=20, r=20, t=40, b=20),
        **kwargs,
    )


def score_gauge(ats_score: float) -> go.Figure:
    """
    Animated gauge chart for ATS score.
    """
    if ats_score >= 75:
        color = SUCCESS
        label = "Excellent"
    elif ats_score >= 55:
        color = WARNING
        label = "Good"
    elif ats_score >= 35:
        color = "#f97316"  # orange
        label = "Needs Work"
    else:
        color = DANGER
        label = "Poor"

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=ats_score,
        domain={"x": [0, 1], "y": [0, 1]},
        title={"text": f"ATS Score — <b>{label}</b>", "font": {"size": 16, "color": "white"}},
        delta={"reference": 70, "increasing": {"color": SUCCESS}, "decreasing": {"color": DANGER}},
        gauge={
            "axis": {
                "range": [0, 100],
                "tickwidth": 1,
                "tickcolor": "rgba(255,255,255,0.3)",
                "tickfont": {"color": "white", "size": 10},
            },
            "bar": {"color": color, "thickness": 0.25},
            "bgcolor": "rgba(255,255,255,0.05)",
            "borderwidth": 0,
            "steps": [
                {"range": [0, 35], "color": "rgba(239,68,68,0.15)"},
                {"range": [35, 55], "color": "rgba(249,115,22,0.15)"},
                {"range": [55, 75], "color": "rgba(245,158,11,0.15)"},
                {"range": [75, 100], "color": "rgba(34,197,94,0.15)"},
            ],
            "threshold": {
                "line": {"color": "white", "width": 2},
                "thickness": 0.75,
                "value": 70,
            },
        },
        number={"suffix": "%", "font": {"size": 40, "color": color}},
    ))
    fig.update_layout(**_base_layout(height=280))
    return fig


def skill_donut(matched: list, missing: list) -> go.Figure:
    """
    Pie chart: matched vs missing skills.
    """
    labels = ["Matched Skills", "Missing Skills"]
    values = [len(matched), len(missing)]
    colors_list = [SUCCESS, DANGER]

    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        marker=dict(colors=colors_list, line=dict(color="rgba(0,0,0,0.3)", width=2)),
        textinfo="label+percent",
        textfont=dict(size=12, color="white"),
        hovertemplate="<b>%{label}</b><br>Count: %{value}<extra></extra>",
    ))

    fig.update_layout(
        **_base_layout(height=300),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.15,
            xanchor="center",
            x=0.5,
            font=dict(color="white"),
        ),
    )
    return fig


def score_breakdown_radar(analysis: dict) -> go.Figure:
    """
    Radar chart showing all scoring dimensions.
    """
    categories = [
        "Semantic\nSimilarity",
        "Skill\nMatch",
        "Keyword\nMatch",
        "Experience",
        "Education",
        "Format\nQuality",
    ]
    values = [
        analysis.get("semantic_similarity", 0),
        analysis.get("skill_match_pct", 0),
        analysis.get("keyword_match_pct", 0),
        analysis.get("experience_score", 0),
        analysis.get("education_score", 0),
        analysis.get("format_score", 0),
    ]
    # Close the polygon
    categories_closed = categories + [categories[0]]
    values_closed = values + [values[0]]

    fig = go.Figure()

    # Fill area
    fig.add_trace(go.Scatterpolar(
        r=values_closed,
        theta=categories_closed,
        fill="toself",
        fillcolor="rgba(124,58,237,0.2)",
        line=dict(color=ACCENT, width=2),
        name="Your Resume",
        marker=dict(size=6, color=ACCENT),
    ))

    # Target line at 80
    fig.add_trace(go.Scatterpolar(
        r=[80] * len(categories_closed),
        theta=categories_closed,
        line=dict(color="rgba(255,255,255,0.3)", width=1, dash="dash"),
        name="Target (80%)",
        mode="lines",
    ))

    fig.update_layout(
        **_base_layout(height=340),
        polar=dict(
            bgcolor="rgba(255,255,255,0.03)",
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                gridcolor=GRID_COLOR,
                tickfont=dict(size=9, color="rgba(255,255,255,0.5)"),
                ticksuffix="%",
            ),
            angularaxis=dict(
                gridcolor=GRID_COLOR,
                tickfont=dict(size=10, color="white"),
            ),
        ),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.15,
            xanchor="center",
            x=0.5,
            font=dict(color="white", size=10),
        ),
    )
    return fig


def skills_by_category_bar(resume_skills: dict, jd_skills: dict) -> go.Figure:
    """
    Grouped bar chart: resume vs JD skills per category.
    """
    categories = sorted(set(list(resume_skills.keys()) + list(jd_skills.keys())))
    resume_counts = [len(resume_skills.get(c, [])) for c in categories]
    jd_counts = [len(jd_skills.get(c, [])) for c in categories]

    cat_labels = [c.replace("_", " ").title() for c in categories]

    fig = go.Figure(data=[
        go.Bar(
            name="Your Resume",
            x=cat_labels,
            y=resume_counts,
            marker_color=ACCENT,
            marker_line_width=0,
        ),
        go.Bar(
            name="Job Description",
            x=cat_labels,
            y=jd_counts,
            marker_color=INFO,
            marker_line_width=0,
        ),
    ])

    fig.update_layout(
        **_base_layout(height=320),
        barmode="group",
        xaxis=dict(
            gridcolor=GRID_COLOR,
            tickfont=dict(size=9, color="rgba(255,255,255,0.7)"),
        ),
        yaxis=dict(
            gridcolor=GRID_COLOR,
            tickfont=dict(size=9, color="rgba(255,255,255,0.7)"),
            title="Skill Count",
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(color="white", size=10),
        ),
    )
    return fig


def keyword_gap_hbar(matched_kw: list, missing_kw: list) -> go.Figure:
    """
    Horizontal bar showing keyword presence status.
    """
    top_missing = list(missing_kw)[:12]
    top_matched = list(matched_kw)[:6]

    words = top_matched + top_missing
    status = ["✅ Present"] * len(top_matched) + ["❌ Missing"] * len(top_missing)
    color_map = {"✅ Present": SUCCESS, "❌ Missing": DANGER}
    colors_list = [color_map[s] for s in status]

    fig = go.Figure(go.Bar(
        x=[1] * len(words),
        y=words,
        orientation="h",
        marker=dict(color=colors_list, line=dict(width=0)),
        text=status,
        textposition="inside",
        insidetextanchor="middle",
        textfont=dict(size=10, color="white"),
        hovertemplate="<b>%{y}</b><br>Status: %{text}<extra></extra>",
    ))

    fig.update_layout(
        **_base_layout(height=max(280, len(words) * 24 + 60)),
        xaxis=dict(visible=False),
        yaxis=dict(
            gridcolor=GRID_COLOR,
            tickfont=dict(size=10, color="white"),
        ),
        showlegend=False,
    )
    return fig
