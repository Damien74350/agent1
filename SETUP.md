# Calo — Guide de setup (Phase 1)

Ce guide te fait passer de "rien" à "je parle à Calo sur mon WhatsApp" en ~45 min.

## Vue d'ensemble

Tu vas créer 4 comptes et brancher leurs secrets dans le `.env`. Le code est déjà prêt.

| Compte | Pourquoi | Coût | Temps |
|---|---|---|---|
| Anthropic | Modèle Claude (cerveau de l'agent) | Pay-as-you-go (~$5 pour tester) | 5 min |
| Airtable | Base de connaissance + données utilisateurs | Gratuit (base déjà créée) | 5 min |
| Twilio | Recevoir et envoyer des messages WhatsApp | Sandbox gratuite | 10 min |
| Railway | Héberger le backend en ligne | Gratuit (500h/mois) | 10 min |

---

## Étape 1 — Compte Anthropic + clé API

1. Va sur https://console.anthropic.com et crée un compte.
2. Ajoute une carte bancaire dans **Settings → Billing** (mets $5-10 pour démarrer).
3. Va dans **API Keys** → **Create Key**, nomme-la "calo", copie la clé `sk-ant-...`.
4. Garde-la, on l'utilisera à l'étape 4.

## Étape 2 — Token Airtable (PAT)

La base Calo est **déjà créée** dans ton workspace (id `appDlXTmOGVJ6ML6z`, 6 tables, base alimentaire et knowledge base seedées). Il faut juste générer un token pour que Calo puisse y lire/écrire.

1. Va sur **https://airtable.com/create/tokens**
2. Clique **Create new token**
3. Nomme-le `calo-api`
4. **Scopes** : coche
   - `data.records:read`
   - `data.records:write`
   - `schema.bases:read`
5. **Access** : coche uniquement la base **Calo** (pas toutes tes bases)
6. **Create token** → copie la chaîne `pat...` (visible une seule fois)
7. Garde-la, on l'utilisera à l'étape 5 (variables d'environnement)

> ⚠️ **Pourquoi un PAT et pas une clé API classique :** Airtable a déprécié les API keys globales. Les PAT sont scopés par base et par scope, donc beaucoup plus sûrs en cas de fuite.

## Étape 3 — Compte Twilio + Sandbox WhatsApp

1. Va sur https://www.twilio.com/try-twilio et crée un compte (carte requise pour le numéro, mais la sandbox WhatsApp est gratuite).
2. Une fois connecté, va dans **Console → Account → API keys & tokens**.
3. Note ton **Account SID** (commence par `AC...`) et ton **Auth Token** (clique sur "Show").
4. Dans le menu de gauche, va dans **Messaging → Try it out → Send a WhatsApp message**.
5. Tu verras un numéro Twilio sandbox (style `+1 415 523 8886`) et un **code d'activation** (style `join brave-tiger`).
6. **Depuis ton WhatsApp**, envoie le code d'activation à ce numéro. Ton numéro est maintenant lié à la sandbox.
7. Note le numéro Twilio sandbox (format `whatsapp:+14155238886`).

> 💡 **Limitation sandbox :** seuls les numéros qui ont envoyé le code de jonction peuvent recevoir des messages. Parfait pour tester, on passera à un vrai numéro WhatsApp Business à la Phase 3.

## Étape 4 — Compte Railway + déploiement

1. Va sur https://railway.app et connecte-toi avec GitHub.
2. Crée un nouveau projet → **Deploy from GitHub repo** → sélectionne ce repo + la branche `claude/epic-babbage-dn0rR`.
3. Railway détecte le `Dockerfile` et commence le build.
4. **Ne lance pas tout de suite**, on doit d'abord configurer les variables d'environnement (étape 4).

## Étape 5 — Variables d'environnement sur Railway

Dans Railway → ton projet → **Variables**, ajoute chacune de ces variables :

| Variable | Valeur |
|---|---|
| `ANTHROPIC_API_KEY` | la clé `sk-ant-...` de l'étape 1 |
| `AIRTABLE_PAT` | le token `pat...` de l'étape 2 |
| `CALO_MODEL` | `claude-sonnet-4-6` |
| `CALO_EFFORT` | `medium` |
| `CALO_PHOTO_ENCRYPTION_KEY` | une nouvelle clé (voir ci-dessous) |
| `TWILIO_ACCOUNT_SID` | `AC...` de l'étape 3 |
| `TWILIO_AUTH_TOKEN` | l'auth token de l'étape 3 |
| `TWILIO_WHATSAPP_FROM` | `whatsapp:+14155238886` (ou le numéro de ta sandbox) |
| `CALO_PUBLIC_URL` | l'URL Railway de ton service (visible après le 1er deploy, format `https://xxxx.up.railway.app`) |
| `CALO_ADMIN_NUMBER` | `whatsapp:+33XXXXXXXXX` (ton numéro WhatsApp perso) |

**Pour générer `CALO_PHOTO_ENCRYPTION_KEY`**, sur ta machine (n'importe quelle machine avec Python) :
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```
→ ça affiche une clé base64. Copie-la dans Railway. **Garde-la précieusement** (perte de clé = perte des photos chiffrées).

Une fois toutes les variables ajoutées, Railway redéploie automatiquement. Attends que le build passe au vert (~2 min).

## Étape 6 — Connecter le webhook Twilio à Railway

1. Récupère ton URL Railway publique (ex: `https://calo-production-abcd.up.railway.app`).
2. Va sur Twilio → **Messaging → Try it out → WhatsApp Sandbox Settings**.
3. Dans "**WHEN A MESSAGE COMES IN**", colle : `https://<ton-url-railway>/twilio/webhook`
4. Méthode : **POST**. Sauvegarde.

## Étape 7 — Test !

Depuis WhatsApp, envoie un message au numéro sandbox Twilio. Exemple :

```
Salut !
```

Au bout de quelques secondes (le temps que Claude réfléchisse), tu devrais recevoir une réponse de Calo te demandant ton prénom.

### Test du flow complet :

1. **Onboarding** : réponds aux questions (prénom, sexe, âge, taille, poids, activité, objectif, photo consent).
2. **Photo de repas** : envoie une photo de ton prochain repas. Calo doit identifier les aliments et logger les calories.
3. **Bilan** : envoie *"bilan de la journée"*. Calo répond avec ton récap chiffré.

---

## Débogage

| Symptôme | Cause probable | Fix |
|---|---|---|
| Pas de réponse du tout | Webhook pas connecté, ou app down | Vérifier les logs Railway, vérifier l'URL du webhook Twilio |
| "Erreur technique" générique | Erreur côté agent | Logs Railway → cherche la stack trace |
| Réponse mais incohérente | Mauvais profil utilisateur | Le DB est dans `/app/data/calo.db` sur Railway (volume éphémère en Phase 1 — ça repart à zéro à chaque redeploy ; on ajoutera un volume persistant en Phase 2) |
| 403 invalid signature | `CALO_PUBLIC_URL` faux | Vérifie que `CALO_PUBLIC_URL` correspond exactement à l'URL Railway, sans slash final |

Pour voir les logs en direct : Railway → ton service → **Deployments** → clique sur le déploiement actif → **View Logs**.

---

## Coûts attendus (Phase 1)

- Anthropic Sonnet 4.6 : ~$0.005 par photo de repas analysée + ~$0.02 par bilan. Pour toi seul testant : <$1/jour.
- Twilio sandbox : gratuit.
- Railway : gratuit (free tier de 500h/mois suffit largement).

**Budget total estimé pour 2 semaines de tests intensifs : <$30.**

---

## Prochaines étapes (Phase 2)

Une fois que tu as validé que Phase 1 fonctionne :
- Ajout d'un volume Railway persistant (la DB ne se reset plus)
- Migration de SQLite → Postgres (Supabase)
- Rappels proactifs (matin, midi, soir) via un scheduler
- Onboarding amélioré (vidéos d'exemple)
- Préparation du numéro WhatsApp officiel (vérification Meta Business)
