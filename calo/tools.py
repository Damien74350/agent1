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

import random
from datetime import datetime, timezone
from typing import Any

from anthropic import beta_tool

from .airtable_db import AirtableDB
from .nutrition import daily_targets


def _build_workout_exercises(equipment: str, focus: str) -> dict[str, list[str]]:
    """Return a session→exercise mapping based on equipment + focus."""
    eq = (equipment or "").lower()

    if "maison_basique" in eq or "aucun" in eq or "extérieur" in eq:
        return {
            "Full body A": [
                "Squat sans charge 4x15",
                "Pompes (ou genoux) 4x10-15",
                "Fentes alternées 4x12/jambe",
                "Rowing élastique ou table 4x12",
                "Planche 3x45 sec",
                "Mountain climbers 3x30 sec",
            ],
            "Full body B": [
                "Squat sauté 4x12",
                "Pompes diamant 4x8-12",
                "Step-up sur banc 4x12/jambe",
                "Tirage horizontal élastique 4x15",
                "Hollow body hold 3x30 sec",
                "Burpees 3x10",
            ],
            "Full body C": [
                "Pistol squat assisté 4x6/jambe",
                "Dips chaise 4x10",
                "Hip thrust pieds élevés 4x15",
                "Pike push-up 4x8",
                "Plank side-to-side 3x40 sec",
                "Squat jumps 3x12",
            ],
            "default": [
                "Squat 4x12-15",
                "Pompes 4x10-15",
                "Fentes 4x12/jambe",
                "Planche 3x45 sec",
                "Mountain climbers 3x30 sec",
            ],
        }

    if "maison_équipée" in eq or "haltères" in eq or "kettlebell" in eq:
        return {
            "Full body A": [
                "Goblet squat 4x10",
                "Développé couché haltères 4x10",
                "Soulevé de terre roumain haltères 4x10",
                "Rowing haltère unilatéral 4x10/côté",
                "Développé militaire haltères 3x10",
                "Planche 3x45 sec",
            ],
            "Full body B": [
                "Fentes haltères 4x10/jambe",
                "Développé incliné haltères 4x10",
                "Hip thrust avec poids 4x12",
                "Rowing buste penché barre 4x10",
                "Élévations latérales 3x15",
                "Russian twists 3x20",
            ],
            "Full body C": [
                "Sumo squat haltère 4x12",
                "Dips banc avec lest 4x10",
                "Single leg deadlift 4x8/jambe",
                "Curl haltères 3x12",
                "Triceps overhead 3x12",
                "Hollow rocks 3x30 sec",
            ],
            "Upper A": [
                "Développé couché haltères 4x8-10",
                "Rowing haltère 4x10/côté",
                "Développé militaire haltères 4x10",
                "Tirage poulie (élastique) 4x12",
                "Curl haltères 3x12",
                "Triceps extension 3x12",
            ],
            "Lower A": [
                "Goblet squat 4x10",
                "Soulevé de terre roumain 4x10",
                "Fentes marchées 3x12/jambe",
                "Hip thrust 4x15",
                "Mollets debout 4x15",
                "Planche 3x45 sec",
            ],
            "Upper B": [
                "Développé incliné haltères 4x10",
                "Rowing buste penché 4x10",
                "Élévations latérales 4x15",
                "Pull-ups (assistées si besoin) 3xAMRAP",
                "Pompes prise serrée 3x10",
                "Curl marteau 3x12",
            ],
            "Lower B": [
                "Sumo squat 4x12",
                "Single leg deadlift 4x10/jambe",
                "Step-up lestée 4x10/jambe",
                "Curl jambes (élastique) 3x15",
                "Mollets assis 4x20",
                "Hollow body hold 3x30 sec",
            ],
            "Push": [
                "Développé couché haltères 4x8",
                "Développé militaire haltères 4x10",
                "Pompes lestées 3x10",
                "Élévations latérales 4x15",
                "Triceps extension 3x12",
            ],
            "Pull": [
                "Tirage barre/élastique 4x10",
                "Rowing haltère 4x10/côté",
                "Face pulls élastique 3x15",
                "Curl haltères 3x12",
                "Curl marteau 3x12",
            ],
            "Legs": [
                "Goblet squat 4x10",
                "Soulevé de terre roumain 4x10",
                "Fentes 3x12/jambe",
                "Hip thrust 4x15",
                "Mollets 4x15",
            ],
            "default": [
                "Squat haltères 4x10",
                "Développé couché 4x10",
                "Rowing 4x10",
                "Planche 3x45 sec",
            ],
        }

    # Default: salle / gym
    return {
        "Full body A": [
            "Squat barre 4x6-8",
            "Développé couché barre 4x6-8",
            "Soulevé de terre roumain 4x8",
            "Tractions ou tirage vertical 4x8",
            "Développé militaire 3x10",
            "Gainage 3x45 sec",
        ],
        "Full body B": [
            "Front squat 4x8",
            "Développé incliné haltères 4x10",
            "Hip thrust 4x10",
            "Rowing barre 4x8",
            "Élévations latérales 3x12",
            "Russian twists 3x20",
        ],
        "Full body C": [
            "Fentes bulgares 4x10/jambe",
            "Dips lestés 4x8",
            "Single leg deadlift 4x8/jambe",
            "Tirage horizontal 4x10",
            "Crunch lesté 3x15",
            "Sprint en côte 5x20 sec",
        ],
        "Upper A": [
            "Développé couché barre 4x6-8",
            "Tractions ou tirage vertical 4x8",
            "Développé militaire barre 4x8",
            "Rowing buste penché 4x10",
            "Curl barre 3x10",
            "Dips 3xAMRAP",
        ],
        "Lower A": [
            "Squat barre 4x6-8",
            "Soulevé de terre 4x6",
            "Fentes marchées 3x12/jambe",
            "Hip thrust 4x10",
            "Mollets debout 4x15",
            "Planche pondérée 3x45 sec",
        ],
        "Upper B": [
            "Développé incliné haltères 4x10",
            "Rowing T-bar 4x10",
            "Élévations latérales 4x15",
            "Face pulls 4x15",
            "Pompes lestées 3x10",
            "Triceps poulie 3x12",
        ],
        "Lower B": [
            "Front squat 4x8",
            "Soulevé de terre roumain 4x10",
            "Presse à cuisses 3x12",
            "Curl ischio 3x12",
            "Mollets assis 4x15",
            "Hollow rocks 3x30 sec",
        ],
        "Push": [
            "Développé couché barre 4x6-8",
            "Développé militaire 4x8",
            "Développé incliné haltères 3x10",
            "Élévations latérales 4x15",
            "Dips lestés 3x10",
            "Triceps poulie 3x12",
        ],
        "Pull": [
            "Tractions lestées 4xAMRAP",
            "Rowing barre 4x8",
            "Tirage vertical 4x10",
            "Face pulls 3x15",
            "Curl barre 3x10",
            "Curl marteau 3x12",
        ],
        "Legs": [
            "Squat barre 4x6-8",
            "Soulevé de terre 4x6",
            "Fentes marchées 3x12/jambe",
            "Hip thrust 4x10",
            "Curl ischio 3x12",
            "Mollets debout 4x15",
        ],
        "default": [
            "Squat barre 4x8",
            "Développé couché 4x8",
            "Soulevé de terre 4x6",
            "Tirage vertical 4x10",
            "Gainage 3x45 sec",
        ],
    }


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
    def remember(memory: str, category: str = "divers", importance: int = 3) -> str:
        """Save an important fact about the user that you want to remember for \
future conversations. Use this PROACTIVELY whenever the user shares something \
that would help you serve them better next time.

When to call this tool (be generous, save liberally):
- Preferences: 'I hate fish', 'I love spicy food', 'I'm vegetarian on Mondays'
- Health: injuries, allergies, conditions, medications
- Sport: schedule, gym, sports practiced, frequency
- Personal life: family, work, kids, life events ('moving in June', 'wedding next month')
- Professional: job, business projects, current challenges
- Recurring events: 'Tuesday is always cheat day', 'I drink wine on Fridays'
- Goals beyond the basic profile: 'wants to run a marathon in October'
- Quirks/habits: 'doesn't eat breakfast', 'always trains at 6am'

Args:
    memory: The fact to remember, written in 3rd person, concise. \
        Ex: 'Déteste le poisson', 'Bléssé au ménisque gauche depuis 2024', \
        'Coach sportif avec 25 clients', 'Court le marathon de Paris en avril'.
    category: One of 'préférence' | 'objectif' | 'santé' | 'sport' | \
        'vie pro' | 'vie perso' | 'événement' | 'divers'.
    importance: 1 (anecdote) to 5 (critical, never forget). Default 3.
"""
        memory_id = db.add_memory(user_id, memory, category, importance)
        return f"Memory saved [{category}, importance={importance}]: {memory[:80]}"

    @beta_tool
    def find_recipe(
        query: str = "",
        category: str = "",
        max_kcal: int = 0,
        max_prep_min: int = 0,
        tags: list[str] | None = None,
    ) -> str:
        """Find a Calo recipe matching the user's situation. Use this when the \
user asks for meal ideas, "qu'est-ce que je peux manger", "j'ai X et Y, je \
fais quoi ?", "une recette rapide ?", "un dîner léger ?", etc. Combine \
filters to narrow down. Returns up to 5 matching recipes with macros and \
full instructions.

Args:
    query: Free-text keyword to match against the name OR ingredients \
(e.g. 'poulet', 'avocat', 'curry'). Leave empty if the user just wants \
inspiration without specifying.
    category: One of 'petit-déj' | 'déjeuner' | 'dîner' | 'snack' | 'dessert' | 'entrée'.
    max_kcal: Upper bound on calories per serving (e.g. 400 for light). 0 = no limit.
    max_prep_min: Upper bound on prep time in minutes (e.g. 15 for quick). 0 = no limit.
    tags: List of required tags, ANY of: 'rapide', 'batch cooking', \
'healthy', 'comfort', 'végétarien', 'vegan', 'sans gluten', \
'riche en protéines', 'low-carb', 'low-cal', 'post-training', \
'pré-training', 'anti-inflammatoire', 'perte de poids', 'prise de masse', \
'ménopause-friendly', 'cycle hormonal'.
"""
        recipes = db.search_recipes(
            query=query or None,
            category=category or None,
            tags=tags or None,
            max_kcal=max_kcal if max_kcal > 0 else None,
            max_prep_min=max_prep_min if max_prep_min > 0 else None,
            max_results=5,
        )
        if not recipes:
            return (
                "Aucune recette ne correspond à ces critères. Propose une "
                "suggestion depuis tes connaissances et invite l'utilisateur "
                "à essayer."
            )
        out = []
        for r in recipes:
            tags_str = " · ".join(r.get("tags") or [])
            total_min = (r.get("prep_min") or 0) + (r.get("cook_min") or 0)
            out.append(
                f"## {r['name']} ({r.get('category', '?')})\n"
                f"⏱️ {total_min} min total · 🍽️ {r.get('servings', 1)} pers\n"
                f"📊 {r.get('kcal', 0)} kcal · P:{r.get('protein_g', 0)}g · "
                f"C:{r.get('carbs_g', 0)}g · F:{r.get('fat_g', 0)}g · "
                f"Fibres:{r.get('fiber_g', 0)}g\n"
                f"🏷️ {tags_str}\n\n"
                f"**Ingrédients :**\n{r.get('ingredients', '')}\n\n"
                f"**Préparation :**\n{r.get('instructions', '')}"
            )
        return "\n\n---\n\n".join(out)

    @beta_tool
    def generate_grocery_list(recipe_names: list[str]) -> str:
        """Generate an aggregated grocery list from a list of Calo recipe names. \
Use this when the user asks for "la liste de courses" after a meal plan, or \
ad-hoc when they pick several recipes manually. Returns the consolidated \
shopping list grouped by aisle.

Args:
    recipe_names: List of recipe names (exact match preferred) to aggregate.
"""
        if not recipe_names:
            return "Aucune recette fournie. Demande à l'utilisateur quelles recettes inclure."
        all_ingredients: list[str] = []
        found_count = 0
        missing: list[str] = []
        for name in recipe_names:
            hits = db.search_recipes(query=name, max_results=1)
            if hits and hits[0].get("ingredients"):
                all_ingredients.append(f"### {hits[0]['name']}\n{hits[0]['ingredients']}")
                found_count += 1
            else:
                missing.append(name)
        if found_count == 0:
            return f"Aucune recette trouvée pour : {', '.join(recipe_names)}."
        body = "\n\n".join(all_ingredients)
        notice = ""
        if missing:
            notice = (
                f"\n\n⚠️ Recettes introuvables (à ajouter manuellement) : "
                f"{', '.join(missing)}"
            )
        return (
            f"# Liste de courses agrégée ({found_count} recettes)\n\n"
            f"💡 Calo te donne les ingrédients par recette. À toi de regrouper "
            f"par rayon (légumes, protéines, féculents, sec, frais).\n\n"
            f"{body}{notice}"
        )

    @beta_tool
    def interpret_bloodwork(notes: str = "") -> str:
        """User has just sent a photo of their blood test results. Use Calo's \
vision to read the values, then call THIS tool to record the analysis as a \
Memory + return a structured interpretation framework. Identifies likely \
deficiencies, flags abnormal values, suggests actions, and ALWAYS reminds \
the user to validate with their doctor.

Call this whenever the user shares a 'bilan sanguin', 'prise de sang', \
'analyses', 'NFS', 'thyroïde', 'cholestérol' photo.

Args:
    notes: Brief text summary of what you read on the photo (e.g. \
'Vit D 18, Ferritine 22, TSH 4.5, Cholestérol 2.3 g/L, Glycémie 0.95'). \
You read the photo with vision; this notes string is for traceability."""
        if not notes:
            return (
                "Lis d'abord les valeurs visibles sur la photo et résume-les "
                "dans 'notes' avant de rappeler cet outil. Format conseillé : "
                "'Vit D 18, Ferritine 22, TSH 4.5...'."
            )
        from datetime import datetime, timezone
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        db.add_memory(
            user_id,
            f"Bilan sanguin {today} : {notes}",
            category="santé",
            importance=5,
        )
        return (
            f"📊 **Cadre d'interprétation du bilan**\n\n"
            f"Valeurs lues : {notes}\n\n"
            f"⚠️ **TU N'ES PAS MÉDECIN.** Tu donnes du contexte nutritionnel, "
            f"jamais un diagnostic. Toujours rediriger vers le médecin pour "
            f"interprétation officielle.\n\n"
            f"## Cibles usuelles (valeurs OPTIMALES, plus strictes que 'normales')\n\n"
            f"**Fer & globules**\n"
            f"- Ferritine : 50-150 ng/mL (femme), 80-200 (homme). <30 = "
            f"déficit franc, <50 = sub-optimal\n"
            f"- Hémoglobine : >12 g/dL femme, >13.5 homme\n"
            f"- VGM (volume globulaire) : 82-98 fL\n\n"
            f"**Vitamines**\n"
            f"- Vit D (25-OH) : 40-60 ng/mL optimum, <30 = carence\n"
            f"- B12 : >400 pg/mL (les '200 = normal' sont trop bas)\n"
            f"- Folates : >5 ng/mL\n\n"
            f"**Thyroïde**\n"
            f"- TSH : 1.0-2.5 mIU/L optimum (laboratoires acceptent 0.4-4.0 "
            f"mais 4.5+ avec symptômes = à creuser)\n"
            f"- T4 libre, T3 libre : demander si TSH limite\n"
            f"- Anti-TPO : si élevés → Hashimoto probable\n\n"
            f"**Métabolisme glucidique**\n"
            f"- Glycémie à jeun : <1.0 g/L optimum, >1.10 = pré-diabète\n"
            f"- HbA1c : <5.6% optimum, 5.7-6.4% = pré-diabète\n"
            f"- Insuline à jeun : <10 µUI/mL optimum, >15 = résistance probable\n\n"
            f"**Lipides**\n"
            f"- Cholestérol total : <2 g/L (mais le ratio importe plus)\n"
            f"- HDL : >0.5 g/L femme, >0.4 homme (plus haut = mieux)\n"
            f"- LDL : <1.3 g/L sans risque, <1.0 si risque cardio\n"
            f"- Triglycérides : <1.5 g/L\n"
            f"- Ratio TG/HDL : <2 idéal (marqueur insulino-résistance)\n\n"
            f"**Inflammation**\n"
            f"- CRP : <3 mg/L (<1 idéal)\n"
            f"- Homocystéine : <10 µmol/L (si élevé → B12, folates, B6)\n\n"
            f"## Tes consignes\n\n"
            f"1. Identifie les valeurs HORS cibles (utilise les seuils ci-dessus)\n"
            f"2. Pour CHAQUE valeur problématique, donne :\n"
            f"   - Ce que ça suggère nutritionnellement\n"
            f"   - 2-3 actions alimentaires concrètes\n"
            f"   - Compléments à envisager (avec dosage indicatif)\n"
            f"3. Recommande la consultation médecin pour confirmer\n"
            f"4. Si pathologie suspectée (Hashimoto, pré-diabète, anémie) → "
            f"insiste sur médecin AVANT changements"
        )

    @beta_tool
    def decode_symptom(
        symptom: str,
        duration: str = "",
        context: str = "",
    ) -> str:
        """Decode a non-medical symptom the user reports and return a \
nutrition-angle differential + 3 concrete actions. Use when the user mentions \
fatigue, constipation, ballonnements, brouillard mental, peau, sommeil, \
cravings, douleurs articulaires, etc. NEVER diagnose — frame as 'pistes \
nutritionnelles à explorer' and remind that persistent symptoms need a doctor.

Args:
    symptom: The symptom in French (fatigue, constipation, brouillard mental, \
ballonnements, acné, eczéma, douleurs articulaires, cravings sucré, sommeil \
fragmenté, perte de cheveux, etc.).
    duration: How long (e.g. '2 semaines', 'depuis le confinement', 'tous les \
J22 du cycle').
    context: Anything that helps narrow down (e.g. 'après les repas', \
'le matin', 'le soir uniquement', 'depuis que j'ai arrêté le sport')."""
        sym = symptom.lower().strip()
        report = [f"# 🔍 Décodage symptôme : {symptom}"]
        if duration:
            report.append(f"Durée : {duration}")
        if context:
            report.append(f"Contexte : {context}")
        report.append("")

        differentials: dict[str, list[tuple[str, str]]] = {
            "fatigue": [
                ("Carence en fer / ferritine basse", "Bilan sanguin avec ferritine. Augmenter viande rouge, foie, palourdes, lentilles + vit C."),
                ("Carence vitamine D", "Dosage 25-OH-D3. Supplémenter 1000-2000 UI/j si <40 ng/mL."),
                ("Sommeil dégradé", "Audit hygiène sommeil : écrans, alcool, caféine après 14h, chambre fraîche."),
                ("Stress chronique / cortisol", "Magnésium bisglycinate 300mg soir, gestion stress, marche."),
                ("Carence B12", "Dosage. Si végétarien/vegan → supplémenter."),
                ("Hypothyroïdie", "Dosage TSH + T4l + anti-TPO."),
                ("Sous-alimentation chronique", "Vérifier apport calorique réel. <1400 kcal/j chronique = épuisement."),
            ],
            "constipation": [
                ("Manque de fibres", "30g/jour : légumes, fruits entiers, légumineuses, graines de lin."),
                ("Déshydratation", "2.5L+/jour, eau au réveil 500ml."),
                ("Manque de magnésium", "Citrate de magnésium 300mg soir (effet laxatif doux)."),
                ("Sédentarité", "8000+ pas/jour, marche post-repas 10 min."),
                ("Microbiote appauvri", "Probiotiques (kéfir, yaourt, choucroute), prébiotiques (oignon, ail, artichaut)."),
                ("Réflexe gastro-colique faible", "Petit-déj solide pour stimuler le réflexe."),
            ],
            "ballonnement": [
                ("FODMAP (oignon, ail, choux, légumineuses, lactose, sorbitol)", "Éliminer 2 semaines pour identifier."),
                ("Manque enzymes / dysbiose", "Probiotiques + manger lentement + bien mâcher."),
                ("Excès fibres", "Si transition récente, augmenter progressivement."),
                ("SIBO suspecté", "Si chronique malgré tout → consulter gastro."),
                ("Stress / mastication insuffisante", "Manger calmement, mâcher 20+ fois."),
                ("Boissons gazeuses", "Limiter sodas, eaux gazeuses."),
            ],
            "brouillard": [
                ("Hypoglycémie réactive", "Petit-déj protéiné, glucides complexes, éviter sucres rapides."),
                ("Déshydratation", "Eau au réveil + 2L+/jour."),
                ("Carence B12 / folates", "Dosage. Supplémenter si bas."),
                ("Sommeil dégradé / apnée", "Audit sommeil, polysomnographie si suspect."),
                ("Inflammation chronique", "Oméga 3, curcuma, anti-inflammatoires alimentaires."),
                ("Cortisol élevé chronique", "Gestion stress, magnésium."),
            ],
            "peau": [
                ("Inflammation alimentaire", "Stop sucre raffiné, alcool, lait industriel 4 semaines."),
                ("Carence zinc", "Huîtres, viande rouge, graines de courge."),
                ("Oméga 3 bas", "2-3g/jour."),
                ("Hydratation insuffisante", "2L+/jour."),
                ("Microbiote", "Probiotiques."),
                ("Stress / sommeil", "Cortisol élevé = peau qui souffre."),
            ],
            "sommeil": [
                ("Caféine résiduelle", "Stop après 14h."),
                ("Alcool", "Saboteur n°1 du sommeil profond."),
                ("Magnésium bas", "Bisglycinate 300mg 30 min avant coucher."),
                ("Glycémie déréglée", "Petit-déj protéiné, pas de sucre rapide soir."),
                ("Cortisol élevé", "Gestion stress, lumière du jour matin."),
                ("Chambre trop chaude", "18°C optimal."),
            ],
            "cravings": [
                ("Protéines insuffisantes au petit-déj", "30g+ au PD = -50% fringales en moyenne."),
                ("Restriction trop sévère", "Vérifier déficit calorique <500."),
                ("Sommeil court (<7h)", "Ghréline ↑, leptine ↓ = faim folle."),
                ("Stress / émotionnel", "Identifier le trigger, alternative non-alimentaire."),
                ("Carence magnésium", "Chocolat = signal magnésium pour le corps."),
                ("Cycle lutéal (femme)", "Normal J22-J28, plan protéines+++."),
            ],
            "cheveux": [
                ("Ferritine basse", "Bilan sanguin. Cible >70 pour cheveux."),
                ("Protéines insuffisantes", "1.6g/kg minimum."),
                ("Carence zinc, biotine, sélénium", "Œufs, noix du Brésil, huîtres."),
                ("Stress / cortisol", "Le télogène effluvium est lié au stress."),
                ("Post-partum / post-accouchement", "Normal, ferritine + zinc."),
                ("Thyroïde", "Dosage TSH."),
            ],
            "articulation": [
                ("Inflammation chronique", "Oméga 3, curcuma, légumes crucifères."),
                ("Surpoids", "Pression mécanique."),
                ("Carence vit D", "Dosage."),
                ("Collagène bas", "Bouillon d'os, suppléments 10g/j."),
                ("Déshydratation des cartilages", "Hydratation."),
                ("Suractivité sportive", "Repos + récup."),
            ],
        }

        # Match symptom to differential
        matched = None
        for key, options in differentials.items():
            if key in sym:
                matched = options
                break

        if matched:
            report.append("## Pistes nutritionnelles à explorer\n")
            for i, (cause, action) in enumerate(matched, 1):
                report.append(f"**{i}. {cause}**\n→ {action}\n")
            report.append(
                "\n⚠️ Si le symptôme persiste >2 semaines, consultation médicale "
                "indispensable. La nutrition est un levier, pas un remplacement "
                "du médecin."
            )
        else:
            report.append(
                f"Symptôme non listé dans le décodeur ('{symptom}'). "
                "Approche : décris le symptôme à l'utilisateur, identifie le "
                "facteur déclenchant (timing, alimentation, stress, sommeil, "
                "cycle), propose 2-3 hypothèses nutritionnelles, recommande "
                "consultation médicale si persistant."
            )

        # Save as memory
        db.add_memory(
            user_id,
            f"Symptôme rapporté : {symptom}"
            + (f" ({duration})" if duration else "")
            + (f" — contexte : {context}" if context else ""),
            category="santé",
            importance=3,
        )

        return "\n".join(report)

    @beta_tool
    def recommend_supplements() -> str:
        """Generate a personalised supplement recommendation based on the user's \
profile (sex, age, goal, activity, medical conditions, current meds, cycle, \
ménopause status). Returns ranked recommendations with dosage, timing, and \
when to take them. Always reminds to check with doctor if on medication."""
        user = db.get_user_by_id(user_id)
        if not user:
            return "User not found."

        sex = (user.get("sex") or "").upper()
        age = user.get("age") or 0
        goal = user.get("goal", "maintain")
        activity = user.get("activity_level", "moderate")
        conditions = user.get("medical_conditions") or ""
        meds = user.get("current_meds") or ""
        metabolic_type = user.get("metabolic_type") or ""

        recs: list[tuple[str, str, str, int]] = []  # (name, dose+timing, why, priority)

        # Universal recs
        recs.append((
            "Vitamine D3 + K2",
            "1000-2000 UI/jour, au repas (matin ou midi)",
            "Déficit chez 70-80% des Européens. Os, immunité, humeur. Cible bilan : 40-60 ng/mL.",
            5,
        ))
        recs.append((
            "Magnésium bisglycinate",
            "300-400 mg/jour, 30 min avant le coucher",
            "Sommeil, gestion stress, crampes, métabolisme glucidique. Forme bisglycinate = mieux absorbée que citrate.",
            5,
        ))
        recs.append((
            "Oméga 3 (EPA + DHA)",
            "1-3 g/jour EPA+DHA, au repas",
            "Anti-inflammatoire, santé cardiovasculaire, cerveau, peau. Cible 2g/j si tu ne manges pas 3 poissons gras/sem.",
            4,
        ))

        if sex == "F":
            if age and age >= 40:
                recs.append((
                    "Calcium (alimentaire en priorité)",
                    "1000-1200 mg/jour via laitages + sardines + amandes",
                    "Pré-ménopause + ménopause = perte osseuse. Sup seulement si apport alimentaire insuffisant.",
                    4,
                ))
                recs.append((
                    "Phyto-œstrogènes (graines de lin)",
                    "1-2 cs graines de lin moulues/jour",
                    "Bouffées de chaleur, transit, anti-inflammatoire.",
                    3,
                ))
            recs.append((
                "Fer (uniquement si ferritine <50)",
                "Bisglycinate de fer 25 mg/jour avec vit C, à distance des laitages et thé",
                "Femme menstruée perd ~1mg fer/cycle. NE PAS supplémenter sans dosage ferritine (excès toxique).",
                4,
            ))

        if "muscu" in activity or "sportif" in activity or "intense" in activity:
            recs.append((
                "Créatine monohydrate",
                "5 g/jour, peu importe le timing, tous les jours",
                "Le complément le plus étudié au monde. +5-10% force, +1-2 kg muscle, cognition. Sûr.",
                5,
            ))
            recs.append((
                "Whey protein",
                "20-30g post-training si apport prot alim insuffisant",
                "Pratique pour atteindre 1.8-2g/kg/j si difficile via alimentation.",
                3,
            ))

        if "végétarien" in (user.get("restrictions") or "").lower() or "vegan" in (user.get("restrictions") or "").lower():
            recs.append((
                "Vitamine B12",
                "1000 µg cyanocobalamine 1x/sem OU 250 µg/jour",
                "Indispensable si vegan, recommandé si végétarien strict. Carence = fatigue, neuropathies.",
                5,
            ))
            recs.append((
                "Zinc",
                "15 mg/jour, à distance du fer",
                "Souvent bas chez végé/vegan.",
                3,
            ))

        if "ménopause" in metabolic_type.lower() or "menopause" in conditions.lower():
            recs.append((
                "Collagène hydrolysé type I & III",
                "10-15 g/jour avec vit C",
                "Peau, articulations, os. Particulièrement utile en ménopause.",
                3,
            ))

        if "hashimoto" in conditions.lower() or "thyroïde" in conditions.lower():
            recs.append((
                "Sélénium",
                "100-200 µg/jour (1-2 noix du Brésil)",
                "Soutien thyroïdien, anti-anti-TPO. Pas plus, toxique à haute dose.",
                4,
            ))

        if "sopk" in conditions.lower():
            recs.append((
                "Inositol (myo + d-chiro 40:1)",
                "2-4 g/jour répartis",
                "Améliore insulino-sensibilité et restaure ovulation chez SOPK.",
                5,
            ))

        if "résistance insuline" in metabolic_type.lower() or "résistance insuline" in conditions.lower():
            recs.append((
                "Berbérine",
                "500 mg x 3/jour aux repas",
                "Efficacité comparable à la metformine sur la glycémie. À discuter avec médecin si antidiabétique en cours.",
                3,
            ))

        if "stress" in conditions.lower() or (user.get("stress_level") or 0) >= 4:
            recs.append((
                "Ashwagandha KSM-66",
                "300-600 mg/jour le soir",
                "Adaptogène, baisse cortisol, améliore sommeil et résistance au stress.",
                3,
            ))

        # Sort by priority
        recs.sort(key=lambda r: -r[3])

        # Build report
        report = [f"# 💊 Compléments personnalisés pour {user.get('name', 'toi')}"]
        report.append("")
        report.append("⚠️ **Si tu prends des médicaments, valide avec ton médecin.**")
        report.append("")
        report.append("## Recommandations classées par impact")
        report.append("")
        priority_label = {5: "🔴 PRIORITÉ", 4: "🟠 IMPORTANT", 3: "🟡 RECOMMANDÉ"}
        for name, dose, why, prio in recs:
            label = priority_label.get(prio, "")
            report.append(f"### {label} — {name}")
            report.append(f"**Dosage** : {dose}")
            report.append(f"**Pourquoi** : {why}")
            report.append("")

        report.append("## Achat")
        report.append(
            "Privilégie les marques certifiées tierces (NSF, Informed Sport). "
            "Bonnes adresses : Nutripure, Yamamoto, Nutrimuscle, Now Foods, "
            "ThorneResearch."
        )
        report.append("")
        report.append("## Ce que tu NE DOIS PAS prendre sans raison")
        report.append(
            "- Multivitamines à mégadoses (souvent trop de vit A/E et pas assez "
            "de ce dont tu as besoin)\n"
            "- BCAA si apport prot >1.6g/kg (inutile)\n"
            "- Brûleurs de graisse type 'fat burner' (stress + arnaque)\n"
            "- Pre-workouts à 300mg caféine si tu dors mal\n"
            "- Détoxs / cures bidons"
        )

        return "\n".join(report)

    @beta_tool
    def generate_workout(
        days_per_week: int = 3,
        equipment: str = "salle",
        focus: str = "auto",
    ) -> str:
        """Generate a personalised training week based on the user's profile, \
goal, sex and equipment. Returns a structured 3-5 day plan. Use when the \
user asks for "un plan d'entraînement", "que faire en muscu", "comment \
m'entraîner cette semaine".

Args:
    days_per_week: 2 to 6 sessions per week. Default 3.
    equipment: 'salle' (machines + libres) | 'maison_basique' (élastiques, \
poids du corps) | 'maison_équipée' (haltères, banc) | 'extérieur' (course, \
parc) | 'aucun'.
    focus: 'auto' (Calo choisit selon objectif) | 'force' | 'hypertrophie' | \
'perte de poids' | 'endurance' | 'mobilité'.
"""
        user = db.get_user_by_id(user_id)
        if not user:
            return "User not found."

        days_per_week = max(2, min(6, int(days_per_week)))
        goal = user.get("goal", "maintain")
        sex = (user.get("sex") or "").upper()
        age = user.get("age") or 30
        metabolic_type = (user.get("metabolic_type") or "").lower()

        # Auto-resolve focus
        if focus == "auto":
            if goal == "lose":
                focus = "hypertrophie"  # préserver muscle en déficit
            elif goal == "gain":
                focus = "force"
            else:
                focus = "hypertrophie"
            if "ménopause" in metabolic_type or (sex == "F" and age >= 45):
                focus = "force"  # critique pour sarcopénie

        # Decide split
        if days_per_week <= 2:
            split = "Full body (2 séances identiques ou alternées A/B)"
            sessions = ["Full body A", "Full body B"]
        elif days_per_week == 3:
            split = "Full body 3x ou Push/Pull/Legs"
            sessions = ["Full body A", "Full body B", "Full body C"]
        elif days_per_week == 4:
            split = "Upper/Lower 2x"
            sessions = ["Upper A", "Lower A", "Upper B", "Lower B"]
        elif days_per_week == 5:
            split = "Push / Pull / Legs / Upper / Lower"
            sessions = ["Push", "Pull", "Legs", "Upper", "Lower"]
        else:
            split = "PPL 2x"
            sessions = ["Push A", "Pull A", "Legs A", "Push B", "Pull B", "Legs B"]

        # Exercise library by equipment
        exercises = _build_workout_exercises(equipment, focus)

        report = [
            f"# 💪 Plan d'entraînement {days_per_week}j/sem",
            f"Objectif : **{goal}** · Focus : **{focus}** · Matériel : **{equipment}**",
            f"Structure : {split}",
            "",
            "## Paramètres",
        ]

        if focus == "force":
            report.append("- **Charges** : lourdes, 80-90% 1RM")
            report.append("- **Réps** : 3-6 par série")
            report.append("- **Repos** : 2-3 min entre séries")
            report.append("- **Séries** : 4-5 par exercice principal")
        elif focus == "hypertrophie":
            report.append("- **Charges** : modérées-lourdes, 70-80% 1RM")
            report.append("- **Réps** : 8-12 par série (difficile à la dernière)")
            report.append("- **Repos** : 60-90 sec")
            report.append("- **Séries** : 3-4 par exercice")
        elif focus == "endurance":
            report.append("- **Charges** : légères-modérées")
            report.append("- **Réps** : 15-25")
            report.append("- **Repos** : 30-60 sec")
        elif focus == "perte de poids":
            report.append("- **Format** : circuits + cardio HIIT")
            report.append("- **Cardio** : 1-2 séances HIIT 25 min/sem")

        # Build per-session plan
        for i, session_name in enumerate(sessions[:days_per_week]):
            report.append(f"\n## {session_name}")
            session_exercises = exercises.get(session_name, exercises.get("default", []))
            for ex in session_exercises:
                report.append(f"- {ex}")

        # Cardio guidance
        report.append("\n## Cardio complémentaire")
        if goal == "lose":
            report.append("- **Marche** : 8000+ pas/jour OBLIGATOIRE")
            report.append("- **HIIT** : 1-2x/sem 20-25 min (après muscu ou jour séparé)")
            report.append("- **Z2** : 1x/sem 45 min (course lente, vélo)")
        elif goal == "gain":
            report.append("- **Marche** : 6000 pas/jour (suffisant)")
            report.append("- **Pas de HIIT** : compromet la prise")
            report.append("- **Z2 1x/sem** pour santé cardio (option)")
        else:
            report.append("- **Marche** : 7000-10000 pas/jour")
            report.append("- **Z2 ou HIIT** : 1-2x/sem au choix")

        # Recovery rule
        report.append("\n## Récup")
        report.append("- **Sommeil 7h+** non négociable")
        report.append("- **Protéines 1.8-2g/kg/j** réparties")
        report.append("- **Repos complet** : minimum 1 jour off/sem")
        report.append("- **Mobilité** : 5-10 min/jour (utile, pas optionnel)")

        # Progression
        report.append("\n## Progression")
        report.append(
            "Augmente CHAQUE semaine : soit la charge (+2.5-5%), soit "
            "le nombre de reps (+1-2). Si tu n'arrives plus à progresser "
            "2 semaines d'affilée → 1 semaine deload (volume -40%)."
        )

        # Save as memory
        db.add_memory(
            user_id,
            f"Plan entraînement généré : {days_per_week}j/sem, focus {focus}, équipement {equipment}",
            category="sport",
            importance=3,
        )

        return "\n".join(report)

    @beta_tool
    def workout_fuel(
        workout_time: str,
        workout_type: str = "muscu",
        duration_min: int = 60,
    ) -> str:
        """Tell the user exactly what to eat before, during, and after a \
training session. Use when the user asks "je m'entraîne à X, je mange quoi", \
"pre-workout", "post-workout", "nutrition autour de l'entraînement".

Args:
    workout_time: ISO datetime or human time (e.g. '07h00', '18h30', 'matin', \
'midi', 'soir').
    workout_type: 'muscu' | 'cardio léger' | 'HIIT' | 'course longue' | \
'match' | 'sport co' | 'crossfit' | 'yoga'.
    duration_min: Session duration in minutes.
"""
        user = db.get_user_by_id(user_id)
        if not user:
            return "User not found."
        weight = float(user.get("current_weight_kg") or 70)

        # Determine time slot
        slot = "matin"
        try:
            hour = int(workout_time.split(":")[0].replace("h", "").strip())
            if hour < 10:
                slot = "matin"
            elif hour < 16:
                slot = "midi"
            else:
                slot = "soir"
        except (ValueError, IndexError):
            t = workout_time.lower()
            if "midi" in t or "12h" in t or "13h" in t:
                slot = "midi"
            elif "soir" in t or "18h" in t or "19h" in t or "20h" in t:
                slot = "soir"

        report = [
            f"# 🍴 Fuel autour de ton {workout_type} ({slot}, {duration_min} min)",
            "",
        ]

        # Pre-workout
        report.append("## ⏱️ PRE-WORKOUT")
        if slot == "matin":
            if workout_type in ("muscu", "HIIT", "crossfit"):
                report.append(
                    "**90 min avant** (si possible) :\n"
                    "- 40g flocons d'avoine + 1 banane + 20g whey + 1 c.à.c. miel\n"
                    "- OU 2 tartines pain complet + 1 c.à.s. beurre cacahuète + 1 banane\n\n"
                    "**Si tu t'entraînes à JEUN (intermittent fasting)** :\n"
                    "- 1 espresso ou caféine 200mg\n"
                    "- BCAA 10g + sel rose si effort >45 min\n"
                    "- Petit-déj copieux JUSTE APRÈS"
                )
            else:
                report.append(
                    "À jeun ou ultra léger : 1 banane + 1 café.\n"
                    "Pour cardio léger / yoga, pas besoin de fuel."
                )
        elif slot == "midi":
            report.append(
                "**Petit-déj 3-4h avant** : protéines + glucides complexes\n"
                "- Ex : œufs + avoine + fruit, OU yaourt grec + granola + banane\n\n"
                "**1h avant** :\n"
                "- 1 banane + 10g amandes\n"
                "- OU 1 compote sans sucre ajouté + 1 oeuf dur"
            )
        else:  # soir
            report.append(
                "**Déjeuner 4-5h avant** : repas complet équilibré\n"
                "- Protéine (poulet, poisson) + glucides (riz, patate douce) + légumes\n\n"
                "**1-1h30 avant** :\n"
                "- 1 fruit + 1 yaourt grec\n"
                "- OU 1 tartine pain complet + 1 c.à.c. miel"
            )

        # During (if >75 min)
        if duration_min >= 75 or workout_type == "course longue":
            report.append("\n## 💦 PENDANT (effort >75 min)")
            report.append(
                f"- Eau + électrolytes : 500-700 ml/heure\n"
                f"- Glucides : 30-60g/h (gel, banane, dattes, boisson isotonique)\n"
                f"- Sel rose ou sodium 300-700mg/h si tu transpires beaucoup"
            )
        else:
            report.append("\n## 💦 PENDANT")
            report.append("- Eau : 500ml minimum sur la séance")

        # Post-workout
        report.append("\n## ✅ POST-WORKOUT (fenêtre 60 min)")
        protein_g = int(weight * 0.3)
        carbs_g = int(weight * 0.5) if workout_type in ("muscu", "HIIT", "crossfit", "course longue") else int(weight * 0.3)
        report.append(
            f"**{protein_g}g protéines + {carbs_g}g glucides** :\n"
            f"- Option 1 : shake whey 30g + 1 grosse banane + 1 cs miel\n"
            f"- Option 2 : 2 œufs + 60g avoine + fruits rouges + 1 cs miel\n"
            f"- Option 3 : 150g blanc poulet + 80g riz + légumes\n"
            f"- Option 4 (vegan) : 100g tofu + 80g quinoa + légumes + sauce tahini"
        )

        report.append("\n## 💧 HYDRATATION POST")
        report.append(
            f"Pèse-toi avant/après : pour chaque 500g perdus, bois 750ml d'eau "
            f"avec une pincée de sel rose."
        )

        # Save as memory
        db.add_memory(
            user_id,
            f"Demande fuel workout : {workout_type} {workout_time} {duration_min} min",
            category="sport",
            importance=2,
        )

        return "\n".join(report)

    @beta_tool
    def recovery_protocol(intensity: str = "modérée") -> str:
        """Generate a recovery protocol after a training session. Use when the \
user mentions courbatures, fatigue post-entraînement, "comment récupérer".

Args:
    intensity: 'légère' | 'modérée' | 'intense' | 'épuisante (compétition)'.
"""
        report = ["# 🛌 Protocole récupération"]
        report.append(f"Intensité de la séance : **{intensity}**\n")

        report.append("## Dans l'heure qui suit")
        report.append(
            "- Repas/shake post-training (cf workout_fuel)\n"
            "- 500ml-1L eau + sodium\n"
            "- 5-10 min stretching doux ou foam roller léger"
        )

        report.append("\n## Le soir même")
        report.append(
            "- Repas complet : protéines + glucides + légumes + bon gras\n"
            "- 1h avant coucher : magnésium bisglycinate 300mg\n"
            "- Pas d'écrans 60 min avant dodo\n"
            "- Chambre fraîche (18°C)\n"
            "- Sommeil 8h+ visé"
        )

        if intensity in ("intense", "épuisante (compétition)"):
            report.append("\n## Jour suivant")
            report.append(
                "- Repos COMPLET ou marche douce (Z1)\n"
                "- Repas +200-400 kcal vs normal (glucides+++)\n"
                "- Bain chaud (38-40°C) ou sauna 15 min\n"
                "- Massage / foam roller 15 min\n"
                "- Étirements légers"
            )
            report.append("\n## Surveillance")
            report.append(
                "Si DOMS >72h ou fatigue persiste → sous-récupération. Réduis "
                "le volume de 30% la semaine suivante."
            )
        else:
            report.append("\n## Jour suivant")
            report.append(
                "- Activité légère ok (marche, mobilité)\n"
                "- Si DOMS gênants : bain tiède + magnésium topique sur la zone\n"
                "- Hydratation maintenue 2.5L+"
            )

        return "\n".join(report)

    @beta_tool
    def log_daily_check(
        hydration_l: float = 0,
        sleep_hours: float = 0,
        sleep_quality: int = 0,
        stress_level: int = 0,
        steps: int = 0,
        note: str = "",
    ) -> str:
        """Save the user's daily lifestyle check. Call this when the user \
mentions hydration, sleep, steps, stress in conversation, or proactively at \
the daily/weekly check-in. Stores as a structured memory so analyze_progress \
can correlate lifestyle with weight trajectory.

Args:
    hydration_l: Litres of water/fluid drunk today (e.g. 2.5).
    sleep_hours: Hours of sleep last night (e.g. 7.5).
    sleep_quality: 1 (terrible) to 5 (excellent).
    stress_level: 1 (zen) to 5 (chronic high).
    steps: Step count for the day.
    note: Optional free text (e.g. "réveil 3h cette nuit, anxiety pre-meeting").
"""
        parts: list[str] = []
        if hydration_l > 0:
            parts.append(f"💧 {hydration_l}L eau")
        if sleep_hours > 0:
            q = f"{sleep_quality}/5" if sleep_quality > 0 else "?"
            parts.append(f"😴 {sleep_hours}h sommeil ({q})")
        if stress_level > 0:
            parts.append(f"⚡ stress {stress_level}/5")
        if steps > 0:
            parts.append(f"👟 {steps} pas")
        if note:
            parts.append(f"📝 {note}")
        if not parts:
            return "Rien à logger — repose la question naturellement."

        from datetime import datetime, timezone
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        memory_text = f"Daily check {today} — " + " · ".join(parts)
        db.add_memory(
            user_id,
            memory_text,
            category="santé",
            importance=2,
        )

        # Update user profile rating fields if recent rating provided
        updates: dict[str, Any] = {}
        if 1 <= sleep_quality <= 5:
            updates["sleep_quality"] = sleep_quality
        if 1 <= stress_level <= 5:
            updates["stress_level"] = stress_level
        if updates:
            db.update_user(user_id, **updates)

        feedback: list[str] = []
        if hydration_l > 0 and hydration_l < 1.5:
            feedback.append("⚠️ Hydratation basse")
        if sleep_hours > 0 and sleep_hours < 6:
            feedback.append("⚠️ Sommeil insuffisant (<6h) — impact cortisol+leptine")
        if stress_level >= 4:
            feedback.append("⚠️ Stress élevé — pense gestion (respiration, marche, magnésium)")
        if steps > 0 and steps < 5000:
            feedback.append("⚠️ Activité spontanée basse (<5000 pas)")

        return (
            "✅ Daily check loggué : " + " · ".join(parts) +
            ("\n\n" + "\n".join(feedback) if feedback else "") +
            "\n\nTu peux maintenant utiliser ces données dans tes conseils du jour."
        )

    @beta_tool
    def get_streak() -> str:
        """Compute the user's current logging streak: consecutive days with at \
least 1 meal logged. Use proactively to gamify / motivate. Mention the \
streak in responses when it's >5 days (encourages continuity)."""
        from datetime import datetime, timedelta, timezone
        # Pull last 60 days of meals
        since = (datetime.now(timezone.utc) - timedelta(days=60)).strftime("%Y-%m-%d")
        meals = db.meals_since(user_id, since)
        if not meals:
            return "Aucun repas loggué récemment. Streak = 0."
        # Collect distinct days
        days = sorted({(m.get("eaten_at") or "")[:10] for m in meals if m.get("eaten_at")}, reverse=True)
        if not days:
            return "Aucun repas loggué récemment. Streak = 0."
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")
        # Streak is broken if neither today nor yesterday has a log (1-day grace)
        if days[0] not in (today, yesterday):
            return f"Streak rompue. Dernier log : {days[0]}."
        streak = 1
        cursor = datetime.strptime(days[0], "%Y-%m-%d")
        for d in days[1:]:
            prev = datetime.strptime(d, "%Y-%m-%d")
            if (cursor - prev).days == 1:
                streak += 1
                cursor = prev
            else:
                break
        emoji = "🔥" if streak >= 7 else "💪" if streak >= 3 else "👍"
        return (
            f"{emoji} **Streak actuelle : {streak} jours consécutifs** avec au moins un repas loggué. "
            f"Dernier log : {days[0]}. "
            + ("Continue, casse pas la chaîne." if streak >= 3 else "Encourage à continuer.")
        )

    @beta_tool
    def suggest_habit_stack() -> str:
        """Suggest ONE micro-habit tailored to the user's current profile + \
patterns. Use when the user wants progress without big effort, or when \
sleep/hydration/activity ratings are low. The science: tiny habits compound."""
        user = db.get_user_by_id(user_id)
        if not user:
            return "User not found."
        candidates: list[tuple[str, str, int]] = []  # (habit, why, priority)

        sleep = user.get("sleep_quality") or 3
        stress = user.get("stress_level") or 3
        goal = user.get("goal", "maintain")
        metabolic = (user.get("metabolic_type") or "").lower()

        if sleep <= 2:
            candidates.append((
                "Verre d'eau au réveil + lumière naturelle 5 min",
                "Réinitialise le rythme circadien. Dormir mieux le soir commence le matin.",
                5,
            ))
            candidates.append((
                "Pas d'écran 30 min avant coucher",
                "Mélatonine ↑. Effet visible dès la 3e nuit.",
                5,
            ))
        if stress >= 4:
            candidates.append((
                "Respiration 4-7-8 : 3 cycles avant chaque repas",
                "Active le parasympathique. Mange en mode digestion, pas en mode survie.",
                4,
            ))
            candidates.append((
                "10 min marche sans téléphone après le déjeuner",
                "Glycémie ↓, stress ↓, cortisol ↓. Le plus sous-estimé.",
                4,
            ))
        if goal == "lose":
            candidates.append((
                "Protéines à CHAQUE repas (paume de main minimum)",
                "Satiété, perte de muscle prévenue. Le réflexe n°1 de la perte durable.",
                5,
            ))
            candidates.append((
                "Légumes en 1er dans l'assiette",
                "Fibres mangées d'abord = glycémie stable + satiété précoce.",
                3,
            ))
        if "ménopause" in metabolic or (user.get("sex") == "F" and (user.get("age") or 0) >= 45):
            candidates.append((
                "1 portion de protéines AU PETIT-DÉJ (30g)",
                "Sarcopénie = ennemi n°1 en ménopause. Le PD est le levier le + facile.",
                5,
            ))
            candidates.append((
                "2 séances muscu/sem dans l'agenda (rendez-vous bloqué)",
                "Sans bloc agenda, ça ne se fait pas. C'est la priorité ménopause.",
                5,
            ))

        # Generic add-ons
        candidates.append((
            "Bouteille d'eau 1L visible sur ton bureau",
            "Visuel = 2L/jour atteints sans y penser.",
            3,
        ))
        candidates.append((
            "Photo de chaque repas, même rapide",
            "Le simple acte de photographier réduit l'apport de 10-15% (étudié).",
            3,
        ))
        candidates.append((
            "1 fruit ENTIER à porte de main (frigo, sac)",
            "Snack par défaut = fruit, pas chips. La friction décide.",
            2,
        ))

        candidates.sort(key=lambda c: -c[2])
        habit, why, _ = candidates[0]
        return (
            f"# 🌱 Ta micro-habitude de la semaine\n\n"
            f"**{habit}**\n\n"
            f"_Pourquoi_ : {why}\n\n"
            f"💡 Pas 10 habitudes en même temps. UNE seule, 7 jours. "
            f"Ensuite on en ajoute une nouvelle. Engage-toi : tu fais quoi "
            f"pour la déclencher AU MÊME MOMENT chaque jour ?"
        )

    @beta_tool
    def detect_trigger_foods() -> str:
        """Analyse the user's meal history + memories + patterns to surface \
foods/situations that consistently lead to drift (over-eating, plateau, \
poor sleep). Use when the user feels stuck or asks 'qu'est-ce qui me \
plombe ?'. Returns a curated list of suspected triggers + actions."""
        user = db.get_user_by_id(user_id)
        if not user:
            return "User not found."

        # Pull last 30 days of meals
        from datetime import datetime, timedelta, timezone
        since = (datetime.now(timezone.utc) - timedelta(days=30)).strftime("%Y-%m-%d")
        meals = db.meals_since(user_id, since)

        # Heuristic detection
        triggers: list[str] = []

        # Detect frequent high-calorie items
        item_counts: dict[str, list[int]] = {}
        for m in meals:
            for item in (m.get("items") or []):
                name = (item.get("name") or "").lower()
                kcal = int(item.get("kcal", 0) or 0)
                if name and kcal > 0:
                    item_counts.setdefault(name, []).append(kcal)

        # Find items appearing 5+ times with avg kcal > 200
        for name, kcals in item_counts.items():
            if len(kcals) >= 5 and sum(kcals) / len(kcals) >= 200:
                triggers.append(
                    f"🍴 **{name.capitalize()}** apparait {len(kcals)}x ce mois "
                    f"(moy {int(sum(kcals)/len(kcals))} kcal). À vérifier : "
                    f"est-ce un réflexe automatique ?"
                )

        # Detect evening meal heaviness (>40% of daily kcal post-19h)
        # Simplified: count meals after 19h
        late_meals_kcal = []
        all_meals_kcal = []
        for m in meals:
            ts = m.get("eaten_at") or ""
            try:
                h = int(ts[11:13])
                kcal = int(m.get("total_calories") or 0)
                all_meals_kcal.append(kcal)
                if h >= 19:
                    late_meals_kcal.append(kcal)
            except (ValueError, IndexError):
                continue
        if late_meals_kcal and all_meals_kcal:
            late_avg = sum(late_meals_kcal) / len(late_meals_kcal)
            all_avg = sum(all_meals_kcal) / len(all_meals_kcal)
            if late_avg > all_avg * 1.4:
                triggers.append(
                    f"🌙 **Dîners chargés** : tes repas du soir font en moyenne "
                    f"{int(late_avg)} kcal vs {int(all_avg)} kcal/repas. "
                    f"Décalage de l'apport vers la fin de journée = plateau probable."
                )

        # Look at memories for behavioral patterns
        memories = db.memories_for_user(user_id, limit=50)
        alcohol_signals = sum(
            1 for m in memories
            if any(w in (m.get("memory") or "").lower() for w in ("alcool", "verre", "vin", "bière", "apéro"))
        )
        if alcohol_signals >= 3:
            triggers.append(
                f"🍷 **Alcool revient {alcohol_signals}x** dans tes souvenirs/échanges. "
                f"Si plateau : tester 21 jours sans = test de causalité simple."
            )

        if not triggers:
            return (
                "Pas de trigger flagrant détecté dans les 30 derniers jours. "
                "C'est plutôt bon signe : ta consommation est variée. Si tu te "
                "sens bloqué, le facteur est peut-être hors alimentaire "
                "(sommeil, stress, cycle, hormones). Lance "
                "`analyze_progress` + `decode_symptom` pour creuser."
            )

        return (
            "# 🔍 Triggers détectés (30 derniers jours)\n\n"
            + "\n\n".join(triggers)
            + "\n\n💡 Présente ces constats SANS jugement. Demande à "
            "l'utilisateur quels patterns lui parlent. Choisis UN trigger à "
            "tester (élimination 21 jours, observation) avant d'en attaquer un autre."
        )

    @beta_tool
    def generate_client_report(weeks: int = 4) -> str:
        """⚠️ TOOL POUR LE COACH (Damien), pas pour le client final. Génère un \
résumé pro de l'état d'un client sur les N dernières semaines. Utilisable \
quand Damien lui-même cause à Calo via WhatsApp pour avoir une vue rapide \
sur un de ses clients.

Args:
    weeks: Période à analyser (1-12). Default 4.
"""
        user = db.get_user_by_id(user_id)
        if not user:
            return "User not found."
        weeks = max(1, min(12, int(weeks)))
        from datetime import datetime, timedelta, timezone
        since = (datetime.now(timezone.utc) - timedelta(days=weeks * 7)).strftime("%Y-%m-%d")
        meals = db.meals_since(user_id, since)
        weights = db.weights_history(user_id, limit=weeks * 2)
        memories = db.memories_for_user(user_id, limit=10)

        report = [
            f"# 📋 Bilan client — {user.get('name')} ({weeks} sem)",
            "",
            f"## Profil",
            f"- {user.get('sex')} · {user.get('age')} ans · {user.get('height_cm')} cm",
            f"- Poids actuel : {user.get('current_weight_kg')} kg "
            f"(cible {user.get('target_weight_kg') or '?'} kg)",
            f"- Objectif : {user.get('goal')}",
            f"- Type métabolique : {user.get('metabolic_type') or 'non évalué'}",
            f"- Ajustement perso : {int((user.get('calorie_adjustment') or 1) * 100)}% vs textbook",
        ]

        if user.get("medical_conditions"):
            report.append(f"- Pathologies : {user.get('medical_conditions')}")
        if user.get("current_meds"):
            report.append(f"- Médicaments : {user.get('current_meds')}")

        # Activity
        report.append(f"\n## Activité {weeks} sem")
        report.append(f"- Repas loggués : {len(meals)}")
        report.append(f"- Pesées : {len(weights)}")

        if weights and len(weights) >= 2:
            latest = float(weights[0]["weight_kg"] or 0)
            oldest = float(weights[-1]["weight_kg"] or 0)
            delta = latest - oldest
            sign = "+" if delta >= 0 else ""
            report.append(f"- Variation poids : {sign}{delta:.1f} kg")

        if meals:
            avg_kcal = sum(int(m.get("total_calories") or 0) for m in meals) // max(1, len(meals))
            avg_meals_day = len(meals) / (weeks * 7)
            report.append(f"- Moyenne kcal/repas : {avg_kcal}")
            report.append(f"- Moyenne repas/jour : {avg_meals_day:.1f}")

        # Engagement
        sleep = user.get("sleep_quality") or 0
        stress = user.get("stress_level") or 0
        report.append(f"\n## Lifestyle")
        report.append(f"- Sommeil : {sleep}/5" if sleep else "- Sommeil : non renseigné")
        report.append(f"- Stress : {stress}/5" if stress else "- Stress : non renseigné")

        # Recent memories (key context)
        if memories:
            report.append(f"\n## Faits clés mémorisés (top 5)")
            for m in memories[:5]:
                stars = "★" * int(m.get("importance") or 3)
                report.append(f"- {m.get('memory')} {stars}")

        # Patterns
        if user.get("personal_patterns"):
            report.append(f"\n## Patterns personnels")
            report.append(user.get("personal_patterns"))

        # Coach action items
        report.append(f"\n## 🎯 Recommandations coach")
        actions: list[str] = []
        if sleep and sleep <= 2:
            actions.append("🛌 Sommeil <2/5 — adresser en priorité (cortisol bloque tout)")
        if stress and stress >= 4:
            actions.append("⚡ Stress ≥4/5 — gestion stress avant déficit")
        if len(meals) < weeks * 5:
            actions.append("📸 Engagement faible (<5 repas/sem) — relancer ou diminuer la friction")
        if weights and len(weights) < weeks // 2:
            actions.append("⚖️ Pesées rares — proposer rituel hebdo fixe (J7 cycle)")
        if user.get("metabolic_type") in (None, "", "non évalué"):
            actions.append("🧬 Type métabolique pas encore classifié — observer 1-2 sem de plus")
        if user.get("calorie_adjustment") and user.get("calorie_adjustment") < 0.85:
            actions.append("🐢 Métabolisme adapté (-15%+) — diet break envisageable")

        if actions:
            report.extend(actions)
        else:
            report.append("✅ Tout est sous contrôle. Maintenir le rythme.")

        return "\n".join(report)

    @beta_tool
    def check_milestones() -> str:
        """Check for goal milestones reached and return what to celebrate. \
Call this PROACTIVELY when the user logs a weight, completes a challenge \
phase, or weekly. Helps with motivation/retention.

Detects:
- Premiers -1kg / -3kg / -5kg / -10kg
- 25% / 50% / 75% / 100% du chemin vers la cible
- 1 semaine / 1 mois / 3 mois / 6 mois d'engagement
- Streak de logs (7/30/100 repas consécutifs)
"""
        user = db.get_user_by_id(user_id)
        if not user:
            return "User not found."

        weights = db.weights_history(user_id, limit=100)
        if len(weights) < 2:
            return "Pas assez de mesures pour des jalons (besoin de 2 pesées+)."

        # Sort weights ascending by logged_at
        weights_sorted = list(reversed(weights))
        start_weight = float(weights_sorted[0]["weight_kg"] or 0)
        current_weight = float(weights_sorted[-1]["weight_kg"] or 0)
        target_weight = float(user.get("target_weight_kg") or current_weight)
        goal = user.get("goal", "maintain")

        loss = start_weight - current_weight
        total_to_lose = start_weight - target_weight
        progress_pct = (
            int(loss / total_to_lose * 100) if total_to_lose > 0 else 0
        )

        # Days since first weight
        from datetime import datetime, timezone
        try:
            first_dt = datetime.fromisoformat(
                weights_sorted[0]["logged_at"].replace("Z", "+00:00")
            )
            days_engaged = (datetime.now(timezone.utc) - first_dt).days
        except (ValueError, TypeError, KeyError):
            days_engaged = 0

        achievements: list[str] = []

        if goal == "lose":
            for milestone in (1, 3, 5, 10, 15, 20):
                if loss >= milestone:
                    achievements.append(f"🏆 **-{milestone} kg perdus** depuis le début")
            for pct in (25, 50, 75, 100):
                if progress_pct >= pct:
                    achievements.append(
                        f"🎯 **{pct}% du chemin** vers ta cible "
                        f"({current_weight} kg → cible {target_weight} kg)"
                    )
        elif goal == "gain":
            gain = current_weight - start_weight
            for milestone in (1, 3, 5, 10):
                if gain >= milestone:
                    achievements.append(f"🏆 **+{milestone} kg gagnés**")

        for d in (7, 30, 90, 180, 365):
            if days_engaged >= d:
                achievements.append(
                    f"💪 **{d} jours d'engagement** ({d//30}m si applicable)"
                )

        # Count meals logged
        try:
            recent_meals = db.meals_since(
                user_id,
                (datetime.now(timezone.utc) - __import__("datetime").timedelta(days=days_engaged or 30)).strftime("%Y-%m-%d"),
            )
            meal_count = len(recent_meals)
            for m in (10, 50, 100, 250, 500):
                if meal_count >= m:
                    achievements.append(f"📸 **{m} repas loggués** au compteur")
        except Exception:
            pass

        if not achievements:
            return (
                "Pas de nouveau milestone à célébrer pour l'instant. "
                "Continue d'encourager dans le quotidien."
            )

        # Pick only the 1-2 most recent / impactful to avoid overload
        return (
            "🎉 Jalons atteints — célèbre-les AVEC l'utilisateur :\n\n"
            + "\n".join(achievements[-3:])  # 3 most recent
            + "\n\nUtilise UN ou DEUX de ces jalons dans ta réponse, "
            "pas tous. Personnalise (utilise son prénom, rappelle son point "
            "de départ). Si c'est un jalon majeur (-5kg, 50%, 3 mois), "
            "marque vraiment le coup."
        )

    @beta_tool
    def travel_mode(
        destination: str,
        days: int,
        travel_type: str = "loisir",
    ) -> str:
        """Adapt Calo's coaching to a travel period. Call when the user says \
"je pars en voyage", "vacances", "déplacement pro", "weekend escapade". \
Returns a structured travel-adapted plan respecting the user's profile.

Args:
    destination: Country or region (e.g. 'Marrakech', 'Italie', 'New York', \
'Bali', 'séminaire Lyon'). Used to anticipate food culture.
    days: Number of days of travel.
    travel_type: 'loisir' | 'business' | 'famille' | 'sportif' | 'détox'.
"""
        user = db.get_user_by_id(user_id)
        if not user:
            return "User not found."
        goal = user.get("goal", "maintain")
        name = user.get("name", "")

        # Strategy depends on duration and travel type
        if days <= 3:
            mode = "maintien strict"
            kcal_mod = "Reste sur tes cibles, c'est court."
        elif days <= 7:
            mode = "flex sans culpabilité"
            kcal_mod = (
                "Cible MAINTIEN (pas perte). Profite culture locale 1-2 fois, "
                "le reste structuré."
            )
        elif days <= 14:
            mode = "rythme balanced"
            kcal_mod = (
                "Maintien semaine 1, possibilité petit déficit semaine 2 si "
                "tu vois la balance bouger. PRIORITÉ : ne pas reprendre."
            )
        else:
            mode = "vie locale, on s'adapte"
            kcal_mod = (
                "C'est presque un déménagement. On bascule sur un objectif "
                "MAINTIEN strict avec recalibration possible si activité change."
            )

        report = [
            f"# 🧳 Mode voyage activé · {destination} · {days}j ({travel_type})",
            f"",
            f"## Stratégie : {mode}",
            kcal_mod,
            f"",
            "## Les 7 règles voyage Calo",
            "**1. Petit-déj PROTÉINÉ obligatoire** (œufs / yaourt grec / charcuterie maigre). "
            "Cale le reste de la journée et limite les craquages.",
            "**2. 1 repas culturel/jour** — fais-toi plaisir au déjeuner OU au dîner, "
            "pas les deux + dessert + apéro.",
            "**3. Hydratation MAX** (3L/jour mini). Voyage = déshydratation cachée "
            "(climatisation, alcool, climat sec/chaud).",
            "**4. Marche +++ ** : 12000+ pas/jour visent. Visite à pied, ça compense "
            "naturellement les écarts.",
            "**5. Alcool stratégique** : choisis tes verres. 2-3 verres/sem max si "
            "objectif perte. Vin sec > cocktails sucrés > bière.",
            "**6. 0 grignotage avion/route** : prépare 1 sandwich complet + fruits + "
            "amandes. Les sandwiches aéroport = pièges à 700+ kcal.",
            "**7. Photo systématique** : continue à m'envoyer tes repas. Pas de "
            "jugement, juste pour qu'on garde le rythme et qu'on évite la dérive.",
        ]

        # Cuisine-specific tips
        dest_lower = destination.lower()
        cuisine_tip = ""
        if any(x in dest_lower for x in ["italie", "ital", "rome", "milan"]):
            cuisine_tip = (
                "🇮🇹 **Italie** : focus poisson grillé, antipasti légumes, salade caprese. "
                "Pizza margherita partagée OK. Évite la carbonara grande portion + tiramisu."
            )
        elif any(x in dest_lower for x in ["marrakech", "maroc", "tunisie", "tunis"]):
            cuisine_tip = (
                "🇲🇦 **Maghreb** : tajine poulet/poisson EXCELLENT (peu gras), "
                "salades méchouia/zaalouk. Évite les pâtisseries au miel quotidiennes."
            )
        elif any(x in dest_lower for x in ["bali", "thailand", "thaïlande", "vietnam"]):
            cuisine_tip = (
                "🌴 **Asie du SE** : phở, salades thaï, poisson grillé + riz. "
                "Évite pad thaï + smoothie sucré + dessert tous les jours."
            )
        elif any(x in dest_lower for x in ["new york", "usa", "états-unis", "etats-unis"]):
            cuisine_tip = (
                "🇺🇸 **USA** : portions XXL. Partage tout. Choisis 'lunch portion' si dispo. "
                "Bowls poke/Sweetgreen plutôt que diners."
            )
        elif any(x in dest_lower for x in ["mexique", "mexico", "cuba"]):
            cuisine_tip = (
                "🌶️ **Amérique latine** : ceviche TOP, tacos al pastor OK, fajitas. "
                "Évite burrito XXL + nachos + margaritas XL combo."
            )
        if cuisine_tip:
            report.append(f"\n## Culture locale\n{cuisine_tip}")

        report.append(
            f"\n💡 {name}, propose à l'utilisateur que tu reprennes le check-in "
            f"complet J+1 du retour pour évaluer impact + relancer le rythme."
        )

        # Save as memory for later reference
        db.add_memory(
            user_id,
            f"Voyage {destination} {days}j ({travel_type}) — mode {mode}",
            category="événement",
            importance=3,
        )
        return "\n".join(report)

    @beta_tool
    def prepare_for_event(
        event_type: str,
        days_until: int,
        event_name: str = "",
    ) -> str:
        """Build a countdown protocol before an important event. Call when the \
user mentions "mariage", "vacances plage", "shooting photo", "compétition", \
"date importante", "anniversaire 40 ans", etc.

Args:
    event_type: 'mariage' | 'plage' | 'photo' | 'compétition' | 'social' | \
'shoot' | 'date'.
    days_until: Days remaining until the event.
    event_name: Optional description (e.g. 'Mariage frère 14 juin').
"""
        user = db.get_user_by_id(user_id)
        if not user:
            return "User not found."
        weight = float(user.get("current_weight_kg") or 70)

        report = [f"# 🎯 Protocole {event_type.upper()} — J-{days_until}"]
        if event_name:
            report.insert(0, f"# Event : {event_name}")

        # Strategy by timeline
        if days_until >= 60:
            phase = "Phase 1 — Construction (J-60+)"
            plan = (
                "Tu as le TEMPS. Approche durable : déficit doux -300 kcal, "
                "muscu 3x/sem, sommeil 7h+. Objectif réaliste : -3 à -5 kg sur "
                f"{days_until // 7} semaines. Pas de panique, c'est gagné."
            )
        elif days_until >= 28:
            phase = "Phase 2 — Push (J-30 à J-60)"
            plan = (
                "Tu peux encore faire bouger les choses. Déficit -400 kcal, "
                "muscu 4x/sem, +1 HIIT, hydratation 3L. Objectif : -2 à -4 kg "
                "+ raffermissement visible."
            )
        elif days_until >= 14:
            phase = "Phase 3 — Affûte (J-14 à J-30)"
            plan = (
                "On serre. Déficit -500 kcal, glucides modérés focus pré/post "
                "training, élimination alcool, sodium contrôlé. -1.5 à -2.5 kg "
                "réaliste."
            )
        elif days_until >= 7:
            phase = "Phase 4 — Peak Week (J-7 à J-14)"
            plan = (
                "Stratégie pro :\n"
                "- J-14 à J-8 : maintien strict, hydratation 4L, 0 alcool, "
                "carbs moyens\n"
                "- J-7 à J-4 : déplétion glucides douce (-30%), sodium normal\n"
                "- J-3 à J-1 : recharge glucides intelligents + sodium en baisse"
            )
        elif days_until >= 3:
            phase = "Phase 5 — Last Days (J-3)"
            plan = (
                "Plus de gains massifs possibles, c'est de la finition :\n"
                "- Glucides modérés (200g/j)\n"
                "- Sodium réduit (pas de plats industriels)\n"
                "- Hydratation 3-4L jusque J-2, puis 2L J-1\n"
                "- 0 alcool, 0 légumineuses (ballonnements)\n"
                "- Sommeil 8h+"
            )
        else:
            phase = "Phase 6 — Jour J / Veille"
            plan = (
                "Veille : repas léger, sans légumineuses ni crucifères. "
                "Hydratation normale. Bonne nuit. Le matin : protéine + fruits, "
                "peu de glucides. Pas d'expérimentation. **Tu profites.**"
            )

        report.append(f"\n## {phase}")
        report.append(plan)

        # Event-specific tweaks
        event_tips = {
            "mariage": (
                "💍 **Mariage** : tu vas marcher, danser, peu manger pendant la "
                "cérémonie. Préparation cardio + hydratation. Évite la 'crise "
                "préparatifs' qui dérègle sommeil + cortisol."
            ),
            "plage": (
                "🏖️ **Plage** : focus définition + ventre plat. Anti-bloat 48h "
                "avant : 0 légumineuses, 0 crucifères, 0 sodas, 0 alcool. "
                "Crème solaire bien sûr, et pose mémorable !"
            ),
            "photo": (
                "📸 **Shoot** : peak week classique (déplétion + recharge). "
                "Sommeil parfait la veille (visage frais). Eau citronnée le "
                "matin (drainage)."
            ),
            "compétition": (
                "🏆 **Compétition sportive** : pre-fuel J-1 + jour J (glucides "
                "complexes 6-7g/kg). Hydratation 35-40 ml/kg + électrolytes. "
                "Pas d'expérimentation. Repos J-1."
            ),
            "social": (
                "🎉 **Événement social** : la pression sociale fait souvent "
                "craquer. Mange un repas léger AVANT pour ne pas arriver "
                "affamé. Choisis tes verres."
            ),
        }
        if event_type.lower() in event_tips:
            report.append(f"\n## Spécifique\n{event_tips[event_type.lower()]}")

        report.append(
            "\n💡 Engage l'utilisateur : qu'il visualise l'événement, c'est ce "
            "qui maintient la motivation. Photo J-30, J-14, J-3 pour mesurer "
            "le chemin parcouru."
        )

        # Save as memory
        db.add_memory(
            user_id,
            f"Protocole événement {event_type} — J-{days_until}"
            + (f" ({event_name})" if event_name else ""),
            category="événement",
            importance=4,
        )

        return "\n".join(report)

    @beta_tool
    def compare_body_photos() -> str:
        """Compare the latest body photo with the previous one. Use this when \
the user sends a new body photo AND a prior one exists. Returns the previous \
analysis text so you can visually compare the current image with what was \
observed before. NEVER guess if no previous exists; just analyse the new one."""
        photos = db.body_photos_for_user(user_id)
        if len(photos) < 2:
            return (
                "Pas de photo précédente à comparer (c'est la 1ère ou la 2e). "
                "Fais juste une analyse complète de la photo actuelle et "
                "sauvegarde-la via log_body_photo. La comparaison se fera la "
                "prochaine fois."
            )
        # photos are sorted by captured_at desc; [0] is latest, [1] is previous
        prev = photos[1]
        return (
            f"## Photo précédente ({prev.get('captured_at')})\n"
            f"Angle : {prev.get('angle', '?')}\n"
            f"Semaine #{prev.get('week_number', '?')}\n\n"
            f"### Analyse précédente\n"
            f"{prev.get('analysis') or '(pas d analyse texte)'}\n\n"
            f"---\n\n"
            f"**À toi de comparer** : regarde la photo qui vient d'être envoyée "
            f"et l'analyse ci-dessus. Note les évolutions positives concrètes "
            f"(définition, tonus, posture) et les zones en cours. Reste "
            f"factuel, encourageant, jamais culpabilisant. Sauve l'analyse "
            f"comparative via log_body_photo."
        )

    @beta_tool
    def start_anamnese() -> str:
        """Start a 7-day baseline food assessment (anamnèse) for the user. \
PROPOSE THIS PROACTIVELY in two situations:

1. **At the END of onboarding** (after `complete_profile`) : "Avant qu'on \
attaque, j'aimerais avoir une photo réelle de comment tu manges. Pendant \
7 jours, envoie-moi TOUT — chaque repas, snack, boisson (eau, café, alcool, \
sodas), même les petits grignotages. Pas de jugement, c'est notre baseline. \
Après je te fais un debrief PRO avec un plan calibré sur TOI."

2. **Quand l'utilisateur est bloqué et que tu doutes de sa déclaration** : \
"On va remettre à plat. 7 jours d'anamnèse stricte, on saura exactement \
où on en est et je recalibre."

L'anamnèse est CRUCIALE : les gens sous-déclarent en moyenne de 30%. \
La formule TDEE ne sert à rien si la consommation réelle est inconnue. \
C'est aussi un moment d'engagement fort (le client sent un vrai suivi pro)."""
        from datetime import datetime, timezone
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        db.update_user(user_id, anamnese_started=today)
        db.add_memory(
            user_id,
            f"Anamnèse 7 jours démarrée le {today}",
            category="objectif",
            importance=4,
        )
        return (
            f"✅ Anamnèse démarrée ({today}). Pendant 7 jours, demande à "
            f"l'utilisateur de logger TOUT (repas, snacks, boissons, alcool, "
            f"sauces, grignotages). Pas de jugement. À J7-J8, appelle "
            f"`analyze_anamnese` pour le debrief structuré."
        )

    @beta_tool
    def analyze_anamnese(days: int = 7) -> str:
        """Analyse the user's last N days of food logs as a professional dietitian \
would do for a first consultation. Returns averages, patterns, suspected \
under-reporting, macro distribution, meal frequency, weekend variance, \
and the FIRST diagnostic + adjustment proposal.

Call this 7-8 days after `start_anamnese` (or whenever the user asks for a \
"bilan", "où j'en suis", "qu'est-ce que je devrais changer").

Args:
    days: Number of days to analyse. Default 7. Min 3, max 14.
"""
        from datetime import datetime, timedelta, timezone
        days = max(3, min(14, int(days)))
        user = db.get_user_by_id(user_id)
        if not user or not user.get("onboarding_complete"):
            return "Onboarding incomplet. Calo doit d'abord compléter le profil."

        since = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")
        meals = db.meals_since(user_id, since)
        if len(meals) < 3:
            return (
                f"Pas assez de repas loggués sur les {days} derniers jours "
                f"({len(meals)} trouvés). Relance l'utilisateur pour qu'il "
                f"continue à logger, on refera le bilan dans qq jours."
            )

        # Group by day
        by_day: dict[str, list[dict[str, Any]]] = {}
        for m in meals:
            day = (m.get("eaten_at") or "")[:10]
            if day:
                by_day.setdefault(day, []).append(m)

        days_with_data = sorted(by_day.keys())
        actual_days = len(days_with_data)

        # Compute totals per day
        day_totals = []
        for day in days_with_data:
            day_meals = by_day[day]
            kcal = sum(int(m.get("total_calories") or 0) for m in day_meals)
            p = sum(int(m.get("total_protein_g") or 0) for m in day_meals)
            c = sum(int(m.get("total_carbs_g") or 0) for m in day_meals)
            f = sum(int(m.get("total_fat_g") or 0) for m in day_meals)
            day_totals.append({
                "day": day,
                "kcal": kcal, "p": p, "c": c, "f": f,
                "meal_count": len(day_meals),
            })

        avg_kcal = sum(d["kcal"] for d in day_totals) // actual_days
        avg_p = sum(d["p"] for d in day_totals) // actual_days
        avg_c = sum(d["c"] for d in day_totals) // actual_days
        avg_f = sum(d["f"] for d in day_totals) // actual_days
        avg_meals = sum(d["meal_count"] for d in day_totals) / actual_days
        min_kcal = min(d["kcal"] for d in day_totals)
        max_kcal = max(d["kcal"] for d in day_totals)
        variance_kcal = max_kcal - min_kcal

        # Weekend vs weekday
        weekday_kcal = []
        weekend_kcal = []
        for d in day_totals:
            try:
                dt = datetime.strptime(d["day"], "%Y-%m-%d")
                if dt.weekday() >= 5:
                    weekend_kcal.append(d["kcal"])
                else:
                    weekday_kcal.append(d["kcal"])
            except ValueError:
                pass
        avg_weekday = sum(weekday_kcal) // len(weekday_kcal) if weekday_kcal else 0
        avg_weekend = sum(weekend_kcal) // len(weekend_kcal) if weekend_kcal else 0

        # Compare to textbook TDEE
        textbook_kcal = int(user.get("daily_calories") or 0)
        gap_pct = (
            int((avg_kcal - textbook_kcal) / textbook_kcal * 100)
            if textbook_kcal else 0
        )

        # Macro distribution (% of kcal)
        protein_pct = round(avg_p * 4 / avg_kcal * 100) if avg_kcal else 0
        carbs_pct = round(avg_c * 4 / avg_kcal * 100) if avg_kcal else 0
        fat_pct = round(avg_f * 9 / avg_kcal * 100) if avg_kcal else 0

        # Protein per kg
        weight = float(user.get("current_weight_kg") or 70)
        p_per_kg = round(avg_p / weight, 1)

        # Diagnostic flags
        flags: list[str] = []
        if avg_kcal < textbook_kcal * 0.75 and user.get("goal") == "lose":
            flags.append(
                "⚠️ **SOUS-DÉCLARATION PROBABLE** : tu déclares avg "
                f"{avg_kcal} kcal/j (vs cible {textbook_kcal}). "
                "Si la perte n'arrive pas, c'est qu'il manque des items dans le log "
                "(grignotages, boissons sucrées, alcool, sauces, 'goûter du plat')."
            )
        if p_per_kg < 1.2:
            flags.append(
                f"⚠️ **PROTÉINES INSUFFISANTES** : {p_per_kg}g/kg (cible "
                f"{'1.8-2.0' if user.get('goal') in ('lose', 'gain') else '1.4-1.8'}g/kg). "
                "Manque de satiété + risque perte musculaire."
            )
        if fat_pct > 40:
            flags.append(
                f"⚠️ **TROP DE LIPIDES** : {fat_pct}% des kcal (cible 25-35%). "
                "Souvent dû aux sauces, fromages, charcuteries cachés."
            )
        if avg_meals < 3:
            flags.append(
                f"⚠️ **TROP PEU DE REPAS** : {avg_meals:.1f}/jour. Risque de craquage soir."
            )
        if variance_kcal > 700:
            flags.append(
                f"⚠️ **VARIANCE ÉNORME** : du jour le plus light au plus chargé "
                f"= {variance_kcal} kcal d'écart. Manque de structure."
            )
        if weekend_kcal and weekday_kcal and avg_weekend > avg_weekday + 400:
            flags.append(
                f"⚠️ **WEEK-END EXPLOSIF** : +{avg_weekend - avg_weekday} kcal/j "
                "vs semaine. C'est souvent là que disparaît le déficit."
            )

        # Build report
        report = [
            f"# 📊 Bilan anamnèse {actual_days} jours",
            "",
            f"## Moyennes quotidiennes",
            f"- **{avg_kcal} kcal/jour** (vs cible {textbook_kcal} = {gap_pct:+d}%)",
            f"- Protéines : {avg_p}g ({protein_pct}% · {p_per_kg}g/kg)",
            f"- Glucides : {avg_c}g ({carbs_pct}%)",
            f"- Lipides : {avg_f}g ({fat_pct}%)",
            f"- Repas/jour : {avg_meals:.1f}",
            "",
            f"## Variation jour à jour",
            f"- Plus light : {min_kcal} kcal",
            f"- Plus chargé : {max_kcal} kcal",
            f"- Écart : {variance_kcal} kcal",
        ]
        if weekend_kcal and weekday_kcal:
            report.append(f"- Semaine : {avg_weekday} kcal/j · Week-end : {avg_weekend} kcal/j")

        if flags:
            report.append("\n## 🔍 Diagnostic")
            for f in flags:
                report.append(f"\n{f}")

        report.append(
            "\n## 🎯 Action recommandée"
            "\nPrésente ces constats à l'utilisateur AVEC empathie (pas accusateur)."
            " Propose 1-2 ajustements MAX, jamais 5 à la fois."
            " Mets à jour `personal_patterns` avec les insights découverts via"
            " `update_metabolic_profile`. Si l'écart vs textbook est marqué, propose"
            " une `recalibrate_calories` justifiée."
        )

        return "\n".join(report)

    @beta_tool
    def update_metabolic_profile(
        metabolic_history: str = "",
        metabolic_type: str = "",
        prior_diets_tried: str = "",
        lifetime_lowest_kg: float = 0,
        lifetime_highest_kg: float = 0,
        current_meds: str = "",
        medical_conditions: str = "",
        digestive_profile: str = "",
        sleep_quality: int = 0,
        stress_level: int = 0,
        personal_patterns: str = "",
    ) -> str:
        """Enrich the user's adaptive metabolic profile. Call this PROACTIVELY \
whenever the user shares ANY of the following during conversation. NEVER ask \
all of these at once — weave them into natural conversation across days/weeks. \
For free-text fields, APPEND to existing content (don't overwrite) — pass the \
COMPLETE new text including the previous content. Pass only what's new this turn.

WHEN to call:
- User mentions a prior diet → fill `prior_diets_tried`
- User mentions thyroid, SOPK, diabetes, endometriosis, IBS, IBD, NASH... → \
  `medical_conditions` AND consider `metabolic_type` = "lent - hormonal..."
- User mentions medications (anti-depressants, statins, thyroid hormones, \
  contraception, corticosteroids, insulin) → `current_meds`
- User mentions yo-yo, ED recovery, post-partum, hormonal events → \
  `metabolic_history`
- User mentions her lowest/highest adult weight → `lifetime_lowest_kg` / \
  `lifetime_highest_kg`
- User mentions bloating, lactose, gluten, FODMAP → `digestive_profile`
- User reports sleep quality / stress level → ratings
- User reveals a personal pattern ("je reprends 2kg dès que je bois") → \
  `personal_patterns`
- After 2-3 weeks of observation you classify their metabolic type → set it

Args:
    metabolic_history: New narrative entry to append (e.g. 'Yo-yo 2018-2024, \
4 régimes successifs, perte muscle estimée -3kg').
    metabolic_type: 'rapide' | 'normal' | 'lent - régimes à répétition' | \
'lent - hormonal (thyroïde, SOPK)' | 'lent - ménopause' | 'résistance insuline' \
| 'récupération TCA' | 'athlète entraîné'.
    prior_diets_tried: New entry to append (e.g. 'Keto 6 mois 2022 -8kg puis \
+12kg en 4 mois').
    lifetime_lowest_kg: Adult lifetime minimum weight.
    lifetime_highest_kg: Adult lifetime maximum weight.
    current_meds: Medications + brief reason (e.g. 'Lévothyrox 75µg matin \
(Hashimoto)').
    medical_conditions: Diagnosed conditions (e.g. 'Hashimoto diagnostiqué 2019').
    digestive_profile: Intolerances, symptoms (e.g. 'Ballonnements quotidiens \
soir, intolérance lactose probable').
    sleep_quality: Rating 1-5 (1 horrible, 5 excellent).
    stress_level: Rating 1-5 (1 zen, 5 stress chronique).
    personal_patterns: Pattern observed (e.g. 'Reprend +2kg dès qu'elle boit \
3 verres / sem').
"""
        updates: dict[str, Any] = {}

        # For free-text append-style fields, fetch current value and append
        current = db.get_user_by_id(user_id) if any(
            v for v in (metabolic_history, prior_diets_tried, current_meds,
                        medical_conditions, digestive_profile, personal_patterns)
        ) else {}

        def appended(field_key: str, new_text: str) -> str:
            existing = (current or {}).get(field_key) or ""
            ts = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            if existing:
                return f"{existing}\n[{ts}] {new_text}".strip()
            return f"[{ts}] {new_text}".strip()

        if metabolic_history:
            updates["metabolic_history"] = appended("metabolic_history", metabolic_history)
        if prior_diets_tried:
            updates["prior_diets_tried"] = appended("prior_diets_tried", prior_diets_tried)
        if current_meds:
            updates["current_meds"] = appended("current_meds", current_meds)
        if medical_conditions:
            updates["medical_conditions"] = appended("medical_conditions", medical_conditions)
        if digestive_profile:
            updates["digestive_profile"] = appended("digestive_profile", digestive_profile)
        if personal_patterns:
            updates["personal_patterns"] = appended("personal_patterns", personal_patterns)

        if metabolic_type:
            updates["metabolic_type"] = metabolic_type
        if lifetime_lowest_kg > 0:
            updates["lifetime_lowest_kg"] = float(lifetime_lowest_kg)
        if lifetime_highest_kg > 0:
            updates["lifetime_highest_kg"] = float(lifetime_highest_kg)
        if 1 <= sleep_quality <= 5:
            updates["sleep_quality"] = int(sleep_quality)
        if 1 <= stress_level <= 5:
            updates["stress_level"] = int(stress_level)

        if not updates:
            return "Aucun champ à mettre à jour."
        db.update_user(user_id, **updates)
        return f"Profil métabolique mis à jour : {', '.join(updates.keys())}"

    @beta_tool
    def recalibrate_calories(
        new_daily_kcal: int,
        reason: str,
        adjustment_pct: int = 0,
    ) -> str:
        """Recalculate the user's daily calorie target when the textbook TDEE \
formula doesn't match reality. Use this AFTER analyze_progress has detected a \
persistent plateau or regression (2+ weeks) AND you've ruled out compliance \
issues (alcohol, sleep, stress, cycle).

This is what separates Calo from a static dashboard : Calo adjusts to the \
ACTUAL response of the person's metabolism.

When to call:
- Plateau >2 weeks, compliance verified → -100 to -200 kcal/jour
- Loss too fast (>0.8 kg/sem femme, >1 kg/sem homme) → +100 to +200 kcal
- Gain not happening despite surplus → +200 to +300 kcal
- After 4-6 weeks of stable trajectory → record the personal adjustment

Args:
    new_daily_kcal: The NEW daily calorie target (replaces the previous one).
    reason: WHY you're adjusting (e.g. 'plateau 3 sem à 1700 kcal sans \
écart, compliance OK, ralentissement métabolique probable -10%').
    adjustment_pct: Personal multiplier vs textbook TDEE (e.g. 90 means -10% \
slower metabolism than textbook). Leave 0 to skip.
"""
        user = db.get_user_by_id(user_id)
        if not user:
            return "User not found."
        previous = user.get("daily_calories") or 0
        # Adjust protein proportionally to keep g/kg ratio
        weight = user.get("current_weight_kg") or 70
        new_protein = round(float(weight) * 1.8)
        # Approximate macro split for the new target
        protein_kcal = new_protein * 4
        fat_kcal = int(new_daily_kcal * 0.30)
        carbs_kcal = max(0, new_daily_kcal - protein_kcal - fat_kcal)
        new_carbs = carbs_kcal // 4
        new_fat = fat_kcal // 9

        updates = {
            "daily_calories": int(new_daily_kcal),
            "daily_protein_g": int(new_protein),
            "daily_carbs_g": int(new_carbs),
            "daily_fat_g": int(new_fat),
            "last_calibration": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        }
        if adjustment_pct and 60 <= adjustment_pct <= 140:
            updates["calorie_adjustment"] = int(adjustment_pct)
        db.update_user(user_id, **updates)

        # Log this calibration as a memory for traceability
        db.add_memory(
            user_id,
            f"Calo a recalibré les calories : {previous} → {new_daily_kcal} kcal. "
            f"Raison : {reason}",
            category="objectif",
            importance=4,
        )
        return (
            f"✅ Cible recalibrée : {previous} → {new_daily_kcal} kcal/jour. "
            f"Protéines {new_protein}g, glucides {new_carbs}g, lipides {new_fat}g. "
            f"Raison enregistrée : {reason}. "
            f"Annonce le changement à l'utilisateur AVEC l'explication, et "
            f"engage-le sur 2 semaines de test avant nouvelle évaluation."
        )

    @beta_tool
    def analyze_progress(weeks: int = 4) -> str:
        """Smart progress analyser. Detects plateau, regression, or great \
trajectory and suggests a concrete intervention (refeed, diet break, \
recalculate calories, hold the course). Use this when the user asks "je \
stagne", "je n'avance plus", "ça bouge plus", "j'ai pris du poids cette \
semaine", or proactively in weekly check-ins.

Args:
    weeks: Number of weeks to analyse. Default 4. Min 2, max 12.
"""
        weeks = max(2, min(12, int(weeks)))
        user = db.get_user_by_id(user_id)
        if not user or not user.get("onboarding_complete"):
            return "Onboarding incomplet."
        weights = db.weights_history(user_id, limit=weeks * 2)
        if len(weights) < 2:
            return (
                "Pas assez de mesures pour analyser (besoin de 2+ pesées). "
                "Encourage l'utilisateur à se peser 1x/semaine au même jour."
            )
        latest = float(weights[0]["weight_kg"] or 0)
        oldest = float(weights[-1]["weight_kg"] or 0)
        delta = latest - oldest
        goal = user.get("goal", "maintain")
        target = float(user.get("target_weight_kg") or latest)
        sign = "+" if delta >= 0 else ""
        days_span = max(1, len(weights) * 7)
        weekly_change = delta / (days_span / 7)

        # Determine state
        report = [
            f"# Analyse progression ({len(weights)} pesées sur ~{days_span} jours)",
            f"Poids actuel : {latest} kg",
            f"Variation : {sign}{delta:.1f} kg ({sign}{weekly_change:.2f} kg/sem)",
            f"Objectif : {goal} → cible {target} kg ({latest - target:+.1f} kg restants)",
            "",
        ]

        if goal == "lose":
            if weekly_change <= -0.3:
                report.append("**État : 🟢 EXCELLENTE PROGRESSION**")
                report.append(
                    "Rythme sain (-0.3 à -0.7 kg/sem idéal). Continue ce qui marche, "
                    "ne durcis surtout pas le déficit. Stratégie : maintien strict, "
                    "pas de changement."
                )
            elif -0.3 < weekly_change <= -0.1:
                report.append("**État : 🟡 PROGRESSION LENTE MAIS RÉELLE**")
                report.append(
                    "Tu avances doucement, c'est durable. Possibles ajustements : "
                    "+1000 pas/jour, +1 séance cardio courte, ou serrer un poil les "
                    "calories (-100 kcal/j). Ne touche PAS aux protéines."
                )
            elif -0.1 < weekly_change < 0.1:
                report.append("**État : 🟠 PLATEAU DÉTECTÉ**")
                report.append(
                    "Plateau >2 semaines = signal métabolique. Trois options "
                    "scientifiques :\n"
                    "1. **Refeed 1-2 jours** : monte les glucides au maintien "
                    "(reset leptine, relance la combustion)\n"
                    "2. **Diet break 7-10 jours** : maintien calorique complet "
                    "(reset hormonal profond, repart plus fort après)\n"
                    "3. **Recalibrer les calories** : si poids -2-3 kg depuis le "
                    "calcul initial, le besoin a baissé de 50-100 kcal. Tu peux "
                    "soit relancer le déficit, soit prendre l'option 1 ou 2 d'abord."
                )
            else:
                report.append("**État : 🔴 STAGNATION / RÉGRESSION**")
                report.append(
                    "Le poids monte malgré l'objectif perte. Causes probables :\n"
                    "- Compliance compromise (week-end, alcool, snacks invisibles)\n"
                    "- Stress + cortisol → rétention d'eau\n"
                    "- Sommeil dégradé\n"
                    "- Cycle (femme) en phase lutéale → +1-3 kg eau normal\n\n"
                    "Action recommandée : passe en revue les 7 derniers jours "
                    "avec l'utilisateur (alcool, sommeil, stress, cycle) AVANT "
                    "de modifier les calories."
                )
        elif goal == "gain":
            if weekly_change >= 0.2:
                report.append("**État : 🟢 PRISE DE MASSE EN COURS**")
                report.append(
                    "Bonne dynamique. Rappelle que 0.2-0.4 kg/sem est l'idéal "
                    "(moins = pas assez de stimulus, plus = trop de gras pris)."
                )
            elif 0 <= weekly_change < 0.2:
                report.append("**État : 🟡 PRISE LENTE**")
                report.append(
                    "Bump : +200-300 kcal/jour (glucides priorité), +1 sucre lent "
                    "post-training, prendre vraiment 4 repas/jour. Si toujours "
                    "stagnation après 2 sem, +500 kcal."
                )
            else:
                report.append("**État : 🔴 PERTE DE POIDS NON DÉSIRÉE**")
                report.append(
                    "L'objectif est la prise mais tu perds. Soit l'apport est "
                    "insuffisant (à augmenter), soit l'activité est en hausse. "
                    "Recalcule les besoins."
                )
        else:  # maintain
            if abs(weekly_change) < 0.2:
                report.append("**État : 🟢 MAINTIEN PARFAIT**")
            else:
                report.append("**État : 🟡 VARIATION HORS CIBLE**")
                report.append(
                    f"Tu vises le maintien mais tu varies de {weekly_change:+.2f} "
                    "kg/sem. Léger ajustement calorique nécessaire (+/- 150 kcal/j)."
                )
        return "\n".join(report)

    @beta_tool
    def generate_meal_plan(
        days: int = 7,
        focus: str = "auto",
        vegetarian: bool = False,
        vegan: bool = False,
    ) -> str:
        """Generate a personalised meal plan from Calo's recipes, tuned to the \
user's daily kcal/macro targets. Use this when the user asks for a meal plan, \
"un plan de repas", "menu semaine", "qu'est-ce que je mange cette semaine", \
"prépare-moi mes repas", "menu menopause", "menu sèche", etc. The plan picks \
1 petit-déj + 1 déjeuner + 1 dîner + 1 snack per day, trying to hit ±15% of \
the user's daily kcal target. No recipe repeats within a 4-day window.

Args:
    days: Number of days to plan (1-14). Default 7.
    focus: 'auto' | 'perte de poids' | 'prise de masse' | 'menopause-friendly' \
| 'cycle hormonal' | 'anti-inflammatoire' | 'rapide' | 'batch cooking'. \
Filters recipes by tag.
    vegetarian: If True, only include vegetarian-tagged recipes.
    vegan: If True, only include vegan-tagged recipes.
"""
        user = db.get_user_by_id(user_id)
        if not user or not user.get("onboarding_complete"):
            return "Onboarding incomplet. Termine d'abord le profil avec complete_profile."

        target_kcal = int(user.get("daily_calories") or 2000)
        require_tags: list[str] = []
        if vegan:
            require_tags.append("vegan")
        elif vegetarian:
            require_tags.append("végétarien")
        if focus and focus != "auto":
            require_tags.append(focus)

        grouped = db.recipes_for_meal_plan(require_tags=require_tags or None)

        # Fallback: if a category is empty after filter, retry without tag filter
        if any(not v for v in grouped.values()):
            grouped = db.recipes_for_meal_plan(
                require_tags=require_tags[:-1] if require_tags else None
            )

        days = max(1, min(14, int(days)))
        recent: dict[str, list[str]] = {k: [] for k in grouped.keys()}
        out_lines: list[str] = [
            f"# Plan repas {days} jours · cible {target_kcal} kcal/j",
            f"Profil : {user.get('name')} · {user.get('goal')} · "
            f"P:{user.get('daily_protein_g')}g C:{user.get('daily_carbs_g')}g "
            f"F:{user.get('daily_fat_g')}g",
        ]

        def pick(category: str, target_kcal_meal: int) -> dict[str, Any] | None:
            pool = grouped.get(category, [])
            if not pool:
                return None
            # avoid last 3 used in same category
            blocked = set(recent[category][-3:])
            candidates = [r for r in pool if r["id"] not in blocked]
            if not candidates:
                candidates = pool
            # pick the recipe closest to target kcal
            candidates.sort(
                key=lambda r: abs((r.get("kcal") or 0) - target_kcal_meal)
            )
            top3 = candidates[: min(3, len(candidates))]
            chosen = random.choice(top3)
            recent[category].append(chosen["id"])
            return chosen

        # Meal kcal split: PD 25%, déj 35%, dîner 30%, snack 10%
        for day in range(1, days + 1):
            day_total_kcal = 0
            day_total_p = 0.0
            day_total_c = 0.0
            day_total_f = 0.0
            out_lines.append(f"\n## Jour {day}")
            for cat, share in (
                ("petit-déj", 0.25),
                ("déjeuner", 0.35),
                ("dîner", 0.30),
                ("snack", 0.10),
            ):
                recipe = pick(cat, int(target_kcal * share))
                if not recipe:
                    out_lines.append(f"- _{cat} : aucune recette disponible_")
                    continue
                day_total_kcal += int(recipe.get("kcal") or 0)
                day_total_p += float(recipe.get("protein_g") or 0)
                day_total_c += float(recipe.get("carbs_g") or 0)
                day_total_f += float(recipe.get("fat_g") or 0)
                total_min = (recipe.get("prep_min") or 0) + (recipe.get("cook_min") or 0)
                out_lines.append(
                    f"- **{cat}** : {recipe['name']} "
                    f"({recipe.get('kcal')} kcal · {total_min} min)"
                )
            out_lines.append(
                f"  → Total jour : {day_total_kcal} kcal · "
                f"P:{day_total_p:.0f}g C:{day_total_c:.0f}g F:{day_total_f:.0f}g"
            )

        out_lines.append(
            "\n💡 Tu peux demander la liste de courses agrégée avec "
            "`generate_grocery_list` une fois le plan validé."
        )
        return "\n".join(out_lines)

    @beta_tool
    def list_challenges(
        category: str = "",
        difficulty: str = "",
        audience: str = "",
    ) -> str:
        """List Calo's structured challenges (30/60/90-day programmes). Use this \
when the user asks for a challenge, a structured programme, "un défi", "un plan \
sur 30 jours", "qu'est-ce que tu proposes comme programme été ?", etc. Filter \
to narrow down.

Args:
    category: One of 'perte de poids' | 'prise de muscle' | 'habitudes saines' | \
'anti-inflammation' | 'été - bikini body' | 'rentrée' | 'menopause-friendly' | \
'performance sport'.
    difficulty: 'facile' | 'modéré' | 'exigeant'.
    audience: 'femme' | 'homme' | 'débutant' | 'intermédiaire' | 'avancé' | \
'menopause' | 'post-grossesse' | 'sportif'.
"""
        challenges = db.list_challenges(
            category=category or None,
            difficulty=difficulty or None,
            audience=audience or None,
            max_results=10,
        )
        if not challenges:
            return "Aucun challenge ne matche ces critères. Élargis la recherche."
        out = []
        for c in challenges:
            out.append(
                f"## {c['name']} ({c.get('duration_days', '?')} jours · "
                f"{c.get('difficulty', '?')})\n"
                f"🎯 Catégorie : {c.get('category', '?')}\n"
                f"👥 Pour : {', '.join(c.get('target_audience') or [])}\n"
                f"🔖 Slug : `{c.get('slug')}`\n\n"
                f"{c.get('pitch', '')}\n\n"
                f"**Résultats attendus :**\n{c.get('expected_outcome', '')}"
            )
        return "\n\n---\n\n".join(out)

    @beta_tool
    def get_challenge_details(slug: str) -> str:
        """Fetch the full details of a challenge by its slug — daily structure, \
rules, expected outcome. Use this when the user wants more detail on a specific \
challenge before committing.

Args:
    slug: The challenge stable identifier (e.g. 'summer-shred-30', 'lean-90', \
'meno-strong-30', 'cycle-sync-90', 'hydra-sleep-21', 'sucre-zero-30', \
'anti-inflam-60', 'mediterranean-30', 'perf-sport-60', 'rentree-reset-30').
"""
        c = db.get_challenge_by_slug(slug)
        if not c:
            return f"Aucun challenge avec le slug '{slug}'. Appelle list_challenges pour voir les options."
        return (
            f"# {c['name']}\n"
            f"⏱️ {c.get('duration_days', '?')} jours · {c.get('difficulty', '?')}\n"
            f"🎯 {c.get('category', '?')}\n"
            f"👥 Pour : {', '.join(c.get('target_audience') or [])}\n\n"
            f"## Pitch\n{c.get('pitch', '')}\n\n"
            f"## Structure quotidienne\n{c.get('daily_structure', '')}\n\n"
            f"## Règles non négociables\n{c.get('rules', '')}\n\n"
            f"## Résultats attendus\n{c.get('expected_outcome', '')}"
        )

    @beta_tool
    def start_challenge(slug: str) -> str:
        """Subscribe the current user to a challenge. ONLY call this once the \
user has clearly confirmed they want to start (e.g. "ok je commence", "go", \
"je m'inscris"). Saves the start date and tracks progress.

Args:
    slug: The challenge stable identifier (e.g. 'summer-shred-30').
"""
        c = db.get_challenge_by_slug(slug)
        if not c:
            return f"Aucun challenge avec le slug '{slug}'."
        existing = db.get_active_user_challenge(user_id)
        if existing:
            return (
                "L'utilisateur a déjà un challenge actif. Demande-lui s'il veut "
                "le terminer avant d'en commencer un autre."
            )
        rec_id = db.start_user_challenge(user_id, c["id"])
        return (
            f"✅ Challenge **{c['name']}** démarré aujourd'hui (J1/{c.get('duration_days')}). "
            f"Rappelle les 3 règles les plus importantes maintenant, et engage l'utilisateur "
            f"sur la 1ère action concrète à faire dès aujourd'hui."
        )

    @beta_tool
    def get_my_active_challenge() -> str:
        """Check if the user has an active challenge running, and return its \
status (current day, name, slug). Use this when the user asks 'où en suis-je \
sur mon challenge', 'mon programme', or to contextualise advice."""
        uc = db.get_active_user_challenge(user_id)
        if not uc:
            return "Aucun challenge actif pour cet utilisateur."
        return (
            f"Challenge actif : record UC {uc['id']}. "
            f"Statut : {uc.get('status')}. Jour actuel : {uc.get('current_day')}. "
            f"Démarré : {uc.get('started_at')}."
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
        analyze_progress,
        update_metabolic_profile,
        recalibrate_calories,
        start_anamnese,
        analyze_anamnese,
        log_daily_check,
        check_milestones,
        travel_mode,
        prepare_for_event,
        compare_body_photos,
        interpret_bloodwork,
        decode_symptom,
        recommend_supplements,
        generate_workout,
        workout_fuel,
        recovery_protocol,
        get_streak,
        suggest_habit_stack,
        detect_trigger_foods,
        generate_client_report,
        find_recipe,
        generate_meal_plan,
        generate_grocery_list,
        list_challenges,
        get_challenge_details,
        start_challenge,
        get_my_active_challenge,
        search_knowledge,
        remember,
    ]
