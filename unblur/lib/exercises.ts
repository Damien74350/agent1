// Bibliothèque exercices + machines + équipements — la référence

export type MuscleGroup = "Pectoraux" | "Dos" | "Épaules" | "Biceps" | "Triceps" | "Quadriceps" | "Ischios" | "Fessiers" | "Mollets" | "Abdos" | "Lombaires" | "Avant-bras" | "Trapèzes" | "Cardio" | "Mobilité";

export type Equipment = "Poids du corps" | "Haltères" | "Barre" | "Kettlebell" | "Câble" | "Machine" | "Élastique" | "Banc" | "Rack" | "TRX" | "Tapis" | "Vélo" | "Rameur";

export type ExerciseCategory = "Force" | "Hypertrophie" | "Cardio" | "Mobilité" | "Plyométrique" | "Powerlifting" | "Olympique" | "Calisthénie" | "Préparation physique";

export type Difficulty = "Débutant" | "Intermédiaire" | "Avancé" | "Expert";

export type Exercise = {
  id: string;
  name: string;
  alternativeNames?: string[];
  category: ExerciseCategory;
  primaryMuscles: MuscleGroup[];
  secondaryMuscles?: MuscleGroup[];
  equipment: Equipment[];
  difficulty: Difficulty;
  shortDescription: string;
  technique: string[];      // 4-6 cues techniques
  mistakes: string[];       // 3-5 erreurs courantes
  variations?: string[];    // noms de variantes
  recommendedSets?: string; // "3-5 séries de 5-8 reps"
  caloriesPerHour?: number; // pour cardio
  hasCreatorDemos: number;  // nb de créateurs qui ont une démo
  popularity: number;       // 0-100
  emoji: string;            // pour visuel
};

export const MUSCLE_GROUPS: MuscleGroup[] = [
  "Pectoraux", "Dos", "Épaules", "Biceps", "Triceps",
  "Quadriceps", "Ischios", "Fessiers", "Mollets",
  "Abdos", "Lombaires", "Avant-bras", "Trapèzes",
  "Cardio", "Mobilité",
];

export const EQUIPMENTS: Equipment[] = [
  "Poids du corps", "Haltères", "Barre", "Kettlebell", "Câble",
  "Machine", "Élastique", "Banc", "Rack", "TRX",
  "Tapis", "Vélo", "Rameur",
];

export const EXERCISE_CATEGORIES: ExerciseCategory[] = [
  "Force", "Hypertrophie", "Cardio", "Mobilité",
  "Plyométrique", "Powerlifting", "Olympique", "Calisthénie", "Préparation physique",
];

export const EXERCISES: Exercise[] = [
  // ─── PECTORAUX ───
  { id: "ex_bench_press", name: "Développé couché", alternativeNames: ["Bench press"],
    category: "Force", primaryMuscles: ["Pectoraux"], secondaryMuscles: ["Triceps", "Épaules"],
    equipment: ["Barre", "Banc", "Rack"], difficulty: "Intermédiaire",
    shortDescription: "Le roi des exercices de poussée pour le haut du corps.",
    technique: ["Omoplates serrées et plaquées au banc", "Pieds bien ancrés au sol", "Descente contrôlée vers le bas du sternum", "Touche poitrine sans rebond", "Poussée explosive en gardant les pieds vissés"],
    mistakes: ["Décoller les fesses du banc", "Cambrer excessivement le bas du dos", "Pousser avec les bras avant le sternum", "Coudes à 90° (risque épaule)"],
    variations: ["Incliné", "Décliné", "Avec haltères", "Prise serrée"],
    recommendedSets: "4 séries de 5-10 reps · 2-3 min repos",
    hasCreatorDemos: 8, popularity: 98, emoji: "💪" },

  { id: "ex_pushup", name: "Pompes", alternativeNames: ["Push-up"],
    category: "Calisthénie", primaryMuscles: ["Pectoraux"], secondaryMuscles: ["Triceps", "Épaules", "Abdos"],
    equipment: ["Poids du corps"], difficulty: "Débutant",
    shortDescription: "L'exercice complet de poussée, partout, sans matériel.",
    technique: ["Corps en planche stricte", "Mains légèrement plus larges que les épaules", "Descente coude à 45°", "Touche poitrine au sol", "Poussée en gardant le bassin neutre"],
    mistakes: ["Bassin cassé (creux ou pointu)", "Coudes ouverts à 90°", "Tête qui pend", "Demi-amplitude"],
    variations: ["Incliné", "Décliné", "Pike", "Diamant", "Archer", "Une main"],
    recommendedSets: "3-5 séries de 8-20 reps",
    hasCreatorDemos: 12, popularity: 95, emoji: "💪" },

  // ─── DOS ───
  { id: "ex_deadlift", name: "Soulevé de terre", alternativeNames: ["Deadlift"],
    category: "Powerlifting", primaryMuscles: ["Dos", "Fessiers", "Ischios"], secondaryMuscles: ["Trapèzes", "Avant-bras", "Lombaires"],
    equipment: ["Barre", "Rack"], difficulty: "Avancé",
    shortDescription: "Le mouvement le plus fonctionnel et le plus performant.",
    technique: ["Pieds largeur bassin, barre au-dessus du milieu du pied", "Tibias contre la barre", "Dos plat, scapulas au-dessus de la barre", "Poussée jambes d'abord, hanches montent ensemble", "Verrouillage hanches en haut, pas en arrière"],
    mistakes: ["Dos arrondi (le plus dangereux)", "Hanches qui montent trop vite (devient un good morning)", "Barre éloignée du tibia", "Hyperextension en haut"],
    variations: ["Sumo", "Roumain", "Trap bar", "Snatch grip", "Déficit"],
    recommendedSets: "3-5 séries de 1-5 reps · 3-5 min repos",
    hasCreatorDemos: 9, popularity: 92, emoji: "🏋️" },

  { id: "ex_pullup", name: "Tractions", alternativeNames: ["Pull-up"],
    category: "Calisthénie", primaryMuscles: ["Dos"], secondaryMuscles: ["Biceps", "Avant-bras"],
    equipment: ["Poids du corps", "Rack"], difficulty: "Intermédiaire",
    shortDescription: "Le test ultime du haut du corps en tirage vertical.",
    technique: ["Prise pronation, mains largeur épaules", "Engagement scapulaire avant tirage", "Coudes vers le bas et l'arrière", "Menton au-dessus de la barre", "Descente complète, bras tendus"],
    mistakes: ["Élan pour monter", "Demi-amplitude", "Coudes en avant", "Cou tendu vers la barre"],
    variations: ["Supination (chin-up)", "Wide grip", "Lestée", "Une main (assistée)", "L-sit"],
    recommendedSets: "4-5 séries de 3-12 reps",
    hasCreatorDemos: 7, popularity: 90, emoji: "🔥" },

  { id: "ex_row", name: "Rowing barre", alternativeNames: ["Barbell row", "Pendlay row"],
    category: "Hypertrophie", primaryMuscles: ["Dos"], secondaryMuscles: ["Biceps", "Trapèzes"],
    equipment: ["Barre"], difficulty: "Intermédiaire",
    shortDescription: "Le tirage horizontal qui construit l'épaisseur du dos.",
    technique: ["Hanches en charnière, dos plat parallèle au sol", "Genoux légèrement fléchis", "Prise pronation largeur épaules", "Tire vers le nombril ou bas du sternum", "Squeeze scapulas en haut"],
    mistakes: ["Dos arrondi", "Élan avec les jambes", "Tirage vers la poitrine (mauvaise mécanique)", "Coudes ouverts"],
    variations: ["Pendlay", "T-bar", "Avec haltères", "Inversé sur TRX"],
    recommendedSets: "4 séries de 6-10 reps",
    hasCreatorDemos: 6, popularity: 88, emoji: "🏋️" },

  // ─── ÉPAULES ───
  { id: "ex_ohp", name: "Développé militaire", alternativeNames: ["Overhead press", "OHP"],
    category: "Force", primaryMuscles: ["Épaules"], secondaryMuscles: ["Triceps", "Trapèzes", "Abdos"],
    equipment: ["Barre", "Rack"], difficulty: "Intermédiaire",
    shortDescription: "Le développé debout, base de la force des épaules.",
    technique: ["Pieds largeur bassin, barre sur l'avant des épaules", "Coudes légèrement en avant de la barre", "Gainage abdo + fessiers verrouillés", "Pousse droit vers le haut", "Tête passe sous la barre en fin de course"],
    mistakes: ["Cambrer comme un développé incliné", "Coudes ouverts à 90°", "Barre trop loin du corps", "Genoux qui aident"],
    variations: ["Push press", "Strict", "Avec haltères", "Assis"],
    recommendedSets: "4 séries de 5-8 reps",
    hasCreatorDemos: 5, popularity: 82, emoji: "🏋️" },

  { id: "ex_lateral_raise", name: "Élévations latérales", alternativeNames: ["Lateral raise"],
    category: "Hypertrophie", primaryMuscles: ["Épaules"],
    equipment: ["Haltères", "Câble"], difficulty: "Débutant",
    shortDescription: "L'isolation pour épaules larges.",
    technique: ["Buste droit, légère inclinaison avant", "Léger pli au coude maintenu", "Monte les coudes (pas les poignets)", "Stop au niveau des épaules", "Descente contrôlée"],
    mistakes: ["Trop lourd → triche avec élan", "Monter trop haut (trapèzes prennent le relais)", "Poignets plus hauts que les coudes"],
    recommendedSets: "4 séries de 12-20 reps",
    hasCreatorDemos: 4, popularity: 86, emoji: "💪" },

  // ─── BRAS ───
  { id: "ex_curl", name: "Curl biceps", alternativeNames: ["Bicep curl"],
    category: "Hypertrophie", primaryMuscles: ["Biceps"], secondaryMuscles: ["Avant-bras"],
    equipment: ["Haltères", "Barre", "Câble"], difficulty: "Débutant",
    shortDescription: "L'exercice signature pour les biceps.",
    technique: ["Coudes collés au tronc", "Supination en montant", "Stop avant que les coudes avancent", "Descente lente sur 2-3 sec"],
    mistakes: ["Élan avec le dos", "Coudes qui partent en avant", "Demi-amplitude"],
    variations: ["Marteau", "Incliné", "Concentré", "21s"],
    recommendedSets: "3-4 séries de 8-15 reps",
    hasCreatorDemos: 3, popularity: 91, emoji: "💪" },

  { id: "ex_dips", name: "Dips", alternativeNames: ["Triceps dips"],
    category: "Calisthénie", primaryMuscles: ["Triceps", "Pectoraux"], secondaryMuscles: ["Épaules"],
    equipment: ["Poids du corps"], difficulty: "Intermédiaire",
    shortDescription: "Le squat du haut du corps.",
    technique: ["Buste droit pour triceps, penché pour pecs", "Descente contrôlée jusqu'à coudes à 90°", "Coudes vers l'arrière (pas écartés)", "Poussée explosive vers le haut"],
    mistakes: ["Descendre trop bas (épaules)", "Hauts du dos arrondis", "Vitesse de yo-yo"],
    variations: ["Lestés", "Sur banc", "Anneaux", "Russian dips"],
    recommendedSets: "4 séries de 6-12 reps",
    hasCreatorDemos: 5, popularity: 84, emoji: "🔥" },

  // ─── JAMBES ───
  { id: "ex_squat", name: "Squat", alternativeNames: ["Back squat"],
    category: "Powerlifting", primaryMuscles: ["Quadriceps", "Fessiers"], secondaryMuscles: ["Ischios", "Lombaires", "Abdos"],
    equipment: ["Barre", "Rack"], difficulty: "Intermédiaire",
    shortDescription: "Le mouvement roi pour les jambes et la force globale.",
    technique: ["Barre haute (trap) ou basse (omoplates)", "Pieds largeur épaules, pointes 15-30° vers l'extérieur", "Hanches reculent légèrement avant les genoux", "Descente jusqu'à hanches sous les genoux", "Poussée bien équilibrée sur tout le pied"],
    mistakes: ["Genoux qui rentrent en valgus", "Talons qui décollent", "Dos arrondi en bas", "Pas d'amplitude complète"],
    variations: ["Front squat", "Goblet", "Bulgarian", "Box squat", "Pause"],
    recommendedSets: "4-5 séries de 5-8 reps · 3 min repos",
    hasCreatorDemos: 10, popularity: 97, emoji: "🦵" },

  { id: "ex_lunge", name: "Fentes", alternativeNames: ["Lunges"],
    category: "Hypertrophie", primaryMuscles: ["Quadriceps", "Fessiers"], secondaryMuscles: ["Ischios", "Abdos"],
    equipment: ["Poids du corps", "Haltères", "Barre"], difficulty: "Débutant",
    shortDescription: "Unilatéral et fonctionnel, corrige les déséquilibres.",
    technique: ["Grand pas en avant", "Genou avant aligné avec la cheville", "Descente verticale, genou arrière effleure le sol", "Poussée jambe avant pour remonter", "Buste droit"],
    mistakes: ["Genou qui dépasse la pointe du pied", "Buste qui penche en avant", "Pas trop petit ou trop grand"],
    variations: ["Marchées", "Reverse", "Latérales", "Bulgarian split squat"],
    recommendedSets: "3-4 séries de 10-12 par côté",
    hasCreatorDemos: 4, popularity: 87, emoji: "🦵" },

  { id: "ex_hip_thrust", name: "Hip thrust", alternativeNames: ["Pont fessier lesté"],
    category: "Hypertrophie", primaryMuscles: ["Fessiers"], secondaryMuscles: ["Ischios", "Abdos"],
    equipment: ["Barre", "Banc"], difficulty: "Intermédiaire",
    shortDescription: "Le meilleur exercice pour les fessiers.",
    technique: ["Hauts du dos sur le banc", "Pieds bien plantés, tibias verticaux en haut", "Pousse en serrant les fessiers", "Pause 1 sec en haut", "Hanches alignées avec les genoux"],
    mistakes: ["Hyperextension lombaire", "Pieds trop loin (sollicite les ischios)", "Tête qui se relève"],
    variations: ["Une jambe", "B-stance", "Pause", "Avec élastique"],
    recommendedSets: "4 séries de 8-12 reps",
    hasCreatorDemos: 6, popularity: 89, emoji: "🍑" },

  { id: "ex_rdl", name: "Soulevé de terre roumain", alternativeNames: ["RDL", "Romanian deadlift"],
    category: "Hypertrophie", primaryMuscles: ["Ischios", "Fessiers"], secondaryMuscles: ["Dos", "Lombaires"],
    equipment: ["Barre", "Haltères"], difficulty: "Intermédiaire",
    shortDescription: "Hinge pur, étire et renforce la chaîne postérieure.",
    technique: ["Jambes presque tendues (léger pli)", "Hanches reculent, barre glisse contre les cuisses", "Descente jusqu'à étirement des ischios", "Dos plat tout le long", "Pousse les hanches en avant pour remonter"],
    mistakes: ["Plier les genoux (devient un soulevé)", "Dos arrondi", "Barre qui s'éloigne des jambes"],
    recommendedSets: "4 séries de 8-10 reps",
    hasCreatorDemos: 5, popularity: 85, emoji: "🦵" },

  // ─── ABDOS ───
  { id: "ex_plank", name: "Planche", alternativeNames: ["Plank"],
    category: "Calisthénie", primaryMuscles: ["Abdos"], secondaryMuscles: ["Lombaires", "Épaules"],
    equipment: ["Poids du corps", "Tapis"], difficulty: "Débutant",
    shortDescription: "L'iso parfait pour le gainage profond.",
    technique: ["Coudes sous les épaules", "Corps en ligne parfaite tête-talons", "Fessiers + abdos contractés", "Respiration calme", "Regard vers le bas"],
    mistakes: ["Bassin cassé (creux ou en pointe)", "Tête qui pend", "Trop long sans qualité"],
    variations: ["Latérale", "RKC", "Avec mouvements épaule", "Sur swiss ball"],
    recommendedSets: "3 séries de 30-60 sec",
    hasCreatorDemos: 8, popularity: 93, emoji: "🛡️" },

  { id: "ex_hanging_leg_raise", name: "Relevé de jambes suspendu", alternativeNames: ["Hanging leg raise"],
    category: "Calisthénie", primaryMuscles: ["Abdos"], secondaryMuscles: ["Avant-bras"],
    equipment: ["Poids du corps"], difficulty: "Avancé",
    shortDescription: "Le top pour les abdos complets, contrôle ultime.",
    technique: ["Suspendu, scapulas activées", "Monte les genoux ou jambes tendues en contrôlé", "Légère rétroversion du bassin en haut", "Descente lente sans balancier"],
    mistakes: ["Élan avec le bassin", "Bras qui plient", "Tirer avec les psoas en cambrant"],
    variations: ["Genoux pliés", "Toes-to-bar", "L-sit", "Wipers"],
    recommendedSets: "3-4 séries de 6-12 reps",
    hasCreatorDemos: 3, popularity: 78, emoji: "🛡️" },

  // ─── CARDIO ───
  { id: "ex_burpee", name: "Burpees", alternativeNames: [],
    category: "Plyométrique", primaryMuscles: ["Cardio"], secondaryMuscles: ["Pectoraux", "Quadriceps", "Abdos"],
    equipment: ["Poids du corps"], difficulty: "Intermédiaire",
    shortDescription: "Le full-body intensité maximale.",
    technique: ["Squat, mains au sol", "Saut arrière en planche", "Pompe (optionnelle)", "Saut avant ramène les pieds", "Saut explosif vertical"],
    mistakes: ["Sauter sans poser les pieds en planche", "Lombaires creuses en planche", "Trop vite, on perd la technique"],
    variations: ["Sans pompe", "Avec push press", "Sur box", "Half"],
    recommendedSets: "5 rounds de 10 reps · ou 3 min AMRAP",
    caloriesPerHour: 720,
    hasCreatorDemos: 6, popularity: 80, emoji: "🔥" },

  { id: "ex_rowing", name: "Rameur", alternativeNames: ["Rower", "Concept2"],
    category: "Cardio", primaryMuscles: ["Cardio", "Dos"], secondaryMuscles: ["Quadriceps", "Fessiers", "Biceps"],
    equipment: ["Rameur"], difficulty: "Débutant",
    shortDescription: "Le cardio le plus complet, 85% des muscles activés.",
    technique: ["Pousse jambes d'abord (60%)", "Buste se penche en arrière (20%)", "Tire avec les bras en dernier (20%)", "Retour inverse : bras, buste, jambes", "Cadence 24-28 spm en endurance"],
    mistakes: ["Tirer avec les bras d'abord", "Dos arrondi", "Coups trop courts ou trop longs"],
    recommendedSets: "Intervals 5x500m · ou 2k all-out",
    caloriesPerHour: 600,
    hasCreatorDemos: 3, popularity: 75, emoji: "🚣" },

  { id: "ex_kb_swing", name: "Kettlebell swing",
    category: "Plyométrique", primaryMuscles: ["Fessiers", "Ischios", "Cardio"], secondaryMuscles: ["Dos", "Abdos", "Épaules"],
    equipment: ["Kettlebell"], difficulty: "Intermédiaire",
    shortDescription: "Le mouvement balistique russe — puissance + cardio.",
    technique: ["Pieds largeur épaules, genoux légèrement fléchis", "Hinge hanches, kettlebell entre les jambes", "Pousse explosivement les hanches en avant", "La kettlebell flotte par projection (pas par les bras)", "Hauteur d'épaule (russe) ou au-dessus (américain)"],
    mistakes: ["Squat (au lieu de hinge)", "Tirer avec les bras", "Hyperextension en haut"],
    variations: ["Russe", "Américain", "Une main", "Hand-to-hand"],
    recommendedSets: "5 séries de 20 reps · EMOM 10 min de 15 reps",
    hasCreatorDemos: 4, popularity: 82, emoji: "🔥" },

  // ─── MOBILITÉ ───
  { id: "ex_cossack", name: "Cossack squat", alternativeNames: ["Squat cosaque"],
    category: "Mobilité", primaryMuscles: ["Quadriceps", "Adducteurs" as any, "Mobilité"], secondaryMuscles: ["Fessiers", "Ischios"],
    equipment: ["Poids du corps", "Kettlebell"], difficulty: "Intermédiaire",
    shortDescription: "Mobilité hanches + force unilatérale.",
    technique: ["Position large", "Descends sur un côté en gardant l'autre jambe tendue", "Pointe du pied opposé vers le haut", "Talon de la jambe pliée au sol", "Transition lente d'un côté à l'autre"],
    mistakes: ["Talon qui décolle", "Buste qui s'effondre vers l'avant"],
    recommendedSets: "3 séries de 8-10 par côté",
    hasCreatorDemos: 2, popularity: 60, emoji: "🧘" },

  { id: "ex_jefferson", name: "Jefferson curl",
    category: "Mobilité", primaryMuscles: ["Lombaires", "Ischios", "Mobilité"],
    equipment: ["Haltères", "Barre"], difficulty: "Avancé",
    shortDescription: "Renforce et étire la chaîne postérieure en flexion.",
    technique: ["Charge LÉGÈRE (5-10 kg max au début)", "Descente vertèbre par vertèbre", "Genoux tendus", "Touche les pieds avec la charge", "Remontée en déroulant le dos"],
    mistakes: ["Trop lourd (très dangereux)", "Plier les genoux", "Vitesse"],
    recommendedSets: "3 séries de 8 reps · CHARGE LÉGÈRE",
    hasCreatorDemos: 2, popularity: 45, emoji: "🧘" },

  // ─── MACHINES SPÉCIFIQUES ───
  { id: "ex_lat_pulldown", name: "Tirage vertical", alternativeNames: ["Lat pulldown"],
    category: "Hypertrophie", primaryMuscles: ["Dos"], secondaryMuscles: ["Biceps"],
    equipment: ["Machine", "Câble"], difficulty: "Débutant",
    shortDescription: "Alternative aux tractions pour débuter le tirage vertical.",
    technique: ["Cuisses bloquées sous le coussin", "Léger angle du buste en arrière", "Tire vers le haut de la poitrine", "Coudes en arrière, scapulas qui descendent", "Contrôle de la remontée"],
    mistakes: ["Tirer derrière la nuque (épaules)", "Buste qui balance", "Demi-amplitude"],
    variations: ["Prise serrée", "Supination", "Une main", "Câble"],
    recommendedSets: "4 séries de 10-15 reps",
    hasCreatorDemos: 3, popularity: 84, emoji: "🏋️" },

  { id: "ex_leg_press", name: "Presse à cuisses", alternativeNames: ["Leg press"],
    category: "Hypertrophie", primaryMuscles: ["Quadriceps", "Fessiers"], secondaryMuscles: ["Ischios"],
    equipment: ["Machine"], difficulty: "Débutant",
    shortDescription: "Charges lourdes pour quadriceps, sans contrainte de stabilité.",
    technique: ["Pieds largeur épaules au milieu de la plateforme", "Bas du dos collé au siège (CRUCIAL)", "Descente jusqu'à 90° au genou", "Pousse à fond, ne verrouille pas complètement en haut", "Respire bien"],
    mistakes: ["Décoller les fesses (lombaires cassées)", "Descendre trop bas (sécurité)", "Verrouillage à fond (genoux)"],
    variations: ["Pieds hauts (fessiers/ischios)", "Pieds bas (quads)", "Une jambe"],
    recommendedSets: "4 séries de 10-15 reps",
    hasCreatorDemos: 2, popularity: 81, emoji: "🦵" },

  { id: "ex_cable_fly", name: "Écarté à la poulie", alternativeNames: ["Cable fly", "Cable crossover"],
    category: "Hypertrophie", primaryMuscles: ["Pectoraux"],
    equipment: ["Câble"], difficulty: "Débutant",
    shortDescription: "Isolation des pectoraux avec tension constante.",
    technique: ["Léger pli au coude maintenu", "Trajectoire d'arc descendant", "Croise les mains devant", "Étirement contrôlé en haut", "Pousse comme pour un câlin"],
    mistakes: ["Plier les coudes en cours de route (devient un développé)", "Aller trop loin en arrière (épaules)", "Hausser les épaules"],
    variations: ["Haut", "Milieu", "Bas", "Allongé"],
    recommendedSets: "3-4 séries de 12-15 reps",
    hasCreatorDemos: 2, popularity: 77, emoji: "💪" },

  { id: "ex_treadmill_hiit", name: "HIIT tapis de course", alternativeNames: ["Sprint intervals"],
    category: "Cardio", primaryMuscles: ["Cardio"], secondaryMuscles: ["Quadriceps", "Fessiers"],
    equipment: ["Tapis"], difficulty: "Intermédiaire",
    shortDescription: "Intervalles à haute intensité, brûle un max.",
    technique: ["Échauffement 5 min facile", "Sprint 30 sec à 90% (16-18 km/h)", "Récup marche 60-90 sec", "Répète 8-12 fois", "Retour au calme 5 min"],
    mistakes: ["Sauter de la bande au lieu de ralentir progressivement", "Mauvaise posture en sprint"],
    recommendedSets: "8-12 intervalles · 25-30 min total",
    caloriesPerHour: 800,
    hasCreatorDemos: 3, popularity: 79, emoji: "🏃" },
];

// Helpers
export function findExercise(id: string) {
  return EXERCISES.find(e => e.id === id);
}

export function exercisesByMuscle(muscle: MuscleGroup) {
  return EXERCISES.filter(e => e.primaryMuscles.includes(muscle) || e.secondaryMuscles?.includes(muscle));
}

export function exercisesByEquipment(eq: Equipment) {
  return EXERCISES.filter(e => e.equipment.includes(eq));
}

export function exercisesByCategory(cat: ExerciseCategory) {
  return EXERCISES.filter(e => e.category === cat);
}
