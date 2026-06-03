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
from datetime import datetime, timedelta, timezone
from typing import Any

from anthropic import beta_tool

from . import chart_generator
from . import image_gen
from . import pdf_report as pdf_mod
from .airtable_db import AirtableDB
from .nutrition import daily_targets


def _get_micro_courses() -> dict[str, dict[str, Any]]:
    """Return the catalog of micro-courses. Each lesson is a self-contained
    text/audio module the user consumes 5-15 min per day."""
    return {
        "macros-5j": {
            "title": "Maîtrise tes macros en 5 jours",
            "duration_days": 5,
            "level": "débutant",
            "lessons": [
                "**Jour 1 — Les 3 macros expliqués simplement**\n\n"
                "Les macronutriments (\"macros\") sont les 3 types d'énergie dans la nourriture :\n\n"
                "1. **Protéines** (4 kcal/g) : construire/réparer muscle, satiété. Ex : poulet, œufs, lentilles\n"
                "2. **Glucides** (4 kcal/g) : énergie rapide + soutenue. Ex : riz, pâtes, fruits, légumes\n"
                "3. **Lipides** (9 kcal/g) : hormones, satiété, vitamines liposolubles. Ex : huile olive, avocat, noix\n\n"
                "**Action aujourd'hui** : Note les 3 macros que tu vois dans ton prochain repas.",

                "**Jour 2 — Combien de chaque ?**\n\n"
                "Cibles pour un adulte actif (par kg de poids) :\n"
                "- Protéines : 1.6-2.2 g/kg\n"
                "- Glucides : 3-6 g/kg (selon activité)\n"
                "- Lipides : 0.8-1.2 g/kg\n\n"
                "Pour 70 kg : ~140g prot, 280g glucides, 70g lipides = 2310 kcal\n\n"
                "**Action** : Calcule TES cibles macros aujourd'hui.",

                "**Jour 3 — Comment les compter**\n\n"
                "- App : MyFitnessPal, Cronometer (gratuite, plus précise)\n"
                "- Ou estimer visuellement : paume = portion protéine, poing = légumes, etc.\n"
                "- Pesée 1-2 sem au début pour calibrer ton œil\n"
                "- Ensuite : estimation suffit\n\n"
                "**Action** : Logge tes repas pendant 1 journée.",

                "**Jour 4 — Le TIMING des macros**\n\n"
                "- **Matin** : protéines + glucides + fibres (énergie + satiété)\n"
                "- **Avant sport** : glucides 1h avant\n"
                "- **Après sport** : protéines + glucides dans les 2h\n"
                "- **Soir** : protéines + lipides + légumes (moins glucides)\n\n"
                "**Action** : Ajuste UN repas pour optimiser le timing.",

                "**Jour 5 — Adapter selon objectif**\n\n"
                "- **Perte de poids** : -400 kcal/jour, garde protéines hautes (préserve muscle)\n"
                "- **Maintien** : maintenance kcal, équilibrage normal\n"
                "- **Prise muscle** : +200-300 kcal/jour, protéines 2g/kg\n"
                "- **Performance sport** : glucides élevés autour de l'entrainement\n\n"
                "**Quiz final** : Quels sont les 3 macros ? Combien par kg ? Comment adapter pour perdre poids ?\n\n"
                "🎉 Bravo, tu maîtrises les bases !"
            ],
        },
        "boxing-init-14j": {
            "title": "Premiers pas en boxing en 14 jours",
            "duration_days": 14,
            "level": "débutant",
            "lessons": [
                "**Jour 1 — La position de combat**\n\nLa base de tout. Pied avant (gauche pour droitier) "
                "pointant vers la cible, pied arrière écarté largeur d'épaules à 45°. Genoux fléchis. "
                "Mains AU MENTON. Menton rentré. Pratique 5 min devant un miroir.",
                "**Jour 2 — Le jab** (coup 1). Le plus utilisé. Poing avant en ligne droite. Retour rapide en garde. Pratique : 5 min de jabs lents.",
                "**Jour 3 — Le cross** (coup 2). Poing arrière + pivot pied arrière + hanche. Le plus puissant des directs. Pratique : 5 min jabs + cross.",
                "**Jour 4 — Le combo 1-2** (jab-cross). LE classique. 5 min de combos lents.",
                "**Jour 5 — Le footwork**. Avance, recule, latéral. JAMAIS croiser les jambes. 5 min de footwork solo.",
                "**Jour 6 — Le hook (crochet)**. Coude plié 90°, pivot hanche. 5 min de hooks.",
                "**Jour 7 — REVIEW + premier shadow boxing 10 min**. Mets ce que tu as appris en pratique.",
                "**Jour 8 — L'uppercut**. Vient du bas, explosion jambes + hanches. 5 min d'uppercuts.",
                "**Jour 9 — Combos 4 coups** : 1-2-3-2 (jab-cross-hook-cross). 5 min.",
                "**Jour 10 — Le slip (esquive)**. Pivote le tronc pour faire passer le coup à côté. 5 min de slips.",
                "**Jour 11 — Combos + esquives** : jab-slip-cross, cross-slip-hook. 5 min.",
                "**Jour 12 — La respiration**. Expire (\"tss\") sur chaque coup. Pratique respiratoire 5 min.",
                "**Jour 13 — Shadow boxing 15 min full** : applique tout.",
                "**Jour 14 — Quiz + plan pour la suite**. Tu connais maintenant : 4 coups (jab, cross, hook, uppercut), 1 esquive (slip), footwork, respiration. Prêt pour rejoindre un club ou passer au challenge Box & Burn 30 jours.",
            ],
        },
        "stress-5j": {
            "title": "Gestion du stress en 5 jours",
            "duration_days": 5,
            "level": "tous",
            "lessons": [
                "**Jour 1 — Comprendre le stress chronique**\n\nLe stress aigu est BON (réaction de survie). Le stress chronique est mauvais (cortisol élevé permanent = inflammation, prise de gras abdominal, sommeil cassé, dépression).\n\nDeux types : externe (boulot, finances, relations) et interne (perfectionnisme, anxiété).\n\n**Action** : Note 3 sources de stress chronique dans ta vie actuelle.",
                "**Jour 2 — La cohérence cardiaque (technique #1)**\n\n5 min, 6 respirations/min : inspire 5s, expire 5s. Baisse cortisol -25%, mesuré.\n\n**Action** : Fais 5 min de cohérence cardiaque MAINTENANT. Note comment tu te sens après.",
                "**Jour 3 — La marche en nature (technique #2)**\n\n30 min en nature (parc, forêt) = cortisol -25% mesuré. Sans téléphone. Conscience corporelle.\n\n**Action** : Fais une marche en nature aujourd'hui.",
                "**Jour 4 — Identifier tes triggers (cognitive)**\n\nQuelles situations te stressent le PLUS ? Pourquoi ? Que ressens-tu physiquement ? Recadrage cognitif possible ?\n\n**Action** : Tiens un journal stress 24h : note chaque pic + situation + ressenti.",
                "**Jour 5 — Plan anti-stress quotidien**\n\nTon stack quotidien :\n- Matin : 5 min méditation OU cohérence cardiaque\n- Midi : marche post-repas 10 min\n- Soir : 5 min cohérence cardiaque\n- Hebdo : 1 séance sport modérée (anti-cortisol)\n- Avant coucher : magnésium bisglycinate 300 mg\n\n**Action** : Implémente ce stack pendant 7 jours. Tu vas sentir la différence.",
            ],
        },
        "sommeil-7j": {
            "title": "Sommeil optimal en 7 jours",
            "duration_days": 7,
            "level": "tous",
            "lessons": [
                "**Jour 1 — La science du sommeil**\n\n4 stades (N1, N2, N3, REM). 4-5 cycles/nuit de 90 min. N3 (sommeil profond) = récupération physique + GH. REM = mémoire émotionnelle. **Tu as besoin des deux**.",
                "**Jour 2 — Calcule ton timing optimal**\n\nSi tu te réveilles à 6h30, couche-toi 22h45 (5 cycles + 15 min endormissement). Mieux : 21h15 (6 cycles = 9h sommeil).",
                "**Jour 3 — La pièce parfaite**\n\nFraîche (17-19°C), noire (rideaux occultants), silencieuse (oreilles bouchées si besoin). Pas de télé dans la chambre.",
                "**Jour 4 — La routine soir (60 min avant)**\n\nStop écrans (mélatonine). Stop alcool (détruit N3). Pas de gros repas. Magnésium bisglycinate 300mg. Lumière tamisée. Lecture / méditation.",
                "**Jour 5 — Le matin (cale le rythme circadien)**\n\nLumière naturelle dans les 10 min après réveil. Cale ta mélatonine 14h plus tard. Stop café après 14h (demi-vie 7h).",
                "**Jour 6 — Naps stratégiques**\n\n20 min = power nap (N1-N2, boost cognition, pas de groggy). 90 min = cycle complet. Entre 13h et 15h idéal. PAS après 17h.",
                "**Jour 7 — Plan d'optimisation**\n\nNote pendant 7 jours : heure coucher/lever, qualité (1-10), facteurs (sport, alcool, stress). Identifie patterns. Optimise.\n\n**Quiz final** : Pourquoi le sommeil profond est-il critique ? Quelle T° de chambre ? Quand stopper la caféine ?",
            ],
        },
        "habitudes-7j": {
            "title": "Habitudes durables en 7 jours",
            "duration_days": 7,
            "level": "tous",
            "lessons": [
                "**Jour 1 — Pourquoi les habitudes >>> motivation**\n\n40% de tes actions quotidiennes sont des habitudes (Wood 2002). Si tu changes tes habitudes, tu changes ta vie. La motivation est volatile, les habitudes sont durables.",
                "**Jour 2 — La méthode Tiny Habits (BJ Fogg)**\n\nB = MAP : Behavior = Motivation × Ability × Prompt. Pour qu'un comportement se produise, il faut les 3. Solution : commencer MINUSCULE + anchor sur action existante + célébrer.",
                "**Jour 3 — La règle des 2 minutes**\n\nN'importe quelle nouvelle habitude doit prendre <2 min pour commencer. 'Je vais courir 5 min' pas '10 km'. 'Je lis 1 page' pas '1 livre'.\n\n**Action** : Choisis UNE habitude à commencer demain. Format : 2 min max.",
                "**Jour 4 — Habit stacking**\n\nFormat : 'Apres X (action existante), je vais Y (nouvelle habitude)'. Ex : 'Apres mon café, je médite 2 min'. +130% de chances de stick.\n\n**Action** : Crée 3 habit stacks possibles.",
                "**Jour 5 — Identity-based habits**\n\nNe vise pas un résultat ('perdre 10 kg'). Vise une identité ('je suis quelqu'un qui prend soin de son corps'). Les actions découlent naturellement.",
                "**Jour 6 — Environment design**\n\nFais que la bonne habitude soit FACILE et la mauvaise DIFFICILE. Eau au comptoir, bonbons en cave. Tenue sport visible. App distractive cachée.",
                "**Jour 7 — Plan tes 90 prochains jours**\n\nUNE habitude par mois. Mois 1 : action 2 min anchor + célébration. Mois 2 : augmente la durée. Mois 3 : c'est ancré, ajoute la 2e habitude.\n\n**Quiz** : C'est quoi B=MAP ? La règle 2 min ? Le habit stacking ?",
            ],
        },
    }


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
    attachments: list[dict[str, str]] | None = None,
    public_url_base: str = "",
):
    """Create tools bound to the current request context.

    `attachments` (list of `{"url": ..., "caption": ...}`) is populated by tools
    that want to send media (charts, audio) back to the user. The coach layer
    reads this list after the turn and dispatches via Twilio. `public_url_base`
    is the externally reachable host (Railway URL) used to build chart URLs.
    """
    if attachments is None:
        attachments = []

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
    def scan_food_label(label_summary: str = "") -> str:
        """User has sent a photo of a food product label (Nutri-Score, table \
nutritionnelle, ingrédients). Read with vision, then call THIS tool with a \
short summary string. Returns a decryption framework: ultra-processed score, \
sugar density, fat profile, ingredient red flags, verdict.

Args:
    label_summary: What you read on the label (e.g. 'Yaourt aux fruits 125g, \
108 kcal/pot, sucres 14g, protéines 4g, ingrédients : lait, sucre, sirop \
de glucose-fructose, arômes, gélifiants').
"""
        if not label_summary:
            return (
                "Lis d'abord l'étiquette avec vision et fournis 'label_summary' : "
                "valeurs nutritionnelles (kcal, P/C/F, sucres, sel, fibres) + "
                "ingrédients principaux."
            )
        from datetime import datetime, timezone
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        db.add_memory(
            user_id,
            f"Scan étiquette {today} : {label_summary[:120]}",
            category="préférence",
            importance=2,
        )
        return (
            f"📦 **Cadre de décryptage**\n\n"
            f"Étiquette lue : {label_summary}\n\n"
            f"## Tes critères de classement\n\n"
            f"**🟢 Bon produit** :\n"
            f"- Sucres <5g/100g (hors fruits)\n"
            f"- Sel <1g/100g (hors fromages, charcuterie)\n"
            f"- Fibres >3g/100g si céréalier\n"
            f"- Liste d'ingrédients courte (≤5) et compréhensible\n"
            f"- Pas d'huile de palme, pas de sirop de glucose-fructose, "
            f"pas d'arômes artificiels\n\n"
            f"**🟡 Acceptable occasionnel** :\n"
            f"- Sucres 5-15g/100g\n"
            f"- Sel 1-1.5g/100g\n"
            f"- Liste 5-10 ingrédients\n"
            f"- 1-2 additifs E quelconques mais pas sensibles\n\n"
            f"**🔴 À éviter** :\n"
            f"- Sucres >15g/100g (ou >20g/100ml liquide)\n"
            f"- Sel >1.5g/100g (hors fromage)\n"
            f"- Sirop glucose-fructose en top 3 ingrédients\n"
            f"- >10 ingrédients dont nombreux additifs/arômes\n"
            f"- Acides gras trans / huiles partiellement hydrogénées\n\n"
            f"**Additifs à éviter** :\n"
            f"- E249-E252 (nitrites — charcuterie industrielle)\n"
            f"- E951 (aspartame) E950 (acésulfame K)\n"
            f"- E407 (carraghénane — inflammation intestinale)\n"
            f"- E621 (glutamate)\n"
            f"- E338-E452 (phosphates — os/reins)\n\n"
            f"**Tes consignes** :\n"
            f"1. Classe ce produit 🟢🟡🔴 selon les critères\n"
            f"2. Identifie ce qui le tire vers le bas (sucres? sel? additifs?)\n"
            f"3. Propose une alternative concrète si 🟡 ou 🔴\n"
            f"4. Si Nutri-Score visible, contextualise (NS A peut être 🟡 si "
            f"ultra-transformé — sodas zéro sont NS B mais 🔴)"
        )

    @beta_tool
    def pantry_to_meal(
        ingredients: list[str],
        meal_type: str = "déjeuner",
        max_prep_min: int = 30,
    ) -> str:
        """User has shared what they have on hand (fridge/pantry list or photo \
description). Match against Calo recipes + suggest 3 doable meals NOW. \
Returns ranked options.

Args:
    ingredients: List of available items (e.g. ['poulet 200g', 'brocoli', \
'riz', 'œufs', 'yaourt grec', 'pomme', 'huile olive']).
    meal_type: 'petit-déj' | 'déjeuner' | 'dîner' | 'snack' | 'auto'.
    max_prep_min: Maximum prep time the user can spend.
"""
        if not ingredients:
            return "Demande d'abord à l'utilisateur ce qu'il a (texte ou photo)."

        # Find recipes matching any ingredient
        recipe_scores: list[tuple[dict[str, Any], int, list[str]]] = []
        all_recipes: list[dict[str, Any]] = []
        if meal_type and meal_type != "auto":
            all_recipes = db.search_recipes(category=meal_type, max_results=30)
        else:
            for cat in ("petit-déj", "déjeuner", "dîner", "snack"):
                all_recipes += db.search_recipes(category=cat, max_results=10)

        ingredients_lower = [i.lower() for i in ingredients]
        for r in all_recipes:
            ing_text = (r.get("ingredients") or "").lower()
            prep_total = (r.get("prep_min") or 0) + (r.get("cook_min") or 0)
            if prep_total > max_prep_min:
                continue
            matched = [i for i in ingredients_lower if any(
                w in ing_text for w in i.split()
            )]
            if matched:
                recipe_scores.append((r, len(matched), matched))

        if not recipe_scores:
            return (
                f"Aucune recette Calo ne match tes ingrédients en <{max_prep_min} min. "
                f"Propose UNE recette improvisée basée sur ce que l'utilisateur a "
                f"(prot + légumes + féculent + bon gras + assaisonnement)."
            )

        # Sort by match count desc
        recipe_scores.sort(key=lambda x: -x[1])
        top3 = recipe_scores[:3]
        out = ["# 🥘 Que tu peux faire MAINTENANT\n"]
        for i, (r, score, matched) in enumerate(top3, 1):
            total = (r.get("prep_min") or 0) + (r.get("cook_min") or 0)
            out.append(
                f"## Option {i} — {r['name']} ({total} min)\n"
                f"📊 {r.get('kcal')} kcal · P:{r.get('protein_g')}g\n"
                f"✅ Tu as : {', '.join(matched)}\n\n"
                f"**Ingrédients complets :**\n{r.get('ingredients', '')}\n\n"
                f"**Préparation :**\n{r.get('instructions', '')}\n"
            )

        out.append(
            "\n💡 Propose les 3 options à l'utilisateur. S'il manque un "
            "ingrédient pour son choix, propose un substitut équivalent macro."
        )
        return "\n".join(out)

    @beta_tool
    def adapt_recipe_for_family(
        recipe_name: str,
        adults: int = 2,
        children: int = 0,
        children_ages: str = "",
    ) -> str:
        """Adapt a Calo recipe for a family meal. Scales portions and suggests \
kid-friendly tweaks if needed (less spice, smaller pieces, optional sides).

Args:
    recipe_name: Name of the Calo recipe to adapt.
    adults: Number of adults.
    children: Number of children.
    children_ages: Age range or list (e.g. '3 et 7 ans').
"""
        results = db.search_recipes(query=recipe_name, max_results=1)
        if not results:
            return f"Recette '{recipe_name}' introuvable. Suggère 2-3 recettes proches."
        r = results[0]
        servings_original = r.get("servings") or 1

        # Adult equivalent: child = 0.6 adult portion (avg)
        total_equiv = adults + (children * 0.6)
        scale = total_equiv / servings_original

        out = [
            f"# 👨‍👩‍👧 {r['name']} pour famille\n",
            f"Composition : {adults} adulte(s) + {children} enfant(s)"
            + (f" ({children_ages})" if children_ages else ""),
            f"Recette originale : {servings_original} portion(s) → ratio ×{scale:.1f}",
            "",
            "## Ingrédients ajustés (estimation)",
            "_Multiplie chaque quantité par le ratio ci-dessus_",
            "",
            r.get("ingredients", ""),
            "",
            "## Préparation",
            r.get("instructions", ""),
        ]

        # Kid-friendly tips
        if children > 0:
            tips = ["\n## 👶 Adaptation enfants"]
            ing_lower = (r.get("ingredients") or "").lower()
            if any(w in ing_lower for w in ["piment", "harissa", "curry", "épice", "wasabi"]):
                tips.append("- 🌶️ Prépare une portion **sans épices fortes** pour les enfants")
            if "alcool" in ing_lower or "vin" in ing_lower:
                tips.append("- 🍷 Cuit assez longtemps pour évaporer l'alcool, ou divise et ajoute l'alcool seulement à la portion adulte")
            if any(w in ing_lower for w in ["poisson cru", "sashimi", "tartare", "œuf cru"]):
                tips.append("- 🍣 Cuire/grasser la portion enfants (cru déconseillé <5 ans)")
            if any(w in ing_lower for w in ["fruits à coque", "amandes", "noix", "noisettes"]):
                tips.append("- 🥜 Couper finement ou broyer pour <4 ans (risque étouffement)")

            # Generic tips
            tips.append("- ✂️ Coupe en plus petits morceaux pour les enfants <6 ans")
            tips.append("- 🍞 Propose une portion de pain ou riz à part pour les difficiles")
            tips.append("- 🥦 Présente les légumes séparément du reste (les enfants triient)")
            tips.append("- 🥄 Laisse-les se servir = plus d'engagement")
            out.extend(tips)

        # Macro tracking
        out.append("\n## Macros par adulte (inchangées)")
        out.append(
            f"{r.get('kcal')} kcal · P:{r.get('protein_g')}g · "
            f"C:{r.get('carbs_g')}g · F:{r.get('fat_g')}g"
        )
        out.append(
            "_Logge UNIQUEMENT ta portion d'adulte avec log_meal — les enfants "
            "ne sont pas dans ton compteur._"
        )
        return "\n".join(out)

    @beta_tool
    def cravings_toolkit(craving_type: str = "sucré") -> str:
        """Anti-cravings protocol — 5-question diagnostic + alternatives. Use \
when the user says "j'ai envie de X", "fringale", "je craque", "je vais \
craquer". This is a BEHAVIORAL tool, not a guilt tool — frame it as \
problem-solving.

Args:
    craving_type: 'sucré' | 'salé' | 'gras' | 'chocolat' | 'alcool' | 'pain'.
"""
        ct = craving_type.lower()
        questions = [
            "1. **Est-ce que j'ai vraiment faim ?** (Si je devais manger une "
            "pomme là maintenant, est-ce que j'en aurais envie ? Si non = "
            "envie émotionnelle, pas faim.)",
            "2. **Quand ai-je mangé ma dernière vraie protéine ?** "
            "(<6h satiété ok, >6h faim physiologique.)",
            "3. **Combien d'eau aujourd'hui ?** (Soif déguisée en faim chez "
            "60% des cas.)",
            "4. **Quelle émotion juste avant l'envie ?** (Ennui, anxiété, "
            "fatigue, frustration, célébration. Nomme-la.)",
            "5. **C'est quoi le besoin réel ?** (Pause, câlin, dormir, "
            "respirer, plaisir, m'autoriser. Soigne le besoin, pas le symptôme.)",
        ]

        alternatives = {
            "sucré": [
                "🍎 1 pomme + 1 c.à.c. beurre cacahuète (sucre lent + gras = satiété)",
                "🍫 1 carré de chocolat noir 85% (8g, 50 kcal)",
                "🍓 100g fruits rouges + 100g skyr nature (200 kcal, 12g prot)",
                "🥤 1 grand verre d'eau + 1 c.à.c. miel (30 kcal, casse le pic)",
                "☕ Thé cannelle infusé fort (mime sucré, 0 kcal)",
                "🥥 1 datte Medjool (75 kcal, magnésium)",
            ],
            "salé": [
                "🥒 Concombre + 1 c.à.s. houmous (100 kcal, fibres)",
                "🥚 1 œuf dur + sel rose + poivre (75 kcal, prot)",
                "🌰 15g amandes (90 kcal, gras+prot)",
                "🥬 1 poignée olives (50 kcal)",
                "🧀 30g feta + tomates cerises (100 kcal)",
                "🍿 30g popcorn maison (sans gras) salté (110 kcal)",
            ],
            "gras": [
                "🥑 1/4 avocat + sel + citron (80 kcal)",
                "🧀 30g comté / parmesan (130 kcal, prot)",
                "🐟 60g saumon fumé (120 kcal, oméga 3)",
                "🥥 1 c.à.s. beurre de cacahuète + 1 fruit (180 kcal)",
            ],
            "chocolat": [
                "🍫 10g chocolat noir 85%+ (60 kcal) — savoure lentement",
                "☕ Cacao non sucré dans lait chaud + cannelle (80 kcal)",
                "🥄 1 c.à.c. pâte à tartiner maison (cacao + amande + dattes)",
                "🍌 Banane congelée + 1 c.à.c. cacao mixé (sorbet chocolat 100 kcal)",
            ],
            "alcool": [
                "🥤 Eau gazeuse + jus citron + glace + menthe (mojito sans alcool)",
                "🍷 1/2 verre vin allongé d'eau gazeuse (spritz léger 50 kcal)",
                "🌿 Kombucha (boisson fermentée, sensation 'adulte' 30 kcal)",
                "🍋 Tisane glacée citron-gingembre (0 kcal)",
            ],
            "pain": [
                "🍞 1 vraie tranche de pain complet + houmous (150 kcal, fibres)",
                "🥖 1/4 baguette tradition + 1 œuf + tomate (200 kcal)",
                "🌾 30g flocons d'avoine + lait chaud + cannelle (200 kcal)",
            ],
        }

        alts = alternatives.get(ct, alternatives["sucré"])
        return (
            f"# 🧠 Protocole anti-fringale ({craving_type})\n\n"
            f"**Étape 1 — 5 questions** (réponds DANS TA TÊTE) :\n\n"
            + "\n".join(questions)
            + "\n\n**Étape 2 — Si la fringale est réelle, voici 6 alternatives "
            f"intelligentes pour {craving_type}** :\n\n"
            + "\n".join(f"- {a}" for a in alts)
            + "\n\n**Étape 3 — Au moment de manger** :\n"
            + "- Assieds-toi (pas debout, pas devant l'écran)\n"
            + "- Sers UNE portion (pas le paquet)\n"
            + "- Mange lentement (20+ mâchouillages)\n"
            + "- Profite vraiment\n\n"
            + "💡 Pas d'auto-flagellation si tu craques quand même. Un écart = "
            + "un repas, pas un échec. Reprends au repas suivant."
        )

    @beta_tool
    def track_mood(mood: int, note: str = "") -> str:
        """Log the user's mood today (1-10) + optional context. Use whenever \
the user mentions emotional state. Calo correlates mood with food/sleep/cycle.

Args:
    mood: 1 (terrible) to 10 (au top).
    note: Optional context (e.g. 'réunion stressante', 'super dodo', 'pre-règles').
"""
        if not (1 <= mood <= 10):
            return "Mood doit être entre 1 et 10."
        from datetime import datetime, timezone
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        emoji = "😢" if mood <= 3 else "😕" if mood <= 5 else "🙂" if mood <= 7 else "😄" if mood <= 9 else "🤩"
        text = f"Mood {today} : {mood}/10 {emoji}"
        if note:
            text += f" — {note}"
        db.add_memory(user_id, text, category="santé", importance=2)
        feedback = ""
        if mood <= 3:
            feedback = (
                "\n\n⚠️ Mood très bas. Vérifie : sommeil hier, repas, hydratation, "
                "stress actif. Si <4 plus de 3 jours/sem → consultation pro."
            )
        elif mood >= 9:
            feedback = "\n\n🌟 Super état. Repère ce qui a déclenché ça (sommeil, repas, sport) — c'est de l'or pour `personal_patterns`."
        return f"✅ Mood logué : {mood}/10{feedback}"

    @beta_tool
    def rate_recipe(recipe_name: str, rating: int, note: str = "") -> str:
        """Save the user's rating of a recipe (1-5 stars) + optional comment. \
Calo uses this to learn preferences and suggest better recipes over time.

Args:
    recipe_name: Name of the Calo recipe.
    rating: 1 (hâté) à 5 (love).
    note: Optional ('trop sec', 'à refaire', 'manque de sel'...).
"""
        if not (1 <= rating <= 5):
            return "Rating doit être entre 1 et 5."
        stars = "★" * rating + "☆" * (5 - rating)
        text = f"Recette '{recipe_name}' notée {stars}"
        if note:
            text += f" — {note}"
        db.add_memory(user_id, text, category="préférence", importance=2)
        if rating >= 4:
            advice = "Repère-la pour la repropose plus souvent."
        elif rating <= 2:
            advice = "On évite cette recette. Note la raison dans personal_patterns."
        else:
            advice = "OK occasionnel."
        return f"✅ Avis sauvegardé : {stars} pour '{recipe_name}'. {advice}"

    @beta_tool
    def elimination_test(food: str, days: int = 21) -> str:
        """Set up a food elimination test. The user removes X for N days, then \
reintroduces and notes the difference. Used to identify intolerances or \
problematic foods.

Args:
    food: The food/family to eliminate (e.g. 'gluten', 'laitages', 'sucre ajouté', \
'alcool', 'caféine', 'œufs', 'soja').
    days: Duration of elimination. Default 21 (minimum scientifique pour voir effet).
"""
        from datetime import datetime, timezone, timedelta
        today = datetime.now(timezone.utc)
        end_date = (today + timedelta(days=days)).strftime("%Y-%m-%d")
        db.add_memory(
            user_id,
            f"Test d'élimination {food} — {days} jours (J1: {today.strftime('%Y-%m-%d')}, fin: {end_date})",
            category="santé",
            importance=4,
        )
        return (
            f"# 🧪 Test d'élimination — {food} pendant {days} jours\n\n"
            f"Démarre : {today.strftime('%Y-%m-%d')}\n"
            f"Fin : {end_date}\n\n"
            f"## Règles\n"
            f"1. **STRICT** : 0 trace de {food} pendant {days} jours. Une seule "
            f"exposition fait perdre le test.\n"
            f"2. **Vérifie les ingrédients** sur chaque étiquette (le {food} se "
            f"cache partout).\n"
            f"3. **Note quotidiennement** : énergie (1-10), sommeil, digestion, "
            f"peau, humeur, douleurs.\n"
            f"4. **Pas de changement majeur** ailleurs (calories, sport) pour "
            f"isoler la variable.\n\n"
            f"## J1-J3 (sevrage)\n"
            f"Tu peux te sentir moins bien (fatigue, mal de tête, irritabilité). "
            f"Normal, c'est l'adaptation.\n\n"
            f"## J4-J{days}\n"
            f"Observation. Si symptômes améliorés → {food} est probablement "
            f"impliqué. Si rien ne change → ce n'était pas {food} le problème.\n\n"
            f"## Réintroduction (après J{days})\n"
            f"Mange une portion normale de {food} sur 1 jour. Observe les "
            f"symptômes les 48-72h suivantes. Si retour des symptômes → causalité "
            f"confirmée.\n\n"
            f"💡 Mets un rappel J{days} pour le debrief. À ce moment-là Calo "
            f"t'aide à interpréter."
        )

    @beta_tool
    def detect_macro_response(weeks: int = 6) -> str:
        """Look at the past N weeks of meals + weights and detect whether the \
user responds better to higher carbs or higher fats (some lose better with \
60g carbs/day, others with 200g+). Returns a hypothesis for tuning macro split.

Args:
    weeks: Lookback window. Default 6 (need 4+ for signal).
"""
        from datetime import datetime, timezone, timedelta
        weeks = max(4, min(12, int(weeks)))
        since = (datetime.now(timezone.utc) - timedelta(days=weeks * 7)).strftime("%Y-%m-%d")
        meals = db.meals_since(user_id, since)
        weights = db.weights_history(user_id, limit=weeks * 2)
        if len(meals) < weeks * 7 // 2 or len(weights) < 4:
            return (
                "Pas assez de données pour détecter une réponse macro fiable. "
                f"Il faut min 4 sem de logs + 4 pesées. Encourage l'utilisateur "
                f"à logger plus."
            )

        # Group meals by week, compute avg carb % per week
        by_week: dict[int, dict[str, int]] = {}
        for m in meals:
            try:
                dt = datetime.fromisoformat((m.get("eaten_at") or "")[:19].replace("Z", ""))
                week_num = dt.isocalendar()[1]
                day = by_week.setdefault(week_num, {"kcal": 0, "p": 0, "c": 0, "f": 0, "days": set()})
                day["kcal"] += int(m.get("total_calories") or 0)
                day["p"] += int(m.get("total_protein_g") or 0)
                day["c"] += int(m.get("total_carbs_g") or 0)
                day["f"] += int(m.get("total_fat_g") or 0)
                day["days"].add(dt.strftime("%Y-%m-%d"))
            except (ValueError, TypeError):
                continue

        if len(by_week) < 4:
            return "Pas assez de semaines avec données. Continue à logger."

        weeks_sorted = sorted(by_week.keys())
        week_carb_pct: dict[int, float] = {}
        for w in weeks_sorted:
            d = by_week[w]
            days_count = max(1, len(d["days"]))
            avg_kcal = d["kcal"] / days_count
            week_carb_pct[w] = (d["c"] * 4 / avg_kcal * 100) if avg_kcal else 0

        # Try to correlate with weight change per week
        report = ["# 🧬 Analyse de réponse macro\n"]
        report.append(f"Période analysée : {weeks} semaines, {len(by_week)} semaines avec données.\n")
        report.append("## Carb % par semaine")
        for w in weeks_sorted:
            d = by_week[w]
            days_count = max(1, len(d["days"]))
            avg_kcal = d["kcal"] / days_count
            report.append(
                f"- Semaine {w} : {int(avg_kcal)} kcal/j, "
                f"glucides {int(week_carb_pct[w])}% des kcal"
            )

        # Simple heuristic: compare high-carb weeks vs low-carb weeks
        carb_values = list(week_carb_pct.values())
        avg_carb_pct = sum(carb_values) / len(carb_values)
        high_carb_weeks = [w for w in week_carb_pct if week_carb_pct[w] > avg_carb_pct]
        low_carb_weeks = [w for w in week_carb_pct if week_carb_pct[w] <= avg_carb_pct]

        report.append(f"\n## Moyenne : {int(avg_carb_pct)}% des kcal en glucides")
        report.append(
            f"- Semaines high-carb (>{int(avg_carb_pct)}%) : {len(high_carb_weeks)}\n"
            f"- Semaines low-carb (≤{int(avg_carb_pct)}%) : {len(low_carb_weeks)}"
        )

        # Conclusion guidance
        report.append("\n## 🎯 Recommandations")
        report.append(
            "Calo a besoin de plus de variabilité expérimentale pour confirmer : "
            "essaie 2 semaines à 30% carbs (low-carb), puis 2 semaines à 50% "
            "carbs (mod-carb), avec MÊME calories totales. Observe :\n"
            "- Énergie quotidienne\n"
            "- Sommeil\n"
            "- Performance sportive\n"
            "- Évolution poids (à profil cycle constant pour femmes)\n"
            "- Fringales\n\n"
            "Si tu perds mieux ET te sens mieux à 30% carbs → tu es **fat-friendly**. "
            "Si l'inverse → **carb-friendly**. Si pareil → **flexible**, choisis "
            "le rythme qui te plaît le plus.\n\n"
            "Cette info est un TRÉSOR : enregistre-la dans `personal_patterns` "
            "via `update_metabolic_profile`."
        )
        return "\n".join(report)

    @beta_tool
    def refeed_day_plan() -> str:
        """Generate a 1-day refeed plan to reset leptine after extended deficit. \
Use when the user has been in deficit 3+ weeks, is plateauing, or feels \
chronic low energy."""
        user = db.get_user_by_id(user_id)
        if not user:
            return "User not found."
        weight = float(user.get("current_weight_kg") or 70)
        # Refeed = back to maintenance, big carb bump
        carbs_g = int(weight * 4)  # 4 g/kg = high
        protein_g = int(weight * 1.8)
        fat_g = int(weight * 0.6)  # low fat to fit kcal
        total_kcal = protein_g * 4 + carbs_g * 4 + fat_g * 9

        return (
            f"# 🍚 Refeed Day — Reset léptine\n\n"
            f"Pour {weight} kg, cibles d'aujourd'hui :\n"
            f"- **{total_kcal} kcal** (≈ maintenance)\n"
            f"- **{protein_g}g protéines** (1.8g/kg)\n"
            f"- **{carbs_g}g glucides** (4g/kg — HAUT)\n"
            f"- **{fat_g}g lipides** (BAS)\n\n"
            f"## Journée type\n\n"
            f"**Petit-déj (550 kcal)**\n"
            f"- 80g flocons d'avoine + 250ml lait demi-écrémé\n"
            f"- 1 banane + 100g myrtilles\n"
            f"- 1 c.à.s. miel + cannelle\n\n"
            f"**Snack matin (200 kcal)**\n"
            f"- 200g yaourt grec 0% + 1 c.à.s. miel + 1 pomme\n\n"
            f"**Déjeuner (700 kcal)**\n"
            f"- 150g blanc poulet\n"
            f"- 120g riz basmati cuit (cru: 40g)\n"
            f"- 200g légumes vapeur\n"
            f"- 1 fruit + 1 c.à.s. sirop d'érable\n\n"
            f"**Snack après-midi (250 kcal)**\n"
            f"- 1 sandwich pain complet + œuf + tomate\n\n"
            f"**Dîner (500 kcal)**\n"
            f"- 150g cabillaud vapeur\n"
            f"- 200g patate douce four\n"
            f"- 150g légumes\n"
            f"- 1 trait huile olive\n\n"
            f"**Dessert (100-150 kcal)**\n"
            f"- 1 fruit frais ou 30g chocolat noir 70%\n\n"
            f"## Règles\n"
            f"- **Limite les graisses** (le refeed mise sur les glucides)\n"
            f"- **0 alcool** (sabote l'effet leptine)\n"
            f"- **Hydratation 3L** (sodium suit les glucides)\n"
            f"- **Pas de sport HIIT** ce jour-là (récup)\n"
            f"- **Sommeil 8h+** la nuit suivante\n\n"
            f"## Lendemain\n"
            f"- Pèse-toi : poids souvent **+1-2kg le matin suivant** (eau + "
            f"glycogène). C'est NORMAL, ce n'est pas du gras.\n"
            f"- Reprends ton déficit habituel\n"
            f"- Observe l'énergie sur les 3-5 jours suivants (souvent meilleure)\n\n"
            f"💡 Refeed = max 1x/semaine si plateau confirmé. Pas un cheat day, "
            f"un OUTIL physiologique."
        )

    @beta_tool
    def meal_prep_sunday(servings_per_meal: int = 1, lunches_count: int = 5) -> str:
        """Generate a Sunday batch-cooking plan to set up the user's lunches \
for the week. Picks 2-3 batch-friendly recipes from Calo, gives the assembly \
plan + storage tips.

Args:
    servings_per_meal: Portions per meal (default 1).
    lunches_count: How many lunches to prep. Default 5 (Mon-Fri).
"""
        # Find batch-cooking-tagged recipes
        recipes = db.search_recipes(
            tags=["batch cooking"],
            category="déjeuner",
            max_results=5,
        )
        if len(recipes) < 2:
            recipes = db.search_recipes(category="déjeuner", max_results=5)
        if not recipes:
            return "Pas de recettes batch trouvées. Encourage l'utilisateur à enregistrer ses recettes préférées."

        # Pick 2-3 recipes that combined give the lunches count
        picks = recipes[:3] if lunches_count >= 5 else recipes[:2]
        out = [
            f"# 🥘 Plan Batch Cooking — Dimanche pour {lunches_count} déjeuners\n",
            "## Recettes sélectionnées",
        ]
        total_kcal = 0
        for i, r in enumerate(picks, 1):
            multiplier = (lunches_count // len(picks))
            if i <= lunches_count % len(picks):
                multiplier += 1
            out.append(
                f"\n### {i}. {r['name']} × {multiplier} portions\n"
                f"⏱️ {r.get('prep_min')} prep + {r.get('cook_min')} cuisson · "
                f"📊 {r.get('kcal')} kcal/portion"
            )
            total_kcal += (r.get('kcal') or 0) * multiplier
            out.append(f"\n**Ingrédients :**\n{r.get('ingredients', '')}")

        out.append("\n## 🔪 Ordre d'exécution (optimisation temps)")
        out.append(
            "1. **Préchauffe** le four en premier (15 min)\n"
            "2. **Lance les protéines** longues à cuire (poulet, poisson au four)\n"
            "3. **Cuit les féculents** à l'eau pendant que ça cuit au four\n"
            "4. **Hache tous les légumes** en parallèle\n"
            "5. **Sautes les légumes** en fin (5-7 min)\n"
            "6. **Refroidis 30 min** avant de mettre en boîtes\n"
            "7. **Stocke** au frigo"
        )

        out.append("\n## 📦 Storage")
        out.append(
            "- Conteneurs en verre type Pyrex (mieux que plastique pour réchauffer)\n"
            "- Légumes croquants à part si possible (qualité texture)\n"
            "- Frigo 3-4 jours max. Au-delà → congèle.\n"
            "- Sauce vinaigrette à part dans petits pots (sinon les salades sont tristes)"
        )

        out.append("\n## 💡 Astuces pro")
        out.append(
            "- Cuit ton riz/quinoa avec un peu de sel pour qu'il garde du goût refroidi\n"
            "- Acidifie les avocats avec citron pour pas qu'ils noircissent\n"
            "- Lave et essore TOUTE ta salade le dimanche, conserve dans linge propre + boîte\n"
            "- Fais ton snack protéiné aussi (skyr portionné, œufs durs, etc.)"
        )

        out.append(
            f"\n📊 **Total cuisiné** : {total_kcal} kcal sur {lunches_count} déjeuners "
            f"(≈ {total_kcal // lunches_count} kcal/déjeuner)"
        )
        return "\n".join(out)

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

    # ==========================================================================
    # SPORT MODULE — programmes structurés, exos, séances, PRs
    # ==========================================================================

    @beta_tool
    def list_programs(
        goal: str = "",
        equipment: str = "",
        difficulty: str = "",
    ) -> str:
        """List structured multi-week workout programs. Call when the user asks \
"quel programme pour moi", "j'ai besoin d'un plan", "comment m'entraîner sur \
plusieurs semaines". A program is a serious commitment (4-16 weeks) vs a \
one-off `generate_workout`.

Args:
    goal: 'hypertrophie' | 'force' | 'perte de poids' | 'endurance' | \
'marathon' | 'postpartum' | 'senior strength' | 'débutant' | 'home no equipment'.
    equipment: 'salle' | 'maison_basique' | 'maison_équipée' | 'extérieur' | 'course'.
    difficulty: 'débutant' | 'intermédiaire' | 'avancé'.
"""
        progs = db.list_programs(
            goal=goal or None,
            equipment=equipment or None,
            difficulty=difficulty or None,
        )
        if not progs:
            return "Aucun programme ne match ces critères. Ré-essaie sans filtre."
        out = ["# 📋 Programmes Calo disponibles\n"]
        for p in progs:
            out.append(
                f"## {p['name']} ({p.get('duration_weeks')} sem · "
                f"{p.get('days_per_week')}j/sem · {p.get('difficulty')})"
            )
            out.append(f"🎯 Objectif : {p.get('goal')}")
            out.append(f"🏋️ Matériel : {', '.join(p.get('equipment') or [])}")
            out.append(f"_{p.get('description', '')[:200]}..._" if p.get('description') and len(p.get('description', '')) > 200 else f"_{p.get('description', '')}_")
            out.append(f"Slug : `{p.get('slug')}`\n")
        out.append("💡 Propose à l'utilisateur le programme le plus adapté à son profil, "
                   "son matériel et son objectif. Appelle `get_program_details(slug)` "
                   "pour voir la structure complète.")
        return "\n".join(out)

    @beta_tool
    def get_program_details(slug: str) -> str:
        """Get the full structure of a specific program (weekly plan day by day).

Args:
    slug: The program slug (e.g. 'hypertrophie-12sem', 'marathon-12sem').
"""
        p = db.get_program_by_slug(slug)
        if not p:
            return f"Aucun programme trouvé avec slug '{slug}'. Appelle `list_programs`."
        return (
            f"# {p['name']}\n"
            f"⏱️ {p.get('duration_weeks')} sem · {p.get('days_per_week')}j/sem · "
            f"{p.get('difficulty')}\n"
            f"🎯 {p.get('goal')}\n"
            f"🏋️ Matériel : {', '.join(p.get('equipment') or [])}\n\n"
            f"## Description\n{p.get('description', '')}\n\n"
            f"## Structure hebdomadaire\n{p.get('weekly_structure', '')}"
        )

    @beta_tool
    def start_program(slug: str) -> str:
        """Subscribe the user to a structured workout program. ONLY call once \
the user has confirmed ("ok je commence", "go"). Saves start date + resets \
workouts counter.

Args:
    slug: The program slug.
"""
        from datetime import datetime, timezone
        p = db.get_program_by_slug(slug)
        if not p:
            return f"Programme '{slug}' introuvable."
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        db.update_user(
            user_id,
            active_program=slug,
            program_started_at=today,
            workouts_completed=0,
        )
        db.add_memory(
            user_id,
            f"Programme {p['name']} démarré le {today} "
            f"({p.get('duration_weeks')} sem, {p.get('days_per_week')}j/sem)",
            category="sport",
            importance=4,
        )
        return (
            f"✅ Programme **{p['name']}** activé. J1/{p.get('duration_weeks') * 7}.\n\n"
            f"Présente la STRUCTURE de la 1ère semaine à l'utilisateur, propose la "
            f"première séance MAINTENANT, rappelle les règles clés (sommeil, prot, "
            f"hydratation), et engage-le sur un J1 concret aujourd'hui ou demain."
        )

    @beta_tool
    def get_today_workout() -> str:
        """Return today's workout session based on the user's active program + \
elapsed days. Calo computes which day of the week structure to suggest."""
        from datetime import datetime, timezone
        user = db.get_user_by_id(user_id)
        if not user:
            return "User not found."
        slug = user.get("active_program")
        if not slug:
            return ("Aucun programme actif. Propose à l'utilisateur d'en "
                    "choisir un via `list_programs`.")
        p = db.get_program_by_slug(slug)
        if not p:
            return f"Programme '{slug}' introuvable (peut-être supprimé)."
        started = user.get("program_started_at")
        if not started:
            return "Date de démarrage manquante. Relance `start_program(slug)`."
        try:
            d0 = datetime.strptime(started, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            days_elapsed = (datetime.now(timezone.utc) - d0).days
            week_num = days_elapsed // 7 + 1
            day_in_week = days_elapsed % 7 + 1
        except (ValueError, TypeError):
            week_num, day_in_week = 1, 1
        return (
            f"# 📅 Séance du jour — {p['name']}\n"
            f"Sem {week_num}/{p.get('duration_weeks')} · Jour {day_in_week}/7\n\n"
            f"## Structure complète\n{p.get('weekly_structure', '')}\n\n"
            f"💡 Identifie la séance correspondant au jour {day_in_week} (ou jour "
            f"de repos si applicable). Présente UNIQUEMENT cette séance avec exos, "
            f"séries, reps, repos. Ajoute des conseils d'exécution sur les exos clés. "
            f"À la fin demande au user de logger la séance via `log_workout_session`."
        )

    @beta_tool
    def log_workout_session(
        session_name: str,
        exercises_text: str,
        day_name: str = "",
        duration_min: int = 0,
        rpe: int = 0,
        pr_hit: bool = False,
        note: str = "",
    ) -> str:
        """Log a completed workout session. Call AFTER the user reports having \
done a training. Format `exercises_text` as lines: `Exercise|sets|reps|weight_kg|rpe`.

Args:
    session_name: Short label (e.g. 'Upper A Sem 3').
    exercises_text: Multi-line log e.g. 'Squat|4|8|80|7\\nBench|4|8|60|7\\nDeadlift|3|5|100|8'.
    day_name: Optional day label from program (e.g. 'Upper A', 'Push').
    duration_min: Session duration.
    rpe: Global RPE 1-10.
    pr_hit: True if user hit a personal record this session.
    note: Free text (energy, form, soreness).
"""
        from datetime import datetime, timezone
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        user = db.get_user_by_id(user_id)
        program_id = None
        if user and user.get("active_program"):
            p = db.get_program_by_slug(user["active_program"])
            if p:
                program_id = p["id"]
        db.log_workout(
            user_id=user_id,
            session_name=session_name,
            date_iso=today,
            exercises_text=exercises_text,
            program_id=program_id,
            day_name=day_name or None,
            duration_min=duration_min or None,
            rpe=rpe or None,
            note=note or None,
            pr_hit=pr_hit,
        )
        # Increment counter
        if user:
            new_count = int(user.get("workouts_completed") or 0) + 1
            db.update_user(user_id, workouts_completed=new_count)
        feedback = []
        if pr_hit:
            feedback.append("🏆 **PR atteint** — célèbre ce moment, c'est de l'or pour la motivation !")
            db.add_memory(
                user_id,
                f"PR session {today} : {session_name}",
                category="sport",
                importance=4,
            )
        if rpe and rpe >= 9:
            feedback.append("⚠️ RPE 9+ : récupération sera longue. Sommeil 8h+, hydratation, nutrition post.")
        if duration_min and duration_min > 90:
            feedback.append("⏱️ Séance >90 min : risque chute testostérone, viser <75 min sur les prochaines.")
        return (
            f"✅ Séance loggée : **{session_name}** ({today})"
            + (f"\n\n" + "\n".join(feedback) if feedback else "")
        )

    @beta_tool
    def get_exercise_help(name: str) -> str:
        """Look up an exercise in the library : technique, common mistakes, \
regressions, progressions. Call when the user asks "comment faire X", \
"technique squat", "j'ai mal au dos en deadlift".

Args:
    name: Exercise name in French (e.g. 'squat', 'développé couché', 'soulevé de terre').
"""
        ex = db.get_exercise_by_name(name)
        if not ex:
            return (
                f"Exercice '{name}' pas dans la bibliothèque. "
                "Réponds depuis ton expertise, focus technique + erreurs courantes + "
                "régressions/progressions."
            )
        return (
            f"# {ex['name']}\n"
            f"📂 Catégorie : {ex.get('category')}\n"
            f"🏋️ Matériel : {', '.join(ex.get('equipment') or [])}\n"
            f"⚡ Difficulté : {ex.get('difficulty')}\n"
            f"💪 Muscles : {', '.join(ex.get('primary_muscles') or [])}\n\n"
            f"## Technique\n{ex.get('technique', '')}\n\n"
            f"## ❌ Erreurs courantes\n{ex.get('common_mistakes', '')}\n\n"
            f"## ⬇️ Régressions (plus facile)\n{ex.get('regressions', '')}\n\n"
            f"## ⬆️ Progressions (plus difficile)\n{ex.get('progressions', '')}"
        )

    @beta_tool
    def analyze_training_progress(weeks: int = 4) -> str:
        """Analyse the user's last N weeks of workout logs : volume, intensity, \
PRs, fatigue patterns. Detects need for deload or progression. Use when user \
asks 'où j'en suis sur mon programme', 'je stagne', 'devrais-je déloader'.

Args:
    weeks: Lookback weeks. Default 4.
"""
        from datetime import datetime, timedelta, timezone
        weeks = max(2, min(12, int(weeks)))
        since = (datetime.now(timezone.utc) - timedelta(days=weeks * 7)).strftime("%Y-%m-%d")
        logs = db.workout_logs_since(user_id, since)
        if not logs:
            return f"Aucune séance loggée sur les {weeks} dernières sem. Relance le logging."

        total_sessions = len(logs)
        prs = sum(1 for l in logs if l.get("pr_hit"))
        avg_rpe = (
            sum(int(l.get("rpe") or 0) for l in logs if l.get("rpe"))
            / max(1, sum(1 for l in logs if l.get("rpe")))
        )
        avg_duration = (
            sum(int(l.get("duration_min") or 0) for l in logs if l.get("duration_min"))
            / max(1, sum(1 for l in logs if l.get("duration_min")))
        )
        sessions_per_week = total_sessions / weeks

        # Flags
        flags = []
        if sessions_per_week < 2:
            flags.append(f"⚠️ Adhérence faible ({sessions_per_week:.1f} séance/sem). Identifier obstacles.")
        if avg_rpe >= 8.5:
            flags.append(f"⚠️ RPE moyen {avg_rpe:.1f} = très intense. Déload conseillé semaine prochaine.")
        if avg_duration > 80:
            flags.append(f"⏱️ Durée moyenne {avg_duration:.0f} min = long. Viser <75 min pour optimiser.")
        if prs == 0 and weeks >= 4:
            flags.append("⚠️ 0 PR sur la période = plateau force probable. Revoir programmation ou déload.")

        return (
            f"# 📊 Bilan training {weeks} sem\n\n"
            f"- **{total_sessions} séances** ({sessions_per_week:.1f}/sem)\n"
            f"- **{prs} PRs** atteints\n"
            f"- **RPE moyen** : {avg_rpe:.1f}/10\n"
            f"- **Durée moyenne** : {avg_duration:.0f} min\n\n"
            + ("## 🔍 Constats\n" + "\n".join(flags) + "\n\n" if flags else "")
            + "💡 Présente ce bilan AVEC empathie. Si RPE élevé constant ou 0 PR : "
            "propose déload (-40% volume sem prochaine). Si bonne progression : célèbre. "
            "Si adhérence faible : creuse les obstacles, ajuste le programme."
        )

    @beta_tool
    def update_personal_records(updates: str) -> str:
        """Update the user's personal records (PRs). Use when they report a new \
max (squat, bench, dead, course 10km, etc.).

Args:
    updates: Text of new records, e.g. 'squat 100kg\\nbench 80kg\\n10km 52min'.
"""
        from datetime import datetime, timezone
        user = db.get_user_by_id(user_id)
        if not user:
            return "User not found."
        existing = user.get("personal_records") or ""
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        new_block = f"[{ts}]\n{updates}"
        merged = (existing + "\n\n" + new_block).strip() if existing else new_block
        db.update_user(user_id, personal_records=merged)
        db.add_memory(
            user_id,
            f"Nouveau(x) PR le {ts} : {updates}",
            category="sport",
            importance=4,
        )
        return f"🏆 PRs sauvegardés :\n{updates}\n\nCélèbre ces progressions avec l'utilisateur !"

    # ==========================================================================
    # MENTAL MODULE — stress, anxiety, burnout, cognition
    # ==========================================================================

    @beta_tool
    def breathing_protocol(situation: str = "stress") -> str:
        """Generate a tailored breathing protocol for the user's current state. \
Use when user mentions stress, anxiety, panic, sleep prep, pre-workout, \
post-workout, focus needed.

Args:
    situation: 'stress' | 'panic' | 'sommeil' | 'pre-workout' | 'post-workout' | 'focus'.
"""
        s = situation.lower()
        protocols = {
            "stress": (
                "# 🌬️ Cohérence cardiaque — Anti-stress\n\n"
                "**5 minutes, 6 respirations/min.**\n\n"
                "- Inspire 5 secondes par le nez\n"
                "- Expire 5 secondes par la bouche\n"
                "- Répète 30 cycles (= 5 min)\n\n"
                "**Effet** : active le parasympathique, baisse cortisol de 20-30%, "
                "stabilise variabilité cardiaque. À faire 3x/jour (matin, midi, "
                "avant coucher) pour effet cumulatif maximal."
            ),
            "panic": (
                "# 🚨 SOS Panique — Respiration 4-7-8\n\n"
                "**Cycle physiologique, force le calme.**\n\n"
                "- Inspire **4 sec** par le nez\n"
                "- Retiens **7 sec** poumons pleins\n"
                "- Expire **8 sec** par la bouche (souffle long)\n"
                "- Répète 4 cycles, puis pause 30 sec\n"
                "- Refais 4 cycles\n\n"
                "**Bonus** : ancrage 5-4-3-2-1 simultanément (5 choses que tu "
                "vois, 4 que tu touches, 3 que tu entends, 2 que tu sens, 1 "
                "que tu goûtes). Recentre le système nerveux en 90 sec."
            ),
            "sommeil": (
                "# 😴 Pré-sommeil — Respiration nasale lente\n\n"
                "**Allongé dans le lit, lumières éteintes.**\n\n"
                "- Inspire 4 sec par le nez\n"
                "- Expire 6-8 sec par le nez (plus long que l'inspiration)\n"
                "- 10-15 cycles\n"
                "- Si pensées : reviens à la respiration sans juger\n\n"
                "**Bonus** : scan corporel (tête → orteils, relâche chaque zone). "
                "90% des cas, sommeil <15 min."
            ),
            "pre-workout": (
                "# 🔥 Pre-workout — Activation\n\n"
                "**3 minutes pour mobiliser.**\n\n"
                "- Inspire 4 sec par le nez\n"
                "- Expire 2 sec par la bouche (forte, courte)\n"
                "- Répète 20 cycles\n"
                "- Termine par 3 grandes inspirations\n\n"
                "**Effet** : augmente CO2 toléré, baisse anxiété de performance, "
                "active sympathique modéré (pas panique)."
            ),
            "post-workout": (
                "# 🧘 Post-workout — Récupération\n\n"
                "**5 min cohérence cardiaque + nasal**\n\n"
                "- Allongé sur le dos\n"
                "- Inspire 4 sec par le nez\n"
                "- Pause 2 sec\n"
                "- Expire 6 sec par le nez\n"
                "- 30 cycles\n\n"
                "**Effet** : accélère retour parasympathique, baisse cortisol "
                "post-effort, optimise récupération."
            ),
            "focus": (
                "# 🎯 Focus deep work — Box breathing\n\n"
                "**Méthode Navy SEALs.**\n\n"
                "- Inspire 4 sec\n"
                "- Retiens 4 sec\n"
                "- Expire 4 sec\n"
                "- Retiens 4 sec (vide)\n"
                "- Répète 5 min\n\n"
                "**Effet** : calme mental + focus aiguisé. Idéal avant session "
                "deep work ou présentation."
            ),
        }
        return protocols.get(s, protocols["stress"])

    @beta_tool
    def anti_anxiety_toolkit() -> str:
        """SOS anxiety toolkit — 5 immediate techniques to deploy when the user \
is in anxiety/panic. Use when user mentions panic, anxiety attack, racing \
thoughts, can't breathe, overwhelmed."""
        return (
            "# 🆘 SOS Anxiété — Boîte à outils immédiate\n\n"
            "## 1️⃣ Ancrage 5-4-3-2-1 (30 sec)\n"
            "Nomme à voix haute :\n"
            "- **5** choses que tu VOIS autour de toi\n"
            "- **4** choses que tu peux TOUCHER\n"
            "- **3** sons que tu ENTENDS\n"
            "- **2** odeurs que tu peux SENTIR\n"
            "- **1** goût dans ta bouche\n"
            "→ Force le cerveau hors de la spirale anxieuse, retour au présent.\n\n"
            "## 2️⃣ Respiration 4-7-8 (90 sec)\n"
            "- Inspire 4 sec nez\n"
            "- Retiens 7 sec\n"
            "- Expire 8 sec bouche\n"
            "- 4 cycles, pause, 4 cycles\n"
            "→ Active le parasympathique, baisse pulsation en 90 sec.\n\n"
            "## 3️⃣ Eau glacée sur visage (immersion frontale)\n"
            "Plonger le visage dans bol d'eau froide 15-30 sec, OU compresse "
            "froide front + tempes.\n"
            "→ Réflexe mammifère, baisse pulsation immédiate.\n\n"
            "## 4️⃣ Mouvement (10 min)\n"
            "Marche rapide DEHORS ou montée d'escaliers. Le mouvement consomme "
            "le cortisol et l'adrénaline en excès.\n\n"
            "## 5️⃣ Nommer + écrire (15 min)\n"
            "Ouvre un carnet. Écris sans filtre :\n"
            "- Qu'est-ce que je ressens ?\n"
            "- À quoi je le rattache ?\n"
            "- Quel est le pire scénario réaliste ? Le meilleur ? Le plus probable ?\n"
            "- Qu'est-ce que je peux contrôler maintenant ?\n"
            "→ Décharge cognitive, prise de recul.\n\n"
            "## ⚠️ Quand consulter\n"
            "Si attaques de panique répétées (>2/sem), anxiété qui bloque le "
            "quotidien, ou pensées sombres : **consultation pro indispensable** "
            "(psychologue, médecin). Calo n'est PAS un substitut au soin."
        )

    @beta_tool
    def cognitive_reframe(negative_thought: str) -> str:
        """Cognitive behavioral therapy (CBT) framework to reframe a negative \
thought. Use when user expresses harsh self-talk: 'je suis nul', 'jamais je \
n'y arriverai', 'tout est foutu', 'je dois être parfait'.

Args:
    negative_thought: The exact negative thought the user expressed.
"""
        return (
            f"# 🧠 Recadrage cognitif — TCC\n\n"
            f"Pensée actuelle :\n> _\"{negative_thought}\"_\n\n"
            f"## Étape 1 — Identifie le biais\n"
            f"Lesquel(s) reconnais-tu dans cette pensée ?\n\n"
            f"- **Pensée tout-ou-rien** : 'Si je ne suis pas parfait, je suis nul'\n"
            f"- **Catastrophisme** : 'Si je rate, tout est foutu'\n"
            f"- **Filtrage négatif** : ne voir que les échecs, ignorer les réussites\n"
            f"- **Personnalisation** : 'C'est forcément ma faute'\n"
            f"- **Lecture de pensée** : 'Les autres pensent que...'\n"
            f"- **Étiquetage** : 'Je SUIS nul' au lieu de 'J'ai raté'\n"
            f"- **Should statements** : 'Je dois / il faut que' (rigide)\n\n"
            f"## Étape 2 — Questionne la pensée\n"
            f"- Quelle est la PREUVE concrète de cette pensée ?\n"
            f"- Quelle est la preuve du CONTRAIRE ?\n"
            f"- Est-ce que je dirais ça à mon meilleur ami dans la même situation ?\n"
            f"- Dans 5 ans, est-ce que ça aura encore de l'importance ?\n"
            f"- Est-ce un fait ou un sentiment ?\n\n"
            f"## Étape 3 — Reformule\n"
            f"Au lieu de :\n_\"{negative_thought}\"_\n\n"
            f"Propose une version NUANCÉE + ACTIONNABLE. Exemple générique :\n"
            f"- 'J'ai eu UN écart aujourd'hui, ça ne définit pas tout mon parcours'\n"
            f"- 'Cette difficulté est temporaire, j'ai déjà surmonté pire'\n"
            f"- 'Je n'ai pas réussi CETTE FOIS, voici ce que j'apprends pour la prochaine'\n\n"
            f"## Étape 4 — Action\n"
            f"Quelle UNE chose concrète tu peux faire dans les 10 prochaines minutes "
            f"qui aille dans le sens de qui tu veux devenir ?"
        )

    @beta_tool
    def burnout_assessment() -> str:
        """Quick burnout / over-training assessment. Use when user mentions \
chronic fatigue, no motivation, ED-like patterns, training despite injury, \
sleep disorders, emotional flatness."""
        return (
            "# 🔥 Évaluation Burn-out / Surentraînement\n\n"
            "Réponds OUI / NON à chacune (compte les OUI à la fin).\n\n"
            "## Physique\n"
            "1. Fatigue qui ne passe pas après 8h de sommeil\n"
            "2. Fréquence cardiaque de repos en hausse (+5 bpm vs habituel)\n"
            "3. Performances en baisse malgré effort équivalent\n"
            "4. Récupération musculaire qui s'allonge (DOMS >4 jours)\n"
            "5. Sommeil fragmenté (réveils 3-4h)\n"
            "6. Infections à répétition (rhumes, angines)\n"
            "7. Blessures ou douleurs récurrentes\n"
            "8. Perte d'appétit OU fringales sucrées intenses\n"
            "9. Libido en baisse\n"
            "10. Cycles menstruels perturbés / aménorrhée\n\n"
            "## Psychologique\n"
            "11. Plus de plaisir à s'entraîner\n"
            "12. Irritabilité sans raison\n"
            "13. Sentiment de devoir 'mériter' la nourriture / repos\n"
            "14. Anxiété de performance avant chaque séance\n"
            "15. Pensées récurrentes : 'pas assez', 'jamais assez fait'\n"
            "16. Incapacité à déconnecter (boulot, sport)\n"
            "17. Pleurs faciles ou émotionnel à fleur de peau\n"
            "18. Brouillard mental, oublis fréquents\n"
            "19. Sentiment d'épuisement émotionnel\n"
            "20. Désintérêt général (hobbies, famille, amis)\n\n"
            "## Lecture des résultats\n"
            "- **0-4 OUI** : RAS, continue bonne routine\n"
            "- **5-9 OUI** : 🟡 Signaux de surmenage. Déload OBLIGATOIRE 1-2 sem "
            "(volume -50%, sommeil ++, alimentation maintien). Réévalue après.\n"
            "- **10-14 OUI** : 🟠 Pré-burnout. Stop intensité 2-4 sem, focus "
            "récup totale. Consulte médecin pour bilan sanguin complet (TSH, "
            "cortisol salivaire 4x/j, ferritine, vit D, testostérone).\n"
            "- **15+ OUI** : 🔴 BURN-OUT installé. STOP sport intense. "
            "**Consultation médicale obligatoire**, possiblement arrêt travail, "
            "accompagnement psy. Ne joue PAS avec ça.\n\n"
            "💡 Présente ces questions à l'utilisateur SANS dramatiser. "
            "Aide-le à compter ses OUI. Si ≥10, **insiste sur consultation pro** "
            "(médecin + psychologue). Met à jour `mental_profile` avec les insights."
        )

    @beta_tool
    def update_mental_profile(note: str) -> str:
        """Append a structured note to the user's mental health profile. Use when \
the user shares context relevant to mental health: anxiety, depression history, \
ED recovery, burnout, therapy, medication psy.

Args:
    note: What was learned about the user's mental health context.
"""
        from datetime import datetime, timezone
        user = db.get_user_by_id(user_id)
        if not user:
            return "User not found."
        existing = user.get("mental_profile") or ""
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        new = f"[{ts}] {note}"
        merged = (existing + "\n" + new).strip() if existing else new
        db.update_user(user_id, mental_profile=merged)
        return f"✅ Profil mental enrichi : {note}"

    # ==========================================================================
    # PREMIUM features — machine recognition, charts, coach handoff
    # ==========================================================================

    @beta_tool
    def explain_gym_machine(
        machine_summary: str = "",
        target_muscles_guess: str = "",
    ) -> str:
        """User has sent a photo of a gym machine or exercise they want to \
understand. Read the photo with vision, then call THIS tool with what you see. \
Returns a structured guide : matched library entry if available (technique, \
common mistakes, regressions, progressions), or a comprehensive framework if \
not. PREMIUM feature : un débutant en salle arrête de stresser, un confirmé \
optimise.

Args:
    machine_summary: Précisément ce que tu vois sur la photo (e.g. 'machine \
guidée développé couché Hammer Strength', 'leg press 45° avec 4 poids de \
20kg', 'rameur Concept2', 'smith machine avec barre', 'pec deck butterfly', \
'TRX avec sangles', 'banc Larry Scott preacher curl', 'hack squat machine', \
'cable crossover'). Si tu reconnais une machine de la liste : utilise SON \
nom exact pour optimiser le match.
    target_muscles_guess: Muscles visiblement ciblés (e.g. 'pectoraux + \
triceps', 'fessiers + ischios', 'quadriceps', 'lats + biceps').
"""
        if not machine_summary:
            return (
                "Décris d'abord ce que tu vois sur la photo dans 'machine_summary' "
                "(type de machine, accessoires visibles, charge, position des \
appuis). Plus tu es précis, mieux je matche dans la bibliothèque."
            )

        # Try multiple matches to find the best library entry.
        # Match strategies (order of priority) :
        #  1. Direct name search
        #  2. Each keyword in the summary
        matched_ex = db.get_exercise_by_name(machine_summary)
        if not matched_ex:
            # Try each significant keyword
            words = [w for w in machine_summary.lower().split() if len(w) >= 4]
            for w in words[:5]:  # cap to avoid spam
                matched_ex = db.get_exercise_by_name(w)
                if matched_ex:
                    break

        if matched_ex:
            # Récupère les conditions médicales de l'utilisateur pour adapter
            user = db.get_user_by_id(user_id)
            user_conditions = (user or {}).get("medical_conditions") or ""
            contraindic = matched_ex.get("contraindications") or ""
            best_for = matched_ex.get("best_for") or []

            # Détection automatique des risques selon les pathologies user
            warnings: list[str] = []
            user_lower = user_conditions.lower()
            contraindic_lower = contraindic.lower()
            risk_zones = [
                ("genou", "genoux"),
                ("hanche", "hanche"),
                ("dos", "lombaires"),
                ("lombaire", "lombaires"),
                ("hernie", "lombaires"),
                ("épaule", "épaules"),
                ("arthrose", "arthrose"),
                ("ostéoporose", "ostéoporose"),
                ("postpartum", "postpartum"),
                ("grossesse", "grossesse"),
            ]
            for user_word, zone_key in risk_zones:
                if user_word in user_lower and zone_key in contraindic_lower:
                    warnings.append(
                        f"⚠️ Tu as mentionné **{user_word}** dans ton profil médical. "
                        f"Pour cet exo, regarde la section Contraindications ci-dessous."
                    )

            return (
                f"# 🏋️ {matched_ex['name']} (matché bibliothèque Calo)\n\n"
                f"📂 **Catégorie** : {matched_ex.get('category')}\n"
                f"🏋️ **Matériel** : {', '.join(matched_ex.get('equipment') or [])}\n"
                f"⚡ **Difficulté** : {matched_ex.get('difficulty')}\n"
                f"💪 **Muscles ciblés** : {', '.join(matched_ex.get('primary_muscles') or [])}\n"
                + (f"🎯 **Recommandé pour** : {', '.join(best_for)}\n" if best_for else "")
                + ("\n" + "\n".join(warnings) + "\n" if warnings else "")
                + (f"\n## ⚕️ Contraindications / adaptations\n{contraindic}\n" if contraindic else "")
                + f"\n## 📋 Technique\n{matched_ex.get('technique', '')}\n\n"
                f"## ❌ Erreurs courantes\n{matched_ex.get('common_mistakes', '')}\n\n"
                f"## ⬇️ Régressions (plus facile)\n{matched_ex.get('regressions', '')}\n\n"
                f"## ⬆️ Progressions (plus dur)\n{matched_ex.get('progressions', '')}\n\n"
                f"## 💡 À toi de jouer\n"
                f"1. Présente ces infos à l'utilisateur avec ton ton humain\n"
                f"2. **VÉRIFIE les pathologies du user** dans le state reminder "
                f"(medical_conditions). Si match avec contraindications → propose "
                f"une **régression** ou alternative safe\n"
                f"3. Adapte les conseils à son OBJECTIF (perte de poids = "
                f"séries longues 12-15 reps ; force = lourd 4-6 reps ; "
                f"hypertrophie = 8-12 reps modéré-lourd)\n"
                f"4. Suggère un nombre de séries/reps précis basé sur son "
                f"state reminder (programme actif, niveau, expérience)\n"
                f"5. Si pathologie sérieuse + douleur active : recommande "
                f"consultation kiné / médecin AVANT.\n"
                f"6. Termine par : 'Tu veux qu'on l'intègre dans ta prochaine "
                f"séance ?' pour engager."
            )

        # Fallback : pas dans la library → cadre générique mais riche
        return (
            f"# 🏋️ Décodage machine (pas dans la bibliothèque — utilise ton expertise)\n\n"
            f"Tu as vu : **{machine_summary}**\n"
            f"Muscles ciblés : {target_muscles_guess or 'à identifier'}\n\n"
            f"## 📋 Cadre d'analyse à fournir\n\n"
            f"### 1. Identifier le mouvement principal\n"
            f"- C'est une **machine guidée** (smith, hammer strength, machine "
            f"convergente, machine guidée verticale) ou **libre** (haltères, "
            f"barre, kettlebell, TRX) ?\n"
            f"- Mouvement de **poussée** (push), **tirage** (pull), ou "
            f"**isolation** ?\n"
            f"- Plan : horizontal / vertical / oblique ?\n\n"
            f"### 2. Réglages avant utilisation (TRÈS IMPORTANT)\n"
            f"- **Hauteur du siège** : varie selon l'exercice. Repère : "
            f"l'articulation principale (épaule, hanche, genou) doit être alignée "
            f"avec l'axe de rotation de la machine\n"
            f"- **Position des pieds / appuis** : stable, plante complète au sol\n"
            f"- **Sécurités** : ceinture, butées, prise correcte des poignées\n"
            f"- **Charge** : commence LÉGER (40-50% de ce que tu fais en libre)\n\n"
            f"### 3. Exécution\n"
            f"- 2-3 sec descente (excentrique = le plus important pour "
            f"croissance musculaire)\n"
            f"- 1 sec pause / contraction max\n"
            f"- 1-2 sec montée explosive\n"
            f"- ROM (amplitude) complet sans hyperextension\n"
            f"- Respiration : inspire à la descente, expire à la montée\n"
            f"- 8-12 reps si hypertrophie, 4-6 reps si force, 15+ reps si "
            f"endurance\n\n"
            f"### 4. Erreurs classiques sur les machines\n"
            f"- **Mauvaise hauteur de siège** : impacte le mouvement et "
            f"stresse les articulations\n"
            f"- **Charge trop lourde** : la machine guide = on en met trop. "
            f"Commence léger, augmente quand ROM + form parfaits\n"
            f"- **ROM partiel** : descends complètement, monte complètement\n"
            f"- **Verrouiller l'articulation** en haut : garde légèrement fléchi\n"
            f"- **Lâcher la charge** (les poids claquent) : contrôle la phase "
            f"excentrique\n\n"
            f"### 5. Alternative si machine indispo / occupée\n"
            f"- Variante haltères / barre / élastique\n"
            f"- Variante poids du corps\n"
            f"- Variante autre machine équivalente\n\n"
            f"## Tes consignes Calo\n"
            f"1. **Identifie précisément** la machine avec la photo + summary "
            f"que tu as. Tu connais la plupart des machines de salle.\n"
            f"2. **Donne les réglages spécifiques** (hauteur siège, position "
            f"pieds, prise, charge de départ)\n"
            f"3. **Explique l'exécution** étape par étape, pédagogique, "
            f"comme à un débutant\n"
            f"4. **Cite 3-5 erreurs courantes** pour cette machine "
            f"spécifiquement\n"
            f"5. **Propose 2-3 alternatives** si pas dispo / occupée\n"
            f"6. **Suggère séries/reps** adaptés à l'objectif de l'utilisateur "
            f"(utilise le state reminder pour personnaliser)\n"
            f"7. Termine par engagement : 'Tu veux qu'on l'ajoute à ta "
            f"prochaine séance ?'"
        )

    @beta_tool
    def send_progress_chart(chart_type: str = "weight") -> str:
        """Generate and send a PNG chart via WhatsApp. Call when the user asks \
'mon graphe', 'évolution poids', 'macros du jour', 'mon adhérence', \
'mon training'. Or proactively at end-of-week debrief. PREMIUM feature : le \
client reçoit une image partageable.

Args:
    chart_type: 'weight' (trajectoire poids 90j) | 'macros' (macros du jour) \
| 'adherence' (heatmap 30j) | 'workout' (volume training 12 sem).
"""
        if not public_url_base:
            return (
                "Génération de chart indisponible (public_url_base non configuré). "
                "Donne plutôt la donnée en texte."
            )
        user = db.get_user_by_id(user_id)
        if not user:
            return "User not found."
        name = user.get("name") or "toi"

        try:
            if chart_type == "weight":
                weights = db.weights_history(user_id, limit=60)
                token, _ = chart_generator.weight_chart(
                    name, weights, user.get("target_weight_kg")
                )
                caption = f"📈 Ton évolution poids, {name}. Continue 💪"
            elif chart_type == "macros":
                today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
                meals = db.meals_for_day(user_id, today)
                actual = {
                    "kcal": sum(int(m.get("total_calories") or 0) for m in meals),
                    "protein": sum(int(m.get("total_protein_g") or 0) for m in meals),
                    "carbs": sum(int(m.get("total_carbs_g") or 0) for m in meals),
                    "fat": sum(int(m.get("total_fat_g") or 0) for m in meals),
                }
                target = {
                    "kcal": user.get("daily_calories") or 0,
                    "protein": user.get("daily_protein_g") or 0,
                    "carbs": user.get("daily_carbs_g") or 0,
                    "fat": user.get("daily_fat_g") or 0,
                }
                token, _ = chart_generator.macros_chart(name, actual, target)
                caption = f"🍽️ Macros du jour"
            elif chart_type == "adherence":
                since = (datetime.now(timezone.utc) - timedelta(days=30)).strftime("%Y-%m-%d")
                meals = db.meals_since(user_id, since)
                by_day: dict[str, list] = {}
                for m in meals:
                    day = (m.get("eaten_at") or "")[:10]
                    by_day.setdefault(day, []).append(m)
                target_kcal = user.get("daily_calories") or 2000
                days_data = []
                for day, day_meals in sorted(by_day.items())[-30:]:
                    kcal = sum(int(m.get("total_calories") or 0) for m in day_meals)
                    adherence = min(100, int(kcal / target_kcal * 100)) if target_kcal else 0
                    days_data.append({"date": day, "adherence": adherence})
                token, _ = chart_generator.adherence_heatmap(name, days_data)
                caption = f"✅ Ton adhérence sur 30 jours"
            elif chart_type == "workout":
                since = (datetime.now(timezone.utc) - timedelta(days=84)).strftime("%Y-%m-%d")
                logs = db.workout_logs_since(user_id, since)
                token, _ = chart_generator.workout_volume_chart(name, logs)
                caption = f"🏋️ Ton volume training, {name}"
            else:
                return f"Type de chart inconnu : {chart_type}. Options : weight, macros, adherence, workout."
        except Exception as exc:  # noqa: BLE001
            return f"Erreur génération chart : {exc}. Fais un debrief texte."

        url = f"{public_url_base.rstrip('/')}/chart/{token}"
        attachments.append({"url": url, "caption": caption})
        return (
            f"✅ Chart **{chart_type}** généré et envoyé en image WhatsApp. "
            f"Ajoute un commentaire court dans ta réponse texte pour contextualiser "
            f"(la photo arrive juste après)."
        )

    @beta_tool
    def find_safe_alternatives(
        injury_zone: str,
        muscle_group: str = "",
        max_results: int = 8,
    ) -> str:
        """Liste les exercices SÉCURISÉS pour une zone blessée/fragile. Appelle \
ce tool dès que l'utilisateur mentionne : douleur genou, hanche, dos/lombaires, \
épaule, arthrose, hernie, postpartum, ostéoporose, grossesse. Calo doit TOUJOURS \
préférer des exos validés contre des exos non-évalués pour la zone.

Args:
    injury_zone: 'genoux fragiles' | 'hanche fragile' | 'lombaires fragiles' | \
'épaules fragiles' | 'arthrose' | 'ostéoporose' | 'postpartum' | 'grossesse' | \
'senior 65+' | 'rééducation' (ces valeurs matchent exactement les tags \
'Best for' de la library).
    muscle_group: Optionnel — pour filtrer par catégorie ('jambes', 'dos', \
'pecs', 'épaules', 'bras', 'core', 'cardio', 'mobilité').
"""
        # Match library exercises explicitly tagged for this safe category
        results = db.list_exercises(
            best_for=injury_zone,
            category=muscle_group or None,
            max_results=max_results,
        )
        if not results:
            return (
                f"Aucun exercice spécifiquement tagué '{injury_zone}' dans la "
                f"library. Utilise ton expertise pour proposer : 1) Mouvements "
                f"sans impact ; 2) ROM réduit ; 3) Charge légère ; 4) Focus "
                f"mobilité + activation ; 5) RECOMMANDE consultation kiné/médecin "
                f"si douleur active >3/10."
            )
        out = [f"# ✅ Exos sécurisés pour : **{injury_zone}**"]
        if muscle_group:
            out.append(f"Filtré par : {muscle_group}\n")
        for ex in results:
            out.append(
                f"\n## {ex['name']} ({ex.get('difficulty')})"
            )
            out.append(f"💪 {', '.join(ex.get('primary_muscles') or [])}")
            if ex.get("contraindications"):
                out.append(f"⚕️ {ex['contraindications'][:200]}")
            tech = ex.get("technique") or ""
            out.append(f"📋 {tech[:200]}{'...' if len(tech) > 200 else ''}")
        out.append(
            "\n💡 Présente 3-4 options à l'utilisateur (pas tout d'un coup). "
            "Adapte à son objectif. **Si douleur >3/10 ou aiguë récente → "
            "recommande consultation kiné AVANT le sport.**"
        )
        return "\n".join(out)

    @beta_tool
    def calculate_one_rep_max(weight_kg: float, reps: int, exercise: str = "") -> str:
        """Calculate the estimated 1RM (one-rep max) from a working set. \
Use when the user reports a heavy set (e.g. 'j'ai fait squat 100kg pour 5'). \
Returns estimates from 3 formulas + recommendations for training percentages.

Args:
    weight_kg: Weight lifted in kg.
    reps: Number of reps completed (1-15 range valid).
    exercise: Optional exercise name (squat, bench, deadlift, etc.).
"""
        if reps < 1 or reps > 15 or weight_kg <= 0:
            return "Reps 1-15 et poids > 0 requis."
        # Three formulas + their average
        epley = weight_kg * (1 + reps / 30)
        brzycki = weight_kg * 36 / (37 - reps)
        lombardi = weight_kg * (reps ** 0.10)
        avg_1rm = round((epley + brzycki + lombardi) / 3, 1)

        # Training percentages
        ex_str = f" ({exercise})" if exercise else ""
        return (
            f"# 📊 Estimation 1RM{ex_str}\n\n"
            f"De : **{weight_kg} kg pour {reps} reps**\n\n"
            f"## 3 formules\n"
            f"- Epley : {epley:.1f} kg\n"
            f"- Brzycki : {brzycki:.1f} kg\n"
            f"- Lombardi : {lombardi:.1f} kg\n"
            f"- **Moyenne : {avg_1rm} kg** ← utilise cette valeur\n\n"
            f"## Pourcentages de training\n"
            f"- **Force max (1-3 reps)** : {avg_1rm * 0.90:.1f}-{avg_1rm * 0.95:.1f} kg (90-95%)\n"
            f"- **Force (3-6 reps)** : {avg_1rm * 0.85:.1f}-{avg_1rm * 0.90:.1f} kg (85-90%)\n"
            f"- **Hypertrophie lourde (6-8 reps)** : {avg_1rm * 0.80:.1f}-{avg_1rm * 0.85:.1f} kg (80-85%)\n"
            f"- **Hypertrophie modérée (8-12 reps)** : {avg_1rm * 0.70:.1f}-{avg_1rm * 0.80:.1f} kg (70-80%)\n"
            f"- **Endurance (15+ reps)** : {avg_1rm * 0.60:.1f}-{avg_1rm * 0.70:.1f} kg (60-70%)\n\n"
            f"⚠️ Estimation. Pour 1RM vrai, test en salle avec spotter + échauffement complet."
        )

    @beta_tool
    def find_substitutes(ingredient: str, reason: str = "") -> str:
        """Find appropriate substitutes for an ingredient. Use when the user \
asks 'remplace par quoi', 'je n'ai pas X', 'je suis allergique à Y'.

Args:
    ingredient: The ingredient to substitute (e.g. 'oeufs', 'beurre', 'lait', \
'gluten', 'farine', 'sucre').
    reason: Optional reason ('allergie', 'vegan', 'sans gluten', 'cetogene', \
'low-carb', 'pas chez moi').
"""
        ing = ingredient.lower().strip()
        substitutes: dict[str, str] = {
            "œuf": "**Pour pâtisserie** : 1 œuf = 3 cs compote de pomme OU 1 cs graines de lin moulues + 3 cs eau (chia OK aussi) OU 1/4 banane écrasée OU 60g tofu silken mixé. Pour omelette : tofu brouillé.",
            "oeuf": "**Pour pâtisserie** : 1 œuf = 3 cs compote de pomme OU 1 cs graines de lin moulues + 3 cs eau (chia OK aussi) OU 1/4 banane écrasée OU 60g tofu silken mixé. Pour omelette : tofu brouillé.",
            "beurre": "**Pour cuisson** : huile d'olive (sauté) OU huile de coco (pâtisserie) OU compote pomme (pâtisserie sucrée) OU avocat écrasé OU yaourt grec. Ratio 3/4 du beurre.",
            "lait": "Lait d'amande, soja, avoine, coco, riz. **Pour pâtisserie** : ratio 1:1. **Pour café** : amande/avoine. **Riche en prot** : soja non sucré.",
            "crème": "Crème de coco (riche), crème de soja, yaourt grec dilué, lait + maïzena. Pour montée : crème de coco bien froide.",
            "fromage": "Levure nutritionnelle (saveur fromage), tofu silken avec citron/sel pour ricotta, faux parmesan : noix de cajou + levure nut + sel.",
            "gluten": "Farine de riz, farine de sarrasin, farine d'amandes, farine de pois chiches, farine de quinoa, farine de coco, mix 'sans gluten' du commerce. Texture différente, ajuster liquides.",
            "farine de blé": "Farine de riz (-25% liquides), farine d'amandes (riche), farine de sarrasin (gout), mix sans gluten 1:1. Recettes adapter.",
            "sucre": "Miel (1/2 quantite), sirop d'érable (même quantite), stévia, érythritol, allulose, dates mixées. **À éviter** : sucralose en patisserie (chauffe altere).",
            "huile": "Huile olive (cuisson normale), huile coco (haute température), huile avocat, huile cameline (cru), purée d'amandes / oléagineux.",
            "viande": "Tofu mariné, tempeh, seitan, lentilles, pois chiches, champignons (texture), jackfruit (effiloché). Légumineuses requierent assaisonnement +++",
            "poisson": "Tofu pané dans algues nori, sardines (autre poisson), salmon vegan : carotte fumée marinée + algues, tempeh + sauce wasabi.",
            "pâtes": "Pâtes de légumineuses (lentilles, pois chiches), spaghettis de courgette, konjac (low-carb), shirataki, riz, quinoa, sarrasin.",
            "pain": "Crackers, galettes de riz, pain sans gluten (oats, sarrasin), pain de seigle, wraps de feuilles de salade ou tortillas mais.",
            "riz": "Quinoa, sarrasin, riz de chou-fleur, légumineuses cuites, orge, riz complet vs blanc.",
            "yaourt": "Yaourt soja, coco, amande, skyr (riche prot), fromage blanc, kefir, lait fermente.",
            "ch é colat": "Cacao non sucré, caroube (lighter), poudre cacao + huile coco + miel/dattes maison.",
            "miel": "Sirop d'érable, sirop d'agave, sirop yacon, datesmixées, mélasses noire. Pour vegan : éviter miel.",
            "huile de palme": "OK éviter — utilise huile coco, huile olive, huile colza selon usage."
        }

        # Match flexibility
        result = None
        for key, val in substitutes.items():
            if key in ing:
                result = val
                break

        reason_note = ""
        if reason:
            reason_note = f"\n\n_Raison : {reason}_"

        if result:
            return (
                f"# 🔄 Substituts pour : {ingredient}\n\n"
                f"{result}{reason_note}\n\n"
                f"💡 Conseil Calo : adapter quantités selon recette. Test petit lot d'abord si pâtisserie."
            )
        return (
            f"# 🔄 Substituts pour : {ingredient}\n\n"
            f"Pas de substitut spécifique dans la base. Réponds depuis ton expertise nutritionnelle.\n"
            f"Considère :\n"
            f"1. La fonction de l'ingrédient (liant, gras, sucre, texture, saveur)\n"
            f"2. Le contexte (recette sucrée/salée, allergie, choix éthique)\n"
            f"3. Macros équivalents si pertinent{reason_note}"
        )

    @beta_tool
    def cycle_phase_advisor(day_of_cycle: int) -> str:
        """For women, provide phase-specific nutrition + sport guidance based \
on the day of the menstrual cycle. Use when user asks 'j'en suis où dans \
mon cycle', 'que faire J15', or proactively if cycle date known.

Args:
    day_of_cycle: Day of cycle (1 = first day of period, ~28 = day before next).
"""
        day = max(1, min(35, int(day_of_cycle)))

        # Phase identification
        if day <= 5:
            phase = "MENSTRUELLE"
            phase_desc = "Estrogenes et progesterone au plus bas. Energie physique reduite, mental stable. Comme un homme hormonalement."
            nutrition = (
                "**+200-300 kcal** (perte sang + besoins fer)\n"
                "- Fer +++ (viande rouge, foie, palourdes, lentilles + vit C)\n"
                "- Magnesium 400mg (anti-crampes)\n"
                "- Omega 3 (anti-inflammatoire)\n"
                "- Hydratation 3L\n"
                "- Cafeine moderee (aggrave crampes)"
            )
            sport = (
                "- Cardio LEGER : marche, vélo lent, yoga doux\n"
                "- Muscu si bien : forme/technique > charges\n"
                "- EVITE : HIIT intense, 1RM, sports impact\n"
                "- ECOUTE : fatigue extreme = repos OK"
            )
        elif day <= 13:
            phase = "FOLLICULAIRE"
            phase_desc = "Estrogenes en hausse rapide. Pic energie + libido + humeur. Ta PHASE OR."
            nutrition = (
                "Calories normales\n"
                "- Sensibilite insulino max = + glucides OK\n"
                "- Proteines normales\n"
                "- Cafe sans probleme\n"
                "- Glucides complexes peri-workout"
            )
            sport = (
                "**Pic d'intensite** : powerlifting, CrossFit, sprints\n"
                "- TEST tes PRs ici (force max)\n"
                "- HIIT excellent\n"
                "- Apprentissage moteur optimum (nouveaux mouvements)"
            )
        elif day <= 16:
            phase = "OVULATION"
            phase_desc = "Pic LH déclenche ovulation. Estrogenes au sommet. Energie au top, libido pic."
            nutrition = (
                "Calories normales\n"
                "- Mange ce que tu veux structure\n"
                "- Hydratation +++\n"
                "- Vitamine E (qualite ovulation)"
            )
            sport = (
                "Continue intensite élevée\n"
                "- Force pic\n"
                "- **ATTENTION** : risque lésion ligament croisé augmenté (50%) chez femmes sportives → échauffe bien, prudence pivots"
            )
        elif day <= 21:
            phase = "LUTÉALE PRECOCE"
            phase_desc = "Progestérone monte. Energie encore OK, sommeil legerement perturbé."
            nutrition = (
                "Calories normales\n"
                "- Glucides moderes\n"
                "- Magnesium 400mg (calmant)\n"
                "- B6 (anti-SPM)"
            )
            sport = (
                "Volume normal\n"
                "- Intensite modere a haute\n"
                "- Force se stabilise"
            )
        else:
            phase = "LUTÉALE TARDIVE (SPM)"
            phase_desc = "Progestérone qui chute, estrogènes en baisse. SPM : irritabilite, ballonnements, fringales, sommeil mauvais."
            nutrition = (
                "**+200 kcal** (besoins reels accrus)\n"
                "- +30g glucides pour stabiliser humeur\n"
                "- Chocolat noir 85%+ OK (magnesium)\n"
                "- Tryptophane : dinde, banane, oeufs (serotonine)\n"
                "- B6 : avocat, banane (anti-SPM)\n"
                "- Calcium 1200mg (anti-SPM)\n"
                "- Magnesium 400mg\n"
                "- LIMITER : cafe (>2 = anxiete), alcool (sommeil), sucre raffiné (yo-yo emotionnel)"
            )
            sport = (
                "- Volume modéré\n"
                "- Intensité baisse\n"
                "- Yoga, marche, natation\n"
                "- Force baisse 5-10% : NORMAL, pas un échec\n"
                "- Pas le moment pour PRs"
            )

        return (
            f"# 🌸 J{day} : Phase **{phase}**\n\n"
            f"{phase_desc}\n\n"
            f"## 🍽️ Nutrition\n{nutrition}\n\n"
            f"## 🏋️ Sport\n{sport}\n\n"
            f"💡 Si tu suis ton cycle dans une app (Clue, Flo, Natural Cycles), "
            f"partage les patterns observés avec moi pour ajuster sur le LONG terme. "
            f"Cycle = ton tableau de bord physiologique."
        )

    @beta_tool
    def pre_competition_brief(competition_type: str, days_until: int) -> str:
        """Generate a pre-competition nutritional + mental briefing. Use for \
marathon, triathlon, powerlifting comp, boxing, etc. Critical for athletes.

Args:
    competition_type: 'marathon' | 'semi' | 'triathlon' | 'powerlifting' | \
'boxing' | 'crossfit' | 'tennis' | 'autre'.
    days_until: Number of days until competition.
"""
        ct = competition_type.lower()

        if days_until > 14:
            phase = "PRÉPARATION LOINTAINE"
            base = (
                "## Phase préparation (J-14 et avant)\n"
                "- Nutrition cible quotidienne maintenue (pas de cycles dramatiques)\n"
                "- Sommeil 8h+\n"
                "- Stress controle\n"
                "- Pas de nouvel aliment / supplement\n"
                "- 0 alcool 2 sem avant si vise PR\n"
                "- Tests materiel + tactique pendant entrainements\n"
                "- Bilan sanguin si pas fait dans l'annee\n"
            )
        elif days_until > 7:
            phase = "AFFUTAGE 7-14J"
            base = (
                "## Phase affutage (J-7 à J-14)\n"
                "- Volume entrainement -30 a -40% (tapering)\n"
                "- Intensite maintenue\n"
                "- Calories cibles maintenues\n"
                "- Sommeil priorité absolue\n"
                "- Pas de muscu lourde 4 jours avant\n"
                "- Hydratation +20%\n"
            )
        elif days_until > 2:
            phase = f"J-{days_until} A J-3 (carb-loading)"
            base = (
                f"## Phase carb-loading (J-{days_until})\n"
                "- **Glucides 7-10 g/kg/jour** (vs 4-5 normal)\n"
                "- Proteines maintenues 1.6-1.8 g/kg\n"
                "- Lipides BAS (15-20% kcal)\n"
                "- Fibres modérées (éviter inconfort)\n"
                "- Volume sport minimal\n"
                "- 0 alcool\n"
                "- Sommeil 9h\n"
                "- Pre-emballer aliments / boissons course\n"
            )
        elif days_until == 2:
            phase = "J-2 (veille de veille)"
            base = (
                "## J-2\n"
                "- Glucides 8-10 g/kg\n"
                "- Repas familiers, faciles à digerer\n"
                "- Eviter legumineuses (fermentation)\n"
                "- Eviter cruciferes crus (gaz)\n"
                "- Lit avant 22h\n"
                "- 0 alcool\n"
            )
        elif days_until == 1:
            phase = "VEILLE"
            base = (
                "## VEILLE (J-1)\n"
                "- Diner 18h-19h max (pas plus tard)\n"
                "- Glucides simples + peu de fibres\n"
                "- Pasta blanche + sauce tomate légère + poisson blanc + légumes cuits + dessert\n"
                "- 0 nouveauté alimentaire\n"
                "- 0 alcool\n"
                "- Hydratation 3L + sodium\n"
                "- Lit avant 22h\n"
                "- Preparer tenue + materiel + dossard\n"
            )
        else:
            phase = "JOUR J"
            base = (
                "## JOUR J\n"
                "- Petit-dej 3-4h avant : 100-150g avoine + banane + miel + café\n"
                "- 1h avant : banane + dattes + 200ml eau\n"
                "- Hydratation : sips eau + electrolytes\n"
                "- Echauffement progressif\n"
                "- Mental : visualisation +++\n"
            )

        # Sport-specific
        sport_specific = {
            "marathon": (
                "## Spécifique MARATHON\n"
                "- Pendant : 60-90g glucides/h (gels testés)\n"
                "- 500-750 ml liquide/h + 300-700 mg sodium\n"
                "- Cafeine 3-6 mg/kg vers km 25\n"
                "- Départ contrôlé (90% des walls = depart trop rapide)\n"
                "- Visualise les 5 derniers km depuis la veille"
            ),
            "semi": (
                "## Spécifique SEMI-MARATHON\n"
                "- Pendant : 30-60g glucides/h\n"
                "- Plus rapide donc moins de carb intra-effort\n"
                "- Strategie pace controllé"
            ),
            "triathlon": (
                "## Spécifique TRIATHLON\n"
                "- Pendant velo : 60-90g/h (le moment idéal de manger)\n"
                "- Test nutrition transition velo->course\n"
                "- Hydratation +++"
            ),
            "powerlifting": (
                "## Spécifique POWERLIFTING\n"
                "- Veille : sodium normal (NE PAS réduire pour faire poids sauf catégorie)\n"
                "- Si fait poids : peser puis manger 1.5L liquide + carbs + sodium\n"
                "- 3h avant compétition : repas riche prot + glucides\n"
                "- Cafeine + L-théanine 45 min avant\n"
                "- Mental : visualisation des charges max"
            ),
            "boxing": (
                "## Spécifique BOXE / SPORT COMBAT\n"
                "- Souvent faire poids (catégories)\n"
                "- 24h avant pesage : sodium réduit\n"
                "- Post-pesage : 1.5-2L liquide + carbs + sodium + proteines\n"
                "- Dîner pre-fight : digestible, protéines + glucides moderate\n"
                "- Echauffement complet, mental ++"
            ),
            "crossfit": (
                "## Spécifique CROSSFIT COMPETITION\n"
                "- Plusieurs WODs : maintien glycogene critical\n"
                "- Entre WODs : glucides 30-60g + electrolytes\n"
                "- Hydratation +++\n"
                "- Recovery active entre"
            ),
        }

        result = f"# 🎯 Briefing pré-competition : {competition_type.upper()}\n"
        result += f"J-{days_until} ({phase})\n\n"
        result += base
        if ct in sport_specific:
            result += "\n\n" + sport_specific[ct]
        result += (
            "\n\n## 💡 Conseil Calo\n"
            "RIEN de nouveau le jour J. Tout ce que tu fais = testé en entrainement. "
            "Mental visualisation = 30% du résultat (etudes psycho sport). "
            "Confiance = préparation répétée."
        )
        return result

    @beta_tool
    def sport_specific_macros(sport: str, body_weight_kg: float = 0) -> str:
        """Return optimal macros tailored to a specific sport. Use when user \
asks 'macros pour MMA', 'glucides pour cyclisme', 'comment manger pour rugby', etc.

Args:
    sport: 'powerlifting' | 'bodybuilding' | 'marathon' | 'cyclisme' | \
'triathlon' | 'mma' | 'crossfit' | 'tennis' | 'football' | 'rugby' | \
'basket' | 'natation' | 'climbing' | 'gymnastique'.
    body_weight_kg: Body weight for calculation. If 0, will use user's weight from profile.
"""
        user = db.get_user_by_id(user_id)
        if body_weight_kg <= 0 and user:
            body_weight_kg = float(user.get("current_weight_kg") or 70)
        if body_weight_kg <= 0:
            return "Poids requis pour calcul. Précise via body_weight_kg."

        w = body_weight_kg
        s = sport.lower()

        profiles = {
            "powerlifting": {
                "prot": (2.0, 2.4),
                "carb": (4, 6),
                "fat": (1.0, 1.4),
                "kcal_mult": (35, 45),
                "note": "Phase prise force/masse. Surplus léger.",
            },
            "bodybuilding": {
                "prot": (2.0, 2.6),
                "carb": (3, 5),
                "fat": (0.8, 1.2),
                "kcal_mult": (32, 42),
                "note": "Selon phase : prise (surplus +500) ou sèche (deficit -500).",
            },
            "marathon": {
                "prot": (1.6, 1.8),
                "carb": (6, 10),
                "fat": (1.0, 1.5),
                "kcal_mult": (50, 70),
                "note": "Carb-loading 3 jours avant comp : 8-10 g/kg.",
            },
            "cyclisme": {
                "prot": (1.4, 1.8),
                "carb": (6, 12),
                "fat": (1.0, 1.5),
                "kcal_mult": (50, 80),
                "note": "Long ride : 60-90g glucides/heure pendant.",
            },
            "triathlon": {
                "prot": (1.6, 1.8),
                "carb": (6, 10),
                "fat": (1.0, 1.5),
                "kcal_mult": (50, 75),
                "note": "Recharge glycogene critical entre disciplines.",
            },
            "mma": {
                "prot": (1.8, 2.2),
                "carb": (4, 6),
                "fat": (1.0, 1.4),
                "kcal_mult": (40, 55),
                "note": "Categories poids = cycles de pesage. Strategy specifique.",
            },
            "crossfit": {
                "prot": (1.8, 2.2),
                "carb": (4, 6),
                "fat": (1.0, 1.4),
                "kcal_mult": (40, 55),
                "note": "Force + endurance. Glucides essentiels.",
            },
            "tennis": {
                "prot": (1.4, 1.8),
                "carb": (5, 7),
                "fat": (1.0, 1.4),
                "kcal_mult": (40, 50),
                "note": "Sport explosif intermittent. Hydratation +++.",
            },
            "football": {
                "prot": (1.6, 1.8),
                "carb": (5, 7),
                "fat": (1.0, 1.4),
                "kcal_mult": (40, 55),
                "note": "Sport mixte explosif/endurance.",
            },
            "rugby": {
                "prot": (2.0, 2.4),
                "carb": (5, 7),
                "fat": (1.0, 1.5),
                "kcal_mult": (45, 60),
                "note": "Force + impact + endurance. Calories elevees.",
            },
            "basket": {
                "prot": (1.6, 1.8),
                "carb": (5, 7),
                "fat": (1.0, 1.4),
                "kcal_mult": (40, 55),
                "note": "Sport explosif aerobie. Bonjour electrolytes.",
            },
            "natation": {
                "prot": (1.6, 1.8),
                "carb": (5, 8),
                "fat": (1.0, 1.5),
                "kcal_mult": (45, 65),
                "note": "Depense elevee. Recharge glycogène critical.",
            },
            "climbing": {
                "prot": (1.8, 2.0),
                "carb": (4, 6),
                "fat": (0.8, 1.2),
                "kcal_mult": (35, 50),
                "note": "Ratio force/poids critique. Lean focus.",
            },
            "gymnastique": {
                "prot": (1.8, 2.0),
                "carb": (4, 6),
                "fat": (0.8, 1.2),
                "kcal_mult": (35, 50),
                "note": "Force/poids + flexibility. Lean physique.",
            },
        }

        if s not in profiles:
            return (
                f"Sport '{sport}' non listé. Réponds depuis ton expertise. "
                f"Considère : type effort (force/endurance/mixte), durée, fréquence, "
                f"catégorie poids éventuelle. Macros base : 1.6-2g prot/kg, "
                f"4-6g glucides/kg, 1g lipides/kg pour mixte modéré."
            )

        p = profiles[s]
        kcal_min = int(w * p["kcal_mult"][0])
        kcal_max = int(w * p["kcal_mult"][1])

        return (
            f"# 🏆 Macros optimaux : **{sport.upper()}** ({w} kg)\n\n"
            f"## Cibles quotidiennes\n"
            f"- **Calories** : {kcal_min}-{kcal_max} kcal\n"
            f"- **Protéines** : {int(w * p['prot'][0])}-{int(w * p['prot'][1])}g ({p['prot'][0]}-{p['prot'][1]} g/kg)\n"
            f"- **Glucides** : {int(w * p['carb'][0])}-{int(w * p['carb'][1])}g ({p['carb'][0]}-{p['carb'][1]} g/kg)\n"
            f"- **Lipides** : {int(w * p['fat'][0])}-{int(w * p['fat'][1])}g ({p['fat'][0]}-{p['fat'][1]} g/kg)\n\n"
            f"## Spécifique\n{p['note']}\n\n"
            f"## Periworkout\n"
            f"- Pre-workout (2h avant) : 1-2g glucides/kg + 0.3g prot/kg\n"
            f"- Intra (>60 min) : 30-60g glucides/h + electrolytes\n"
            f"- Post (0-2h) : 0.3-0.5g prot/kg + 0.5-1g glucides/kg\n\n"
            f"💡 Ajustement individuel nécessaire selon performance + recovery + composition corporelle. "
            f"Track 2-4 sem pour calibrer."
        )

    @beta_tool
    def weight_cut_planner(
        target_weight_kg: float,
        days_until_weighin: int,
    ) -> str:
        """Plan a safe weight cut for combat sports (boxing, MMA, kickboxing). \
Use when user has fight/competition with weight category. Returns a structured \
protocol with phases : long-term fat loss + short-term water cut + post-weigh-in \
rehydration. SAFETY first.

Args:
    target_weight_kg: Target weight (the category weight).
    days_until_weighin: Days until the official weigh-in.
"""
        user = db.get_user_by_id(user_id)
        if not user:
            return "User not found. Calo a besoin de ton profil pour calculer."
        current = float(user.get("current_weight_kg") or 0)
        if current <= 0:
            return "Poids actuel manquant. Met-le à jour dans ton profil."
        kg_to_lose = current - target_weight_kg
        if kg_to_lose <= 0:
            return f"Tu es déjà à ou en dessous de {target_weight_kg} kg. Aucune cut requise."

        pct_to_lose = (kg_to_lose / current) * 100

        warnings = []
        if pct_to_lose > 8 and days_until_weighin < 30:
            warnings.append(
                "⚠️ **CUT >8% du poids corporel** sur courte période = "
                "DANGER (insuffisance rénale, hyponatremia). Reconsidère ta catégorie."
            )
        if pct_to_lose > 5 and days_until_weighin < 7:
            warnings.append(
                "⚠️ **Cut >5% en moins d'1 semaine** = water cut "
                "drastique. Risque perf catastrophique + santé."
            )

        # Phase planning
        phases = []
        if days_until_weighin > 30:
            kg_fat_loss = max(0, kg_to_lose - 2)  # leave 1.5-2kg for water cut
            phases.append(
                f"## Phase 1 - FAT LOSS ({days_until_weighin - 7} jours)\n"
                f"- Cible : perdre **{kg_fat_loss:.1f} kg gras** durablement\n"
                f"- Déficit calorique : -500 kcal/jour\n"
                f"- Protéines : 2.2 g/kg poids actuel = {int(current * 2.2)}g\n"
                f"- Glucides : 3-4 g/kg + cyclisme (boost jours d'entrainement)\n"
                f"- Lipides : 0.8-1 g/kg\n"
                f"- Hydratation : 40 ml/kg ({int(current * 40)} ml/jour)\n"
                f"- Sport : combat 4x/sem + cardio HIIT 2x/sem + muscu 1x\n"
                f"- Sommeil 8h+ obligatoire\n"
                f"- 0 alcool"
            )

        if days_until_weighin >= 7:
            kg_water_cut = min(2, kg_to_lose)
            phases.append(
                f"## Phase 2 - WATER CUT (dernière semaine)\n"
                f"- Cible : perdre **{kg_water_cut:.1f} kg eau**\n\n"
                f"### J-7 à J-5\n"
                f"- Hydratation MAX 5-6 L/jour (corps s'habitue à éliminer)\n"
                f"- Sodium NORMAL (2-3g)\n\n"
                f"### J-4 à J-3\n"
                f"- Hydratation 3 L\n"
                f"- Sodium réduit à 1g\n"
                f"- Glucides baisses (deplete glycogène = -1 kg)\n\n"
                f"### J-2\n"
                f"- Hydratation 1.5 L\n"
                f"- Sodium très bas\n"
                f"- Glucides quasi nulles\n"
                f"- Fibres réduites (vide tube digestif)\n\n"
                f"### J-1 (veille pesee)\n"
                f"- Hydratation 500 ml MAX\n"
                f"- Sodium 0 ajouté\n"
                f"- 1-2 vrais repas (prot + légumes peu)\n"
                f"- Option : sauna 10-15 min dernière sweat\n\n"
                f"### Jour pesee\n"
                f"- Pesee tot le matin\n"
                f"- Tu dois être à **{target_weight_kg} kg** exactement"
            )

        phases.append(
            f"## Phase 3 - REHYDRATATION (post-pesee)\n\n"
            f"### IMMÉDIATEMENT après pesee\n"
            f"- 500 ml-1L liquide électrolyté (Pedialyte)\n"
            f"- Sips toutes les 5-10 min (PAS d'un coup = vomissement)\n"
            f"- 30g glucides simples (jus dilué, miel)\n\n"
            f"### Entre pesee et combat (24-36h)\n"
            f"- 6-8 L liquide (eau + boissons électrolytes)\n"
            f"- 4-6g sodium\n"
            f"- 3g potassium\n"
            f"- 3-4 vrais repas\n"
            f"- 6-10 g glucides/kg poids\n"
            f"- 2 g/kg protéines\n"
            f"- Lipides modérés\n"
            f"- TESTER d'avance, RIEN de nouveau"
        )

        return (
            f"# ⚖️ Plan Cut Combat\n\n"
            f"**Poids actuel** : {current} kg\n"
            f"**Poids cible** : {target_weight_kg} kg\n"
            f"**À perdre** : {kg_to_lose:.1f} kg ({pct_to_lose:.1f}% poids corporel)\n"
            f"**Jours restants** : {days_until_weighin}\n\n"
            + ("\n".join(warnings) + "\n\n" if warnings else "")
            + "\n\n".join(phases)
            + "\n\n## RÈGLES D'OR\n"
            "1. **JAMAIS sans coach expérimenté** combat sport\n"
            "2. **Bilan medical** avant cut majeure\n"
            "3. **STOP IMMÉDIAT** si vertige / lipotymie\n"
            "4. **Hydratation post-pesee CRITIQUE** (mauvaise = perf nulle)\n"
            "5. **0 nouvel aliment** post-pesee\n"
            "6. **Visualisation mental** = 30% du résultat\n\n"
            "💡 Ce protocole est INDICATIF. Ton coach + ton experience "
            "ajustent. Santé > toute catégorie."
        )

    @beta_tool
    def shadow_boxing_routine(
        level: str = "débutant",
        duration_min: int = 15,
    ) -> str:
        """Generate a structured shadow boxing routine. Use when user wants \
boxing workout solo or asks for a shadow boxing routine.

Args:
    level: 'débutant' | 'intermédiaire' | 'avancé'.
    duration_min: Total duration in minutes (5-45).
"""
        duration = max(5, min(45, int(duration_min)))
        level = level.lower().strip()

        # Build routine based on duration
        if level == "débutant":
            rounds_specs = [
                ("Échauffement épaules + cervicales", 2),
                ("Footwork : avance/recule/lateral", 2),
                ("Jab seul à rythme constant", 2),
                ("Cross seul à rythme constant", 2),
                ("Combo 1-2 (jab-cross)", 2),
                ("Combo 1-2 + footwork", 2),
                ("Finish : core (planche 30s + crunch)", 1),
            ]
            tips = (
                "## Conseils débutant\n"
                "- **Technique > Vitesse** : ralenti OK\n"
                "- Mains hautes au menton constamment\n"
                "- Expire (\"tss\") sur chaque coup\n"
                "- Pas trop fort : tu apprends d'abord"
            )
        elif level == "intermédiaire":
            rounds_specs = [
                ("Échauffement complet + corde 2 min", 3),
                ("Footwork + slips technique", 2),
                ("Combos 1-2-3 (jab-cross-hook)", 3),
                ("Combos 1-2-5-2 (uppercut intégré)", 3),
                ("Slips + counters", 3),
                ("Combos libres + intensité", 3),
                ("HIIT round (10s full + 20s contrôle x 6)", 3),
                ("Finish : core boxer (planche, crunch, mountain climbers)", 2),
            ]
            tips = (
                "## Conseils intermédiaire\n"
                "- Variations vitesse / power\n"
                "- Footwork constant\n"
                "- Slips + counters bien intégrés\n"
                "- Cherche le rythme et la fluidité"
            )
        else:  # avancé
            rounds_specs = [
                ("Échauffement complet + corde 3 min", 5),
                ("Footwork complexe + pivots", 3),
                ("Combos 5-8 coups avec esquives", 3),
                ("Setup combos (jab-feinte-cross)", 3),
                ("Counter-puncher style", 3),
                ("Pressure fighter style", 3),
                ("Movement + angles changeants", 3),
                ("Tabata round (20s explosif + 10s repos x 8)", 4),
                ("Finish : core + cardio 5 min", 3),
            ]
            tips = (
                "## Conseils avancé\n"
                "- Sparring simulation (imagine adversaire qui contre)\n"
                "- Footwork = priorité max\n"
                "- Test combos qui marchent en spar réel\n"
                "- Records vidéo tes séances pour analyser"
            )

        # Fit total to duration
        total = sum(r[1] for r in rounds_specs)
        scale = duration / total if total > 0 else 1
        scaled_rounds = [(name, max(1, round(t * scale))) for name, t in rounds_specs]

        out = [f"# 🥊 Shadow Boxing : {level} ({duration} min)\n"]
        cumulative = 0
        for i, (name, t) in enumerate(scaled_rounds, 1):
            cumulative += t
            out.append(f"**Round {i}** ({t} min, t={cumulative} min) : {name}")
        out.append("\n## Repos\n30 sec entre rounds (1 min entre blocs si fatigue)")
        out.append(f"\n{tips}")
        out.append(
            "\n## Équipement minimum\n"
            "- Tenue confortable\n"
            "- Espace 1.5m² minimum\n"
            "- Eau + sel\n"
            "- Music up (playlist combat = bonus +30% intensité)\n"
            "- Timer (app : Boxing Timer Pro, Round Timer)"
        )
        return "\n".join(out)

    @beta_tool
    def boxing_combo_library(combo_difficulty: str = "intermédiaire") -> str:
        """Return a library of boxing combinations from beginner to advanced. \
Use when user asks for boxing combos, wants to learn combinations, or needs \
variety in shadow boxing.

Args:
    combo_difficulty: 'débutant' | 'intermédiaire' | 'avancé' | 'champion'.
"""
        d = combo_difficulty.lower().strip()

        combos = {
            "débutant": [
                "**1-1** : double jab (range + setup)",
                "**1-2** : jab-cross (LE classique)",
                "**1-2-1** : jab-cross-jab (range control)",
                "**1-2-3** : jab-cross-hook avant",
                "**1-1-2** : double jab + cross (decoit l'adversaire)",
                "**2-3** : cross-hook (puissance directe)",
            ],
            "intermédiaire": [
                "**1-2-3-2** : jab-cross-hook-cross",
                "**1-2-5-2** : jab-cross-uppercut avant-cross",
                "**1-2-3-4** : jab-cross-hook avant-hook arrière",
                "**3-2** : hook avant-cross (counter)",
                "**1-2-slip-2** : jab-cross-slip-cross (esquive + counter)",
                "**1-6** : jab + uppercut droit (surprise)",
                "**5-2** : uppercut avant-cross (push up combo)",
                "**1-2-3b** : jab-cross-hook body (changement niveau)",
            ],
            "avancé": [
                "**1-2-3-2-1** : jab-cross-hook-cross-jab (5 hits)",
                "**1-2-slip-3-2** : jab-cross-slip-hook-cross",
                "**1-2-3b-2-3** : jab-cross-hook body-cross-hook head (changement niveau)",
                "**1-1-2-roll-3** : double jab-cross-roll-hook",
                "**5-6-3-2** : uppercut combo + hook + cross (intensité max)",
                "**Feint 1-2-3** : feinte jab + jab-cross-hook (deception)",
                "**1-2-5-3-2** : combo 5 coups changement plans",
                "**Slip-2-3-2-1** : esquive + cross-hook-cross-jab (counter-puncher)",
            ],
            "champion": [
                "**1-1-2-3-2-roll-2** : double jab + cross + hook + cross + roll + cross",
                "**Feint 1-2-step-3-2** : feinte + cross + step away + hook + cross",
                "**1-2-3b-uppercut-3h** : 5 coups changement niveau complet",
                "**Roll-2-3-roll-2-3** : counter-puncher continu",
                "**Footwork 360 + 1-2-3** : pivot complet puis combo",
                "**Setup combinations** (étude adversaire) - personnalisées par fight",
            ],
        }

        if d not in combos:
            d = "intermédiaire"

        result = [f"# 🥊 Combos boxing : **{combo_difficulty}**\n"]
        for combo in combos[d]:
            result.append(f"- {combo}")
        result.append(
            "\n## Légende numérique\n"
            "- **1** : Jab (poing avant)\n"
            "- **2** : Cross (poing arrière)\n"
            "- **3** : Hook avant (crochet gauche pour droitier)\n"
            "- **4** : Hook arrière (crochet droit)\n"
            "- **5** : Uppercut avant\n"
            "- **6** : Uppercut arrière\n"
            "- **b** : suffix body (au corps) ex : 3b = hook body\n"
            "- **slip** : esquive latérale\n"
            "- **roll** : esquive circulaire\n"
            "- **step** : déplacement\n"
            "- **feint** : feinte sans frapper"
        )
        result.append(
            "\n## 💡 Pratique\n"
            "- Chaque combo 10x lent (technique)\n"
            "- Puis 10x vitesse normale\n"
            "- Puis 10x explosif\n"
            "- Combine 2-3 combos dans rounds shadow boxing"
        )
        return "\n".join(result)

    @beta_tool
    def generate_monthly_report() -> str:
        """Generate a luxurious monthly PDF report and send via WhatsApp. \
Premium feature ✨. Use proactively at the start of each month, OR when user asks \
'mon report', 'mon bilan', 'récap du mois'. The PDF includes : weight chart + \
macros + sport + lifestyle + key memories + personal patterns + 3 priority \
actions for next month. Brand Calo, conservable, partageable."""
        if not public_url_base:
            return "Génération PDF indisponible (public_url_base non configuré)."
        user = db.get_user_by_id(user_id)
        if not user:
            return "User not found."
        from datetime import datetime, timedelta, timezone
        since = (datetime.now(timezone.utc) - timedelta(days=30)).strftime("%Y-%m-%d")
        weights = db.weights_history(user_id, limit=60)
        meals = db.meals_since(user_id, since)
        workout_logs = db.workout_logs_since(user_id, since)
        memories = db.memories_for_user(user_id, limit=10)
        body_photos = db.body_photos_for_user(user_id)
        month_label = datetime.now().strftime("%B %Y").capitalize()
        try:
            token, _ = pdf_mod.generate_monthly_report(
                user=user,
                weights=weights,
                meals=meals,
                workout_logs=workout_logs,
                memories=memories,
                body_photos=body_photos,
                month_label=month_label,
            )
            url = f"{public_url_base.rstrip('/')}/report/{token}"
            attachments.append({
                "url": url,
                "caption": f"📄 Ton bilan {month_label} est prêt. Garde-le précieusement !",
            })
            return (
                f"✅ Report mensuel généré et envoyé en PDF WhatsApp. "
                f"Annonce-le brièvement dans ta réponse texte (le PDF arrive juste "
                f"après). Suggère qu'il le partage à son médecin si pertinent."
            )
        except Exception as exc:  # noqa: BLE001
            return f"Erreur génération report : {exc}"

    @beta_tool
    def generate_personalized_recipe(
        constraints: str = "",
        max_prep_min: int = 30,
        meal_type: str = "déjeuner",
        servings: int = 1,
    ) -> str:
        """Generate a fully personalized recipe ON THE SPOT (not from a fixed \
library). Use when user wants something specific that doesn't match existing \
recipes : 'invente-moi une recette avec saumon en 15 min', 'recette vegan riche \
prot pas chere'.

Calo creates the recipe inline using its expertise — no external API needed.

Args:
    constraints: User constraints (ingredients available, avoid, time, preference).
    max_prep_min: Max total prep+cook time.
    meal_type: 'petit-déj' | 'déjeuner' | 'dîner' | 'snack' | 'dessert'.
    servings: Number of servings.
"""
        user = db.get_user_by_id(user_id)
        name = (user or {}).get("name", "")
        restrictions = (user or {}).get("restrictions") or ""
        target_kcal_meal = (user.get("daily_calories", 2000) // 3) if user else 600

        # Calo génère la recette via son intelligence — le LLM la compose en réponse
        return (
            f"# 🍳 Recette personnalisée pour {name or 'toi'}\n\n"
            f"## Contraintes\n"
            f"- {constraints or 'Aucune spécifiée'}\n"
            f"- Temps max : {max_prep_min} min\n"
            f"- Type : {meal_type}\n"
            f"- Portions : {servings}\n"
            f"- Cible kcal/repas : ~{target_kcal_meal}\n"
            f"- Restrictions profil : {restrictions or 'aucune'}\n\n"
            f"## Tes consignes Calo\n"
            f"Crée une recette ORIGINALE répondant à TOUTES ces contraintes. "
            f"Format obligatoire :\n\n"
            f"1. **Nom de la recette** (créatif, appetissant)\n"
            f"2. **Macros estimés** par portion (kcal, P, C, F)\n"
            f"3. **Temps total** (prep + cuisson)\n"
            f"4. **Ingrédients** (quantités précises pour {servings} portion(s))\n"
            f"5. **Préparation** (étapes numérotées claires)\n"
            f"6. **Pourquoi cette recette pour toi** (1-2 phrases personnalisées)\n"
            f"7. **Variante / substitut** (1 alternative si manque ingrédient)\n\n"
            f"💡 Si tu juges la recette super, propose `rate_recipe` après que "
            f"l'utilisateur l'ait essayée."
        )

    @beta_tool
    def morning_brief() -> str:
        """Generate a personalized morning brief for the user. Use first thing \
in the morning (or when user says 'bonjour' before noon). Includes : sleep recap \
if known, today's plan, top priority, motivation. Premium daily ritual."""
        from datetime import datetime, timezone
        user = db.get_user_by_id(user_id)
        if not user:
            return "User not found."
        name = user.get("name") or "toi"
        now = datetime.now(timezone.utc)
        weekday_fr = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"][now.weekday()]
        date_label = now.strftime(f"{weekday_fr} %d/%m")

        # Pull recent context
        sleep = user.get("sleep_quality") or 0
        stress = user.get("stress_level") or 0
        active_program = user.get("active_program")
        active_challenge = db.get_active_user_challenge(user_id)

        brief = [f"# ☀️ Bonjour {name} — {date_label}"]

        if sleep:
            sleep_emoji = "😴" if sleep >= 4 else "🌙" if sleep == 3 else "🥱"
            brief.append(f"{sleep_emoji} Sommeil noté : {sleep}/5")

        if stress and stress >= 4:
            brief.append(f"⚡ Stress élevé en ce moment ({stress}/5) — pense gestion aujourd'hui")

        if active_program:
            brief.append(f"\n## 🏋️ Programme actif : {active_program}")
            brief.append("Utilise `get_today_workout` pour ta séance du jour.")

        if active_challenge:
            brief.append(f"\n## 🎯 Challenge actif")
            brief.append(f"Tu en es au jour {active_challenge.get('current_day', '?')}.")

        brief.append("\n## 💡 Tes consignes Calo")
        brief.append(
            "1. Vérifie les milestones du jour avec `check_milestones`\n"
            "2. Propose 1 action concrète prioritaire pour aujourd'hui\n"
            "3. Demande comment il/elle se sent en 1 mot\n"
            "4. Réponse courte, énergique, personnelle (utilise le prénom)"
        )
        return "\n".join(brief)

    @beta_tool
    def evening_reflection() -> str:
        """Generate an evening reflection prompt. Use after 19h or when user \
mentions end of day. Helps process the day, capture wins, identify frictions, \
prepare tomorrow. Builds the mental discipline of intentional living."""
        from datetime import datetime, timezone
        user = db.get_user_by_id(user_id)
        if not user:
            return "User not found."
        name = user.get("name") or "toi"
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        meals_today = db.meals_for_day(user_id, today)
        return (
            f"# 🌙 Bilan du soir, {name}\n\n"
            f"📊 Résumé objectif :\n"
            f"- Repas loggués aujourd'hui : {len(meals_today)}\n"
            f"- Date : {today}\n\n"
            f"## 💭 Réflexion guidée\n"
            f"Pose ces 4 questions à l'utilisateur, UNE par UNE (pas en bloc) :\n\n"
            f"1. **\"Quel a été ton meilleur moment aujourd'hui ?\"** (capture du positif)\n"
            f"2. **\"Une chose dont tu es fier(e) ?\"** (identité building)\n"
            f"3. **\"Quelle friction t'as ralenti(e) ?\"** (problème à résoudre)\n"
            f"4. **\"Qu'est-ce qui rendrait demain meilleur ?\"** (intention)\n\n"
            f"Sauvegarde les réponses importantes via `remember` (importance 3-4).\n"
            f"Garde tes interventions ENCOURAGEANTES et BRÈVES."
        )

    @beta_tool
    def voice_journal_log(transcript: str, mood: int = 0) -> str:
        """Log a voice journal entry (user spoke 1-3 min about their day/feelings). \
Calo analyzes patterns over time. Use when user sends a vocal that's clearly a \
journaling/reflection (not a question or food log).

Args:
    transcript: The transcribed text of what the user said.
    mood: Optional 1-10 mood score for the moment.
"""
        if not transcript:
            return "Transcript vide."
        from datetime import datetime, timezone
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
        # Simple sentiment heuristic (could be enhanced with LLM analysis)
        positive_words = ["bien", "super", "génial", "fier", "heureux", "joie", "progrès", "réussi"]
        negative_words = ["mal", "triste", "déprimé", "stressé", "fatigué", "échec", "raté", "anxieux"]
        text_lower = transcript.lower()
        pos_count = sum(1 for w in positive_words if w in text_lower)
        neg_count = sum(1 for w in negative_words if w in text_lower)
        tone = "positive" if pos_count > neg_count else "négative" if neg_count > pos_count else "neutre"
        mood_str = f" (mood {mood}/10)" if mood > 0 else ""
        memory_text = f"Voice journal {today}{mood_str} [tone {tone}] : {transcript[:400]}"
        db.add_memory(user_id, memory_text, category="santé", importance=3)
        return (
            f"✅ Journal vocal enregistré ({today}). Tone détecté : {tone}.\n\n"
            f"Tes consignes Calo :\n"
            f"1. Si tone négatif : écoute empathique + 1 question ouverte douce + "
            f"propose 1 mini-action (respiration, marche, appel ami)\n"
            f"2. Si tone positif : célèbre + capture le PATTERN (qu'est-ce qui a "
            f"créé ce bon état ?)\n"
            f"3. Pas de coaching agressif sur du vocal journal\n"
            f"4. Réponse courte, chaleureuse"
        )

    @beta_tool
    def find_kine(zone: str = "", urgent: bool = False) -> str:
        """Help the user find a kiné / physiotherapist in their area. Use when \
user has injury / pain / postural issue requiring kiné. Returns a search \
framework + tips. (Note: actual booking via Doctolib API requires future setup.)

Args:
    zone: City or postal code where the user is.
    urgent: True if pain is acute / blocking daily life.
"""
        urgency_str = "🚨 URGENT" if urgent else "📅 Standard"
        return (
            f"# 🏥 Recherche kiné — {urgency_str}\n\n"
            f"Zone : {zone or 'à préciser'}\n\n"
            f"## Étapes\n\n"
            f"### 1. Recherche\n"
            f"- **Doctolib.fr** ou **Doctolib.ch** : tape 'kiné' + ta ville\n"
            f"- Filtre par spécialité si pertinent (kiné du sport, kiné périnéal, "
            f"kiné respiratoire, kiné de la main)\n"
            f"- Lis les avis (>4.5/5 idéal)\n\n"
            f"### 2. Spécialités selon ton cas\n"
            f"- **Sportif** : kiné du sport\n"
            f"- **Postpartum** : kiné périnéal (souvent 100% remboursé Sécu post-accouchement)\n"
            f"- **Dos / cervicales** : kiné posturologue\n"
            f"- **Main / poignet** : kiné de la main spécialisé\n"
            f"- **Récup post-op** : kiné rééducation\n\n"
            f"### 3. Lors de la consultation\n"
            f"- Apporte tes radios / IRM / bilans\n"
            f"- Note tes symptômes : intensité (1-10), fréquence, déclencheurs\n"
            f"- Demande EXERCICES à faire à la maison entre séances\n"
            f"- Demande pronostic (combien de séances ?)\n\n"
            + (
                "### 4. URGENT — Si douleur >7/10 ou blocage\n"
                "- Médecin généraliste / urgences AVANT kiné\n"
                "- Possible imagerie nécessaire\n"
                "- Pas de sport jusqu'à diagnostic\n" if urgent else ""
            )
            + f"\n## Coût (référence France)\n"
            f"- Consultation kiné conventionné : 22-30€ (remboursé Sécu)\n"
            f"- Souvent reste à charge faible si mutuelle\n\n"
            f"💡 Calo te fait l'**ordonnance d'exercices à faire entre séances** "
            f"si tu veux. Demande-moi des exercices spécifiques à ta zone."
        )

    @beta_tool
    def recommend_supplements_shop(supplement_name: str = "") -> str:
        """Recommend WHERE to buy supplements (brands certifiées + retailers \
de confiance). Use when user asks 'où acheter X', 'quelle marque', 'tu \
recommandes quel X'.

Args:
    supplement_name: Optional specific supplement (vit D, oméga 3, créatine, etc.).
"""
        general = (
            "# 💊 Où acheter tes compléments\n\n"
            "## Marques recommandées par catégorie\n\n"
            "### Premium qualité européenne\n"
            "- **Nutripure** (France) : transparent, certifications, prix moyen\n"
            "- **Nutrimuscle** (France) : labos européens, premium, plus cher\n"
            "- **Yamamoto Nutrition** (Italie) : haute qualité, dosages cliniques\n"
            "- **Solgar** (USA distribué EU) : référence historique, fiable\n\n"
            "### USA premium (importé)\n"
            "- **Thorne Research** : médical-grade, parfois recommandé par médecins\n"
            "- **Now Foods** : excellent rapport qualité/prix\n"
            "- **Pure Encapsulations** : haute pureté\n"
            "- **Nordic Naturals** : référence oméga 3 mondial\n\n"
            "### Spécialiste créatine\n"
            "- **Creapure** (marque allemande) : standard mondial\n"
            "- Vendu par presque tous les fabricants ci-dessus\n\n"
            "### Où acheter\n"
            "- Sites officiels marques (souvent meilleur prix)\n"
            "- **iHerb.com** : USA, livraison EU, énorme catalogue, prix bas\n"
            "- **Amazon** : OK mais vérifie le vendeur (faux supplements en hausse)\n"
            "- **Pharmacies / parapharmacies** : pour cas spécifiques (Vit D liquide ANSM, etc.)\n\n"
            "## 🚩 Signaux à éviter\n"
            "- Pas de certéif NSF / Informed Sport\n"
            "- Liste ingrédients longue avec colorants/sucres\n"
            "- Allégations exagérées (\"brûle 1 kg/jour\")\n"
            "- Vendeurs MLM (Herbalife, Forever Living)\n"
            "- Prix anormalement bas\n\n"
        )
        if supplement_name:
            specific = (
                f"\n## 🎯 Spécifique : {supplement_name}\n\n"
                f"Précise dans ta réponse :\n"
                f"1. La forme optimale du supplément (ex: vit D3+K2, magnésium "
                f"bisglycinate, oméga 3 EPA+DHA en triglycérides)\n"
                f"2. Le dosage recommandé pour l'utilisateur (selon son profil)\n"
                f"3. Quand le prendre (matin/soir, avec/sans repas)\n"
                f"4. Interactions médicaments éventuelles\n"
                f"5. Marques top spécifiques pour ce supplément\n"
            )
            return general + specific
        return general

    @beta_tool
    def identify_emotion(description: str = "") -> str:
        """Help the user precisely identify what they're feeling. Most people \
say 'je suis stressé' but it could be anxious, overwhelmed, frustrated, \
disappointed, etc. Precise identification = better intervention. Use when user \
expresses emotional state vaguely.

Args:
    description: What the user said about their feeling (e.g. 'je me sens \
nul', 'je suis vidé', 'j'ai un truc bizarre').
"""
        return (
            f"# 🎭 Identification émotionnelle\n\n"
            f"L'utilisateur a dit : *\"{description}\"*\n\n"
            f"## La roue des émotions (Plutchik)\n\n"
            f"### 8 émotions primaires\n"
            f"1. **JOIE** : nuances → sérénité, extase, optimisme, fierté\n"
            f"2. **TRISTESSE** : nuances → pensif, mélancolie, deuil, désespoir\n"
            f"3. **PEUR** : nuances → appréhension, anxiété, terreur, panique\n"
            f"4. **COLÈRE** : nuances → irritation, frustration, fureur, rage\n"
            f"5. **DÉGOÛT** : nuances → ennui, aversion, mépris, haine\n"
            f"6. **SURPRISE** : nuances → distrait, étonné, ahuri, choqué\n"
            f"7. **ANTICIPATION** : intérêt, attente, vigilance\n"
            f"8. **CONFIANCE** : acceptation, admiration\n\n"
            f"## Émotions sociales complexes\n"
            f"- **Honte** vs **Culpabilité** (honte = je suis mauvais / culpabilité = j'ai mal fait)\n"
            f"- **Envie** vs **Jalousie**\n"
            f"- **Solitude** vs **Solitude choisie**\n"
            f"- **Désespoir** vs **Tristesse profonde**\n"
            f"- **Burnout** (épuisement émotionnel) vs **Dépression**\n\n"
            f"## Tes consignes Calo\n\n"
            f"1. **Reflète** ce que tu entends : \"Si je comprends bien, tu te sens X...\"\n"
            f"2. **Propose 2-3 émotions précises** parmi la liste ci-dessus\n"
            f"3. **Localise dans le corps** : \"Où tu sens ça dans ton corps ? (poitrine, gorge, ventre, tête, autre)\"\n"
            f"4. **Questionne le déclencheur** : \"Qu'est-ce qui a déclenché ça ?\"\n"
            f"5. **Intensité** : \"Sur 10, c'est à combien ?\"\n"
            f"6. Pas de jugement, juste de la curiosité bienveillante\n"
            f"7. Si >7/10 ET récurrent → suggère consultation pro douce"
        )

    @beta_tool
    def thought_record_cbt(
        situation: str,
        automatic_thought: str,
        emotion: str,
        intensity: int = 5,
    ) -> str:
        """Formal CBT thought record. The GOLD STANDARD of cognitive therapy. \
Use when user has a recurring negative thought pattern they want to work on. \
Identifies cognitive distortions + generates balanced alternative thought.

Args:
    situation: Objective situation that triggered the thought.
    automatic_thought: The exact thought as user said it.
    emotion: The emotion(s) felt (sad, anxious, angry...).
    intensity: 1-10 intensity of emotion.
"""
        return (
            f"# 🧠 CBT Thought Record\n\n"
            f"**Situation** : {situation}\n"
            f"**Pensée automatique** : *\"{automatic_thought}\"*\n"
            f"**Émotion** : {emotion} ({intensity}/10)\n\n"
            f"## Étape 1 — Identifier les distorsions cognitives\n"
            f"Lesquelles reconnais-tu dans cette pensée ? (peut être plusieurs)\n\n"
            f"### Les 20 distorsions classiques\n"
            f"1. **Pensée tout-ou-rien** (\"si je ne suis pas parfait, je suis nul\")\n"
            f"2. **Surgénéralisation** (\"je rate toujours tout\")\n"
            f"3. **Filtrage négatif** (ne voir que le mauvais)\n"
            f"4. **Disqualification du positif** (\"oui mais c'était de la chance\")\n"
            f"5. **Lecture de pensée** (\"il pense forcément que...\")\n"
            f"6. **Voyance** (\"je vais échouer c'est sûr\")\n"
            f"7. **Catastrophisme** (\"si je rate, tout est foutu\")\n"
            f"8. **Minimisation** (du positif) / **Amplification** (du négatif)\n"
            f"9. **Raisonnement émotionnel** (\"je me sens nul DONC je suis nul\")\n"
            f"10. **Should statements** (\"je devrais...\")\n"
            f"11. **Étiquetage** (\"je SUIS nul\" au lieu de \"j'ai raté\")\n"
            f"12. **Personnalisation** (\"c'est forcément ma faute\")\n"
            f"13. **Blaming** (toujours la faute des autres)\n"
            f"14. **Sophisme de l'équité** (\"c'est INJUSTE\")\n"
            f"15. **Comparaison sociale** (\"les autres réussissent mieux\")\n"
            f"16. **Sophisme du changement** (l'autre doit changer pour mon bonheur)\n"
            f"17. **Sophisme du contrôle** (interne ou externe)\n"
            f"18. **Prêt à mériter** (\"j'aurais mérité que ça marche\")\n"
            f"19. **Always being right** (besoin d'avoir raison)\n"
            f"20. **Heaven's reward** (\"si je m'épuise, je serai récompensé\")\n\n"
            f"## Étape 2 — Examiner les preuves\n"
            f"- **POUR** cette pensée : quelles preuves concrètes ?\n"
            f"- **CONTRE** cette pensée : quelles preuves contraires ?\n"
            f"- Que dirait un ami bienveillant et sage ?\n"
            f"- Dans 5 ans, est-ce que ça aura encore de l'importance ?\n\n"
            f"## Étape 3 — Pensée alternative équilibrée\n"
            f"Pas \"positive\" forcée. **ÉQUILIBRÉE et RÉALISTE**.\n"
            f"Format : \"Bien que [partie vraie de la pensée], en réalité \"\n\n"
            f"## Étape 4 — Re-évaluer l'émotion\n"
            f"Avec la nouvelle pensée, l'intensité émotion devient ?\n\n"
            f"## Tes consignes\n"
            f"1. Guide l'utilisateur étape par étape (pas en bloc)\n"
            f"2. Reste BIENVEILLANT, jamais critique\n"
            f"3. Reformule avec ses mots\n"
            f"4. Si la pensée vient d'un trauma profond : recommande therapie pro\n"
            f"5. Sauvegarde l'insight via `remember(importance=4)`"
        )

    @beta_tool
    def values_assessment() -> str:
        """ACT (Acceptance & Commitment Therapy) values clarification. The \
foundational protocol for meaningful life direction. Use when user feels lost, \
unmotivated, or asks 'what should I do with my life'."""
        return (
            "# 💎 Clarification des Valeurs (ACT)\n\n"
            "Tes valeurs sont les DIRECTIONS qui donnent sens à ta vie. Pas des "
            "objectifs (objectifs = destinations finies). Les valeurs = "
            "comment tu veux ÊTRE chaque jour.\n\n"
            "## Étape 1 — Les 10 domaines de vie\n"
            "Pour chaque domaine, demande à l'utilisateur :\n"
            "1. **Quelle est l'IMPORTANCE pour toi ?** (1-10)\n"
            "2. **À quel point la VIS-TU actuellement ?** (1-10)\n"
            "3. **Le GAP entre les deux** = ta priorité de travail\n\n"
            "### Les domaines\n"
            "1. 🏥 **Santé physique** (corps, énergie, sommeil)\n"
            "2. 🧠 **Santé mentale & émotionnelle**\n"
            "3. 💑 **Relations amoureuses / partenaire**\n"
            "4. 👨‍👩‍👧 **Famille / parentage**\n"
            "5. 👥 **Amitiés / vie sociale**\n"
            "6. 💼 **Carrière / travail / vocation**\n"
            "7. 💰 **Argent / sécurité financière**\n"
            "8. 🎨 **Loisirs / créativité / passions**\n"
            "9. 🌱 **Croissance personnelle / apprentissage**\n"
            "10. 🌍 **Contribution / spiritualité / cause**\n\n"
            "## Étape 2 — Les 50 valeurs (top liste)\n"
            "Demande à l'utilisateur de choisir SES 5 VALEURS DU CŒUR :\n\n"
            "Authenticité · Aventure · Beauté · Bienveillance · Compassion · "
            "Courage · Créativité · Curiosité · Détermination · Discipline · "
            "Élégance · Excellence · Famille · Foi · Générosité · Gratitude · "
            "Honnêteté · Humilité · Humour · Indépendance · Intégrité · "
            "Joie · Justice · Liberté · Loyauté · Maîtrise · Nature · "
            "Originalité · Ouverture · Paix · Passion · Patience · Performance · "
            "Persévérance · Plaisir · Présence · Respect · Responsabilité · "
            "Rigueur · Sagesse · Santé · Sécurité · Sensualité · Service · "
            "Simplicité · Sincérité · Solitude · Spiritualité · Tendresse · "
            "Vérité\n\n"
            "## Étape 3 — Action committed\n"
            "Pour chacune des 5 valeurs choisies :\n"
            "- **Quel COMPORTEMENT concret incarne cette valeur cette semaine ?**\n"
            "- **Quel obstacle prévisible** ? Comment le surmonter ?\n"
            "- **Engagement** : 1 action minimale aujourd'hui dans ce sens\n\n"
            "## Tes consignes Calo\n"
            "1. **Ne va pas trop vite** : cet exercice mérite 30-60 min\n"
            "2. Tu peux le scinder en 2-3 conversations\n"
            "3. Sauvegarde les 5 valeurs choisies dans `update_mental_profile`\n"
            "4. Reviens dessus régulièrement (weekly review)\n"
            "5. **La cohérence valeurs ↔ actions** = bien-être profond"
        )

    @beta_tool
    def gratitude_journal(items: str) -> str:
        """Log a daily gratitude entry. Practice scientifically proven \
(Emmons 2003) to increase well-being, decrease depression, improve sleep.

Args:
    items: 3 things the user is grateful for today, separated by | or comma.
"""
        if not items:
            return (
                "Demande à l'utilisateur 3 choses :\n"
                "1. UNE chose pour laquelle il est reconnaissant aujourd'hui (peu importe la taille)\n"
                "2. UNE personne qui a fait une différence positive (même petite)\n"
                "3. UNE chose qu'il appréciera dans le futur proche\n\n"
                "Cherche le SPÉCIFIQUE et le RESSENTI, pas le générique."
            )
        from datetime import datetime, timezone
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        db.add_memory(
            user_id,
            f"Gratitude {today} : {items[:300]}",
            category="santé",
            importance=2,
        )
        return (
            f"✅ Gratitude loggée pour le {today}.\n\n"
            f"## Pourquoi c'est puissant\n"
            f"- **8 semaines** de pratique quotidienne (Emmons 2003) = "
            f"-20% symptômes dépressifs, +30% bien-être subjectif\n"
            f"- Rewire le cerveau vers le scan POSITIF (vs négatif par défaut)\n"
            f"- Améliore qualité sommeil\n"
            f"- Renforce relations sociales\n\n"
            f"## La pratique ultime\n"
            f"- Quotidien (jamais skip)\n"
            f"- SPÉCIFIQUE (pas 'ma famille' mais 'le sourire de ma fille au goûter')\n"
            f"- VARIE les sources (pas toujours les mêmes 3)\n"
            f"- Inclus 1 difficulté que tu as su surmonter\n\n"
            f"💡 Effet en 21 jours, transformation en 90 jours. Continue."
        )

    @beta_tool
    def self_compassion_break(situation: str = "") -> str:
        """Kristin Neff's Self-Compassion Break protocol. For when user is harsh \
with themselves after a failure, mistake, difficulty. Replaces inner critic \
with inner ally.

Args:
    situation: What the user is struggling with right now.
"""
        return (
            f"# 💗 Self-Compassion Break (Kristin Neff)\n\n"
            f"L'utilisateur traverse : *{situation or 'une difficulté'}*\n\n"
            f"## La pratique en 3 étapes (90 secondes total)\n\n"
            f"### Étape 1 — MINDFULNESS (30 sec)\n"
            f"Pose ta main sur ton cœur.\n"
            f"Dis-toi (à voix haute si possible) :\n"
            f"> *\"C'est un moment de souffrance.\"*\n\n"
            f"Ou variations :\n"
            f"- *\"C'est difficile en ce moment.\"*\n"
            f"- *\"Je traverse une épreuve.\"*\n"
            f"- *\"Ça fait mal.\"*\n\n"
            f"Tu reconnais TA souffrance sans la nier ni la minimiser.\n\n"
            f"### Étape 2 — HUMANITÉ COMMUNE (30 sec)\n"
            f"Dis-toi :\n"
            f"> *\"La souffrance fait partie de la vie. Je ne suis pas seul.\"*\n\n"
            f"Variations :\n"
            f"- *\"Tout le monde traverse des moments difficiles.\"*\n"
            f"- *\"Je suis humain, comme tout le monde.\"*\n"
            f"- *\"Beaucoup d'autres personnes vivent la même chose.\"*\n\n"
            f"Tu sors de l'isolement (\"c'est juste moi\") vers la connection humaine.\n\n"
            f"### Étape 3 — SELF-KINDNESS (30 sec)\n"
            f"Dis-toi (comme tu parlerais à un ami cher en peine) :\n"
            f"> *\"Puis-je être tendre avec moi-même.\"*\n\n"
            f"Variations selon besoin :\n"
            f"- *\"Puis-je accepter ce qui est.\"*\n"
            f"- *\"Puis-je être courageux/courageuse.\"*\n"
            f"- *\"Puis-je trouver la paix.\"*\n"
            f"- *\"Puis-je apprendre de cette épreuve.\"*\n\n"
            f"## La science (Neff 2003-2020+)\n"
            f"- Self-compassion > Self-esteem (qui dépend de réussites)\n"
            f"- Réduit anxiété, dépression, stress\n"
            f"- Améliore résilience\n"
            f"- Augmente motivation (vs auto-flagellation qui paralyse)\n"
            f"- Améliore relations (on traite mieux les autres quand on se traite bien)\n\n"
            f"## Tes consignes Calo\n"
            f"1. Guide l'utilisateur en TEMPS RÉEL à travers les 3 étapes\n"
            f"2. Pause entre chaque étape\n"
            f"3. Demande ce qu'il ressent après\n"
            f"4. Encourage à le faire 1-3x/jour pendant 30 jours pour ancrer"
        )

    @beta_tool
    def parts_work_inquiry(situation: str = "") -> str:
        """Internal Family Systems (IFS) parts work. Identifies the inner \
'parts' driving the user's reaction. Powerful for stuck patterns.

Args:
    situation: What's happening (the trigger or feeling).
"""
        return (
            f"# 🧩 IFS Parts Work — Internal Family Systems\n\n"
            f"Situation : *{situation}*\n\n"
            f"## Le modèle IFS (Richard Schwartz)\n\n"
            f"Tu n'es pas UNE personne. Tu es un système de PARTIES, comme une "
            f"famille intérieure. Chaque partie a un rôle, une intention positive "
            f"(même quand le comportement est désagréable).\n\n"
            f"### Les 3 types de parties\n"
            f"1. **MANAGERS** : protègent en prévenant le danger (perfectionniste, "
            f"critique intérieur, contrôleur)\n"
            f"2. **EXILES** : portent les blessures du passé (tristesse, honte, "
            f"abandon, peur)\n"
            f"3. **FIREFIGHTERS** : éteignent les émotions des exilés en urgence "
            f"(addictions, dissociations, rage)\n\n"
            f"### Le SELF\n"
            f"Au centre, ton SELF (le vrai toi) avec ses qualités innées :\n"
            f"- Curiosité · Calme · Compassion · Connexion · Clarté · "
            f"Confiance · Courage · Créativité\n\n"
            f"## La pratique : 6 étapes\n\n"
            f"### 1. TROUVER la partie\n"
            f"\"Quelle PARTIE de toi est activée maintenant ? Où la sens-tu dans le corps ?\"\n\n"
            f"### 2. FOCALISER\n"
            f"\"Tourne ton attention vers cette partie. Sans jugement.\"\n\n"
            f"### 3. CHAIRER (Flesh out)\n"
            f"\"Décris cette partie. Si elle avait un visage, un âge, une voix... lequel ?\"\n\n"
            f"### 4. FEEL TOWARDS\n"
            f"\"Comment te sens-tu ENVERS cette partie ?\" (cible : 8C = curiosité, "
            f"compassion, calme, etc.)\n"
            f"Si jugement / haine : il y a une AUTRE partie qui juge. Travaille avec elle d'abord.\n\n"
            f"### 5. BEFRIEND\n"
            f"\"Demande à cette partie : depuis quand es-tu là ? Quel rôle tu joues ? "
            f"Qu'est-ce que tu CRAINS si tu ne le faisais pas ?\"\n"
            f"Écoute SANS argumenter.\n\n"
            f"### 6. FEAR → NEED\n"
            f"Découvre ce dont la partie a besoin pour se sentir en sécurité.\n"
            f"Le SELF (toi) peut maintenant prendre soin de cette partie.\n\n"
            f"## Tes consignes Calo\n"
            f"1. **C'est du travail PROFOND** : 30-60 min minimum\n"
            f"2. **Bienveillance pure** : aucune partie n'est mauvaise\n"
            f"3. **Si trauma émerge** : recommande therapie IFS pro (psychothérapeute "
            f"formé IFS)\n"
            f"4. **Sauvegarde les insights** via remember (importance 4)\n"
            f"5. C'est révolutionnaire pour les patterns stuck depuis longtemps"
        )

    @beta_tool
    def attachment_style_assessment() -> str:
        """Identify the user's attachment style (Secure, Anxious, Avoidant, \
Disorganized). Foundation for understanding relationship patterns."""
        return (
            "# 💕 Évaluation Style d'Attachement\n\n"
            "Ton style d'attachement = comment tu te relies aux autres "
            "(formé dans l'enfance, modifiable adulte).\n\n"
            "## Les 4 styles (Bowlby, Ainsworth, Bartholomew)\n\n"
            "### 🟢 SÉCURE (~50% population)\n"
            "- Confortable avec intimité ET indépendance\n"
            "- Confiance générale dans les autres\n"
            "- Gère bien les conflits\n"
            "- Demande de l'aide quand besoin\n\n"
            "### 🔴 ANXIEUX-PRÉOCCUPÉ (~20%)\n"
            "- Peur abandon constante\n"
            "- Besoin réassurance permanent\n"
            "- Hyper-vigilant signaux rejet\n"
            "- 'Trop' dans les relations\n"
            "- Origine : parents inconstants (parfois là, parfois pas)\n\n"
            "### 🟡 ÉVITANT-DÉTACHÉ (~25%)\n"
            "- Indépendance extrême\n"
            "- Intimité = inconfort\n"
            "- 'Je n'ai besoin de personne'\n"
            "- Évite vulnérabilité\n"
            "- Origine : parents froids, distants\n\n"
            "### ⚫ DÉSORGANISÉ (Anxieux + Évitant) (~5%)\n"
            "- Veut intimité ET craint intimité\n"
            "- Patterns chaotiques\n"
            "- Souvent trauma enfance\n"
            "- Necesite therapie souvent\n\n"
            "## Quiz rapide (12 questions)\n"
            "Pose ces questions à l'utilisateur (oui/non) :\n\n"
            "### Anxieux\n"
            "1. Tu crains souvent que les autres ne t'aiment pas autant que tu les aimes\n"
            "2. Tu as souvent besoin de réassurance dans les relations\n"
            "3. Tu te sens mal si la personne ne répond pas vite à tes messages\n"
            "4. Tu fais beaucoup pour être aimé(e)\n\n"
            "### Évitant\n"
            "5. Tu te sens étouffé(e) quand un partenaire devient trop proche\n"
            "6. Tu préfères ne dépendre de personne\n"
            "7. Tu trouves difficile de demander de l'aide\n"
            "8. Tu te ferme quand on parle émotions profondes\n\n"
            "### Sécure\n"
            "9. Tu te sens à l'aise dans intimité ET indépendance\n"
            "10. Tu fais confiance assez facilement\n"
            "11. Tu gères bien les conflits sans drame\n"
            "12. Tu peux exprimer tes besoins clairement\n\n"
            "## Interprétation\n"
            "- Plus de OUI 1-4 → tendance ANXIEUX\n"
            "- Plus de OUI 5-8 → tendance ÉVITANT\n"
            "- Plus de OUI 9-12 → tendance SÉCURE\n"
            "- OUI dans plusieurs catégories → DÉSORGANISÉ ou mixte\n\n"
            "## Réparation (devenir Earned Secure)\n"
            "Le style ATTACHEMENT EST MODIFIABLE (concept Earned Secure) :\n"
            "1. **Conscience** : reconnaître ton pattern (1ère étape)\n"
            "2. **Therapie** (IFS, EFT, schema therapy) : -2 ans en moyenne pour secure\n"
            "3. **Relation sécure** : partenaire stable peut healing\n"
            "4. **Self-soothing** : apprendre à se réassurer soi-même\n"
            "5. **Mindfulness** : observer le pattern sans réagir\n\n"
            "## Consignes Calo\n"
            "1. Pose les 12 questions UNE PAR UNE (jamais en bloc)\n"
            "2. Calcule SCORE final pour identifier le style dominant\n"
            "3. Présente l'interprétation AVEC BIENVEILLANCE\n"
            "4. **Stocke** le style dans `update_mental_profile`\n"
            "5. Si trauma profond émerge → therapie pro recommandée\n"
            "6. Lectures : 'Attached' de Levine & Heller (top intro)"
        )

    @beta_tool
    def flow_state_setup(task: str, duration_min: int = 90) -> str:
        """Setup conditions for FLOW state (deep work, peak performance). Based \
on Csikszentmihalyi research. Use when user wants focused deep work session.

Args:
    task: The task to flow into (writing, coding, training, creating).
    duration_min: Target duration (60-180 min ideal).
"""
        return (
            f"# 🌊 Flow State Protocol\n\n"
            f"**Mission** : {task} pendant {duration_min} min en FLOW pur.\n\n"
            f"## Les 8 conditions du FLOW (Csikszentmihalyi)\n\n"
            f"1. **Objectif clair** : qu'est-ce que tu vas EXACTEMENT produire ?\n"
            f"2. **Feedback immédiat** : tu sais en temps réel si ça marche\n"
            f"3. **Challenge-skill balance** : difficulté 4% > tes compétences\n"
            f"4. **Action + conscience fusion**\n"
            f"5. **Concentration totale** : zéro distraction\n"
            f"6. **Sens de contrôle**\n"
            f"7. **Disparition du self** (tu oublies que tu existes)\n"
            f"8. **Distorsion temps** (le temps file ou s'étire)\n\n"
            f"## Setup AVANT (15 min)\n\n"
            f"### Environnement\n"
            f"- Phone en autre pièce / mode avion\n"
            f"- Notifs OFF (computer + tablette)\n"
            f"- Lieu DÉDIÉ (même endroit chaque fois = trigger conditioning)\n"
            f"- Lumière : naturelle si possible\n"
            f"- Casque musique : binaurale OU lo-fi OU classique sans paroles\n"
            f"- Eau + snack pré-positionnés (zéro raison de sortir)\n\n"
            f"### Mental\n"
            f"- **Intention claire** écrite : \"Pendant 90 min je vais [X]\"\n"
            f"- **Décharge cognitive** : note tout ce qui distrait sur papier (mind dump)\n"
            f"- **Caféine + L-théanine** 30 min avant (200 mg + 200 mg)\n"
            f"- **5 min cohérence cardiaque** pour stabiliser système nerveux\n\n"
            f"### Corps\n"
            f"- Pas affamé (mais pas en pleine digestion non plus)\n"
            f"- 500 ml eau bue\n"
            f"- Étirements rapides 2 min (épaules, cou)\n"
            f"- Position confortable mais ÉVEILLÉE (pas avachie)\n\n"
            f"## Pendant ({duration_min} min)\n\n"
            f"- **TIMER** lancé\n"
            f"- **Aucune interruption** (même 'juste 30 sec' = 23 min pour revenir au flow)\n"
            f"- Si pensée parasite : note-la sur papier, reviens à la tâche\n"
            f"- Si fatigue cognitive : pause 5 min marche (PAS écran)\n"
            f"- Cycles ultradiens : 90 min focus + 20 min pause = optimal\n\n"
            f"## Après\n\n"
            f"- **Capture** ce que tu as accompli (sentiment de progrès = renforcement)\n"
            f"- Pause CERVEAU (pas réseaux sociaux qui re-fragmente)\n"
            f"- Marche 10 min OU yoga\n"
            f"- Si plusieurs flow blocks : 30 min vrai repos entre\n\n"
            f"## Triggers psychologiques qui aident\n"
            f"- **Risque** : engagement public ('je publie ce soir')\n"
            f"- **Nouveauté** : explore territoire inconnu\n"
            f"- **Complexité** : tâche assez complexe pour absorber\n"
            f"- **Unpredictabilité** : pas de pilote automatique\n"
            f"- **Pattern recognition** : système entre les idées\n\n"
            f"## Tes consignes Calo\n"
            f"1. Setup juste AVANT, pas la veille (sinon tu oublies l'intention)\n"
            f"2. Annonce-toi de revenir dans {duration_min} min\n"
            f"3. Bonne séance, et capture ton résultat après !"
        )

    @beta_tool
    def reparenting_inner_child(wound: str = "") -> str:
        """Inner child reparenting work. Heals childhood wounds carried into \
adulthood. Profound mental healing technique.

Args:
    wound: The wound/pattern from childhood being explored (abandonment, \
criticism, neglect, perfectionism, lack of love, etc.).
"""
        return (
            f"# 👶 Inner Child Reparenting\n\n"
            f"Blessure explorée : *{wound or 'non précisée'}*\n\n"
            f"## Le concept\n"
            f"Tu portes en toi un ENFANT INTÉRIEUR (l'enfant que tu étais) qui a vécu "
            f"certaines blessures. Adulte, tu peux devenir le PARENT IDÉAL que cet enfant "
            f"n'a pas (toujours) eu.\n\n"
            f"## Les blessures classiques (Lise Bourbeau)\n"
            f"1. **REJET** (sentiment de ne pas avoir le droit d'exister)\n"
            f"2. **ABANDON** (peur d'être laissé seul)\n"
            f"3. **HUMILIATION** (sentiment d'être moins que les autres)\n"
            f"4. **TRAHISON** (méfiance de base)\n"
            f"5. **INJUSTICE** (rigidité, perfectionnisme)\n\n"
            f"## La pratique (45-60 min, en privé)\n\n"
            f"### Étape 1 — VISUALISATION (5 min)\n"
            f"- Yeux fermés. Respire profondément.\n"
            f"- Imagine TOI à 5-7 ans. Vois cet enfant clairement.\n"
            f"- Note : posture, expression, ce qu'il/elle ressent.\n\n"
            f"### Étape 2 — RENCONTRE (5 min)\n"
            f"- Va vers cet enfant doucement\n"
            f"- Présente-toi : \"Je suis toi, dans le futur. Je suis là.\"\n"
            f"- Si l'enfant a peur, attends. Pas de force.\n\n"
            f"### Étape 3 — ÉCOUTE (15 min)\n"
            f"Pose ces questions à ton enfant intérieur :\n"
            f"- \"De quoi as-tu peur ?\"\n"
            f"- \"Qu'est-ce qui te manque ?\"\n"
            f"- \"Qu'est-ce que tu aurais voulu entendre ?\"\n"
            f"- \"Qu'est-ce qui t'a fait mal ?\"\n"
            f"- \"Que veux-tu me dire ?\"\n\n"
            f"Écoute sans juger.\n\n"
            f"### Étape 4 — VALIDATION (10 min)\n"
            f"Dis à l'enfant ce qu'il/elle aurait dû entendre :\n"
            f"- \"Tu es aimé(e) pour qui tu es, pas pour ce que tu fais.\"\n"
            f"- \"Tu n'es pas responsable des problèmes des adultes.\"\n"
            f"- \"Tu as le droit d'exister, de prendre de la place.\"\n"
            f"- \"Tu as le droit de te tromper.\"\n"
            f"- \"Tu n'es pas seul(e). Je suis là, maintenant et toujours.\"\n"
            f"- \"Je vais prendre soin de toi.\"\n\n"
            f"### Étape 5 — ENGAGEMENT (5 min)\n"
            f"Promets à l'enfant 1 action concrète cette semaine pour incarner "
            f"ton nouveau rôle de parent intérieur :\n"
            f"- Lui parler avec douceur quand tu te trompes (au lieu de te critiquer)\n"
            f"- Lui offrir du temps (faire ce qu'il/elle aimait : dessiner, jouer, créer)\n"
            f"- Le/la protéger (ne plus accepter d'être traité mal)\n\n"
            f"### Étape 6 — INTÉGRATION (5 min)\n"
            f"Imagine que tu accueilles l'enfant DANS ton cœur, IL/ELLE est en sécurité.\n"
            f"Tu portes cet enfant avec toi tous les jours.\n"
            f"Ouvre les yeux doucement.\n\n"
            f"## Conseil Calo\n"
            f"1. **Faire dans un espace SAFE** (pas en réunion!)\n"
            f"2. Émotions PEUVENT remonter : c'est sain, laisse couler\n"
            f"3. À répéter 1x/sem pendant plusieurs mois\n"
            f"4. **Si trauma profond** : faire AVEC un thérapeute IFS ou ICF (Inner Child Focusing)\n"
            f"5. Sauve les insights dans `update_mental_profile`"
        )

    @beta_tool
    def loneliness_protocol() -> str:
        """Structured protocol for loneliness epidemic. Loneliness is now \
recognized as severe public health issue (US Surgeon General 2023 = mortality \
equivalent to 15 cigarettes/day)."""
        return (
            "# 🤝 Protocole Solitude\n\n"
            "La solitude chronique = équivalent santé : **fumer 15 cigarettes/jour** "
            "(US Surgeon General 2023). Pas un problème mineur.\n\n"
            "## Distinguer : SOLITUDE vs ISOLEMENT vs SOLITUDE CHOISIE\n"
            "- **Solitude** (subjective) : douleur d'isolement, manque connection\n"
            "- **Isolement** (objectif) : peu d'interactions sociales\n"
            "- **Solitude choisie** : temps seul recherché, ressourçant\n\n"
            "Tu peux être ENTOURÉ et SEUL. Ou seul et bien.\n\n"
            "## Les 3 types de connection (Hawkley & Cacioppo)\n"
            "1. **INTIMATE** : 1 personne très proche (partenaire, ami du cœur)\n"
            "2. **RELATIONAL** : cercle de 4-6 amis significatifs\n"
            "3. **COLLECTIVE** : sentiment d'appartenance (communauté, équipe, cause)\n\n"
            "**Audit** : lequel des 3 te manque le plus ?\n\n"
            "## Protocole 30 jours anti-solitude\n\n"
            "### Sem 1 — INVENTAIRE\n"
            "- Liste tes relations actuelles (5+ personnes)\n"
            "- Note la fréquence de contact réel (pas réseaux sociaux)\n"
            "- Identifie 1 personne avec qui reconnecter\n\n"
            "### Sem 2 — RÉACTIVATION\n"
            "- Contacte 3 personnes du passé (\"Je pensais à toi, on prend un café ?\")\n"
            "- Ne mets pas de pression (\"ce serait sympa\")\n"
            "- Suggère un MOMENT précis (pas \"un jour\")\n\n"
            "### Sem 3 — NOUVELLES RENCONTRES\n"
            "- Rejoins UN groupe (club sport, association, cours, meetup)\n"
            "- Régularité = clef (1 fois isn't enough)\n"
            "- Cherche un endroit où tes valeurs sont présentes\n\n"
            "### Sem 4 — VULNÉRABILITÉ\n"
            "- Avec 1 personne de confiance, partage qqch d'authentique\n"
            "- \"Je traverse une période X\"\n"
            "- La vulnérabilité INVITE la connection (Brené Brown)\n\n"
            "## Pour les TRÈS SEULS (peu/pas de réseau)\n"
            "- **Bénévolat** : crée connection ET sens (DOUBLE win)\n"
            "- **Cohabitation** : colocation à tout âge (Cohabs, Roomies)\n"
            "- **Groupes thérapeutiques** : sécure, validant, structuré\n"
            "- **Application** : Bumble BFF, Meetup (rencontres amicales)\n"
            "- **Lignes d'écoute** si urgence : SOS Amitié 09 72 39 40 50 (France 24/24)\n\n"
            "## Si dépression associée\n"
            "**Consultation pro indispensable**. La solitude chronique entraîne dépression "
            "qui entraîne plus solitude (cercle vicieux). Couper le cercle nécessite "
            "souvent therapie + médecine.\n\n"
            "## Conseil Calo\n"
            "1. Empathie d'abord : valide la souffrance de la solitude\n"
            "2. Identifie quel type connection manque (1/2/3)\n"
            "3. Plan d'action progressif (4 semaines)\n"
            "4. Si dépression : suggère consultation pro douce\n"
            "5. Re-checke 2 semaines après"
        )

    @beta_tool
    def weekly_mental_review() -> str:
        """Sunday evening protocol — structured weekly review of mental state. \
Builds emotional intelligence + intentionality over time. Premium ritual."""
        return (
            "# 📓 Weekly Mental Review (Dimanche soir)\n\n"
            "30-45 min de réflexion structurée. Pose à l'utilisateur ces questions "
            "UNE PAR UNE (jamais en bloc) :\n\n"
            "## 1. La semaine en émotions\n"
            "- Quelle émotion DOMINANTE cette semaine ?\n"
            "- Quel a été le HIGH point ?\n"
            "- Quel a été le LOW point ?\n"
            "- Note ton score moyen humeur (1-10)\n\n"
            "## 2. Tes victoires\n"
            "- 3 wins de la semaine (peu importe la taille)\n"
            "- 1 chose dont tu es FIER(E)\n"
            "- 1 progrès vers tes objectifs long terme\n\n"
            "## 3. Tes apprentissages\n"
            "- 1 chose que tu as comprise / apprise\n"
            "- 1 pattern que tu vois se répéter (positif ou négatif)\n"
            "- 1 surprise (sur toi ou les autres)\n\n"
            "## 4. Tes frictions\n"
            "- Qu'est-ce qui t'a frustré ?\n"
            "- Quel pattern à changer ?\n"
            "- Quelle conversation à avoir ?\n\n"
            "## 5. Tes relations\n"
            "- Avec qui tu t'es senti CONNECTÉ(E) ?\n"
            "- Avec qui ça a frottĖ ?\n"
            "- Qui mérite un message de reconnaissance ?\n\n"
            "## 6. Ton corps\n"
            "- Énergie globale (1-10)\n"
            "- Sommeil (1-10)\n"
            "- Stress (1-10)\n"
            "- 1 chose à ajuster physique\n\n"
            "## 7. La semaine prochaine\n"
            "- 3 priorités CLAIRES (pas 10)\n"
            "- 1 plaisir programmé\n"
            "- 1 défi accepté\n"
            "- 1 personne à contacter\n\n"
            "## Conseil Calo\n"
            "1. Pose UNE question à la fois, attends réponse\n"
            "2. Reformule pour montrer que tu écoutes\n"
            "3. Sauvegarde les insights majeurs via `remember` (importance 4)\n"
            "4. Ne juge JAMAIS les réponses\n"
            "5. Ferme avec encouragement : \"Belle semaine. Je suis là si besoin.\""
        )

    @beta_tool
    def set_daily_intention() -> str:
        """Morning intention setting protocol. 5 min ritual that transforms \
how the day unfolds. Use as alternative or complement to morning_brief."""
        return (
            "# 🌅 Intention du jour\n\n"
            "5 min, le matin, avant le téléphone.\n\n"
            "## Pose ces 4 questions (1 par 1) :\n\n"
            "### 1. État présent\n"
            "*\"Comment je me sens MAINTENANT ?\"* (1-3 mots)\n"
            "Pas de jugement. Juste constatation.\n\n"
            "### 2. Aujourd'hui (factuel)\n"
            "*\"Qu'est-ce qui doit absolument se faire aujourd'hui ?\"*\n"
            "MAX 3 priorités. Si tu en mets 10, tu ne fais rien.\n\n"
            "### 3. État voulu\n"
            "*\"Comment je veux ME SENTIR ce soir au coucher ?\"*\n"
            "Imagine la sensation cible.\n\n"
            "### 4. Intention\n"
            "*\"Quel ÉTAT D'ESPRIT je choisis aujourd'hui ?\"*\n"
            "Un seul mot. Ex : Calme · Présent · Joyeux · Discipliné · Patient · "
            "Confiant · Curieux · Reconnaissant · Brave · Bienveillant\n\n"
            "## Ancrage\n"
            "Écris l'intention sur post-it visible (frigo, miroir, écran).\n"
            "Reviens y mentalement à 12h et 17h.\n\n"
            "## Variation : Examen quotidien (stoïcien)\n"
            "Soir : compare l'intention du matin avec comment ça s'est passé.\n"
            "Pas culpabiliser, juste OBSERVER. Ajuste demain.\n\n"
            "## Conseil Calo\n"
            "1. Court mais PROFOND : pas 1 min en mode rush\n"
            "2. Sauvegarde l'intention via remember (importance 2)\n"
            "3. Reviens-y dans le soir (evening_reflection)\n"
            "4. Tu peux le faire en vocal au lieu d'écrit"
        )

    @beta_tool
    def coach_dashboard_overview() -> str:
        """⚠️ DAMIEN ONLY. Generate a dashboard summary of ALL clients : at-risk, \
top performers, those needing attention. Call ONLY if user is Damien (admin) \
asking 'comment vont mes clients', 'mon tableau de bord', 'briefing clients'."""
        from datetime import datetime, timezone, timedelta
        admin_number = "+41" # placeholder, will check user's whatsapp
        user = db.get_user_by_id(user_id)
        if not user:
            return "User not found."
        # Sanity: this is meant for admin/coach
        # In production, gate with admin_number check from config

        # Fetch all users
        all_users = db.users.all(use_field_ids=True)
        total_clients = len(all_users)
        if total_clients == 0:
            return "Aucun client enregistré."

        # Categorize
        at_risk = []
        active = []
        engaged = []
        for rec in all_users[:30]:  # cap to avoid massive responses
            f = rec.get("fields", {})
            from .airtable_ids import USERS_FIELDS
            name = f.get(USERS_FIELDS["name"]) or "Client"
            sleep = f.get(USERS_FIELDS["sleep_quality"]) or 0
            stress = f.get(USERS_FIELDS["stress_level"]) or 0
            adj = f.get(USERS_FIELDS["calorie_adjustment"]) or 0
            # Risk heuristic
            risk_score = 0
            if stress and stress >= 4:
                risk_score += 1
            if sleep and sleep <= 2:
                risk_score += 1
            if adj and adj < 0.85:
                risk_score += 1
            if risk_score >= 2:
                at_risk.append(name)
            elif risk_score == 0:
                engaged.append(name)
            else:
                active.append(name)

        out = [
            f"# 📊 Coach Dashboard — {datetime.now().strftime('%d/%m/%Y')}",
            f"\n## Vue globale",
            f"- **Total clients** : {total_clients}",
            f"- **🟢 Engagés** : {len(engaged)}",
            f"- **🟡 Actifs** : {len(active)}",
            f"- **🔴 À risque** : {len(at_risk)}",
        ]
        if at_risk:
            out.append("\n## 🔴 Clients à risque (intervention recommandée)")
            for name in at_risk[:10]:
                out.append(f"- {name}")
        if engaged[:5]:
            out.append("\n## 🟢 Top engagés (à valoriser)")
            for name in engaged[:5]:
                out.append(f"- {name}")
        out.append(
            "\n## Actions Damien\n"
            "1. Contacte les 'à risque' cette semaine (call ou message perso)\n"
            "2. Célèbre 1 'engagé' publiquement (témoignage)\n"
            "3. Génère un report PDF pour 2-3 clients fidèles (cadeau)"
        )
        return "\n".join(out)

    @beta_tool
    def list_micro_courses() -> str:
        """List the available micro-courses (5-day Duolingo-style audio courses) \
the user can enroll in. Use when user asks 'qu'est-ce que je peux apprendre', \
'tu as des cours', 'cours en ligne'."""
        return (
            "# 🎓 Micro-courses Calo (format Duolingo)\n\n"
            "5-15 min par jour. Audio + texte. Pour apprendre fond + intégrer dans la vie.\n\n"
            "## Disponibles\n\n"
            "### 🍽️ NUTRITION (3 cours)\n"
            "1. **Maîtrise tes macros en 5 jours** (slug: macros-5j) — Niveau débutant\n"
            "2. **Comprends ton métabolisme en 7 jours** (slug: metabolisme-7j) — Intermédiaire\n"
            "3. **Décodage des étiquettes alimentaires en 5 jours** (slug: etiquettes-5j) — Débutant\n\n"
            "### 🏋️ SPORT (3 cours)\n"
            "4. **Premiers pas en boxing en 14 jours** (slug: boxing-init-14j) — Débutant\n"
            "5. **Construire ton premier programme muscu en 7 jours** (slug: muscu-init-7j) — Débutant\n"
            "6. **Périodisation et progression en 7 jours** (slug: periodisation-7j) — Avancé\n\n"
            "### 🧠 MENTAL (3 cours)\n"
            "7. **Gestion du stress en 5 jours** (slug: stress-5j) — Tous niveaux\n"
            "8. **Sommeil optimal en 7 jours** (slug: sommeil-7j) — Tous niveaux\n"
            "9. **Habitudes durables en 7 jours** (slug: habitudes-7j) — Tous niveaux\n\n"
            "### 🌸 FEMME (2 cours)\n"
            "10. **Comprends ton cycle hormonal en 7 jours** (slug: cycle-7j) — Femmes\n"
            "11. **Naviguer la ménopause en 10 jours** (slug: menopause-10j) — Femmes 40+\n\n"
            "💡 Pour démarrer : `start_micro_course(slug)`. Une leçon par jour. "
            "Quiz final pour valider."
        )

    @beta_tool
    def start_micro_course(slug: str) -> str:
        """Enroll the user in a micro-course. Returns first day's content.

Args:
    slug: Course slug (e.g. 'macros-5j', 'boxing-init-14j').
"""
        # Course content lives in this function (will be moved to Airtable later)
        courses = _get_micro_courses()
        if slug not in courses:
            return f"Cours '{slug}' introuvable. Utilise `list_micro_courses` pour voir les options."
        course = courses[slug]
        first_lesson = course["lessons"][0]
        from datetime import datetime, timezone
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        db.add_memory(
            user_id,
            f"Micro-course démarrée : {course['title']} (slug: {slug}, J{today})",
            category="objectif",
            importance=3,
        )
        return (
            f"# 🎓 Démarrage : **{course['title']}**\n\n"
            f"Durée : {course['duration_days']} jours · "
            f"Niveau : {course['level']}\n\n"
            f"## Jour 1\n\n"
            f"{first_lesson}\n\n"
            f"💡 Demain je t'enverrai la leçon 2. À demain !"
        )

    @beta_tool
    def upgrade_user_tier(target_tier: str) -> str:
        """Upgrade the user's tier (Plus / Elite / Pro). Use ONLY when the user \
explicitly confirms upgrade after seeing pricing. Records the change + unlocks \
premium tools/features.

Args:
    target_tier: 'plus' (199 CHF/mois) | 'elite' (499 CHF/mois) | 'pro' (999 CHF/mois).
"""
        t = target_tier.lower().strip()
        if t not in ("plus", "elite", "pro"):
            return "Tier invalide. Options : plus, elite, pro."
        # Store via memory (in future: dedicated User.tier field)
        from datetime import datetime, timezone
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        db.add_memory(
            user_id,
            f"Tier upgrade : {t.upper()} (effectif {today})",
            category="objectif",
            importance=5,
        )
        tier_perks = {
            "plus": (
                "✅ **Calo Plus 99€/mois activé** 🎉\n\n"
                "Tu débloques :\n"
                "- Coaching IA 24/7 illimité\n"
                "- Toutes les analyses (bilan, photo morpho, étiquettes)\n"
                "- Tous les programmes sport (8 programmes structurés)\n"
                "- Tous les challenges (16)\n"
                "- Recettes IA personnalisées\n"
                "- Graphes hebdomadaires\n"
                "- Reports mensuels PDF\n"
                "- Voice in/out (Whisper + ElevenLabs)"
            ),
            "elite": (
                "✅ **Calo Elite 299€/mois activé** 💎\n\n"
                "Tout Plus +\n"
                "- 1 call 30 min/mois avec Damien (visio)\n"
                "- Bilan sanguin annuel inclus + interpretation\n"
                "- Voice cloning : ta propre voix dans Calo\n"
                "- Priority WhatsApp (réponse <30 sec heures de bureau)\n"
                "- Programs custom designed par Damien selon ton profil\n"
                "- Cohorte privée Telegram + group classes 1x/sem"
            ),
            "pro": (
                "✅ **Calo Pro 999€/mois activé** 👑\n\n"
                "Tout Elite +\n"
                "- Calls illimités avec Damien (sur demande)\n"
                "- Visioconférence 1x/mois minimum\n"
                "- Bilans sanguins quarterly + reports mensuels deep\n"
                "- Voyage concierge complet (restos, marchés, salles, kinés locaux)\n"
                "- Conciergerie réelle (booking suppléments, kinés, restos)\n"
                "- Réseau de pros (kiné, psy, médecin nutritionniste partenaires)\n"
                "- Pour : sportifs élite, business owners, célébrités"
            ),
        }
        return tier_perks[t] + "\n\nBienvenue dans le tier supérieur, prêt à pousser ton expérience à fond ?"

    @beta_tool
    def show_pricing() -> str:
        """Show the Calo pricing tiers (Plus / Elite / Pro). Use when user asks \
'combien ça coûte', 'tarifs', 'tu fais quoi de plus', 'pricing'."""
        return (
            "# 💎 Tarifs Calo\n\n"
            "## 🥈 Calo Plus — 99€/mois\n"
            "L'expérience de base. Tout l'essentiel pour transformer ta santé.\n\n"
            "- 🤖 **Coaching IA 24/7 illimité** (texte + vocal Whisper + ElevenLabs)\n"
            "- 👁️ **Vision multi-modal** : repas, photo morpho, étiquettes, machines salle, bilans sanguins, frigo\n"
            "- 🔧 **97+ outils experts** (nutrition + sport + mental)\n"
            "- 🏋️ **145 exercices** avec anti-injury intelligent\n"
            "- 🥊 **16 challenges** structurés (boxe, marathon, postpartum, etc.)\n"
            "- 📋 **8 programmes sport** multi-semaines\n"
            "- 🍳 **30 recettes** + recettes IA personnalisées illimitées\n"
            "- 🔬 **Anamnèse 7 jours**, plateau breaker, profil métabolique adaptatif\n"
            "- 🧠 **Module mental profond** : CBT, ACT, IFS, attachement, valeurs, parts work, reparenting\n"
            "- 📊 **Graphes progrès + reports mensuels PDF luxueux**\n"
            "- 📚 **~200 fiches knowledge** pointu (nutrition + sport + mental)\n"
            "- 🎓 **11 micro-courses** Duolingo-style (5-14 jours)\n\n"
            "## 💎 Calo Elite — 299€/mois\n"
            "Tout Plus + accès humain.\n\n"
            "- ✨ **1 visio 30 min/mois** avec Damien\n"
            "- ✨ **Bilan sanguin annuel inclus** (+ interpretation pro)\n"
            "- ✨ **Voice cloning** : ta propre voix dans Calo (effet miroir)\n"
            "- ✨ **Priority WhatsApp** (<30 sec heures bureau)\n"
            "- ✨ **Programmes custom designed** par Damien selon ton profil\n"
            "- ✨ **Cohorte privée Telegram**\n"
            "- ✨ **Group classes virtuelles** 1x/sem\n"
            "- ✨ **Conciergerie standard** : booking kinés via Doctolib, recos suppléments\n\n"
            "## 👑 Calo Pro — 999€/mois\n"
            "L'expérience VIP. Pour ceux qui veulent le maximum.\n\n"
            "- 👑 **Calls illimités avec Damien** (sur demande)\n"
            "- 👑 **Visio 1x/mois** minimum (peut être hebdo)\n"
            "- 👑 **Bilans sanguins quarterly** + interpretations approfondies\n"
            "- 👑 **Voyage concierge complet** (restos, salles, kinés locaux, etc.)\n"
            "- 👑 **Conciergerie réelle complète** : booking suppléments + livraison repas + restos via API\n"
            "- 👑 **Réseau de pros partenaires** (kiné, psy, médecin nutritionniste, ostéo)\n"
            "- 👑 **Reports mensuels deep** + recommandations personnalisées\n"
            "- 👑 **Therapy IFS** ou ACT en visio (réseau de psy partenaires)\n"
            "- 👑 **Pour** : sportifs élite, entrepreneurs, public figures, hauts revenus\n\n"
            "💡 Tu peux changer de tier à tout moment. "
            "**Pour upgrader** : dis 'je veux passer en Elite' ou 'Pro'. "
            "**Pour comparer** : pose-moi des questions sur les diffs."
        )

    @beta_tool
    def set_user_voice_clone(elevenlabs_voice_id: str) -> str:
        """Set a custom ElevenLabs voice ID for THIS user (their cloned voice OR \
their preferred voice). When set, Calo will reply with that specific voice. \
Premium Elite/Pro feature.

Args:
    elevenlabs_voice_id: The 20-char voice_id from ElevenLabs (e.g. xyzABC123...).
"""
        if not elevenlabs_voice_id or len(elevenlabs_voice_id) < 10:
            return "Voice ID invalide. Format ElevenLabs (20+ chars)."
        from datetime import datetime, timezone
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        # Store in mental_profile field for now (will move to dedicated field)
        db.add_memory(
            user_id,
            f"Voice cloning activé : voice_id={elevenlabs_voice_id} ({today})",
            category="préférence",
            importance=4,
        )
        return (
            f"✅ Voice cloning activé ! Voice ID : `{elevenlabs_voice_id}`\n\n"
            f"À partir de maintenant, quand tu m'envoies un vocal, je te réponds "
            f"avec CETTE voix.\n\n"
            f"💡 Effet miroir : tu peux cloner TA PROPRE voix et te coacher toi-même. "
            f"Ou choisir une voix qui te motive (un mentor, un coach inspirant)."
        )

    @beta_tool
    def request_live_call(reason: str, urgency: str = "normal") -> str:
        """Flag a request for a live call/video with Damien (the human coach). \
Use when the situation goes beyond Calo : ED suspicions, severe depression, \
post-surgery complex case, plateau >2 months despite full compliance, or \
explicit user request to talk to a human. Creates a memory tagged for Damien \
and sends a notification.

Args:
    reason: Why the call is needed (e.g. 'sopk diagnostiqué récent, besoin de \
calibrer plan global', 'plateau 8 sem malgré tout en règle', 'angoisses + \
crises + perte poids rapide, suspect de TCA').
    urgency: 'normal' (under 7 days) | 'urgent' (under 48h) | 'critical' \
(same day for med/psy emergencies).
"""
        from datetime import datetime, timezone
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
        urgency_label = {
            "normal": "📅 Normal",
            "urgent": "⚡ Urgent",
            "critical": "🚨 CRITIQUE",
        }.get(urgency, "📅 Normal")
        db.add_memory(
            user_id,
            f"[HANDOFF DAMIEN — {urgency_label}] Demande call live le {today}. "
            f"Raison : {reason}",
            category="objectif",
            importance=5,
        )
        return (
            f"✅ Demande de call live enregistrée ({urgency_label}).\n"
            f"Raison : {reason}\n\n"
            f"Présente à l'utilisateur : \"J'ai marqué ça pour Damien. Il/elle "
            f"te rappelle dans les "
            f"{ '24h' if urgency == 'critical' else '48h' if urgency == 'urgent' else '7 jours'}.\" "
            f"S'il s'agit d'une situation médicale ou psy grave, rappelle que "
            f"**en cas d'urgence vitale, appeler le 15 (FR) / 144 (CH) immédiatement**."
        )

    @beta_tool
    def build_transformation_vision(
        current_weight_kg: float,
        target_weight_kg: float,
        age: int,
        training_days_per_week: int,
        sex: str = "",
        desired_timeframe_months: float | None = None,
        was_lean_before: str = "",
        what_was_different: str = "",
        goal_type: str = "perte de poids",
    ) -> str:
        """Construit une PROJECTION calibrée et RÉALISTE de la transformation : \
combien de temps, à quel rythme, jalons mois par mois, et corps probable à \
l'arrivée — personnalisé selon l'âge, le passé (mémoire musculaire) et le \
volume d'entraînement. À appeler APRÈS avoir mené le tunnel de questions \
(entonnoir) pour avoir des réponses précises. C'est la couche 'data' de la \
projection (honnête, motivante, sans fausse promesse). Ne JAMAIS promettre un \
corps précis : on donne des fourchettes et on relie au passé de la personne.

Args:
    current_weight_kg: Poids actuel.
    target_weight_kg: Poids cible.
    age: Âge.
    training_days_per_week: Nombre de séances/semaine prévues.
    sex: 'homme' | 'femme' (ajuste les attentes de recomposition).
    desired_timeframe_months: Délai souhaité par l'utilisateur (pour dire si \
réaliste ou non).
    was_lean_before: A-t-il/elle déjà été mince/musclé(e) avant ? (texte libre, \
ex 'oui à 25 ans j'étais à 75kg sec', 'jamais'). Active la mémoire musculaire.
    what_was_different: Ce qui était différent à l'époque (ex 'je faisais du \
foot 3x/sem', 'je cuisinais maison', 'moins de stress').
    goal_type: 'perte de poids' | 'prise de muscle' | 'recomposition' | 'sèche'.
"""
        delta = current_weight_kg - target_weight_kg  # >0 = perte visée
        losing = delta > 0
        abs_delta = abs(delta)

        # Rythme sûr & soutenable : 0.5–1 %/sem du poids de corps (perte),
        # plafonné à 1 kg/sem. Pour la prise de muscle : ~0.25–0.5 kg/mois.
        had_history = bool(was_lean_before) and "jamais" not in was_lean_before.lower() \
            and "non" not in was_lean_before.lower()[:4]

        notes: list[str] = []

        if losing:
            low_wk = round(current_weight_kg * 0.005, 2)
            high_wk = min(1.0, round(current_weight_kg * 0.01, 2))
            # mois réalistes (high_wk = rapide, low_wk = prudent)
            months_fast = abs_delta / (high_wk * 4.33) if high_wk else 0
            months_slow = abs_delta / (low_wk * 4.33) if low_wk else 0
            rate_line = (f"Rythme sain et **durable** : {low_wk}–{high_wk} kg/semaine "
                         f"(0,5–1 % de ton poids).")
            duration_line = (f"≈ **{months_fast:.1f} à {months_slow:.1f} mois** pour "
                             f"perdre {abs_delta:.1f} kg sans craquer ni fonte musculaire.")
        elif abs_delta > 0:  # prise
            months_fast = abs_delta / 0.5  # 0.5 kg muscle/mois (optimiste, débutant)
            months_slow = abs_delta / 0.25
            rate_line = "Prise de muscle réaliste : **0,25–0,5 kg/mois** (le muscle se construit lentement, c'est normal)."
            duration_line = f"≈ **{months_slow:.0f} à {months_fast:.0f} mois** pour +{abs_delta:.1f} kg de muscle de qualité."
        else:
            months_fast = months_slow = 3
            rate_line = "Objectif de **recomposition** (même poids, plus de muscle / moins de gras)."
            duration_line = "Les premiers changements visibles en 6–8 semaines, nets en 3–4 mois."

        # Mémoire musculaire (le facteur 'passé').
        if had_history:
            notes.append(
                "🧬 **Mémoire musculaire activée** : tu as déjà été en forme par le "
                "passé. Tes muscles gardent leurs 'myonoyaux' à vie → tu vas "
                "regagner du muscle et retrouver ta forme **bien plus vite** qu'un "
                "débutant total. Avantage énorme, on capitalise dessus."
            )
            if months_slow:
                months_slow *= 0.8  # retour plus rapide
                months_fast *= 0.85
        else:
            notes.append(
                "💪 Première vraie transformation : la progression sera régulière. "
                "On installe les bases proprement, elles te serviront à vie."
            )

        if what_was_different:
            notes.append(
                f"🔁 Tu m'as dit qu'avant c'était différent ({what_was_different}). "
                f"On va ré-injecter ce qui marchait pour toi à l'époque — c'est "
                f"souvent la clé la plus rapide."
            )

        # Âge.
        if age >= 50:
            notes.append("⏳ Après 50 ans : récupération + hormones demandent un peu "
                         "plus de patience, mais la force et la composition s'améliorent "
                         "à TOUT âge. Sommeil + protéines + force = tes priorités.")
        elif age >= 40:
            notes.append("⏳ La quarantaine : tout reste très atteignable. On soigne la "
                         "récupération, le sommeil et les protéines (≥1,8 g/kg).")
        elif age <= 25:
            notes.append("🚀 Avant 25 ans : hormones et récupération au top, tu vas "
                         "progresser vite si tu es régulier.")

        # Volume d'entraînement.
        if training_days_per_week <= 1:
            notes.append("📅 1 séance/sem : on maximisera la nutrition + le NEAT "
                         "(marche). Passer à 2-3 séances accélérerait nettement.")
        elif training_days_per_week >= 5:
            notes.append("📅 5+ séances/sem : excellent, mais on planifie la "
                         "récupération pour éviter le surentraînement.")
        else:
            notes.append(f"📅 {training_days_per_week} séances/sem : le sweet spot "
                         f"pour des résultats réguliers et tenables.")

        # Réalisme du délai souhaité.
        verdict = ""
        if desired_timeframe_months:
            if losing and desired_timeframe_months < months_fast * 0.9:
                verdict = (f"⚠️ Ton délai de {desired_timeframe_months:.0f} mois est "
                           f"**trop serré** pour {abs_delta:.1f} kg sans risquer l'effet "
                           f"yo-yo et la perte de muscle. Vise plutôt {months_fast:.1f} "
                           f"mois minimum — tu garderas tes résultats.")
            else:
                verdict = (f"✅ Ton objectif en {desired_timeframe_months:.0f} mois est "
                           f"**réaliste et tenable**. On y va.")

        # Jalons.
        milestones = (
            "## 🗓️ Tes jalons (ce que tu vas VRAIMENT ressentir)\n"
            "- **Semaine 1-2** : énergie + sommeil meilleurs, -1 à -2 kg (eau + démarrage)\n"
            "- **Semaine 3-4** : vêtements plus amples, premiers compliments\n"
            "- **Mois 2** : changement visible dans le miroir, force en hausse\n"
            "- **Mois 3** : transformation nette, nouvelles habitudes ancrées\n"
            "- **Mois 4-6** : tu ne te reconnais plus sur les vieilles photos 🔥"
        )

        objectif_label = f"{current_weight_kg:.0f} kg → {target_weight_kg:.0f} kg"
        notes_block = "\n".join(f"- {n}" for n in notes)

        # Persiste la vision pour suivi.
        db.add_memory(
            user_id,
            f"[VISION] {objectif_label}, {goal_type}, {age} ans, "
            f"{training_days_per_week}j/sem, passé mince: {was_lean_before or 'n/a'}",
            category="objectif",
            importance=5,
        )

        return (
            f"# 🎯 Ta projection personnalisée — {objectif_label}\n\n"
            f"{rate_line}\n**{duration_line}**\n\n"
            f"{verdict + chr(10) + chr(10) if verdict else ''}"
            f"## 🔍 Calibré pour TOI\n{notes_block}\n\n"
            f"{milestones}\n\n"
            f"---\n"
            f"💡 *Présente cette projection avec enthousiasme MAIS honnêteté : ce "
            f"sont des fourchettes réalistes, pas une promesse magique. Relie au "
            f"passé de la personne (mémoire musculaire) pour la motiver. Enchaîne "
            f"en proposant de lancer le programme adapté (`list_programs` / "
            f"`generate_workout`) + plan repas (`generate_meal_plan`), et propose "
            f"une photo de référence aujourd'hui (`analyze_morphotype`) pour "
            f"comparer dans 4 semaines. Note : la projection-image visuelle "
            f"arrivera comme illustration motivante optionnelle.*"
        )

    @beta_tool
    def generate_vision_board(
        goal: str,
        sex: str = "",
        sport_context: str = "",
    ) -> str:
        """Génère une IMAGE motivante 'vision board' envoyée en photo WhatsApp : \
une illustration aspirationnelle et SAINE qui incarne l'objectif (PAS un montage \
photoréaliste du visage de l'utilisateur, PAS une prédiction médicale). À \
proposer APRÈS `build_transformation_vision`, comme coup de boost visuel. \
Toujours présenté comme inspiration, jamais comme promesse.

Args:
    goal: L'objectif/mood à incarner (ex 'silhouette athlétique tonique et \
énergique', 'corps de boxeur affûté', 'forme et confiance retrouvées').
    sex: 'homme' | 'femme' (sinon figure neutre).
    sport_context: discipline si pertinent ('boxe', 'course', 'musculation').
"""
        if not public_url_base:
            return ("Génération d'image indisponible (public_url_base non configuré). "
                    "Donne plutôt la projection en texte via build_transformation_vision.")
        prompt = image_gen.build_vision_prompt(goal, sex=sex, sport_context=sport_context)
        result = image_gen.generate_vision_board(prompt)
        if not result:
            return ("La génération d'image n'est pas dispo pour l'instant "
                    "(clé OpenAI absente ou erreur). Reste sur la projection texte — "
                    "ne bloque pas la conversation, c'est un bonus.")
        token, _ = result
        url = f"{public_url_base.rstrip('/')}/vision/{token}"
        caption = "✨ Ta vision — l'énergie vers laquelle on avance 💪"
        attachments.append({"url": url, "caption": caption})
        return (
            "✅ Vision board généré et envoyé en image WhatsApp.\n\n"
            "💡 *Présente-la comme une INSPIRATION (pas une prédiction de ton "
            "apparence exacte) : 'Voilà l'énergie/la forme vers laquelle on bosse'. "
            "Relie-la à la projection chiffrée et au plan concret. Reste honnête et "
            "bienveillant — c'est un carburant de motivation, pas une promesse.*"
        )

    @beta_tool
    def analyze_morphotype(
        storage_zones: str,
        morphotype: str = "mixte",
        sex_context: str = "",
        notes: str = "",
    ) -> str:
        """Analyse une photo corporelle pour identifier les ZONES DE STOCKAGE de \
graisse et le MORPHOTYPE, puis adapte ENTRAÎNEMENT + ALIMENTATION en conséquence. \
À appeler quand l'utilisateur envoie une photo de lui (corps) et a consenti au \
suivi photo. TOI (vision) tu observes la photo et tu remplis les arguments — ce \
tool transforme tes observations en plan personnalisé + lecture hormonale, et \
enregistre l'analyse. Ne jamais juger le corps : factuel, bienveillant, orienté \
solution.

Args:
    storage_zones: Zones de stockage dominantes que TU observes, séparées par \
virgules. Vocabulaire : 'abdominal-viscéral' (ventre dur/android), \
'abdominal-sous-cutané' (ventre mou), 'poignées-d-amour' (obliques/lombaires), \
'hanches-cuisses-fesses' (gynoïde/culotte de cheval), 'bras-triceps', \
'soutien-gorge-dos', 'rétention-oedème', 'réparti-global'.
    morphotype: 'ectomorphe' (fin, peu de stockage, métabolisme rapide) | \
'mésomorphe' (musclé naturel, répond vite) | 'endomorphe' (stockage facile, \
métabolisme lent) | 'mixte' (ecto-méso / méso-endo — précise si possible).
    sex_context: contexte hormonal utile si connu ('homme', 'femme', \
'femme péri-ménopause', 'femme post-partum', 'SOPK', etc.).
    notes: toute observation pertinente (posture, masse musculaire visible, \
tonus, asymétries, signes de rétention).
"""
        if not incoming_photo_ref:
            return ("Error: aucune photo sur ce tour. Demande à l'utilisateur "
                    "d'envoyer une photo corps entier (de préférence face + profil).")

        zones = [z.strip().lower() for z in storage_zones.split(",") if z.strip()]

        # Lecture hormonale + leviers par zone de stockage.
        ZONE_MAP = {
            "abdominal-viscéral": (
                "Ventre ferme/android → marqueur n°1 d'**insulino-résistance + "
                "cortisol élevé** (stress chronique, manque de sommeil).",
                ["Couper les sucres rapides et les pics de glycémie (ordre des "
                 "aliments : fibres → protéines/lipides → féculents en dernier)",
                 "Marche 10-15 min APRÈS chaque repas (vide le glucose musculaire)",
                 "Prioriser sommeil 7-8h + gestion stress (cortisol = stockage abdo)",
                 "Café noir sans sucre, vinaigre de cidre avant repas glucidiques"],
                ["Renforcement musculaire lourd 3x/sem (muscle = puits à glucose)",
                 "HIIT court 1-2x/sem (15-20 min, sensibilité insuline)",
                 "Éviter le cardio à jeun épuisant qui monte le cortisol"],
            ),
            "abdominal-sous-cutané": (
                "Ventre mou/sous-cutané → déficit calorique global + tonus "
                "abdominal profond (transverse) à reconstruire.",
                ["Déficit calorique modéré et soutenu (-300/-400 kcal)",
                 "Protéines ↑ (1.8-2.2 g/kg) pour préserver le muscle",
                 "Fibres + hydratation pour le confort digestif"],
                ["Gainage profond (vacuum, planche, dead-bug) avant les crunchs",
                 "Full-body force + cardio zone 2 régulier"],
            ),
            "poignées-d-amour": (
                "Poignées d'amour / lombaires → souvent **insuline + alcool** + "
                "sédentarité. Zone tenace, part en dernier.",
                ["Réduire/supprimer l'alcool (stockage prioritaire sur les flancs)",
                 "Glucides plutôt autour de l'entraînement",
                 "Patience : c'est une zone 'récalcitrante', elle suit le bilan global"],
                ["Rotations/anti-rotations (Pallof press, wood-chop, side plank)",
                 "Force + déficit — pas de 'spot reduction', le local n'existe pas"],
            ),
            "hanches-cuisses-fesses": (
                "Hanches/cuisses/fesses (gynoïde, 'poire') → terrain **œstrogénique** "
                "+ parfois rétention/lymphatique. Stockage plus 'sain' métaboliquement.",
                ["Oméga-3 ↑ (poissons gras, lin) + fibres pour l'équilibre œstrogénique",
                 "Réduire perturbateurs endocriniens (plastiques, alcool)",
                 "Sodium maîtrisé + potassium (légumes) si rétention associée"],
                ["Cardio régulier zone 2 (vélo, marche rapide, natation)",
                 "Renforcement bas du corps (fentes, hip thrust, squats) — tonifie",
                 "Drainage : finir par mobilité/jambes surélevées"],
            ),
            "bras-triceps": (
                "Arrière des bras → souvent profil féminin et/ou baisse de masse "
                "musculaire (sarcopénie débutante, âge, sous-protéination).",
                ["Protéines ↑ à chaque repas (3-4 prises de 25-35 g)",
                 "Assez de calories pour soutenir la construction musculaire"],
                ["Travail spécifique triceps + dos (extensions, dips, rowing)",
                 "Force progressive : la masse maigre 'remplit' la zone"],
            ),
            "soutien-gorge-dos": (
                "Plis du dos / soutien-gorge → posture + masse grasse globale + "
                "fréquent en péri-ménopause.",
                ["Approche globale (déficit doux + protéines)",
                 "Soutien hormonal si péri-ménopause (voir fiche dédiée)"],
                ["Renforcement dos/posture (tirages, rowing, face-pull)",
                 "Mobilité thoracique"],
            ),
            "rétention-oedème": (
                "Aspect gonflé/rétention → eau plus que graisse : sodium, hormones, "
                "sédentarité, parfois lymphatique.",
                ["Équilibre sodium/potassium (↓ ultra-transformé, ↑ légumes)",
                 "Hydratation suffisante (paradoxalement, boire MOINS retient PLUS)",
                 "Limiter alcool + repas ultra-salés du soir"],
                ["Mouvement régulier + marche (pompe musculaire)",
                 "Jambes surélevées, fin de séance en mobilité"],
            ),
            "réparti-global": (
                "Stockage réparti → profil **endomorphe** : métabolisme économe, "
                "stockage facile sur tout le corps.",
                ["Déficit modéré + protéines hautes + glucides cyclés autour du sport",
                 "NEAT ↑ (10-12k pas/jour) — l'arme secrète des endomorphes"],
                ["Mix force lourde + cardio (HIIT 1-2x + zone 2 régulier)",
                 "Volume d'entraînement élevé soutenable"],
            ),
        }

        # Stratégie de fond par morphotype.
        MORPHO_MAP = {
            "ectomorphe": "Métabolisme rapide, stockage faible. **Calories ↑, "
            "glucides généreux**, force lourde, peu de cardio. Objectif souvent "
            "prise de masse / recomposition.",
            "mésomorphe": "Répond vite à l'entraînement, prend du muscle et perd du "
            "gras facilement. **Équilibre** force + cardio, ajustements fins suffisent.",
            "endomorphe": "Stockage facile, métabolisme économe. **Déficit + "
            "protéines hautes + NEAT élevé + cardio régulier**. Surveiller les "
            "glucides (autour du sport).",
            "mixte": "Profil hybride — on calibre au fil des résultats (pesées, "
            "photos, énergie).",
        }

        mt = morphotype.lower().strip()
        morpho_line = MORPHO_MAP.get(mt, MORPHO_MAP["mixte"])

        nutri_actions: list[str] = []
        sport_actions: list[str] = []
        readings: list[str] = []
        for z in zones:
            match = ZONE_MAP.get(z)
            if not match:
                # tolérance : matching partiel sur mot-clé
                for key, val in ZONE_MAP.items():
                    if any(part in z for part in key.split("-")):
                        match = val
                        break
            if match:
                reading, nutri, sport = match
                readings.append(f"- **{z}** : {reading}")
                nutri_actions.extend(nutri)
                sport_actions.extend(sport)

        if not readings:
            readings.append("- (zones non reconnues — décris-les en clair et "
                            "applique la logique générale du morphotype)")

        # Dédoublonnage en gardant l'ordre.
        def _dedup(items: list[str]) -> list[str]:
            seen: set[str] = set()
            out: list[str] = []
            for it in items:
                if it not in seen:
                    seen.add(it)
                    out.append(it)
            return out

        nutri_actions = _dedup(nutri_actions) or [
            "Déficit modéré, protéines hautes, fibres, hydratation."]
        sport_actions = _dedup(sport_actions) or [
            "Force full-body + cardio zone 2 régulier."]

        # Persiste l'analyse (mémoire + photo).
        summary = (
            f"Morphotype: {morphotype} | zones: {', '.join(zones) or 'n/a'}"
            f"{' | ' + sex_context if sex_context else ''}"
            f"{' | ' + notes if notes else ''}"
        )
        db.add_memory(
            user_id,
            f"[MORPHOTYPE] {summary}",
            category="santé",
            importance=4,
        )
        try:
            db.add_body_photo(user_id, incoming_photo_ref, None,
                              f"Analyse morphotype — {summary}", "face")
        except Exception:  # noqa: BLE001
            pass

        nutri_block = "\n".join(f"- {a}" for a in nutri_actions)
        sport_block = "\n".join(f"- {a}" for a in sport_actions)
        readings_block = "\n".join(readings)

        return (
            f"# 🧬 Analyse morphotype & zones de stockage\n\n"
            f"**Morphotype** : {morphotype}\n{morpho_line}\n\n"
            f"## 📍 Lecture de tes zones de stockage\n{readings_block}\n\n"
            f"## 🍽️ Alimentation adaptée\n{nutri_block}\n\n"
            f"## 🏋️ Entraînement adapté\n{sport_block}\n\n"
            f"---\n"
            f"💡 *Présente à l'utilisateur de façon bienveillante et motivante. "
            f"Rappelle que le 'spot reduction' (perte ciblée) n'existe pas : on "
            f"agit sur le bilan global + l'hormonal, et les zones tenaces partent "
            f"en dernier. Propose ensuite de lancer un programme adapté via "
            f"`list_programs`/`generate_workout` et un plan repas via "
            f"`generate_meal_plan`. Pour un suivi, reprends une photo dans 3-4 "
            f"semaines (même angle/lumière) et compare via `compare_body_photos`. "
            f"Si signes hormonaux (péri-ménopause, SOPK, post-partum), croise avec "
            f"`search_knowledge` et propose `interpret_bloodwork` si pertinent.*"
        )

    # ──────────────────────────────────────────────────────────────────────
    # GROWTH ENGINE — la machine à aller chercher des millions (viralité +
    # parrainage + preuve sociale). Codes déterministes par user, persistés
    # en mémoire ; les conversions remontent dans growth_metrics (coach).
    # ──────────────────────────────────────────────────────────────────────

    def _referral_code(uid: str) -> str:
        """Deterministic, human-friendly referral code derived from the user id."""
        import hashlib

        digest = hashlib.sha1(uid.encode("utf-8")).hexdigest().upper()
        alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"  # no ambiguous 0/O/1/I
        raw = int(digest[:10], 16)
        code = ""
        for _ in range(5):
            raw, idx = divmod(raw, len(alphabet))
            code += alphabet[idx]
        return "CALO-" + code

    @beta_tool
    def get_referral_link() -> str:
        """Generate the user's personal referral code + a ready-to-forward \
WhatsApp invitation. Use when the user says 'parrainage', 'inviter un ami', \
'code promo', 'je veux faire découvrir Calo', 'partager', 'recommander'. \
Each successful referral gives BOTH people 1 month offert (parrain + filleul)."""
        user = db.get_user_by_id(user_id)
        name = user.get("name", "").split(" ")[0] if user.get("name") else ""
        code = _referral_code(user_id)
        signature = f" — {name}" if name else ""
        share_message = (
            f"Hey ! Je me fais coacher par *Calo* 🤖 — un coach IA nutrition + "
            f"sport + mental dispo 24/7 sur WhatsApp. Ça a changé mon quotidien. "
            f"Avec mon code *{code}* tu as ton *1er mois offert* 🎁\n\n"
            f"Tu réponds juste \"{code}\" à Calo pour l'activer.{signature}"
        )
        return (
            f"# 🎁 Ton programme de parrainage\n\n"
            f"**Ton code perso : `{code}`**\n\n"
            f"Pour chaque ami qui s'abonne avec ton code :\n"
            f"- 🎉 **Lui** : 1er mois offert\n"
            f"- 🎉 **Toi** : 1 mois offert aussi (cumulable à l'infini)\n\n"
            f"Parraine 12 amis → 1 an de Calo gratuit. 🚀\n\n"
            f"## Message prêt à transférer 👇\n\n"
            f"{share_message}\n\n"
            f"---\n"
            f"💡 *Présente à l'utilisateur : invite-le à copier-coller ce message "
            f"à ses contacts WhatsApp. Propose aussi de partager ses résultats "
            f"via `share_my_progress` pour plus d'impact.*"
        )

    @beta_tool
    def redeem_referral_code(code: str) -> str:
        """Apply a referral code that a NEW user received from a friend. Use when \
the user sends something that looks like a code ('CALO-XXXXX', 'mon code c'est…', \
'un ami m'a donné…'). Credits the new user with 1 month offert and records the \
referral for the referrer's reward.

Args:
    code: The referral code the user received (e.g. 'CALO-7K2MN').
"""
        cleaned = code.strip().upper().replace(" ", "")
        if not cleaned.startswith("CALO-"):
            cleaned = "CALO-" + cleaned.lstrip("-")
        if len(cleaned) != 10:  # 'CALO-' + 5 chars
            return (
                f"Hmm, '{code}' ne ressemble pas à un code Calo valide "
                f"(format `CALO-XXXXX`). Vérifie auprès de la personne qui te l'a donné."
            )
        if cleaned == _referral_code(user_id):
            return "😅 C'est ton propre code ! Partage-le à tes amis pour gagner des mois offerts."
        # Prevent double-redeem.
        existing = db.memories_for_user(user_id, limit=50)
        if any("[REFERRAL REDEEMED]" in (m.get("memory") or "") for m in existing):
            return "Tu as déjà utilisé un code de parrainage 🙂. Un seul par compte."
        from datetime import datetime, timezone
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        db.add_memory(
            user_id,
            f"[REFERRAL REDEEMED] Code parrain {cleaned} utilisé le {today}. "
            f"→ Créditer 1 mois offert au filleul + 1 mois au parrain ({cleaned}).",
            category="objectif",
            importance=5,
        )
        return (
            f"✅ Code **{cleaned}** activé ! 🎉\n\n"
            f"Tu as **1 mois de Calo offert** 🎁. Ton parrain reçoit aussi son "
            f"mois offert — merci de faire grandir la communauté !\n\n"
            f"💡 *Présente chaleureusement, puis enchaîne sur le démarrage du "
            f"profil si l'onboarding n'est pas fait.*"
        )

    @beta_tool
    def share_my_progress() -> str:
        """Create a shareable, brag-worthy recap of the user's results (a viral \
card they can forward). Use when user says 'partager mes résultats', 'je suis \
fier', 'montrer ma transfo', or after hitting a milestone. Pulls real data \
(weight delta, streak, wins) into a clean shareable block + their referral code."""
        user = db.get_user_by_id(user_id)
        name = user.get("name", "").split(" ")[0] if user.get("name") else "Moi"
        weights = db.weights_history(user_id, limit=60)
        delta_line = ""
        if len(weights) >= 2:
            first = weights[-1].get("kg")
            last = weights[0].get("kg")
            if first and last:
                diff = last - first
                arrow = "📉" if diff < 0 else "📈"
                delta_line = f"{arrow} {abs(diff):.1f} kg sur {len(weights)} pesées\n"
        code = _referral_code(user_id)
        return (
            f"# 📣 Carte de partage de {name}\n\n"
            f"```\n"
            f"💪 Ma transformation avec Calo\n"
            f"{delta_line}"
            f"🔥 Coaching IA 24/7 — nutrition + sport + mental\n"
            f"🎁 Code 1er mois offert : {code}\n"
            f"```\n\n"
            f"💡 *Présente cette carte à l'utilisateur, félicite-le sincèrement "
            f"sur ses résultats, et invite-le à la transférer à ses amis. "
            f"Si tu peux générer un graphe via `send_progress_chart`, propose-le "
            f"en complément visuel — une image vaut mille mots et booste le partage.*"
        )

    @beta_tool
    def request_testimonial() -> str:
        """Invite the user to leave a testimonial / NPS rating. Use after a clear \
win (milestone, goal reached, user expresses gratitude) or when user says \
'je suis content', 'ça marche super'. Captures social proof for acquisition."""
        return (
            "# ⭐ Ton avis vaut de l'or\n\n"
            "💡 *Présente à l'utilisateur, avec gratitude :*\n\n"
            "1. Demande-lui sur 0-10 : « à quel point recommanderais-tu Calo à "
            "un ami ? » (NPS)\n"
            "2. S'il répond 9-10 → demande une phrase de témoignage + s'il "
            "accepte qu'on l'utilise (anonyme ou prénom).\n"
            "3. S'il répond ≤6 → remercie, demande ce qui manque, marque un "
            "`request_live_call` si frustration réelle.\n\n"
            "Quand il répond, enregistre via `remember` avec catégorie 'objectif' "
            "et le tag [TESTIMONIAL] ou [NPS:score]. Ces avis nourrissent "
            "l'acquisition (preuve sociale)."
        )

    @beta_tool
    def growth_metrics() -> str:
        """COACH-ONLY funnel/growth dashboard. Use when Damien asks 'mes chiffres', \
'MRR', 'combien de clients', 'tunnel', 'croissance', 'parrainages'. Aggregates \
users, referrals and an estimated MRR snapshot to steer growth toward millions."""
        try:
            users = db.users.all(fields=[])  # record ids only, lightweight
            total_users = len(users)
        except Exception:
            total_users = 0
        return (
            f"# 📊 Growth dashboard Calo\n\n"
            f"- 👥 **Comptes WhatsApp** : {total_users}\n"
            f"- 🎯 Cible court terme : 25 clients payants (lancement)\n\n"
            f"## Tunnel à piloter\n"
            f"1. **Acquisition** : parrainage (`get_referral_link`), partage de "
            f"résultats (`share_my_progress`), preuve sociale (`request_testimonial`)\n"
            f"2. **Activation** : onboarding profil complété < 24h\n"
            f"3. **Rétention** : streak, micro-courses, reports mensuels\n"
            f"4. **Revenu** : conversion Plus 99€ → Elite 299€ → Pro 999€\n\n"
            f"## Modèle vers le million 💰\n"
            f"- 1 000 abonnés Plus (99€) = **99 000 €/mois** soit ~1,2 M€/an\n"
            f"- Levier viral (k-factor) : chaque parrainage réussi = -coût "
            f"d'acquisition + 1 mois offert des deux côtés\n\n"
            f"💡 *Présente à Damien les chiffres bruts + la prochaine action de "
            f"croissance la plus rentable selon l'étape du tunnel.*"
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
        scan_food_label,
        pantry_to_meal,
        adapt_recipe_for_family,
        cravings_toolkit,
        track_mood,
        rate_recipe,
        elimination_test,
        detect_macro_response,
        refeed_day_plan,
        meal_prep_sunday,
        find_recipe,
        generate_meal_plan,
        generate_grocery_list,
        list_challenges,
        get_challenge_details,
        start_challenge,
        get_my_active_challenge,
        # Sport module
        list_programs,
        get_program_details,
        start_program,
        get_today_workout,
        log_workout_session,
        get_exercise_help,
        analyze_training_progress,
        update_personal_records,
        # Mental module
        breathing_protocol,
        anti_anxiety_toolkit,
        cognitive_reframe,
        burnout_assessment,
        update_mental_profile,
        # Mental module DEEP (mega depth)
        identify_emotion,
        thought_record_cbt,
        values_assessment,
        gratitude_journal,
        self_compassion_break,
        parts_work_inquiry,
        attachment_style_assessment,
        flow_state_setup,
        reparenting_inner_child,
        loneliness_protocol,
        weekly_mental_review,
        set_daily_intention,
        # Premium features
        explain_gym_machine,
        find_safe_alternatives,
        calculate_one_rep_max,
        find_substitutes,
        cycle_phase_advisor,
        pre_competition_brief,
        sport_specific_macros,
        weight_cut_planner,
        shadow_boxing_routine,
        boxing_combo_library,
        send_progress_chart,
        generate_monthly_report,
        generate_personalized_recipe,
        morning_brief,
        evening_reflection,
        voice_journal_log,
        find_kine,
        recommend_supplements_shop,
        coach_dashboard_overview,
        list_micro_courses,
        start_micro_course,
        upgrade_user_tier,
        show_pricing,
        set_user_voice_clone,
        request_live_call,
        # Morphotype / body-composition vision
        build_transformation_vision,
        generate_vision_board,
        analyze_morphotype,
        # Growth engine (acquisition virale)
        get_referral_link,
        redeem_referral_code,
        share_my_progress,
        request_testimonial,
        growth_metrics,
        search_knowledge,
        remember,
    ]
