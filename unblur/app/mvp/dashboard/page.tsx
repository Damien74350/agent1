"use client";

import Link from "next/link";
import { useState, useEffect } from "react";
import { TrendingUp, Users, Eye, MessageCircle, Upload, Plus, Star, BarChart3, Wallet, Sparkles, ArrowUpRight, Calendar } from "lucide-react";

export default function Dashboard() {
  const [creator, setCreator] = useState<any>(null);

  useEffect(() => {
    if (typeof window !== "undefined") {
      const saved = localStorage.getItem("unblur_creator");
      if (saved) setCreator(JSON.parse(saved));
    }
  }, []);

  const name = creator?.name || "Sarah Yoga";
  const handle = creator?.handle || "sarah.yoga";
  const price = creator?.price || 9.9;

  return (
    <div className="mx-auto max-w-5xl px-4 sm:px-6 py-8">
      {/* HEADER */}
      <div className="flex items-start justify-between mb-8">
        <div>
          <p className="text-xs uppercase tracking-widest text-rose-500 font-bold mb-1">
            ✦ Founding Unblurer · à vie
          </p>
          <h1 className="text-4xl font-black tracking-tight">Hello {name.split(" ")[0]}.</h1>
          <p className="text-white/60 mt-1">unblur.ch/{handle}</p>
        </div>
        <Link
          href="/mvp/studio"
          className="bg-rose-500 hover:bg-rose-600 text-white font-bold px-5 py-3 rounded-full inline-flex items-center gap-2 text-sm transition shadow-lg shadow-rose-500/20"
        >
          <Plus className="w-4 h-4" />
          Publier
        </Link>
      </div>

      {/* REVENUS HERO */}
      <div className="bg-gradient-to-br from-rose-500/20 via-rose-500/5 to-transparent border border-rose-500/30 rounded-3xl p-6 sm:p-8 mb-6">
        <p className="text-xs uppercase tracking-widest text-rose-400 font-bold mb-2">
          Revenus ce mois
        </p>
        <div className="flex items-baseline gap-3 mb-1">
          <p className="text-5xl sm:text-6xl font-black">2 387 €</p>
          <span className="text-emerald-400 font-bold text-sm flex items-center gap-1">
            <ArrowUpRight className="w-4 h-4" />
            +18%
          </span>
        </div>
        <p className="text-white/60 text-sm mb-6">vs mois dernier</p>

        <div className="grid grid-cols-3 gap-3 sm:gap-6 pt-6 border-t border-white/10">
          <div>
            <p className="text-xs text-white/50 mb-1">Abonnements</p>
            <p className="font-black text-lg sm:text-2xl">2 178 €</p>
          </div>
          <div>
            <p className="text-xs text-white/50 mb-1">Programmes</p>
            <p className="font-black text-lg sm:text-2xl">209 €</p>
          </div>
          <div>
            <p className="text-xs text-white/50 mb-1">Tips reçus</p>
            <p className="font-black text-lg sm:text-2xl">0 €</p>
          </div>
        </div>

        <p className="text-xs text-white/40 mt-6">
          Commission unblur Founding 5% · Net pour toi : <strong className="text-emerald-400">2 268 €</strong>
        </p>
      </div>

      {/* STATS GRID */}
      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-3 mb-8">
        <StatCard icon={Users} label="Abonnés actifs" value="241" change="+12" color="text-rose-400" />
        <StatCard icon={Eye} label="Vues séances" value="18.4k" change="+34%" color="text-emerald-400" />
        <StatCard icon={MessageCircle} label="Messages" value="47" change="+8" color="text-amber-400" />
        <StatCard icon={Star} label="Note moyenne" value="4.9" change="142 avis" color="text-violet-400" />
      </div>

      {/* INSIGHT IA */}
      <div className="bg-gradient-to-br from-violet-500/10 to-transparent border border-violet-500/30 rounded-3xl p-6 mb-6">
        <p className="text-xs uppercase tracking-widest text-violet-400 font-bold mb-2 flex items-center gap-2">
          <Sparkles className="w-3 h-3" />
          Insight IA hebdomadaire
        </p>
        <h3 className="font-black text-xl mb-3">Cette semaine, tes meilleurs créneaux</h3>
        <p className="text-sm text-white/70 mb-4 leading-relaxed">
          Tes posts du <strong className="text-white">mardi 19h-21h</strong> ont 3,2x plus d'engagement que la moyenne.
          Tes 5 abonnées les plus fidèles (depuis 6 mois) n'ont pas vu ton dernier post.
          <strong className="text-white"> Envoie-leur un message direct</strong> pour les ré-engager.
        </p>
        <button className="text-sm font-bold text-violet-400 hover:text-violet-300 inline-flex items-center gap-1">
          Voir le rapport complet
          <ArrowUpRight className="w-4 h-4" />
        </button>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* CONTENUS RÉCENTS */}
        <div className="lg:col-span-2">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-black tracking-tight">Contenus récents</h2>
            <Link href="/mvp/studio" className="text-xs text-rose-400 hover:text-rose-300 font-bold">
              Tout voir →
            </Link>
          </div>
          <div className="space-y-2">
            {[
              { title: "Yoga matinal vitalité", views: "1 247", subs: "+8", emoji: "🧘‍♀️" },
              { title: "Flow Sunrise complet", views: "892", subs: "+5", emoji: "🌅" },
              { title: "Power Vinyasa", views: "743", subs: "+11", emoji: "🔥" },
              { title: "Yin Yoga sommeil", views: "612", subs: "+3", emoji: "🌙" },
            ].map((c) => (
              <div
                key={c.title}
                className="bg-white/5 hover:bg-white/10 transition border border-white/10 rounded-2xl p-4 flex items-center gap-4"
              >
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-rose-500 to-purple-600 flex items-center justify-center text-2xl">
                  {c.emoji}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-bold truncate">{c.title}</p>
                  <p className="text-xs text-white/50">{c.views} vues · {c.subs} abonnés gagnés</p>
                </div>
                <button className="text-xs text-white/60 hover:text-white">
                  <BarChart3 className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* SIDEBAR */}
        <div className="space-y-4">
          {/* WAITLIST FOUNDING */}
          <div className="bg-gradient-to-br from-rose-500/10 to-transparent border border-rose-500/30 rounded-3xl p-5">
            <p className="text-xs uppercase tracking-widest text-rose-400 font-bold mb-2 flex items-center gap-2">
              <Sparkles className="w-3 h-3" />
              Statut
            </p>
            <h3 className="font-black text-lg mb-3">Founding Unblurer #142</h3>
            <p className="text-xs text-white/60 mb-4">
              Tu fais partie des 1000 premiers. Commission max 5% à vie.
            </p>
            <div className="h-1 bg-white/10 rounded-full overflow-hidden mb-2">
              <div className="h-full bg-rose-500" style={{ width: "14.2%" }} />
            </div>
            <p className="text-[10px] text-white/40">
              142 / 1000 places réservées
            </p>
          </div>

          {/* PROCHAIN PAIEMENT */}
          <div className="bg-white/5 border border-white/10 rounded-3xl p-5">
            <Wallet className="w-5 h-5 text-emerald-400 mb-3" />
            <p className="text-xs uppercase tracking-widest text-white/40 font-bold mb-1">
              Prochain virement
            </p>
            <p className="font-black text-2xl">2 268 €</p>
            <p className="text-xs text-white/50 mt-1">
              <Calendar className="w-3 h-3 inline mr-1" />
              1er juillet 2026 · IBAN ··· 4218
            </p>
          </div>

          {/* CTA INVITER */}
          <div className="bg-white/5 border border-white/10 rounded-3xl p-5">
            <p className="text-xs uppercase tracking-widest text-white/40 font-bold mb-2">
              Programme mentor
            </p>
            <p className="font-bold mb-3">Invite 5 créatrices, gagne 1% de leur revenu pendant 12 mois.</p>
            <button className="w-full bg-white/10 hover:bg-white/20 text-white font-bold py-2.5 rounded-full text-sm transition">
              Inviter une créatrice
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

function StatCard({
  icon: Icon,
  label,
  value,
  change,
  color,
}: {
  icon: any;
  label: string;
  value: string;
  change: string;
  color: string;
}) {
  return (
    <div className="bg-white/5 border border-white/10 rounded-2xl p-5">
      <Icon className={`w-5 h-5 ${color} mb-2`} />
      <p className="text-xs text-white/50 mb-1">{label}</p>
      <p className="font-black text-2xl">{value}</p>
      <p className={`text-xs ${color} font-medium mt-1`}>{change}</p>
    </div>
  );
}
