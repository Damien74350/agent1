"""Monthly client PDF report generator — premium tier touch.

Generates a beautiful branded PDF summarizing the past month : weight evolution,
photos, macros, sport progress, mental state, milestones, next steps.

Saved to /tmp/calo_reports/{token}.pdf, served via FastAPI /report/{token} endpoint.
"""

from __future__ import annotations

import io
import os
import secrets
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


REPORT_DIR = Path(os.environ.get("CALO_REPORT_DIR", "/tmp/calo_reports"))
REPORT_DIR.mkdir(parents=True, exist_ok=True)

# Brand
BRAND_PRIMARY = colors.HexColor("#1F4E79")
BRAND_ACCENT = colors.HexColor("#E07B00")
BRAND_SUCCESS = colors.HexColor("#3FA34D")
BRAND_DANGER = colors.HexColor("#D9534F")
BRAND_BG = colors.HexColor("#FAFAFA")
BRAND_TEXT = colors.HexColor("#222222")
BRAND_MUTED = colors.HexColor("#666666")


def _styles():
    s = getSampleStyleSheet()
    s.add(ParagraphStyle(
        name="CaloH1",
        parent=s["Heading1"],
        fontSize=24,
        textColor=BRAND_PRIMARY,
        spaceAfter=12,
        alignment=TA_LEFT,
    ))
    s.add(ParagraphStyle(
        name="CaloH2",
        parent=s["Heading2"],
        fontSize=16,
        textColor=BRAND_PRIMARY,
        spaceAfter=8,
        spaceBefore=16,
    ))
    s.add(ParagraphStyle(
        name="CaloH3",
        parent=s["Heading3"],
        fontSize=12,
        textColor=BRAND_ACCENT,
        spaceAfter=4,
    ))
    s.add(ParagraphStyle(
        name="CaloBody",
        parent=s["BodyText"],
        fontSize=10,
        textColor=BRAND_TEXT,
        spaceAfter=6,
        leading=14,
    ))
    s.add(ParagraphStyle(
        name="CaloMuted",
        parent=s["BodyText"],
        fontSize=8,
        textColor=BRAND_MUTED,
    ))
    s.add(ParagraphStyle(
        name="CaloBig",
        parent=s["BodyText"],
        fontSize=28,
        textColor=BRAND_PRIMARY,
        alignment=TA_CENTER,
    ))
    s.add(ParagraphStyle(
        name="CaloAccent",
        parent=s["BodyText"],
        fontSize=14,
        textColor=BRAND_ACCENT,
        alignment=TA_CENTER,
    ))
    return s


def _weight_chart_image(weights: list[dict[str, Any]], target_kg: float | None) -> bytes:
    """Generate a PNG bytes for the weight chart, to embed in PDF."""
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
        return b""
    dates = [p[0] for p in parsed]
    values = [p[1] for p in parsed]
    fig, ax = plt.subplots(figsize=(7, 3))
    fig.patch.set_facecolor("#FAFAFA")
    ax.set_facecolor("#FAFAFA")
    ax.plot(dates, values, color="#1F4E79", marker="o", markersize=5, linewidth=2.2)
    ax.fill_between(dates, values, min(values) - 1, alpha=0.1, color="#1F4E79")
    if target_kg and target_kg > 0:
        ax.axhline(target_kg, linestyle="--", color="#E07B00", linewidth=1.5, alpha=0.8)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m"))
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(True, alpha=0.2)
    ax.set_ylabel("Poids (kg)", color="#222222", fontsize=9)
    ax.tick_params(colors="#222222", labelsize=8)
    fig.autofmt_xdate(rotation=30)
    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=120)
    plt.close(fig)
    return buf.getvalue()


def generate_monthly_report(
    user: dict[str, Any],
    weights: list[dict[str, Any]],
    meals: list[dict[str, Any]],
    workout_logs: list[dict[str, Any]],
    memories: list[dict[str, Any]],
    body_photos: list[dict[str, Any]],
    month_label: str = "",
) -> tuple[str, Path]:
    """Generate a beautiful PDF report. Returns (token, file_path)."""
    token = secrets.token_urlsafe(16)
    path = REPORT_DIR / f"{token}.pdf"

    doc = SimpleDocTemplate(
        str(path),
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
        title=f"Calo Report — {user.get('name', '')}",
        author="Calo",
    )
    styles = _styles()
    story = []

    # --- Cover ---
    story.append(Paragraph(f"Calo Report", styles["CaloH1"]))
    story.append(Paragraph(month_label or datetime.now().strftime("%B %Y"),
                           styles["CaloH3"]))
    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph(f"<b>{user.get('name') or 'Client'}</b>",
                           styles["CaloH2"]))
    story.append(Paragraph(
        f"{user.get('sex')} · {user.get('age')} ans · {user.get('height_cm')} cm · "
        f"Objectif : {user.get('goal') or '?'}",
        styles["CaloMuted"]
    ))
    story.append(Spacer(1, 1 * cm))

    # --- Headline metrics ---
    story.append(Paragraph("Le mois en chiffres", styles["CaloH2"]))
    current = float(user.get("current_weight_kg") or 0)
    target = float(user.get("target_weight_kg") or 0)
    weight_change = 0.0
    if len(weights) >= 2:
        try:
            sorted_w = sorted(weights, key=lambda w: w.get("logged_at") or "")
            weight_change = float(sorted_w[-1].get("weight_kg") or 0) - float(sorted_w[0].get("weight_kg") or 0)
        except (ValueError, TypeError):
            pass

    sign = "+" if weight_change > 0 else ""
    metrics_data = [
        [f"{current} kg", "Poids actuel"],
        [f"{sign}{weight_change:.1f} kg", "Évolution mois"],
        [f"{len(meals)}", "Repas loggués"],
        [f"{len(workout_logs)}", "Séances sport"],
        [f"{len(body_photos)}", "Photos morpho"],
    ]
    t = Table(metrics_data, colWidths=[3.5 * cm, 6.5 * cm])
    t.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (0, -1), 18),
        ("FONTSIZE", (1, 0), (1, -1), 10),
        ("TEXTCOLOR", (0, 0), (0, -1), BRAND_PRIMARY),
        ("TEXTCOLOR", (1, 0), (1, -1), BRAND_MUTED),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.5 * cm))

    # --- Weight chart ---
    chart_bytes = _weight_chart_image(weights, target)
    if chart_bytes:
        story.append(Paragraph("Trajectoire poids", styles["CaloH2"]))
        story.append(Image(io.BytesIO(chart_bytes), width=16 * cm, height=6.5 * cm))
        story.append(Spacer(1, 0.5 * cm))

    # --- Macros average ---
    if meals:
        avg_kcal = sum(int(m.get("total_calories") or 0) for m in meals) // max(1, len(meals))
        avg_p = sum(int(m.get("total_protein_g") or 0) for m in meals) // max(1, len(meals))
        avg_c = sum(int(m.get("total_carbs_g") or 0) for m in meals) // max(1, len(meals))
        avg_f = sum(int(m.get("total_fat_g") or 0) for m in meals) // max(1, len(meals))
        target_kcal = user.get("daily_calories") or 0
        target_p = user.get("daily_protein_g") or 0

        story.append(Paragraph("Macros moyennes par repas", styles["CaloH2"]))
        macro_data = [
            ["", "Moyenne réelle", "Cible quotidienne"],
            ["Calories (par repas)", f"{avg_kcal} kcal", f"{target_kcal} kcal/jour"],
            ["Protéines", f"{avg_p}g", f"{target_p}g/jour"],
            ["Glucides", f"{avg_c}g", "—"],
            ["Lipides", f"{avg_f}g", "—"],
        ]
        macro_t = Table(macro_data, colWidths=[5 * cm, 5 * cm, 5 * cm])
        macro_t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), BRAND_PRIMARY),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 10),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
            ("BACKGROUND", (0, 1), (-1, -1), BRAND_BG),
            ("GRID", (0, 0), (-1, -1), 0.5, BRAND_MUTED),
            ("FONTSIZE", (0, 1), (-1, -1), 10),
            ("ALIGN", (1, 1), (-1, -1), "CENTER"),
        ]))
        story.append(macro_t)
        story.append(Spacer(1, 0.5 * cm))

    # --- Sport ---
    if workout_logs:
        prs = sum(1 for l in workout_logs if l.get("pr_hit"))
        story.append(Paragraph("Sport", styles["CaloH2"]))
        story.append(Paragraph(
            f"<b>{len(workout_logs)} séances</b> réalisées ce mois, dont "
            f"<b><font color='#E07B00'>{prs} records personnels (PRs)</font></b>.",
            styles["CaloBody"]
        ))
        if user.get("active_program"):
            story.append(Paragraph(
                f"Programme actif : <b>{user.get('active_program')}</b>",
                styles["CaloBody"]
            ))
        story.append(Spacer(1, 0.3 * cm))

    # --- Lifestyle ---
    sleep = user.get("sleep_quality") or 0
    stress = user.get("stress_level") or 0
    if sleep or stress:
        story.append(Paragraph("Lifestyle", styles["CaloH2"]))
        if sleep:
            story.append(Paragraph(
                f"<b>Sommeil :</b> {sleep}/5 " + ("★" * int(sleep)),
                styles["CaloBody"]
            ))
        if stress:
            story.append(Paragraph(
                f"<b>Stress :</b> {stress}/5 " + ("⚡" * int(stress)),
                styles["CaloBody"]
            ))
        story.append(Spacer(1, 0.3 * cm))

    # --- Key memories ---
    if memories:
        story.append(Paragraph("Moments clés du mois", styles["CaloH2"]))
        for m in memories[:5]:
            mem = (m.get("memory") or "")[:300]
            importance = int(m.get("importance") or 3)
            stars = "★" * importance
            story.append(Paragraph(
                f"<b><font color='#E07B00'>{stars}</font></b> {mem}",
                styles["CaloBody"]
            ))
        story.append(Spacer(1, 0.3 * cm))

    # --- Patterns ---
    if user.get("personal_patterns"):
        story.append(Paragraph("Tes patterns personnels observés", styles["CaloH2"]))
        story.append(Paragraph(user.get("personal_patterns")[:600], styles["CaloBody"]))
        story.append(Spacer(1, 0.3 * cm))

    # --- Next month action plan ---
    story.append(PageBreak())
    story.append(Paragraph("Plan pour le mois prochain", styles["CaloH2"]))
    story.append(Paragraph(
        "Sur la base des observations de ce mois, voici tes 3 priorités :",
        styles["CaloBody"]
    ))
    # Generic placeholder actions — in production these come from Calo intelligence
    actions = _generate_action_plan(user, weight_change, len(workout_logs), len(meals), sleep, stress)
    for i, action in enumerate(actions, 1):
        story.append(Paragraph(
            f"<b><font color='#1F4E79'>{i}.</font></b> {action}",
            styles["CaloBody"]
        ))
    story.append(Spacer(1, 0.5 * cm))

    # --- Footer ---
    story.append(Spacer(1, 1 * cm))
    story.append(Paragraph(
        f"Report généré par Calo le {datetime.now().strftime('%d/%m/%Y')}. "
        f"Garde-le précieusement, partage-le avec ton médecin si tu veux. "
        f"Ton coach IA + ta volonté = ta transformation.",
        styles["CaloMuted"]
    ))

    doc.build(story)
    return token, path


def _generate_action_plan(
    user: dict[str, Any],
    weight_change: float,
    workouts: int,
    meals: int,
    sleep: int,
    stress: int,
) -> list[str]:
    """Generate 3 priority actions based on the user's state."""
    actions = []
    goal = user.get("goal", "")
    if goal == "lose" and weight_change >= 0:
        actions.append(
            "<b>Ré-calibrer le déficit calorique</b> — Ton poids n'a pas baissé ce mois. "
            "Vérifions ensemble les apports réels (souvent +30% sous-déclaration) "
            "avant d'ajuster les calories."
        )
    elif goal == "lose" and weight_change < -2:
        actions.append(
            "<b>Continue exactement comme ça</b> — Trajectoire idéale. "
            "Pas de changement nécessaire, just la constance."
        )
    if workouts < 8:
        actions.append(
            "<b>Augmenter la fréquence sport</b> — 8 séances/mois minimum pour "
            "préserver la masse musculaire pendant la transformation."
        )
    if sleep and sleep <= 2:
        actions.append(
            "<b>Priorité absolue : sommeil</b> — Ton sommeil noté ≤ 2/5 sabote "
            "tout le reste. Magnésium bisglycinate 300mg, stop écrans 60 min avant, "
            "chambre 18°C."
        )
    if stress and stress >= 4:
        actions.append(
            "<b>Gestion du stress</b> — Cortisol élevé chronique = plateau garanti. "
            "Cohérence cardiaque 5 min × 3/jour + marche nature 30 min."
        )
    if meals < 60:
        actions.append(
            "<b>Logger plus régulièrement les repas</b> — Plus tu logges, plus "
            "je peux ajuster. 2 repas/jour minimum loggués."
        )
    # Always add a positive forward action
    actions.append(
        "<b>Continuer à explorer</b> — Ce mois, tente une nouveauté : un nouveau plat, "
        "un nouveau type de séance, une méditation. La variété est l'alliée de la durabilité."
    )
    return actions[:3]
