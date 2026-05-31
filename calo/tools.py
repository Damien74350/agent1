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
