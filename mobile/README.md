# Calo — App mobile (iOS / Android)

La coquille premium de Calo, construite avec **Expo (React Native) + TypeScript**.
Elle parle au **même cerveau Calo** que WhatsApp via l'API `/app/*` du backend
FastAPI (Railway). Un client peut donc utiliser l'app OU WhatsApp, sur le même
compte (clé = numéro de téléphone).

## Écrans
- **Login** — connexion par téléphone + code SMS (OTP)
- **Coach** — chat avec Calo (texte + photo), bulles, médias
- **Progrès** — calories du jour + courbe de poids
- **Apprendre** — micro-cours + sujets populaires
- **Profil** — infos, stats, lien WhatsApp, déconnexion
- **Paywall** — abonnements Plus 99€ / Elite 299€ / Pro 999€

## Prérequis
- Node.js 18+ et npm
- L'app **Expo Go** sur ton téléphone (pour tester sans build), ou Xcode (iOS) / Android Studio
- Un compte **Expo** (gratuit) pour les builds stores via EAS

## Démarrer en local (test immédiat)
```bash
cd mobile
npm install
npx expo start
```
Scanne le QR code avec **Expo Go** (iOS/Android) → l'app tourne sur ton téléphone
en quelques secondes, connectée au backend de prod.

## Configurer l'URL du backend
Par défaut : `https://coachwarrior-production.up.railway.app`
(voir `app.json` → `expo.extra.apiBaseUrl`). Modifie-la si besoin.

## Build pour les stores (quand prêt)
```bash
npm install -g eas-cli
eas login
eas build:configure
eas build --platform ios       # nécessite un compte Apple Developer (99$/an)
eas build --platform android   # Google Play (25$ une fois)
eas submit --platform ios
```

## Auth / OTP
- `POST /app/auth/start { phone }` envoie un code SMS (Twilio).
- En dev, si `CALO_TWILIO_SMS_FROM` n'est pas configuré, le code est **loggé
  côté serveur** (visible dans les logs Railway) pour pouvoir tester.
- `POST /app/auth/verify { phone, code }` renvoie un token (stocké dans
  SecureStore). Le token unifie l'identité app + WhatsApp.

## Structure
```
app/                 routes (expo-router)
  _layout.tsx        racine + AuthProvider + gating
  login.tsx          écran de connexion
  (tabs)/            navigation par onglets
    index.tsx        Coach (chat)
    progress.tsx     Progrès
    learn.tsx        Apprendre
    profile.tsx      Profil
  paywall.tsx        abonnements (modal)
src/
  api/client.ts      client typé de l'API /app/*
  store/auth.tsx     contexte auth (SecureStore)
  components/ui.tsx   primitives UI brandées
  theme/index.ts      couleurs / espacements Calo
```

## TODO produit (prochaines itérations)
- Vocal in/out dans l'app (enregistrement + lecture)
- Paiement in-app réel (RevenueCat recommandé pour App Store/Play)
- Push notifications (expo-notifications) pour les rappels Calo
- Onboarding profil guidé dans l'app
- Mode hors-ligne / cache des messages
