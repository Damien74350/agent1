import type { Creator, Content, SubscriberStat, PayoutEntry, Category } from "./types";

export const ALL_CATEGORIES: Category[] = [
  "Yoga", "HIIT", "Calisthenics", "Running", "Strength", "Pilates",
  "Boxing", "Crossfit", "Mobility", "Nutrition", "Cycling", "Climbing",
];

// ────────── CREATORS — pseudo-réalistes ──────────

export const CREATORS: Creator[] = [
  {
    id: "c_louise", handle: "@louise.training", name: "Louise Carmin",
    avatar: "LC", bio: "Étudiante en kiné · J'apprends en montrant, je montre ce que j'apprends.",
    tagline: "Calisthenics & mobilité pour débutants",
    city: "Lyon", country: "France", countryFlag: "🇫🇷",
    category: "Calisthenics", subCategories: ["Calisthenics", "Mobility"],
    tier: "Trusted", monthlyPriceEUR: 9.90, yearlyPriceEUR: 89,
    subscribers: 2_840, freeFollowers: 18_400, monthlyEarningsEUR: 22_513, totalEarningsEUR: 184_220,
    rating: 4.92, isLive: true, liveTitle: "Mobilité matin 25 min — épaules & hanches", liveViewers: 312,
    joinedAt: "2025-03-14", certifications: ["BTS APS", "L3 STAPS"],
    banner: "linear-gradient(135deg, #ff2e7e, #ffb347)",
    story: "J'ai démarré sur Insta il y a 2 ans en partageant mes propres entraînements et mes notes de cours. J'ai vite compris que ce que les gens cherchent vraiment, c'est de la régularité accessible — pas des routines parfaites. Mon abonnement à 9,90 €/mois donne accès à mes 4 séances/semaine en direct + tout mon catalogue de programmes débutant.",
  },
  {
    id: "c_marko", handle: "@marko.run", name: "Marko Voronov",
    avatar: "MV", bio: "Ultra-trailer, coach running depuis 8 ans. Trans-Alpes 2024 #3.",
    tagline: "Préparation marathon & ultratrail",
    city: "Chamonix", country: "France", countryFlag: "🇫🇷",
    category: "Running", subCategories: ["Running"],
    tier: "Pro", monthlyPriceEUR: 19.90, yearlyPriceEUR: 179,
    subscribers: 5_620, freeFollowers: 42_100, monthlyEarningsEUR: 89_410, totalEarningsEUR: 720_840,
    rating: 4.97, isLive: false,
    joinedAt: "2024-09-02", certifications: ["BPJEPS Triathlon", "FFA niveau 2"],
    banner: "linear-gradient(135deg, #5eead4, #5b9eff)",
    story: "Mes programmes ont fait passer 480+ coureurs sous la barre des 4h marathon. Si tu veux progresser sans te blesser, suis mon plan annuel.",
  },
  {
    id: "c_amira", handle: "@amira.yoga", name: "Amira Bouzid",
    avatar: "AB", bio: "Vinyasa & Yin. Plus de 1200 séances en ligne. Calme + profondeur.",
    tagline: "Yoga pour le sport et la récup",
    city: "Marseille", country: "France", countryFlag: "🇫🇷",
    category: "Yoga", subCategories: ["Yoga", "Mobility"],
    tier: "Elite", monthlyPriceEUR: 12.50, yearlyPriceEUR: 109,
    subscribers: 12_840, freeFollowers: 84_200, monthlyEarningsEUR: 160_500, totalEarningsEUR: 1_840_220,
    rating: 4.95, isLive: false,
    joinedAt: "2024-06-21", certifications: ["RYT 500", "Yoga Alliance"],
    banner: "linear-gradient(135deg, #a78bfa, #ff2e7e)",
    story: "Je crée des séances que les sportifs intègrent à leur semaine pour ne pas se blesser et durer.",
  },
  {
    id: "c_jules", handle: "@jules.fit", name: "Jules Manceau",
    avatar: "JM", bio: "Calisthenics & gymnastique. Champion régional 2023.",
    tagline: "Maîtrise ton poids de corps",
    city: "Bordeaux", country: "France", countryFlag: "🇫🇷",
    category: "Calisthenics", subCategories: ["Calisthenics", "Strength"],
    tier: "Rising", monthlyPriceEUR: 7.90,
    subscribers: 980, freeFollowers: 9_400, monthlyEarningsEUR: 6_192, totalEarningsEUR: 32_140,
    rating: 4.86, isLive: false,
    joinedAt: "2025-08-11", certifications: ["BPJEPS AGFF"],
    banner: "linear-gradient(135deg, #5eead4, #ffb347)",
    story: "Le poids de corps, c'est le meilleur outil. Aucun matériel requis. Programme progression 12 semaines vers le muscle-up.",
  },
  {
    id: "c_naima", handle: "@naima.box", name: "Naima Reggad",
    avatar: "NR", bio: "Ancienne boxeuse pro, coach mental & technique.",
    tagline: "Boxe technique + cardio",
    city: "Paris", country: "France", countryFlag: "🇫🇷",
    category: "Boxing", subCategories: ["Boxing", "HIIT"],
    tier: "Pro", monthlyPriceEUR: 14.90, yearlyPriceEUR: 129,
    subscribers: 3_120, freeFollowers: 28_400, monthlyEarningsEUR: 46_488, totalEarningsEUR: 380_220,
    rating: 4.91, isLive: true, liveTitle: "Round 1 — boxing fundamentals", liveViewers: 184,
    joinedAt: "2024-12-04", certifications: ["FFB instructeur", "BPJEPS"],
    banner: "linear-gradient(135deg, #ff2e7e, #a78bfa)",
    story: "J'enseigne ce que j'ai mis 20 ans à comprendre dans la boxe. La technique avant la puissance.",
  },
  {
    id: "c_theo", handle: "@theo.lifts", name: "Théo Rivière",
    avatar: "TR", bio: "Powerlifter compétiteur, programme strength.",
    tagline: "Force & hypertrophie sérieuse",
    city: "Toulouse", country: "France", countryFlag: "🇫🇷",
    category: "Strength", subCategories: ["Strength"],
    tier: "Trusted", monthlyPriceEUR: 12.90,
    subscribers: 1_840, freeFollowers: 14_200, monthlyEarningsEUR: 23_716, totalEarningsEUR: 168_400,
    rating: 4.88, isLive: false,
    joinedAt: "2025-01-22", certifications: ["IPF coach"],
    banner: "linear-gradient(135deg, #ffb347, #ff2e7e)",
    story: "Programme 5/3/1 adapté, conseils technique en vidéo, review form check chaque semaine.",
  },
  {
    id: "c_emma", handle: "@emma.pilates", name: "Emma Lange",
    avatar: "EL", bio: "Pilates Reformer & santé du dos.",
    tagline: "Posture & core force",
    city: "Strasbourg", country: "France", countryFlag: "🇫🇷",
    category: "Pilates", subCategories: ["Pilates", "Mobility"],
    tier: "Trusted", monthlyPriceEUR: 11.90, yearlyPriceEUR: 99,
    subscribers: 2_140, freeFollowers: 16_800, monthlyEarningsEUR: 25_466, totalEarningsEUR: 184_400,
    rating: 4.93, isLive: false,
    joinedAt: "2025-02-08", certifications: ["Stott Pilates", "Reformer Pro"],
    banner: "linear-gradient(135deg, #a78bfa, #5eead4)",
    story: "J'ai sauvé mon dos avec le Pilates après une hernie. Je partage la méthode qui m'a guérie.",
  },
  {
    id: "c_yuki", handle: "@yuki.cyclist", name: "Yuki Tanaka",
    avatar: "YT", bio: "Cycliste route + gravel. Ex-équipe pro Asie.",
    tagline: "Cycling structure + nutrition",
    city: "Tokyo", country: "Japon", countryFlag: "🇯🇵",
    category: "Cycling", subCategories: ["Cycling", "Nutrition"],
    tier: "Pro", monthlyPriceEUR: 16.90,
    subscribers: 4_240, freeFollowers: 38_400, monthlyEarningsEUR: 71_656, totalEarningsEUR: 480_120,
    rating: 4.95, isLive: false,
    joinedAt: "2024-11-12", certifications: ["UCI level 2"],
    banner: "linear-gradient(135deg, #5b9eff, #5eead4)",
    story: "20 semaines de prep pour ton premier Granfondo. Watts, FTP, intervalles, recovery.",
  },
  {
    id: "c_inès", handle: "@ines.hiit", name: "Inès Laurent",
    avatar: "IL", bio: "HIIT efficace, sans équipement.",
    tagline: "20 min suffisent. Vraiment.",
    city: "Lille", country: "France", countryFlag: "🇫🇷",
    category: "HIIT", subCategories: ["HIIT"],
    tier: "Rising", monthlyPriceEUR: 5.90,
    subscribers: 1_620, freeFollowers: 8_900, monthlyEarningsEUR: 7_645, totalEarningsEUR: 38_420,
    rating: 4.84, isLive: false,
    joinedAt: "2025-09-15", certifications: [],
    banner: "linear-gradient(135deg, #ffb347, #ff2e7e)",
    story: "Mère solo, je n'ai que 20 min/jour. Je partage ce qui marche vraiment dans cette contrainte.",
  },
  {
    id: "c_adam", handle: "@adam.cross", name: "Adam Belmondo",
    avatar: "AB", bio: "CrossFit L2, programmation WOD pour gym.",
    tagline: "Conditioning haut niveau",
    city: "Nice", country: "France", countryFlag: "🇫🇷",
    category: "Crossfit", subCategories: ["Crossfit", "Strength"],
    tier: "Trusted", monthlyPriceEUR: 13.90,
    subscribers: 1_980, freeFollowers: 12_600, monthlyEarningsEUR: 27_522, totalEarningsEUR: 198_400,
    rating: 4.89, isLive: false,
    joinedAt: "2024-10-30", certifications: ["CrossFit L2"],
    banner: "linear-gradient(135deg, #5eead4, #a78bfa)",
    story: "Programmation 4 jours/semaine. WODs adaptables à tout box, scaling complet.",
  },
  {
    id: "c_chloé", handle: "@chloe.climb", name: "Chloé Demarc",
    avatar: "CD", bio: "Grimpeuse bloc + voie. Coaching mental.",
    tagline: "Le climbing pour grimper plus haut",
    city: "Grenoble", country: "France", countryFlag: "🇫🇷",
    category: "Climbing", subCategories: ["Climbing", "Strength"],
    tier: "Rising", monthlyPriceEUR: 8.90,
    subscribers: 720, freeFollowers: 6_400, monthlyEarningsEUR: 6_408, totalEarningsEUR: 22_140,
    rating: 4.97, isLive: false,
    joinedAt: "2025-07-04", certifications: ["FFME"],
    banner: "linear-gradient(135deg, #a78bfa, #ffb347)",
    story: "Du 6a au 7b en 12 mois — méthode, doigts, mental, projection.",
  },
  {
    id: "c_karim", handle: "@karim.warrior", name: "Karim Bensalem",
    avatar: "KB", bio: "Coach boxe & combat, 1500+ séances. Légende WARfit.",
    tagline: "Boxe + mental warrior",
    city: "Casablanca", country: "Maroc", countryFlag: "🇲🇦",
    category: "Boxing", subCategories: ["Boxing", "HIIT"],
    tier: "Elite", monthlyPriceEUR: 19.90, yearlyPriceEUR: 179,
    subscribers: 8_420, freeFollowers: 64_800, monthlyEarningsEUR: 167_558, totalEarningsEUR: 1_820_400,
    rating: 4.96, isLive: false,
    joinedAt: "2024-04-18", certifications: ["WBF", "BPJEPS"],
    banner: "linear-gradient(135deg, #ff2e7e, #ffb347)",
    story: "Je vais te montrer pourquoi la boxe change ta vie. Programme 16 semaines + masterclass mentale.",
  },
];

// Featured creators for the landing
export const FEATURED_CREATORS = CREATORS.slice(0, 4);
export const TRENDING_CREATORS = [CREATORS[2], CREATORS[0], CREATORS[11], CREATORS[1]];
export const RISING_CREATORS = CREATORS.filter(c => c.tier === "Rising");
export const LIVE_NOW = CREATORS.filter(c => c.isLive);

// ────────── ME — l'utilisateur demo, à la fois créateur ET abonné ──────────

export const ME = CREATORS[0]; // Louise — moi en tant que créatrice

// Mes abonnements (en tant que subscriber)
export const MY_SUBSCRIPTIONS: SubscriberStat[] = [
  { creatorId: "c_amira", subscribedAt: "2025-08-12", monthlyPrice: 12.50, totalPaid: 137.50, contentWatched: 42, lastViewed: new Date(Date.now() - 2 * 3600000).toISOString() },
  { creatorId: "c_marko", subscribedAt: "2025-11-04", monthlyPrice: 19.90, totalPaid: 159.20, contentWatched: 18, lastViewed: new Date(Date.now() - 24 * 3600000).toISOString() },
  { creatorId: "c_naima", subscribedAt: "2026-01-22", monthlyPrice: 14.90, totalPaid: 74.50, contentWatched: 24, lastViewed: new Date(Date.now() - 5 * 86400000).toISOString() },
];

// ────────── CONTENU ──────────

const TITLES_BY_CATEGORY: Record<string, string[]> = {
  Yoga: ["Vinyasa flow 30 min", "Yin matin pour le dos", "Mobilité hanches", "Séance restauratrice"],
  HIIT: ["Tabata 20 min total", "AMRAP 15 min sans matériel", "EMOM full body"],
  Calisthenics: ["Progression pull-up", "Push routine débutant", "Handstand 8 semaines", "Core dur"],
  Running: ["Sortie fractionnée 8x400", "Endurance fond 1h30", "Récup active jambes lourdes"],
  Strength: ["Squat 5x5 — focus technique", "Deadlift form check live", "Bench progression 12 sem"],
  Pilates: ["Reformer débutant 45 min", "Core posture 30 min", "Hernie discale rebuild"],
  Boxing: ["Round 1 jab cross", "Footwork drills", "Sparring vidéo analyse"],
  Crossfit: ["WOD Murph scaled", "Olympic clean form", "Conditioning 12 min"],
  Mobility: ["Routine soir 15 min", "Décompression dos", "Préparation course matin"],
  Nutrition: ["Plan macros marathon", "Nutrition pré-séance", "Récup post-effort"],
  Cycling: ["Intervals Sweet Spot", "Sortie ville 1h", "Granfondo prep semaine"],
  Climbing: ["Doigts crimping safe", "Voie 7a projection", "Bloc dynamique"],
};

export const CONTENTS: Content[] = CREATORS.flatMap((c, ci) =>
  [0, 1, 2].map(i => {
    const titles = TITLES_BY_CATEGORY[c.category] ?? ["Séance"];
    return {
      id: `co_${c.id}_${i}`,
      creatorId: c.id,
      type: (["video", "video", "program", "live"] as const)[i % 4],
      title: titles[i % titles.length],
      description: "Une séance bien construite par " + c.name + ". Découverte gratuite : 1 minute, le reste pour les abonnés.",
      durationMin: [22, 45, 30, 60][i % 4],
      publishedAt: new Date(Date.now() - (ci * 3 + i) * 86400000).toISOString(),
      thumbnail: c.banner,
      thumbnailEmoji: ["🔥", "💪", "🎯", "⚡"][i % 4],
      views: Math.round(c.subscribers * (0.4 + Math.random() * 0.6) / (i + 1)),
      likes: Math.round(c.subscribers * 0.3 / (i + 1)),
      comments: Math.round(c.subscribers * 0.05 / (i + 1)),
      isPremium: i % 4 !== 0,         // 1 sur 4 en gratuit
      category: c.category,
      difficulty: (["Débutant", "Intermédiaire", "Avancé"] as const)[i % 3],
    };
  })
);

// Mes propres contenus (en tant que créatrice Louise)
export const MY_CONTENTS = CONTENTS.filter(c => c.creatorId === ME.id);

// Pour le feed de l'abonné — contenus des créateurs auxquels MOI je suis abonnée
export const MY_FEED = CONTENTS
  .filter(c => MY_SUBSCRIPTIONS.some(s => s.creatorId === c.creatorId))
  .sort((a, b) => new Date(b.publishedAt).getTime() - new Date(a.publishedAt).getTime());

// ────────── PAYOUTS — Louise gagne ──────────

export const MY_PAYOUTS: PayoutEntry[] = [
  { id: "p_1", periodLabel: "Juin 2026 (en cours)", grossEUR: 22_513, platformFeeEUR: 4_502.60, netEUR: 18_010.40, status: "pending",   payoutMethod: "stripe" },
  { id: "p_2", periodLabel: "Mai 2026",              grossEUR: 21_140, platformFeeEUR: 4_228,    netEUR: 16_912,    status: "paid",      payoutMethod: "stripe" },
  { id: "p_3", periodLabel: "Avril 2026",            grossEUR: 19_880, platformFeeEUR: 3_976,    netEUR: 15_904,    status: "paid",      payoutMethod: "stripe" },
  { id: "p_4", periodLabel: "Mars 2026",             grossEUR: 18_220, platformFeeEUR: 3_644,    netEUR: 14_576,    status: "paid",      payoutMethod: "stripe" },
];

// ────────── HELPERS ──────────

export function findCreator(id: string): Creator | undefined { return CREATORS.find(c => c.id === id); }
export function findContent(id: string): Content | undefined { return CONTENTS.find(c => c.id === id); }
export function contentsForCreator(creatorId: string): Content[] { return CONTENTS.filter(c => c.creatorId === creatorId); }
export function creatorsByCategory(cat: Category): Creator[] { return CREATORS.filter(c => c.category === cat || c.subCategories.includes(cat)); }

export function platformTotals() {
  const totalCreators = CREATORS.length;
  const totalSubs = CREATORS.reduce((s, c) => s + c.subscribers, 0);
  const totalGMV = CREATORS.reduce((s, c) => s + c.monthlyEarningsEUR, 0);
  const platformRevenue = totalGMV * 0.20;
  const creatorPayout = totalGMV * 0.80;
  return { totalCreators, totalSubs, totalGMV, platformRevenue, creatorPayout };
}
