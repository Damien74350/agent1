# Calo — Coach nutrition WhatsApp

Coach nutritionnel par WhatsApp propulsé par Claude. L'utilisateur envoie des photos de repas, Calo identifie les aliments, estime les calories/macros, et suit la progression hebdomadaire avec photos morphologiques (avec consentement).

## État du projet

**Phase 1 — Prototype technique** (présent) : backend opérationnel + intégration Twilio Sandbox WhatsApp.

Roadmap : voir [SETUP.md](./SETUP.md#prochaines-étapes-phase-2).

## Architecture

```
agent1/
├── agent/           # Agent CLI générique (assistant tout-terrain, hérité)
├── calo/            # Produit Calo (logique métier)
│   ├── config.py    # Chargement .env
│   ├── nutrition.py # BMR / TDEE / cibles macro (Mifflin-St Jeor)
│   ├── db.py        # SQLite (users / meals / weights / photos / messages)
│   ├── storage.py   # Chiffrement Fernet des photos
│   ├── prompts.py   # System prompt + messages de rappel
│   ├── tools.py     # 6 outils Claude (complete_profile, log_meal, ...)
│   ├── coach.py     # Boucle agent — handle_turn(text, photo) → reply
│   └── cli.py       # Chat local pour itérer sans Twilio
└── api/             # Backend FastAPI
    ├── main.py      # App + webhook Twilio
    └── twilio_client.py  # Envoi messages + téléchargement médias
```

## Démarrage rapide

### Setup distant (production)

Lis [SETUP.md](./SETUP.md). Tu créeras des comptes Anthropic / Twilio / Railway, tu connecteras 9 variables d'environnement, et tu auras un bot WhatsApp fonctionnel en ~45 min.

### Setup local (développement)

```bash
git clone <repo>
cd agent1
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edite .env : au minimum ANTHROPIC_API_KEY et CALO_PHOTO_ENCRYPTION_KEY
```

**Chat avec Calo en local (sans Twilio) :**

```bash
python -m calo.cli
```

Tu peux envoyer une photo via : `photo:/chemin/vers/image.jpg Voici mon déjeuner`.

**Lancer le backend FastAPI en local :**

```bash
uvicorn api.main:app --reload
```

Pour tester le webhook localement, utilise ngrok :

```bash
ngrok http 8000
# → copie l'URL https dans CALO_PUBLIC_URL et dans la config webhook Twilio
```

## Modèles utilisés

- **Claude Sonnet 4.6** (`CALO_MODEL`) — vision de qualité Opus à 1/3 du prix. Suffisant pour identifier des aliments sur photo.
- Adaptive thinking + effort=`medium` par défaut — bon compromis qualité/coût.

Bascule sur Opus 4.7 (`CALO_MODEL=claude-opus-4-7`) si tu veux du raisonnement plus poussé (ex: plans alimentaires hebdo personnalisés en Phase 4).

## Sécurité & RGPD

- Photos chiffrées sur disque via Fernet (clé symétrique). Sans la clé, les fichiers `.enc` sont illisibles.
- Validation cryptographique de la signature Twilio sur le webhook (anti-spoofing).
- Pas de stockage des photos en clair, jamais.
- En Phase 4 : politique de confidentialité, droit à l'effacement (1 message = tout supprimé), CGU.

## Agent CLI générique (legacy)

Le package `agent/` est l'assistant générique créé en amont — assistant tout-terrain avec outils fichier/bash/web search. Pas utilisé par Calo, conservé pour référence et tests :

```bash
./run.sh
```

## Coûts opérationnels (Phase 1)

Estimations pour 1 utilisateur (toi) sur 1 mois :
- Anthropic Sonnet 4.6 : ~$10-20 (10 messages/jour, dont la moitié avec photo)
- Twilio Sandbox : gratuit
- Railway : gratuit (free tier)

**Total estimé : <$25/mois en test.** Multiplie par N utilisateurs au scale.
