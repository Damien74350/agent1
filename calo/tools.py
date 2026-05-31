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
        find_recipe,
        list_challenges,
        get_challenge_details,
        start_challenge,
        get_my_active_challenge,
        search_knowledge,
        remember,
    ]
