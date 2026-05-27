"""Calo-specific tools — they all close over (db, user_id, photo_path)
so each request gets its own bound toolset."""

from datetime import datetime, timezone
from typing import Any

from anthropic import beta_tool

from .db import Database
from .nutrition import daily_targets


def build_tools(
    db: Database,
    user_id: int,
    incoming_photo_path: str | None,
):
    """Create the Calo tools bound to the current request context."""

    @beta_tool
    def complete_profile(
        name: str,
        sex: str,
        age: int,
        height_cm: int,
        weight_kg: float,
        activity_level: str,
        goal: str,
        photo_consent: bool,
        target_weight_kg: float | None = None,
        target_date: str | None = None,
        restrictions: str | None = None,
    ) -> str:
        """Save the user's profile and compute daily nutrition targets. Call this \
ONLY when you have collected every required field through conversation.

Args:
    name: User's first name.
    sex: 'M' or 'F'.
    age: Age in years.
    height_cm: Height in centimeters.
    weight_kg: Current weight in kilograms.
    activity_level: One of 'sedentary' | 'light' | 'moderate' | 'intense'.
    goal: One of 'lose' | 'maintain' | 'gain'.
    photo_consent: True if the user agreed to body photo tracking, False otherwise.
    target_weight_kg: Goal weight in kg (None for 'maintain').
    target_date: ISO date 'YYYY-MM-DD' for the target (optional).
    restrictions: Free-text dietary restrictions (vegetarian, halal, allergies...).
"""
        sex_norm = "M" if sex.upper().startswith("M") or sex.lower().startswith("h") else "F"
        targets = daily_targets(
            sex_norm, weight_kg, height_cm, age, activity_level, goal
        )
        db.update_user(
            user_id,
            name=name,
            sex=sex_norm,
            age=age,
            height_cm=height_cm,
            weight_kg=weight_kg,
            activity_level=activity_level,
            goal=goal,
            target_weight_kg=target_weight_kg,
            target_date=target_date,
            restrictions=restrictions,
            photo_consent=1 if photo_consent else 0,
            daily_calories=targets.calories,
            daily_protein_g=targets.protein_g,
            daily_carbs_g=targets.carbs_g,
            daily_fat_g=targets.fat_g,
            onboarding_complete=1,
        )
        return (
            f"Profile saved. Daily targets: {targets.calories} kcal, "
            f"P:{targets.protein_g}g C:{targets.carbs_g}g F:{targets.fat_g}g. "
            f"Photo consent: {photo_consent}."
        )

    @beta_tool
    def log_meal(
        items: list[dict[str, Any]],
        notes: str = "",
    ) -> str:
        """Log a meal the user just ate.

Args:
    items: A list of food items, each a dict with keys:
        name (str), grams (int), kcal (int), protein_g (int), carbs_g (int), fat_g (int).
    notes: Optional free text (e.g. 'au restaurant', 'estimation imprécise').
"""
        meal_id = db.add_meal(user_id, items, incoming_photo_path, notes or None)
        total = sum(int(i.get("kcal", 0)) for i in items)
        return f"Meal #{meal_id} logged. Total: {total} kcal across {len(items)} item(s)."

    @beta_tool
    def log_weight(kg: float) -> str:
        """Log a weight measurement.

Args:
    kg: Weight in kilograms (e.g. 78.4).
"""
        db.add_weight(user_id, kg)
        db.update_user(user_id, weight_kg=kg)
        return f"Weight logged: {kg} kg."

    @beta_tool
    def log_body_photo(analysis: str, week_number: int | None = None) -> str:
        """Save the analysis of a body/morphotype photo. Only call this when the \
user has sent a body photo (not a meal photo) AND they have consented to photo tracking.

Args:
    analysis: Your written observations about the photo (encouraging, factual).
    week_number: Week index in the user's program (1 = first photo, 2 = next week, etc.).
"""
        if not incoming_photo_path:
            return "Error: no photo attached to this turn."
        db.add_body_photo(user_id, incoming_photo_path, week_number, analysis)
        return "Body photo saved."

    @beta_tool
    def get_daily_summary() -> str:
        """Return today's nutrition status: target, consumed so far, and remaining."""
        user = db.get_user_by_id(user_id)
        if not user.get("onboarding_complete"):
            return "User onboarding not complete yet."
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        meals = db.meals_for_day(user_id, today)
        consumed_kcal = sum(m["total_kcal"] for m in meals)
        consumed_protein = sum(m["total_protein_g"] for m in meals)
        consumed_carbs = sum(m["total_carbs_g"] for m in meals)
        consumed_fat = sum(m["total_fat_g"] for m in meals)
        target = user["daily_calories"] or 0
        return (
            f"Today ({today}): {len(meals)} meal(s) logged. "
            f"Consumed: {consumed_kcal}/{target} kcal "
            f"(P:{consumed_protein}/{user['daily_protein_g']}g, "
            f"C:{consumed_carbs}/{user['daily_carbs_g']}g, "
            f"F:{consumed_fat}/{user['daily_fat_g']}g). "
            f"Remaining: {max(0, target - consumed_kcal)} kcal."
        )

    @beta_tool
    def get_weekly_progress() -> str:
        """Return the user's weight trend and meal compliance over the last 7 days."""
        weights = db.weights_history(user_id, limit=10)
        photos = db.body_photos(user_id)
        if not weights:
            return "No weight history yet."
        latest = weights[0]["weight_kg"]
        oldest = weights[-1]["weight_kg"]
        delta = latest - oldest
        photo_count = len(photos)
        return (
            f"Latest weight: {latest} kg. Trend over last {len(weights)} measurements: "
            f"{'+' if delta >= 0 else ''}{delta:.1f} kg. "
            f"Body photos on record: {photo_count}."
        )

    return [
        complete_profile,
        log_meal,
        log_weight,
        log_body_photo,
        get_daily_summary,
        get_weekly_progress,
    ]
