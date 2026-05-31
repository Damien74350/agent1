"""Airtable-backed storage for Calo (users, meals, weights, body photos,
foods, knowledge base).

Conversation history stays in SQLite (high frequency, low admin value).
Everything else lives in Airtable so the operator can audit, edit, and enrich
it through the Airtable UI.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from pyairtable import Api

from .airtable_ids import (
    BASE_ID,
    BODY_PHOTOS_FIELDS,
    BODY_PHOTOS_TABLE,
    CHALLENGES_FIELDS,
    CHALLENGES_TABLE,
    FOODS_FIELDS,
    FOODS_TABLE,
    KNOWLEDGE_FIELDS,
    KNOWLEDGE_TABLE,
    MEALS_FIELDS,
    MEALS_TABLE,
    MEMORIES_FIELDS,
    MEMORIES_TABLE,
    RECIPES_FIELDS,
    RECIPES_TABLE,
    USER_CHALLENGES_FIELDS,
    USER_CHALLENGES_TABLE,
    USERS_FIELDS,
    USERS_TABLE,
    WEIGHT_LOGS_FIELDS,
    WEIGHT_LOGS_TABLE,
)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


class AirtableDB:
    def __init__(self, pat: str):
        if not pat:
            raise RuntimeError("AirtableDB requires an Airtable PAT.")
        self.api = Api(pat)
        self.users = self.api.table(BASE_ID, USERS_TABLE)
        self.foods = self.api.table(BASE_ID, FOODS_TABLE)
        self.knowledge = self.api.table(BASE_ID, KNOWLEDGE_TABLE)
        self.meals = self.api.table(BASE_ID, MEALS_TABLE)
        self.weights = self.api.table(BASE_ID, WEIGHT_LOGS_TABLE)
        self.body_photos = self.api.table(BASE_ID, BODY_PHOTOS_TABLE)
        self.memories = self.api.table(BASE_ID, MEMORIES_TABLE)
        self.recipes = self.api.table(BASE_ID, RECIPES_TABLE)
        self.challenges = self.api.table(BASE_ID, CHALLENGES_TABLE)
        self.user_challenges = self.api.table(BASE_ID, USER_CHALLENGES_TABLE)

    # pyairtable returns fields keyed by NAME by default. Our schema uses
    # field IDs everywhere (so renames in the UI don't break us), so every
    # read MUST pass `use_field_ids=True`. Centralised here.
    _BY_ID = {"use_field_ids": True}

    # ------------------------------------------------------------------
    # users
    # ------------------------------------------------------------------

    def get_or_create_user(self, whatsapp_number: str) -> dict[str, Any]:
        rec = self.users.first(
            formula=f"{{{USERS_FIELDS['whatsapp_number']}}} = '{_escape(whatsapp_number)}'",
            **self._BY_ID,
        )
        if rec:
            return _unwrap_user(rec)
        rec = self.users.create(
            {
                USERS_FIELDS["whatsapp_number"]: whatsapp_number,
                USERS_FIELDS["created_at"]: now_iso(),
                USERS_FIELDS["onboarding_complete"]: False,
                USERS_FIELDS["photo_consent"]: False,
            },
            typecast=True,
            use_field_ids=True,
        )
        return _unwrap_user(rec)

    def get_user_by_id(self, record_id: str) -> dict[str, Any]:
        try:
            rec = self.users.get(record_id, **self._BY_ID)
            return _unwrap_user(rec)
        except Exception:
            return {}

    def update_user(self, record_id: str, **fields: Any) -> None:
        if not fields:
            return
        mapped: dict[str, Any] = {}
        for key, value in fields.items():
            field_id = USERS_FIELDS.get(key)
            if not field_id:
                continue
            if key in {"photo_consent", "onboarding_complete"}:
                value = bool(value)
            if key == "calorie_adjustment" and value is not None:
                # Airtable percent expects a decimal (0.85 = 85%)
                value = float(value) / 100.0 if float(value) > 2 else float(value)
            mapped[field_id] = value
        if mapped:
            self.users.update(record_id, mapped, typecast=True, use_field_ids=True)

    # ------------------------------------------------------------------
    # meals
    # ------------------------------------------------------------------

    def add_meal(
        self,
        user_id: str,
        items: list[dict[str, Any]],
        photo_path: str | None,
        notes: str | None = None,
        eaten_at: str | None = None,
        meal_type: str | None = None,
    ) -> str:
        total_kcal = sum(int(i.get("kcal", 0)) for i in items)
        total_protein = sum(int(i.get("protein_g", 0)) for i in items)
        total_carbs = sum(int(i.get("carbs_g", 0)) for i in items)
        total_fat = sum(int(i.get("fat_g", 0)) for i in items)
        fields = {
            MEALS_FIELDS["eaten_at"]: eaten_at or now_iso(),
            MEALS_FIELDS["user"]: [user_id],
            MEALS_FIELDS["items"]: json.dumps(items, ensure_ascii=False),
            MEALS_FIELDS["total_calories"]: total_kcal,
            MEALS_FIELDS["total_protein_g"]: total_protein,
            MEALS_FIELDS["total_carbs_g"]: total_carbs,
            MEALS_FIELDS["total_fat_g"]: total_fat,
        }
        if notes:
            fields[MEALS_FIELDS["notes"]] = notes
        if meal_type:
            fields[MEALS_FIELDS["meal_type"]] = meal_type
        rec = self.meals.create(fields, typecast=True, use_field_ids=True)
        return rec["id"]

    def meals_for_day(self, user_id: str, day_iso: str) -> list[dict[str, Any]]:
        """`day_iso` is YYYY-MM-DD. Returns meals whose `Eaten At` starts with that date."""
        formula = (
            f"AND(FIND('{day_iso}', {{{MEALS_FIELDS['eaten_at']}}}) = 1, "
            f"FIND('{user_id}', ARRAYJOIN({{{MEALS_FIELDS['user']}}})) > 0)"
        )
        recs = self.meals.all(formula=formula, **self._BY_ID)
        return [_unwrap_meal(r) for r in recs]

    def meals_since(self, user_id: str, since_iso: str) -> list[dict[str, Any]]:
        """All meals for a user whose `Eaten At` >= since_iso (YYYY-MM-DD).
        Sorted by eaten_at ascending."""
        formula = (
            f"AND({{{MEALS_FIELDS['eaten_at']}}} >= '{since_iso}', "
            f"FIND('{user_id}', ARRAYJOIN({{{MEALS_FIELDS['user']}}})) > 0)"
        )
        recs = self.meals.all(
            formula=formula,
            sort=[MEALS_FIELDS["eaten_at"]],
            **self._BY_ID,
        )
        return [_unwrap_meal(r) for r in recs]

    # ------------------------------------------------------------------
    # weight logs
    # ------------------------------------------------------------------

    def add_weight(self, user_id: str, kg: float) -> None:
        self.weights.create(
            {
                WEIGHT_LOGS_FIELDS["logged_at"]: now_iso(),
                WEIGHT_LOGS_FIELDS["user"]: [user_id],
                WEIGHT_LOGS_FIELDS["weight_kg"]: kg,
            },
            typecast=True,
            use_field_ids=True,
        )

    def weights_history(self, user_id: str, limit: int = 30) -> list[dict[str, Any]]:
        formula = (
            f"FIND('{user_id}', ARRAYJOIN({{{WEIGHT_LOGS_FIELDS['user']}}})) > 0"
        )
        recs = self.weights.all(
            formula=formula,
            sort=[f"-{WEIGHT_LOGS_FIELDS['logged_at']}"],
            max_records=limit,
            **self._BY_ID,
        )
        return [_unwrap_weight(r) for r in recs]

    # ------------------------------------------------------------------
    # body photos
    # ------------------------------------------------------------------

    def add_body_photo(
        self,
        user_id: str,
        encrypted_ref: str,
        week_number: int | None,
        analysis: str | None,
        angle: str = "face",
    ) -> str:
        rec = self.body_photos.create(
            {
                BODY_PHOTOS_FIELDS["captured_at"]: now_iso(),
                BODY_PHOTOS_FIELDS["user"]: [user_id],
                BODY_PHOTOS_FIELDS["week_number"]: week_number,
                BODY_PHOTOS_FIELDS["encrypted_photo_ref"]: encrypted_ref,
                BODY_PHOTOS_FIELDS["analysis"]: analysis,
                BODY_PHOTOS_FIELDS["angle"]: angle,
            },
            typecast=True,
            use_field_ids=True,
        )
        return rec["id"]

    def body_photos_for_user(self, user_id: str) -> list[dict[str, Any]]:
        formula = (
            f"FIND('{user_id}', ARRAYJOIN({{{BODY_PHOTOS_FIELDS['user']}}})) > 0"
        )
        recs = self.body_photos.all(
            formula=formula,
            sort=[f"-{BODY_PHOTOS_FIELDS['captured_at']}"],
            **self._BY_ID,
        )
        return [_unwrap_body_photo(r) for r in recs]

    # ------------------------------------------------------------------
    # knowledge base
    # ------------------------------------------------------------------

    def search_knowledge(self, query: str, max_results: int = 3) -> list[dict[str, Any]]:
        """Keyword search over Title + Content + Tags. Only `Active = TRUE` entries.
        Returns up to `max_results` hits."""
        q = _escape(query.lower())
        title = KNOWLEDGE_FIELDS["title"]
        content = KNOWLEDGE_FIELDS["content"]
        tags = KNOWLEDGE_FIELDS["tags"]
        active = KNOWLEDGE_FIELDS["active"]
        formula = (
            f"AND({{{active}}}, OR("
            f"FIND('{q}', LOWER({{{title}}})), "
            f"FIND('{q}', LOWER({{{content}}})), "
            f"FIND('{q}', LOWER(ARRAYJOIN({{{tags}}}, ',')))"
            f"))"
        )
        recs = self.knowledge.all(formula=formula, max_records=max_results, **self._BY_ID)
        return [_unwrap_knowledge(r) for r in recs]

    def list_knowledge_titles(self) -> list[dict[str, Any]]:
        """Return all knowledge titles (for an index view)."""
        recs = self.knowledge.all(
            formula=f"{{{KNOWLEDGE_FIELDS['active']}}}",
            fields=[KNOWLEDGE_FIELDS["title"], KNOWLEDGE_FIELDS["topic"]],
            **self._BY_ID,
        )
        return [
            {
                "id": r["id"],
                "title": r["fields"].get(KNOWLEDGE_FIELDS["title"]),
                "topic": r["fields"].get(KNOWLEDGE_FIELDS["topic"]),
            }
            for r in recs
        ]

    # ------------------------------------------------------------------
    # foods database
    # ------------------------------------------------------------------

    def lookup_food(self, name: str) -> dict[str, Any] | None:
        """Try exact name match first, then substring."""
        name_field = FOODS_FIELDS["name_fr"]
        active = FOODS_FIELDS["active"]
        exact = self.foods.first(
            formula=f"AND({{{active}}}, LOWER({{{name_field}}}) = '{_escape(name.lower())}')",
            **self._BY_ID,
        )
        if exact:
            return _unwrap_food(exact)
        fuzzy = self.foods.first(
            formula=f"AND({{{active}}}, FIND('{_escape(name.lower())}', LOWER({{{name_field}}})))",
            **self._BY_ID,
        )
        return _unwrap_food(fuzzy) if fuzzy else None

    # ------------------------------------------------------------------
    # memories (long-term facts about the user)
    # ------------------------------------------------------------------

    def add_memory(
        self,
        user_id: str,
        memory: str,
        category: str = "divers",
        importance: int = 3,
    ) -> str:
        rec = self.memories.create(
            {
                MEMORIES_FIELDS["created_at"]: now_iso(),
                MEMORIES_FIELDS["user"]: [user_id],
                MEMORIES_FIELDS["memory"]: memory,
                MEMORIES_FIELDS["category"]: category,
                MEMORIES_FIELDS["importance"]: max(1, min(5, int(importance))),
                MEMORIES_FIELDS["active"]: True,
            },
            typecast=True,
            use_field_ids=True,
        )
        return rec["id"]

    def memories_for_user(
        self, user_id: str, limit: int = 30
    ) -> list[dict[str, Any]]:
        """Most important / most recent active memories for a user.
        Sort by importance desc, then created_at desc."""
        formula = (
            f"AND({{{MEMORIES_FIELDS['active']}}}, "
            f"FIND('{user_id}', ARRAYJOIN({{{MEMORIES_FIELDS['user']}}})) > 0)"
        )
        recs = self.memories.all(
            formula=formula,
            sort=[
                f"-{MEMORIES_FIELDS['importance']}",
                f"-{MEMORIES_FIELDS['created_at']}",
            ],
            max_records=limit,
            **self._BY_ID,
        )
        return [_unwrap_memory(r) for r in recs]

    def search_foods(self, partial: str, limit: int = 10) -> list[dict[str, Any]]:
        name_field = FOODS_FIELDS["name_fr"]
        active = FOODS_FIELDS["active"]
        formula = (
            f"AND({{{active}}}, FIND('{_escape(partial.lower())}', LOWER({{{name_field}}})))"
        )
        recs = self.foods.all(formula=formula, max_records=limit, **self._BY_ID)
        return [_unwrap_food(r) for r in recs]

    # ------------------------------------------------------------------
    # recipes
    # ------------------------------------------------------------------

    def search_recipes(
        self,
        query: str | None = None,
        category: str | None = None,
        tags: list[str] | None = None,
        max_kcal: int | None = None,
        max_prep_min: int | None = None,
        max_results: int = 5,
    ) -> list[dict[str, Any]]:
        """Search the Recipes table with flexible filters.

        - `query` matches against name OR ingredients (substring, case-insensitive)
        - `category` exact match on category (petit-déj / déjeuner / dîner / snack / dessert / entrée)
        - `tags` requires ALL listed tags to be present
        - `max_kcal` / `max_prep_min` are numeric upper bounds per serving
        """
        conditions = [f"{{{RECIPES_FIELDS['active']}}}"]
        if query:
            q = _escape(query.lower())
            conditions.append(
                f"OR(FIND('{q}', LOWER({{{RECIPES_FIELDS['name']}}})), "
                f"FIND('{q}', LOWER({{{RECIPES_FIELDS['ingredients']}}})))"
            )
        if category:
            conditions.append(
                f"{{{RECIPES_FIELDS['category']}}} = '{_escape(category)}'"
            )
        if tags:
            for tag in tags:
                conditions.append(
                    f"FIND('{_escape(tag)}', ARRAYJOIN({{{RECIPES_FIELDS['tags']}}}, ',')) > 0"
                )
        if max_kcal is not None:
            conditions.append(f"{{{RECIPES_FIELDS['kcal']}}} <= {int(max_kcal)}")
        if max_prep_min is not None:
            conditions.append(f"{{{RECIPES_FIELDS['prep_min']}}} <= {int(max_prep_min)}")
        formula = "AND(" + ", ".join(conditions) + ")"
        recs = self.recipes.all(
            formula=formula,
            max_records=max_results,
            sort=[RECIPES_FIELDS["prep_min"]],
            **self._BY_ID,
        )
        return [_unwrap_recipe(r) for r in recs]

    def get_recipe_by_id(self, record_id: str) -> dict[str, Any] | None:
        try:
            rec = self.recipes.get(record_id, **self._BY_ID)
            return _unwrap_recipe(rec)
        except Exception:
            return None

    # ------------------------------------------------------------------
    # challenges
    # ------------------------------------------------------------------

    def list_challenges(
        self,
        category: str | None = None,
        difficulty: str | None = None,
        audience: str | None = None,
        max_results: int = 10,
    ) -> list[dict[str, Any]]:
        """List active challenges, optionally filtered by category/difficulty/audience."""
        conditions = [f"{{{CHALLENGES_FIELDS['active']}}}"]
        if category:
            conditions.append(
                f"{{{CHALLENGES_FIELDS['category']}}} = '{_escape(category)}'"
            )
        if difficulty:
            conditions.append(
                f"{{{CHALLENGES_FIELDS['difficulty']}}} = '{_escape(difficulty)}'"
            )
        if audience:
            conditions.append(
                f"FIND('{_escape(audience)}', ARRAYJOIN({{{CHALLENGES_FIELDS['target_audience']}}}, ',')) > 0"
            )
        formula = "AND(" + ", ".join(conditions) + ")"
        recs = self.challenges.all(
            formula=formula,
            max_records=max_results,
            sort=[CHALLENGES_FIELDS["duration_days"]],
            **self._BY_ID,
        )
        return [_unwrap_challenge(r) for r in recs]

    def get_challenge_by_slug(self, slug: str) -> dict[str, Any] | None:
        rec = self.challenges.first(
            formula=f"{{{CHALLENGES_FIELDS['slug']}}} = '{_escape(slug)}'",
            **self._BY_ID,
        )
        return _unwrap_challenge(rec) if rec else None

    def start_user_challenge(self, user_id: str, challenge_id: str) -> str:
        """Subscribe a user to a challenge. Returns the UserChallenge record ID."""
        rec = self.user_challenges.create(
            {
                USER_CHALLENGES_FIELDS["started_at"]: now_iso(),
                USER_CHALLENGES_FIELDS["user"]: [user_id],
                USER_CHALLENGES_FIELDS["challenge"]: [challenge_id],
                USER_CHALLENGES_FIELDS["status"]: "actif",
                USER_CHALLENGES_FIELDS["current_day"]: 1,
            },
            typecast=True,
            use_field_ids=True,
        )
        return rec["id"]

    def get_active_user_challenge(self, user_id: str) -> dict[str, Any] | None:
        """Return the user's currently active challenge, if any."""
        formula = (
            f"AND({{{USER_CHALLENGES_FIELDS['status']}}} = 'actif', "
            f"FIND('{user_id}', ARRAYJOIN({{{USER_CHALLENGES_FIELDS['user']}}})) > 0)"
        )
        rec = self.user_challenges.first(formula=formula, **self._BY_ID)
        return _unwrap_user_challenge(rec) if rec else None

    def recipes_for_meal_plan(
        self,
        exclude_tags: list[str] | None = None,
        require_tags: list[str] | None = None,
    ) -> dict[str, list[dict[str, Any]]]:
        """Return active recipes grouped by category for meal-plan composition.

        `exclude_tags` removes recipes carrying ANY of those tags (e.g.
        ['végétarien'] won't be excluded — it's just a tag — but if the user
        is allergic to a category we'd pass it here).
        `require_tags` keeps only recipes carrying ALL listed tags (e.g.
        ['végétarien'] for a vegetarian user).
        """
        conditions = [f"{{{RECIPES_FIELDS['active']}}}"]
        if require_tags:
            for tag in require_tags:
                conditions.append(
                    f"FIND('{_escape(tag)}', ARRAYJOIN({{{RECIPES_FIELDS['tags']}}}, ',')) > 0"
                )
        formula = "AND(" + ", ".join(conditions) + ")"
        recs = self.recipes.all(formula=formula, **self._BY_ID)
        grouped: dict[str, list[dict[str, Any]]] = {
            "petit-déj": [],
            "déjeuner": [],
            "dîner": [],
            "snack": [],
            "dessert": [],
        }
        for r in recs:
            recipe = _unwrap_recipe(r)
            cat = recipe.get("category") or ""
            if exclude_tags and any(t in (recipe.get("tags") or []) for t in exclude_tags):
                continue
            if cat in grouped:
                grouped[cat].append(recipe)
        return grouped


# ----------------------------------------------------------------------
# unwrapping helpers — turn the field-ID-keyed Airtable record into a friendly dict
# ----------------------------------------------------------------------


def _unwrap_user(rec: dict[str, Any]) -> dict[str, Any]:
    f = rec.get("fields", {})
    out = {"id": rec["id"]}
    for friendly, field_id in USERS_FIELDS.items():
        out[friendly] = f.get(field_id)
    return out


def _unwrap_meal(rec: dict[str, Any]) -> dict[str, Any]:
    f = rec.get("fields", {})
    raw_items = f.get(MEALS_FIELDS["items"]) or "[]"
    try:
        items = json.loads(raw_items)
    except (ValueError, TypeError):
        items = []
    return {
        "id": rec["id"],
        "eaten_at": f.get(MEALS_FIELDS["eaten_at"]),
        "user": f.get(MEALS_FIELDS["user"], []),
        "items": items,
        "total_calories": f.get(MEALS_FIELDS["total_calories"], 0),
        "total_protein_g": f.get(MEALS_FIELDS["total_protein_g"], 0),
        "total_carbs_g": f.get(MEALS_FIELDS["total_carbs_g"], 0),
        "total_fat_g": f.get(MEALS_FIELDS["total_fat_g"], 0),
        "notes": f.get(MEALS_FIELDS["notes"]),
        "meal_type": f.get(MEALS_FIELDS["meal_type"]),
    }


def _unwrap_weight(rec: dict[str, Any]) -> dict[str, Any]:
    f = rec.get("fields", {})
    return {
        "id": rec["id"],
        "logged_at": f.get(WEIGHT_LOGS_FIELDS["logged_at"]),
        "weight_kg": f.get(WEIGHT_LOGS_FIELDS["weight_kg"]),
    }


def _unwrap_body_photo(rec: dict[str, Any]) -> dict[str, Any]:
    f = rec.get("fields", {})
    return {
        "id": rec["id"],
        "captured_at": f.get(BODY_PHOTOS_FIELDS["captured_at"]),
        "week_number": f.get(BODY_PHOTOS_FIELDS["week_number"]),
        "encrypted_photo_ref": f.get(BODY_PHOTOS_FIELDS["encrypted_photo_ref"]),
        "analysis": f.get(BODY_PHOTOS_FIELDS["analysis"]),
        "angle": f.get(BODY_PHOTOS_FIELDS["angle"]),
    }


def _unwrap_memory(rec: dict[str, Any]) -> dict[str, Any]:
    f = rec.get("fields", {})
    return {
        "id": rec["id"],
        "created_at": f.get(MEMORIES_FIELDS["created_at"]),
        "memory": f.get(MEMORIES_FIELDS["memory"]),
        "category": f.get(MEMORIES_FIELDS["category"]),
        "importance": f.get(MEMORIES_FIELDS["importance"], 3),
    }


def _unwrap_recipe(rec: dict[str, Any]) -> dict[str, Any]:
    f = rec.get("fields", {})
    tags_raw = f.get(RECIPES_FIELDS["tags"]) or []
    return {
        "id": rec["id"],
        "name": f.get(RECIPES_FIELDS["name"]),
        "category": f.get(RECIPES_FIELDS["category"]),
        "tags": tags_raw if isinstance(tags_raw, list) else [],
        "servings": f.get(RECIPES_FIELDS["servings"]),
        "prep_min": f.get(RECIPES_FIELDS["prep_min"]),
        "cook_min": f.get(RECIPES_FIELDS["cook_min"]),
        "kcal": f.get(RECIPES_FIELDS["kcal"]),
        "protein_g": f.get(RECIPES_FIELDS["protein_g"]),
        "carbs_g": f.get(RECIPES_FIELDS["carbs_g"]),
        "fat_g": f.get(RECIPES_FIELDS["fat_g"]),
        "fiber_g": f.get(RECIPES_FIELDS["fiber_g"]),
        "ingredients": f.get(RECIPES_FIELDS["ingredients"]),
        "instructions": f.get(RECIPES_FIELDS["instructions"]),
    }


def _unwrap_challenge(rec: dict[str, Any]) -> dict[str, Any]:
    f = rec.get("fields", {})
    audience_raw = f.get(CHALLENGES_FIELDS["target_audience"]) or []
    return {
        "id": rec["id"],
        "name": f.get(CHALLENGES_FIELDS["name"]),
        "slug": f.get(CHALLENGES_FIELDS["slug"]),
        "duration_days": f.get(CHALLENGES_FIELDS["duration_days"]),
        "category": f.get(CHALLENGES_FIELDS["category"]),
        "difficulty": f.get(CHALLENGES_FIELDS["difficulty"]),
        "target_audience": audience_raw if isinstance(audience_raw, list) else [],
        "pitch": f.get(CHALLENGES_FIELDS["pitch"]),
        "daily_structure": f.get(CHALLENGES_FIELDS["daily_structure"]),
        "rules": f.get(CHALLENGES_FIELDS["rules"]),
        "expected_outcome": f.get(CHALLENGES_FIELDS["expected_outcome"]),
    }


def _unwrap_user_challenge(rec: dict[str, Any]) -> dict[str, Any]:
    f = rec.get("fields", {})
    return {
        "id": rec["id"],
        "started_at": f.get(USER_CHALLENGES_FIELDS["started_at"]),
        "challenge": f.get(USER_CHALLENGES_FIELDS["challenge"], []),
        "status": f.get(USER_CHALLENGES_FIELDS["status"]),
        "current_day": f.get(USER_CHALLENGES_FIELDS["current_day"], 1),
        "adherence": f.get(USER_CHALLENGES_FIELDS["adherence"]),
    }


def _unwrap_knowledge(rec: dict[str, Any]) -> dict[str, Any]:
    f = rec.get("fields", {})
    return {
        "id": rec["id"],
        "title": f.get(KNOWLEDGE_FIELDS["title"]),
        "topic": f.get(KNOWLEDGE_FIELDS["topic"]),
        "content": f.get(KNOWLEDGE_FIELDS["content"]),
        "tags": f.get(KNOWLEDGE_FIELDS["tags"], []),
    }


def _unwrap_food(rec: dict[str, Any]) -> dict[str, Any]:
    f = rec.get("fields", {})
    return {
        "id": rec["id"],
        "name": f.get(FOODS_FIELDS["name_fr"]),
        "category": f.get(FOODS_FIELDS["category"]),
        "kcal_per_100g": f.get(FOODS_FIELDS["kcal_per_100g"]),
        "protein_per_100g": f.get(FOODS_FIELDS["protein_per_100g"]),
        "carbs_per_100g": f.get(FOODS_FIELDS["carbs_per_100g"]),
        "fat_per_100g": f.get(FOODS_FIELDS["fat_per_100g"]),
        "fiber_per_100g": f.get(FOODS_FIELDS["fiber_per_100g"]),
        "standard_portion_g": f.get(FOODS_FIELDS["standard_portion_g"]),
        "source": f.get(FOODS_FIELDS["source"]),
    }


def _escape(value: str) -> str:
    """Escape a value for safe inclusion in an Airtable formula string literal."""
    return value.replace("\\", "\\\\").replace("'", "\\'")
