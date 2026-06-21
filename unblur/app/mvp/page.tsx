"use client";

import Link from "next/link";
import { useState } from "react";
import { ArrowRight, Check, Eye, EyeOff, Zap, Users, TrendingUp, Lock, Sparkles } from "lucide-react";
import { MvpLogo } from "./_components";

export default function MvpLanding() {
  const [unblurred, setUnblurred] = useState(false);

  return (
    <div className="mx-auto max-w-6xl px-4 sm:px-6">
      {/* HERO */}
      <section className="pt-16 sm:pt-24 pb-16">
        <p className="text-xs uppercase tracking-[0.3em] text-rose-500 mb-6 font-bold">
          plateforme créateur — sport, fitness, lifestyle, coach
        </p>
        <h1 className="text-5xl sm:text-7xl lg:text-8xl font-black tracking-tighter leading-[0.95]">
          Transforme<br />
          ta passion<br />
          en revenu.
        </h1>
        <p className="mt-8 text-xl sm:text-2xl text-white/70 max-w-2xl leading-snug">
          Tu partages déjà gratuitement sur Instagram.{" "}
          <span className="text-white font-bold">Sur unblur, tu gagnes vraiment.</span>
        </p>
        <p className="mt-4 text-base text-white/50 max-w-2xl">
          Tes vrais fans payent un abonnement mensuel pour accéder à ton contenu. Tu gardes jusqu'à 95%. Tes followers Insta restent libres.
        </p>
        <div className="mt-10 flex flex-wrap gap-3">
          <Link
            href="/mvp/waitlist"
            className="bg-rose-500 hover:bg-rose-600 text-white font-bold px-7 py-4 rounded-full text-base inline-flex items-center gap-2 transition shadow-2xl shadow-rose-500/20"
          >
            Devenir Founding Unblurer
            <ArrowRight className="w-4 h-4" />
          </Link>
          <Link
            href="/mvp/profile/sarah-yoga"
            className="border border-white/20 hover:border-white/40 hover:bg-white/5 text-white font-bold px-7 py-4 rounded-full text-base transition inline-flex items-center gap-2"
          >
            Voir un profil créateur
          </Link>
        </div>
      </section>

      {/* DÉMO FLOUTAGE INTERACTIVE */}
      <section className="border-y border-white/10 py-16 sm:py-24 -mx-4 sm:-mx-6 px-4 sm:px-6">
        <p className="text-xs uppercase tracking-[0.3em] text-rose-500 mb-3 font-bold">
          ↓ démo interactive ↓
        </p>
        <h2 className="text-3xl sm:text-5xl font-black tracking-tight mb-4">
          Le principe en 3 secondes.
        </h2>
        <p className="text-white/60 mb-10 max-w-2xl">
          Sur Instagram, tout est gratuit. Sur unblur, ton contenu est flouté par défaut. Tes vrais fans payent pour le déflouter.
        </p>

        <div className="grid sm:grid-cols-2 gap-6 items-center">
          <div className="relative aspect-[9/16] sm:aspect-[4/5] rounded-3xl overflow-hidden bg-gradient-to-br from-violet-700 via-rose-600 to-orange-500 max-w-md mx-auto w-full">
            <div
              className="absolute inset-0 transition-all duration-700 ease-out"
              style={{
                filter: unblurred ? "blur(0px)" : "blur(40px)",
                transform: unblurred ? "scale(1)" : "scale(1.05)",
              }}
            >
              <div className="absolute inset-0 flex items-center justify-center text-white text-center p-8">
                <div>
                  <div className="text-7xl sm:text-9xl mb-4">🧘‍♀️</div>
                  <p className="text-2xl font-black">Yoga matinal</p>
                  <p className="text-sm opacity-80">Séance complète 30 min</p>
                  <p className="mt-6 text-xs opacity-60">par sarah.yoga</p>
                </div>
              </div>
            </div>
            {!unblurred && (
              <div className="absolute inset-0 flex items-end justify-center pb-12 pointer-events-none">
                <div className="bg-black/60 backdrop-blur-xl border border-white/20 rounded-full px-5 py-2 flex items-center gap-2">
                  <Lock className="w-4 h-4 text-rose-400" />
                  <span className="text-sm font-bold">Contenu flouté</span>
                </div>
              </div>
            )}
            {unblurred && (
              <div className="absolute top-4 right-4 bg-emerald-500/90 backdrop-blur-xl text-black font-black text-xs px-3 py-1.5 rounded-full">
                ✓ DÉFLOUTÉ
              </div>
            )}
          </div>

          <div className="space-y-6">
            <button
              onClick={() => setUnblurred(!unblurred)}
              className={`w-full font-bold px-6 py-5 rounded-2xl text-lg transition shadow-2xl ${
                unblurred
                  ? "bg-white/10 hover:bg-white/20 text-white"
                  : "bg-rose-500 hover:bg-rose-600 text-white shadow-rose-500/30"
              }`}
            >
              {unblurred ? (
                <span className="inline-flex items-center gap-2"><EyeOff className="w-5 h-5" /> Re-flouter</span>
              ) : (
                <span className="inline-flex items-center gap-2"><Eye className="w-5 h-5" /> Déflouter pour 9,90 €/mois</span>
              )}
            </button>
            <div className="space-y-3 text-sm text-white/70">
              <p className="flex gap-3"><Check className="w-5 h-5 text-emerald-400 shrink-0" /> <span><strong className="text-white">Aucune friction</strong> pour le créateur — il fait son contenu comme d'habitude.</span></p>
              <p className="flex gap-3"><Check className="w-5 h-5 text-emerald-400 shrink-0" /> <span><strong className="text-white">Vrais fans seulement</strong> — ils paient pour accéder.</span></p>
              <p className="flex gap-3"><Check className="w-5 h-5 text-emerald-400 shrink-0" /> <span><strong className="text-white">95% pour le créateur</strong> — Founding Unblurer à vie.</span></p>
              <p className="flex gap-3"><Check className="w-5 h-5 text-emerald-400 shrink-0" /> <span><strong className="text-white">Tes followers Insta restent libres</strong> — zéro perte, que du gain.</span></p>
            </div>
          </div>
        </div>
      </section>

      {/* SIMULATEUR DE REVENUS */}
      <Simulator />

      {/* COMPARAISON */}
      <section className="py-16 sm:py-24">
        <p className="text-xs uppercase tracking-[0.3em] text-rose-500 mb-3 font-bold">
          comparaison
        </p>
        <h2 className="text-3xl sm:text-5xl font-black tracking-tight mb-12">
          Pourquoi pas Instagram ?
        </h2>

        <div className="grid sm:grid-cols-2 gap-6">
          <div className="bg-white/5 rounded-3xl p-8 border border-white/10">
            <p className="text-xs uppercase tracking-widest font-bold text-white/40 mb-4">Instagram</p>
            <ul className="space-y-3 text-white/80 text-sm">
              <li className="flex gap-2">❌ <span>Tu donnes ton contenu <strong>gratuit</strong></span></li>
              <li className="flex gap-2">❌ <span>L'algorithme décide qui te voit</span></li>
              <li className="flex gap-2">❌ <span>Pas de revenu direct</span></li>
              <li className="flex gap-2">❌ <span>Tu attends des brand deals aléatoires</span></li>
              <li className="flex gap-2">❌ <span>Aucun lien direct avec tes vrais fans</span></li>
            </ul>
          </div>

          <div className="bg-gradient-to-br from-rose-500/20 to-rose-500/5 rounded-3xl p-8 border border-rose-500/30">
            <p className="text-xs uppercase tracking-widest font-bold text-rose-400 mb-4 flex items-center gap-2">
              <Sparkles className="w-3 h-3" /> unblur
            </p>
            <ul className="space-y-3 text-white text-sm">
              <li className="flex gap-2">✅ <span>Tes vrais fans <strong>payent</strong> pour ton contenu</span></li>
              <li className="flex gap-2">✅ <span>Aucun algorithme — tes abonnés voient tout</span></li>
              <li className="flex gap-2">✅ <span>Revenu mensuel direct, immédiat</span></li>
              <li className="flex gap-2">✅ <span>Tu gardes jusqu'à 95% (Founding à vie)</span></li>
              <li className="flex gap-2">✅ <span>Chat direct, communauté authentique</span></li>
            </ul>
          </div>
        </div>
      </section>

      {/* FEATURES INTÉGRÉES */}
      <section className="border-t border-white/10 py-16 sm:py-24">
        <p className="text-xs uppercase tracking-[0.3em] text-rose-500 mb-3 font-bold">
          tout-en-un
        </p>
        <h2 className="text-3xl sm:text-5xl font-black tracking-tight mb-4">
          N'utilise pas 1000 applis.
        </h2>
        <p className="text-white/60 mb-12 max-w-2xl">
          Tout ce dont tu as besoin est intégré. Studio, paiements, chat, statistiques, communauté.
        </p>

        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {[
            { title: "Studio intégré", desc: "Upload, montage, sous-titres, flou. Pas de Capcut nécessaire." },
            { title: "Paiements Stripe", desc: "Vérification d'identité automatique. Premier virement sous 7 jours." },
            { title: "Chat direct", desc: "Conversations 1-to-1 avec tes vrais fans. Pas de DM perdus." },
            { title: "Statistiques claires", desc: "Revenus, abonnés, engagement. Pilote ton business." },
            { title: "Stories 24h", desc: "Format vertical court, comme Insta, mais pour tes abonnés." },
            { title: "Programmes premium", desc: "Vends des programmes complets 29-199€ à l'unité." },
            { title: "Lives streamés", desc: "Diffuse en direct, replay automatique défloutable." },
            { title: "Lien personnel", desc: "unblur.ch/[ton-pseudo] — partage partout en 1 clic." },
            { title: "Anti-IA breveté", desc: "Ton contenu est protégé contre la reconstruction par IA." },
          ].map((f) => (
            <div key={f.title} className="bg-white/5 hover:bg-white/10 transition rounded-2xl p-6 border border-white/10">
              <p className="font-black text-lg mb-1">{f.title}</p>
              <p className="text-sm text-white/60">{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* PARCOURS */}
      <section className="border-t border-white/10 py-16 sm:py-24">
        <p className="text-xs uppercase tracking-[0.3em] text-rose-500 mb-3 font-bold">
          en 3 minutes
        </p>
        <h2 className="text-3xl sm:text-5xl font-black tracking-tight mb-12">
          Comment ça marche.
        </h2>

        <div className="grid sm:grid-cols-3 gap-6">
          {[
            { n: "01", title: "Tu t'inscris", desc: "Avatar, bio, lien unblur.ch/tonpseudo. Aucun document. 2 minutes." },
            { n: "02", title: "Tu fais comme d'hab", desc: "Tu publies tes contenus comme sur Insta. Mais ils sont floutés par défaut." },
            { n: "03", title: "Tu gagnes", desc: "Tes vrais fans s'abonnent à 9,90€/mois. Tu encaisses sous 7 jours." },
          ].map((s) => (
            <div key={s.n} className="bg-white/5 rounded-3xl p-8 border border-white/10">
              <p className="text-5xl font-black text-rose-500 mb-4">{s.n}</p>
              <p className="font-black text-xl mb-2">{s.title}</p>
              <p className="text-sm text-white/60">{s.desc}</p>
            </div>
          ))}
        </div>

        <div className="mt-12 flex flex-wrap gap-3">
          <Link
            href="/mvp/onboarding"
            className="bg-rose-500 hover:bg-rose-600 text-white font-bold px-7 py-4 rounded-full text-base inline-flex items-center gap-2 transition"
          >
            Démarrer mon onboarding
            <ArrowRight className="w-4 h-4" />
          </Link>
          <Link
            href="/mvp/dashboard"
            className="border border-white/20 hover:border-white/40 hover:bg-white/5 text-white font-bold px-7 py-4 rounded-full text-base transition"
          >
            Voir un dashboard
          </Link>
        </div>
      </section>

      {/* FOUNDING */}
      <section className="border-t border-white/10 py-16 sm:py-24">
        <div className="bg-gradient-to-br from-rose-500/20 via-rose-500/5 to-transparent rounded-3xl p-8 sm:p-12 border border-rose-500/30">
          <p className="text-xs uppercase tracking-[0.3em] text-rose-400 mb-3 font-bold">
            opportunité historique
          </p>
          <h2 className="text-4xl sm:text-6xl font-black tracking-tight mb-4">
            Founding Unblurer.<br />
            <span className="text-rose-400">À vie.</span>
          </h2>
          <p className="text-white/80 max-w-2xl mb-8 text-lg">
            Les <strong>1000 premiers créateurs</strong> deviennent Founding Unblurers. Pour toujours.
          </p>

          <div className="grid sm:grid-cols-2 gap-3 mb-8">
            {[
              "Commission max 5% — à vie (vs 30% standard)",
              "Badge Founding affiché sur ton profil",
              "Boost algorithmique +15% — à vie",
              "Accès anticipé aux nouvelles features",
              "Place sur la home unblur",
              "Communauté privée Founding + events",
            ].map((b) => (
              <p key={b} className="flex gap-3 text-sm text-white">
                <Check className="w-5 h-5 text-rose-400 shrink-0" />
                <span>{b}</span>
              </p>
            ))}
          </div>

          <p className="text-rose-400 font-black text-sm mb-6">
            ⚠ 1000 places. Pas une de plus.
          </p>

          <Link
            href="/mvp/waitlist"
            className="bg-rose-500 hover:bg-rose-600 text-white font-bold px-8 py-4 rounded-full text-lg inline-flex items-center gap-2 transition shadow-2xl shadow-rose-500/30"
          >
            Réserver ma place
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </section>
    </div>
  );
}

function Simulator() {
  const [followers, setFollowers] = useState(15000);
  const [price, setPrice] = useState(9.9);
  const conversionRate = 0.03;
  const monthlySubs = Math.round(followers * conversionRate);
  const grossRevenue = monthlySubs * price;
  const foundingRevenue = grossRevenue * 0.95;

  return (
    <section className="border-t border-white/10 py-16 sm:py-24">
      <p className="text-xs uppercase tracking-[0.3em] text-rose-500 mb-3 font-bold">
        simulateur de revenus
      </p>
      <h2 className="text-3xl sm:text-5xl font-black tracking-tight mb-4">
        Combien tu peux gagner.
      </h2>
      <p className="text-white/60 mb-12 max-w-2xl">
        Estimation basée sur les taux de conversion observés sur Patreon et OnlyFans (3% en moyenne).
      </p>

      <div className="grid sm:grid-cols-2 gap-6">
        <div className="bg-white/5 rounded-3xl p-8 border border-white/10 space-y-8">
          <div>
            <label className="text-xs uppercase tracking-widest text-white/60 font-bold mb-2 block">
              Tes followers Instagram
            </label>
            <input
              type="range"
              min="1000"
              max="200000"
              step="1000"
              value={followers}
              onChange={(e) => setFollowers(parseInt(e.target.value))}
              className="w-full accent-rose-500"
            />
            <p className="text-3xl font-black mt-3">{followers.toLocaleString("fr-FR")} <span className="text-white/40 text-base font-medium">followers</span></p>
          </div>

          <div>
            <label className="text-xs uppercase tracking-widest text-white/60 font-bold mb-2 block">
              Ton prix d'abonnement
            </label>
            <input
              type="range"
              min="5"
              max="49.9"
              step="0.1"
              value={price}
              onChange={(e) => setPrice(parseFloat(e.target.value))}
              className="w-full accent-rose-500"
            />
            <p className="text-3xl font-black mt-3">{price.toFixed(2)} € <span className="text-white/40 text-base font-medium">/ mois</span></p>
          </div>
        </div>

        <div className="bg-gradient-to-br from-rose-500/20 to-transparent rounded-3xl p-8 border border-rose-500/30">
          <p className="text-xs uppercase tracking-widest text-rose-400 font-bold mb-1">
            Si seulement 3% s'abonnent
          </p>
          <p className="text-5xl sm:text-6xl font-black mb-1">
            {Math.round(foundingRevenue).toLocaleString("fr-FR")} €
          </p>
          <p className="text-white/60 text-sm mb-8">par mois — net pour toi (Founding 95%)</p>

          <div className="space-y-3 pt-6 border-t border-white/10 text-sm">
            <div className="flex justify-between">
              <span className="text-white/60">Abonnés payants</span>
              <span className="font-bold">{monthlySubs}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-white/60">Revenu brut</span>
              <span className="font-bold">{Math.round(grossRevenue).toLocaleString("fr-FR")} €</span>
            </div>
            <div className="flex justify-between">
              <span className="text-white/60">Commission unblur (5%)</span>
              <span className="font-bold text-white/40">−{Math.round(grossRevenue - foundingRevenue).toLocaleString("fr-FR")} €</span>
            </div>
            <div className="flex justify-between pt-3 border-t border-white/10">
              <span className="font-black">Sur 12 mois</span>
              <span className="font-black text-rose-400">{Math.round(foundingRevenue * 12).toLocaleString("fr-FR")} €</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
