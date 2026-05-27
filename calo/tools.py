"""Calo tools, bound to the current request context (db + user + photo).

Available tools:
- complete_profile        save the user's profile and compute daily targets
- log_meal                record a meal the user just ate
- lookup_food             query the Foods table for accurate nutritional values
- log_weight              record a weight measurement
- log_body_photo          record a body-photo analysis (consented users only)
- get_daily_summary       fetch today's consumption status
- get_weekly_progress     fetch the weight trend and meal compliance
- search_knowledge        retrieve relevant guidance from the knowledge base
"""

from datetime import datetime, timezone
from typing import Any

from anthropic import beta_tool

from .airtable_db import AirtableDB
from .nutrition import daily_targets


def build_tools(
    db: AirtableDB,
    user_id: str,
    incoming_photo_ref: str | None,
):
    """Create tools bound to the current request context."""

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
        sex_norm = (
            "M"
            if sex.upper().startswith("M") or sex.lower().startswith("h")
            else "F"
        )
        targets = daily_targets(sex_norm, weight_kg, height_cm, age, activity_level, goal)
        db.update_user(
            user_id,
            name=name,
            sex=sex_norm,
            age=age,
            height_cm=height_cm,
            current_weight_kg=weight_kg,
            activity_level=activity_level,
            goal=goal,
            target_weight_kg=target_weight_kg,
            target_date=target_date,
            restrictions=restrictions,
            photo_consent=photo_consent,
            daily_calories=targets.calories,
            daily_protein_g=targets.protein_g,
            daily_carbs_g=targets.carbs_g,
            daily_fat_g=targets.fat_g,
            onboarding_complete=True,
        )
        return (
            f"Profile saved. Daily targets: {targets.calories} kcal, "
            f"P:{targets.protein_g}g C:{targets.carbs_g}g F:{targets.fat_g}g. "
            f"Photo consent: {photo_consent}."
        )

    @beta_tool
    def lookup_food(name: str) -> str:
        """Look up a food in the Calo nutritional database. Use this BEFORE \
estimating values for any identified food to get accurate macros.

Args:
    name: French name of the food (e.g. 'blanc de poulet', 'riz cuit', 'avocat').
"""
        food = db.lookup_food(name)
        if not food:
            return f"No exact match found for '{name}'. You'll have to estimate using your training knowledge."
        return (
            f"{food['name']} ({food['category']}) — per 100g: "
            f"{food['kcal_per_100g']} kcal, "
            f"{food['protein_per_100g']}g protein, "
            f"{food['carbs_per_100g']}g carbs, "
            f"{food['fat_per_100g']}g fat, "
            f"{food.get('fiber_per_100g', 0)}g fiber. "
            f"Standard portion: {food.get('standard_portion_g', '?')}g."
        )

    @beta_tool
    def log_meal(
        items: list[dict[str, Any]],
        notes: str = "",
        meal_type: str = "",
    ) -> str:
        """Log a meal the user just ate. Always call lookup_food FIRST for each \
item where possible, so your macros are accurate. Fall back to estimates only \
for foods absent from the database.

Args:
    items: A list of food items, each a dict with keys:
        name (str), grams (int), kcal (int), protein_g (int), carbs_g (int), fat_g (int).
    notes: Optional free text (e.g. 'au restaurant', 'estimation imprécise').
    meal_type: 'petit-déj' | 'déjeuner' | 'goûter' | 'dîner' | 'snack'.
"""
        meal_id = db.add_meal(
            user_id,
            items,
            incoming_photo_ref,
            notes or None,
            meal_type=meal_type or None,
        )
        total = sum(int(i.get("kcal", 0)) for i in items)
        return f"Meal {meal_id} logged. Total: {total} kcal across {len(items)} item(s)."

    @beta_tool
    def log_weight(kg: float) -> str:
        """Log a weight measurement.

Args:
    kg: Weight in kilograms (e.g. 78.4).
"""
        db.add_weight(user_id, kg)
        db.update_user(user_id, current_weight_kg=kg)
        return f"Weight logged: {kg} kg."

    @beta_tool
    def log_body_photo(
        analysis: str,
        week_number: int | None = None,
        angle: str = "face",
    ) -> str:
        """Save the analysis of a body / morphotype photo. Only call this when \
the user has sent a body photo (not a meal photo) AND they have consented to \
photo tracking.

Args:
    analysis: Your written observations about the photo (encouraging, factual, no body shaming).
    week_number: Week index (1 = baseline, 2 = J+7, etc.).
    angle: 'face' | 'profil gauche' | 'profil droit' | 'dos'.
"""
        if not incoming_photo_ref:
            return "Error: no photo attached to this turn."
        db.add_body_photo(user_id, incoming_photo_ref, week_number, analysis, angle)
        return "Body photo saved."

    @beta_tool
    def get_daily_summary() -> str:
        """Return today's nutrition status: target, consumed so far, and remaining."""
        user = db.get_user_by_id(user_id)
        if not user.get("onboarding_complete"):
            return "User onboarding not complete yet."
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        meals = db.meals_for_day(user_id, today)
        consumed_kcal = sum(int(m.get("total_calories") or 0) for m in meals)
        consumed_protein = sum(int(m.get("total_protein_g") or 0) for m in meals)
        consumed_carbs = sum(int(m.get("total_carbs_g") or 0) for m in meals)
        consumed_fat = sum(int(m.get("total_fat_g") or 0) for m in meals)
        target = user.get("daily_calories") or 0
        return (
            f"Today ({today}): {len(meals)} meal(s) logged. "
            f"Consumed: {consumed_kcal}/{target} kcal "
            f"(P:{consumed_protein}/{user.get('daily_protein_g')}g, "
            f"C:{consumed_carbs}/{user.get('daily_carbs_g')}g, "
            f"F:{consumed_fat}/{user.get('daily_fat_g')}g). "
            f"Remaining: {max(0, (target or 0) - consumed_kcal)} kcal."
        )

    @beta_tool
    def get_weekly_progress() -> str:
        """Return the user's weight trend and recent photo records."""
        weights = db.weights_history(user_id, limit=10)
        photos = db.body_photos_for_user(user_id)
        if not weights:
            return "No weight history yet."
        latest = weights[0]["weight_kg"]
        oldest = weights[-1]["weight_kg"]
        delta = (latest or 0) - (oldest or 0)
        return (
            f"Latest weight: {latest} kg. "
            f"Trend over last {len(weights)} measurements: "
            f"{'+' if delta >= 0 else ''}{delta:.1f} kg. "
            f"Body photos on record: {len(photos)}."
        )

    @beta_tool
    def search_knowledge(query: str) -> str:
        """Search Calo's knowledge base for relevant guidance. Call this when the \
user mentions a topic like 'plateau', 'restaurant', 'sommeil', 'cycle', \
'cheat meal', 'alcool', 'protéines', 'cortisol', etc. The knowledge base \
contains Calo's philosophy and method — use its guidance to inform your reply.

Args:
    query: A short keyword or phrase describing the topic (e.g. 'plateau', \
'manger le soir', 'restaurant').
"""
        hits = db.search_knowledge(query, max_results=3)
        if not hits:
            return f"No knowledge entry found for '{query}'. Reply from your own knowledge."
        out = []
        for h in hits:
            out.append(f"## {h['title']} ({h['topic']})\n{h['content']}")
        return "\n\n---\n\n".join(out)

    return [
        complete_profile,
        lookup_food,
        log_meal,
        log_weight,
        log_body_photo,
        get_daily_summary,
        get_weekly_progress,
        search_knowledge,
    ]
