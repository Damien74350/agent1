"""Generate WhatsApp-ready PNG charts (weight trajectory, macros, adherence).

Files are written to a temp directory and served via the FastAPI `/chart/{token}`
endpoint. Twilio fetches them via media_url.
"""

from __future__ import annotations

import os
import secrets
from datetime import datetime
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")  # headless backend
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch


CHART_DIR = Path(os.environ.get("CALO_CHART_DIR", "/tmp/calo_charts"))
CHART_DIR.mkdir(parents=True, exist_ok=True)

# Calo brand colors
BRAND_PRIMARY = "#1F4E79"
BRAND_ACCENT = "#E07B00"
BRAND_SUCCESS = "#3FA34D"
BRAND_DANGER = "#D9534F"
BRAND_BG = "#FAFAFA"
BRAND_TEXT = "#222222"


def _new_token() -> str:
    return secrets.token_urlsafe(16)


def _save(fig, name_hint: str) -> tuple[str, Path]:
    token = _new_token()
    path = CHART_DIR / f"{token}.png"
    fig.savefig(path, dpi=130, bbox_inches="tight", facecolor=BRAND_BG)
    plt.close(fig)
    return token, path


def weight_chart(
    user_name: str,
    weights: list[dict[str, Any]],
    target_kg: float | None = None,
) -> tuple[str, Path]:
    """`weights` items expected to have `logged_at` (iso) and `weight_kg`."""
    parsed: list[tuple[datetime, float]] = []
    for w in weights:
        try:
            dt = datetime.fromisoformat((w.get("logged_at") or "").replace("Z", "+00:00"))
            kg = float(w.get("weight_kg") or 0)
            if kg > 0:
                parsed.append((dt, kg))
        except (ValueError, TypeError):
            continue
    parsed.sort(key=lambda p: p[0])
    if not parsed:
        return _placeholder_chart(f"Pas encore de pesée pour {user_name}")

    dates = [p[0] for p in parsed]
    values = [p[1] for p in parsed]

    fig, ax = plt.subplots(figsize=(8, 4.5))
    fig.patch.set_facecolor(BRAND_BG)
    ax.set_facecolor(BRAND_BG)

    ax.plot(dates, values, color=BRAND_PRIMARY, marker="o", markersize=6, linewidth=2.5)
    ax.fill_between(dates, values, min(values) - 1, alpha=0.1, color=BRAND_PRIMARY)

    # Target line
    if target_kg and target_kg > 0:
        ax.axhline(target_kg, linestyle="--", color=BRAND_ACCENT, linewidth=1.8, alpha=0.8)
        ax.text(
            dates[-1], target_kg, f" cible {target_kg} kg",
            color=BRAND_ACCENT, va="center", fontsize=10, fontweight="bold",
        )

    # Latest value annotation
    last_dt, last_kg = parsed[-1]
    delta = values[-1] - values[0]
    sign = "+" if delta > 0 else ""
    color = BRAND_SUCCESS if delta < 0 else (BRAND_DANGER if delta > 0 else BRAND_TEXT)
    ax.annotate(
        f"{last_kg:.1f} kg ({sign}{delta:.1f})",
        xy=(last_dt, last_kg),
        xytext=(10, 12),
        textcoords="offset points",
        fontsize=12,
        fontweight="bold",
        color=color,
    )

    ax.set_title(f"📈 Trajectoire poids — {user_name}", fontsize=14, fontweight="bold",
                 color=BRAND_TEXT, pad=15)
    ax.set_ylabel("Poids (kg)", fontsize=11, color=BRAND_TEXT)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m"))
    ax.tick_params(colors=BRAND_TEXT)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(True, alpha=0.2)
    fig.autofmt_xdate(rotation=30)
    fig.text(0.99, 0.01, "calo", ha="right", color=BRAND_ACCENT, fontsize=10,
             fontweight="bold", alpha=0.7)
    fig.tight_layout()
    return _save(fig, "weight")


def macros_chart(
    user_name: str,
    actual: dict[str, float],
    target: dict[str, float],
) -> tuple[str, Path]:
    """Stacked horizontal bars : actual vs target for kcal/protein/carbs/fat."""
    labels = ["Calories", "Protéines (g)", "Glucides (g)", "Lipides (g)"]
    keys = ["kcal", "protein", "carbs", "fat"]
    actuals = [actual.get(k, 0) for k in keys]
    targets = [target.get(k, 0) for k in keys]

    fig, ax = plt.subplots(figsize=(8, 4.5))
    fig.patch.set_facecolor(BRAND_BG)
    ax.set_facecolor(BRAND_BG)

    y = range(len(labels))
    ax.barh(y, targets, color="#dddddd", height=0.5, label="cible")
    ax.barh(y, actuals, color=BRAND_PRIMARY, height=0.35, label="aujourd'hui")

    for i, (a, t) in enumerate(zip(actuals, targets)):
        pct = round(a / t * 100) if t else 0
        ax.text(max(a, t) * 1.02, i, f"{int(a)}/{int(t)} ({pct}%)",
                va="center", fontsize=10, color=BRAND_TEXT)

    ax.set_yticks(list(y))
    ax.set_yticklabels(labels, fontsize=11, color=BRAND_TEXT)
    ax.set_xlim(0, max(max(actuals), max(targets)) * 1.35)
    ax.invert_yaxis()
    ax.set_title(f"🍽️ Macros du jour — {user_name}", fontsize=14,
                 fontweight="bold", color=BRAND_TEXT, pad=15)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.tick_params(left=False, bottom=False, labelbottom=False)
    fig.text(0.99, 0.01, "calo", ha="right", color=BRAND_ACCENT, fontsize=10,
             fontweight="bold", alpha=0.7)
    fig.tight_layout()
    return _save(fig, "macros")


def adherence_heatmap(
    user_name: str,
    days: list[dict[str, Any]],
) -> tuple[str, Path]:
    """`days` items: {date: 'YYYY-MM-DD', adherence: 0-100, meals_count: int}."""
    if not days:
        return _placeholder_chart("Pas encore de données d'adhérence")
    fig, ax = plt.subplots(figsize=(8, 2.5))
    fig.patch.set_facecolor(BRAND_BG)
    ax.set_facecolor(BRAND_BG)
    values = [d.get("adherence", 0) for d in days]
    dates_lbl = [d.get("date", "")[-2:] for d in days]
    colors = []
    for v in values:
        if v >= 80:
            colors.append(BRAND_SUCCESS)
        elif v >= 50:
            colors.append(BRAND_ACCENT)
        else:
            colors.append(BRAND_DANGER)
    ax.bar(range(len(values)), values, color=colors, width=0.85)
    ax.set_xticks(range(len(values)))
    ax.set_xticklabels(dates_lbl, fontsize=8, color=BRAND_TEXT)
    ax.set_ylim(0, 100)
    ax.set_title(f"✅ Adhérence — {user_name} ({len(days)} jours)",
                 fontsize=14, fontweight="bold", color=BRAND_TEXT, pad=10)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_ylabel("%", color=BRAND_TEXT)
    fig.text(0.99, 0.01, "calo", ha="right", color=BRAND_ACCENT, fontsize=10,
             fontweight="bold", alpha=0.7)
    fig.tight_layout()
    return _save(fig, "adherence")


def workout_volume_chart(
    user_name: str,
    logs: list[dict[str, Any]],
) -> tuple[str, Path]:
    """Bar chart of training sessions per week + cumulative PRs."""
    if not logs:
        return _placeholder_chart("Pas encore de séances loggées")
    # Group by ISO week
    by_week: dict[str, dict[str, Any]] = {}
    for l in logs:
        try:
            dt = datetime.fromisoformat((l.get("date") or "")[:10])
            week = dt.strftime("%Y-W%U")
            d = by_week.setdefault(week, {"count": 0, "prs": 0, "rpe_sum": 0, "rpe_n": 0})
            d["count"] += 1
            if l.get("pr_hit"):
                d["prs"] += 1
            if l.get("rpe"):
                d["rpe_sum"] += int(l["rpe"])
                d["rpe_n"] += 1
        except (ValueError, TypeError):
            continue
    weeks = sorted(by_week.keys())
    counts = [by_week[w]["count"] for w in weeks]
    prs = [by_week[w]["prs"] for w in weeks]
    fig, ax = plt.subplots(figsize=(8, 4))
    fig.patch.set_facecolor(BRAND_BG)
    ax.set_facecolor(BRAND_BG)
    x = range(len(weeks))
    ax.bar(x, counts, color=BRAND_PRIMARY, label="séances", width=0.7)
    if any(prs):
        ax.bar(x, prs, color=BRAND_ACCENT, label="PRs", width=0.4)
    ax.set_xticks(list(x))
    ax.set_xticklabels([w.split("-W")[1] for w in weeks], color=BRAND_TEXT, fontsize=9)
    ax.set_xlabel("Semaine ISO", color=BRAND_TEXT)
    ax.set_title(f"🏋️ Training volume — {user_name}", fontsize=14,
                 fontweight="bold", color=BRAND_TEXT, pad=15)
    ax.legend(loc="upper left", frameon=False, fontsize=10)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.text(0.99, 0.01, "calo", ha="right", color=BRAND_ACCENT, fontsize=10,
             fontweight="bold", alpha=0.7)
    fig.tight_layout()
    return _save(fig, "workout")


def _placeholder_chart(message: str) -> tuple[str, Path]:
    fig, ax = plt.subplots(figsize=(7, 3))
    fig.patch.set_facecolor(BRAND_BG)
    ax.set_facecolor(BRAND_BG)
    ax.text(0.5, 0.5, message, ha="center", va="center",
            fontsize=14, color=BRAND_TEXT, fontweight="bold")
    ax.axis("off")
    return _save(fig, "placeholder")
