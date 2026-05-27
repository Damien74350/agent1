"""Nutrition calculations: BMR, TDEE, daily targets."""

from dataclasses import dataclass

ACTIVITY_MULTIPLIERS = {
    "sedentary": 1.2,   # bureau + pas de sport
    "light": 1.375,     # sport 1-3x/sem
    "moderate": 1.55,   # sport 3-5x/sem
    "intense": 1.725,   # sport 6-7x/sem
}

GOAL_DELTAS = {
    "lose": -500,       # déficit modéré ≈ -0.5kg/semaine
    "maintain": 0,
    "gain": +400,
}


@dataclass
class DailyTargets:
    calories: int
    protein_g: int
    carbs_g: int
    fat_g: int


def mifflin_st_jeor_bmr(sex: str, weight_kg: float, height_cm: int, age: int) -> float:
    """Basal Metabolic Rate via Mifflin–St Jeor (the most accurate formula in clinical practice)."""
    base = 10 * weight_kg + 6.25 * height_cm - 5 * age
    return base + (5 if sex.upper() == "M" else -161)


def daily_targets(
    sex: str,
    weight_kg: float,
    height_cm: int,
    age: int,
    activity_level: str,
    goal: str,
) -> DailyTargets:
    """Compute daily calorie + macro targets."""
    bmr = mifflin_st_jeor_bmr(sex, weight_kg, height_cm, age)
    tdee = bmr * ACTIVITY_MULTIPLIERS.get(activity_level, 1.375)
    calories = int(round(tdee + GOAL_DELTAS.get(goal, 0)))

    # Macros: 1.8g protein/kg (good for fat loss + muscle preservation),
    # 25% calories from fat, the rest from carbs.
    protein_g = int(round(weight_kg * 1.8))
    fat_g = int(round((calories * 0.25) / 9))
    remaining = calories - (protein_g * 4 + fat_g * 9)
    carbs_g = max(0, int(round(remaining / 4)))

    return DailyTargets(
        calories=calories, protein_g=protein_g, carbs_g=carbs_g, fat_g=fat_g
    )
