# unblur

Transforme un compte Instagram en page d'abonnement floutée — en 60 secondes.

Le créateur tape son @handle → on récupère ses 9 dernières photos publiques →
on les floute → il fixe son prix → sa page est live, partageable. Les
visiteurs paient pour voir le feed en clair.

## Stack

- **Next.js 15** (App Router, Server Actions)
- **Tailwind + Framer Motion** pour le design premium
- **Apify** pour scraper Instagram (fallback démo si pas configuré)
- **Stripe Checkout** pour l'abonnement (fallback démo si pas configuré)
- Déploiement **Vercel** (gratuit, 1 clic depuis Git)

## Démo locale

```bash
cd unblur
npm install --legacy-peer-deps
npm run dev
```

Ouvre [http://localhost:3000](http://localhost:3000), tape n'importe quel
@handle (ex: `damien`), tu verras le flow complet avec des photos placeholder.

## Mettre en prod sur Vercel (5 min, gratuit)

1. Va sur [vercel.com](https://vercel.com), connecte-toi avec GitHub
2. **Import Project** → choisis `damien74350/agent1`
3. Dans **Root Directory** : tape `unblur`
4. **Framework Preset** : Next.js (auto)
5. **Environment Variables** (optionnel pour le démo) :
   - `APIFY_TOKEN` (si tu veux scraper en vrai)
   - `STRIPE_SECRET_KEY` (si tu veux encaisser pour de vrai)
6. **Deploy**

Vercel te donne une URL `unblur-xxxx.vercel.app` immédiatement. Tu peux
brancher un vrai domaine (`unblur.app`) en 30 secondes après.

## Flow démo conférence (< 60 sec)

1. Tu projettes la landing
2. Tu demandes un créateur dans la salle → tape son @
3. ~20 sec : on importe + floute son feed (Apify) ou affiche un placeholder
4. Page setup → il choisit son prix mensuel
5. Clic « Activer mon compte » → page créateur live
6. Tu projettes l'URL + QR code pour la salle
7. La salle scan → voit la grille floutée + bouton « Débloquer pour X€ » →
   Stripe Checkout (ou succès auto-démo)

## Statut

**MVP démo conférence — SFW uniquement.** À durcir avant prod :
- Auth créateur (actuellement n'importe qui peut prendre n'importe quel @)
- Stripe Connect (paiements directs au créateur, pas à toi)
- Webhook Stripe pour matcher l'abonnement à l'utilisateur
- Vraie DB (actuellement in-memory → perd les données au redémarrage)
- Modération + signalement
- KYC créateur (CGU, vérification d'âge si évolution adulte plus tard)
