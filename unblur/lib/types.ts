export type Category = "Yoga" | "HIIT" | "Calisthenics" | "Running" | "Strength" | "Pilates" | "Boxing" | "Crossfit" | "Mobility" | "Nutrition" | "Cycling" | "Climbing";

export type CreatorTier = "Rising" | "Trusted" | "Pro" | "Elite";

export type Creator = {
  id: string;
  handle: string;        // @louise.training
  name: string;
  avatar: string;        // initials
  bio: string;
  tagline: string;
  city: string;
  country: string;
  countryFlag: string;
  category: Category;
  subCategories: Category[];
  tier: CreatorTier;
  monthlyPriceEUR: number;     // creator-set price
  yearlyPriceEUR?: number;     // optional discounted
  subscribers: number;
  freeFollowers: number;
  monthlyEarningsEUR: number;
  totalEarningsEUR: number;
  rating: number;        // 0-5
  isLive: boolean;
  liveTitle?: string;
  liveViewers?: number;
  joinedAt: string;
  certifications: string[];
  banner: string;        // gradient class or color
  story: string;         // longer bio
};

export type ContentType = "video" | "live" | "program" | "post" | "course";

export type Content = {
  id: string;
  creatorId: string;
  type: ContentType;
  title: string;
  description: string;
  durationMin?: number;
  publishedAt: string;
  thumbnail: string;     // gradient or color
  thumbnailEmoji: string;
  views: number;
  likes: number;
  comments: number;
  isPremium: boolean;    // requires subscription
  category: Category;
  difficulty: "Débutant" | "Intermédiaire" | "Avancé";
};

export type SubscriberStat = {
  creatorId: string;
  subscribedAt: string;
  monthlyPrice: number;
  totalPaid: number;
  contentWatched: number;
  lastViewed: string;
};

export type PayoutEntry = {
  id: string;
  periodLabel: string;   // "Juin 2026"
  grossEUR: number;
  platformFeeEUR: number; // 20%
  netEUR: number;
  status: "pending" | "paid" | "processing";
  payoutMethod: "stripe" | "bank";
};
