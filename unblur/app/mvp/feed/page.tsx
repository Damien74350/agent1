"use client";

import Link from "next/link";
import { useState } from "react";
import { Search, Filter, Lock, Star } from "lucide-react";

const CREATORS = [
  { handle: "sarah.yoga", name: "Sarah Yoga", emoji: "🧘‍♀️", disc: "Yoga · Vinyasa", price: 9.9, subs: 847, badge: "Founding", gradient: "from-amber-400 via-pink-500 to-purple-600", featured: true },
  { handle: "lea.runs", name: "Léa Run", emoji: "🏃‍♀️", disc: "Running · Trail", price: 12.9, subs: 1240, badge: "Founding", gradient: "from-emerald-400 via-teal-500 to-cyan-600" },
  { handle: "pat.crossfit", name: "Pat CrossFit", emoji: "💪", disc: "CrossFit · HIIT", price: 19.9, subs: 2100, badge: "Coach pro", gradient: "from-rose-500 via-red-600 to-orange-600" },
  { handle: "tom.mindful", name: "Mindful Tom", emoji: "🧘‍♂️", disc: "Méditation · Breathwork", price: 7.9, subs: 542, badge: "Founding", gradient: "from-indigo-500 via-purple-600 to-pink-600" },
  { handle: "kat.danse", name: "Kat Danse", emoji: "💃", disc: "Danse · Fitness", price: 14.9, subs: 890, badge: "Coach pro", gradient: "from-fuchsia-500 via-pink-500 to-rose-500" },
  { handle: "max.muscu", name: "Max Muscu", emoji: "🏋️‍♂️", disc: "Musculation · Force", price: 16.9, subs: 1750, badge: "Founding", gradient: "from-zinc-700 via-zinc-900 to-black" },
  { handle: "lou.pilates", name: "Lou Pilates", emoji: "🤸‍♀️", disc: "Pilates · Mobilité", price: 11.9, subs: 670, badge: "Founding", gradient: "from-violet-400 via-violet-600 to-purple-700" },
  { handle: "ben.boxe", name: "Ben Boxe", emoji: "🥊", disc: "Boxe · Self-defense", price: 13.9, subs: 1480, badge: "Coach pro", gradient: "from-red-700 via-rose-600 to-orange-600" },
  { handle: "ana.nutrition", name: "Ana Nutri", emoji: "🥗", disc: "Nutrition saine", price: 9.9, subs: 980, badge: "Founding", gradient: "from-lime-400 via-emerald-500 to-teal-600" },
];

const CATEGORIES = ["Tous", "Yoga", "Running", "Muscu", "Crossfit", "Méditation", "Danse", "Nutrition", "Pilates", "Coach pro"];

export default function Feed() {
  const [cat, setCat] = useState("Tous");

  return (
    <div className="mx-auto max-w-6xl px-4 sm:px-6 py-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-4xl font-black tracking-tight">Découvrir.</h1>
          <p className="text-white/60 text-sm mt-1">L'algorithme méritocratique met en avant la qualité, pas le statut.</p>
        </div>
      </div>

      {/* SEARCH */}
      <div className="bg-white/5 border border-white/10 rounded-2xl flex items-center px-4 py-3 mb-4">
        <Search className="w-4 h-4 text-white/40 mr-3" />
        <input
          type="text"
          placeholder="Chercher un Unblurer, une discipline, un objectif…"
          className="bg-transparent outline-none flex-1 text-sm"
        />
        <Filter className="w-4 h-4 text-white/40" />
      </div>

      {/* CATEGORIES */}
      <div className="flex gap-2 overflow-x-auto pb-2 mb-8 -mx-4 px-4 sm:mx-0 sm:px-0">
        {CATEGORIES.map((c) => (
          <button
            key={c}
            onClick={() => setCat(c)}
            className={`px-4 py-1.5 rounded-full text-xs font-bold whitespace-nowrap transition ${
              cat === c ? "bg-white text-black" : "bg-white/5 text-white/70 hover:bg-white/10"
            }`}
          >
            {c}
          </button>
        ))}
      </div>

      {/* MATCHING IA TEASER */}
      <div className="mb-8 bg-gradient-to-br from-violet-500/10 to-transparent border border-violet-500/30 rounded-3xl p-6 sm:p-8">
        <p className="text-xs uppercase tracking-widest text-violet-400 font-bold mb-2">
          ✦ Matching IA · Q1 2027
        </p>
        <h3 className="text-2xl font-black mb-2">Trouve ton Unblurer parfait en 2 min.</h3>
        <p className="text-white/70 text-sm mb-4 max-w-lg">
          Quiz de 2 minutes. L'IA matche ton profil avec 3 créateurs et 3 programmes parfaitement adaptés à ton niveau, objectifs et style.
        </p>
        <button className="bg-violet-500/20 hover:bg-violet-500/30 border border-violet-500/30 text-violet-300 font-bold px-5 py-2.5 rounded-full text-sm transition">
          Lancer le quiz IA (bientôt)
        </button>
      </div>

      {/* GRID */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
        {CREATORS.map((c) => (
          <Link
            key={c.handle}
            href={c.handle === "sarah.yoga" ? "/mvp/profile/sarah-yoga" : "#"}
            className="group"
          >
            <div className={`aspect-[4/5] rounded-3xl overflow-hidden bg-gradient-to-br ${c.gradient} relative`}>
              <div className="absolute inset-0 flex items-center justify-center text-7xl sm:text-8xl">
                {c.emoji}
              </div>
              <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent" />
              {c.badge === "Founding" && (
                <div className="absolute top-3 right-3 bg-rose-500/90 backdrop-blur text-white text-[9px] font-black px-2 py-1 rounded-full">
                  ✦ FOUNDING
                </div>
              )}
              {c.featured && (
                <div className="absolute top-3 left-3 bg-amber-400/90 backdrop-blur text-black text-[9px] font-black px-2 py-1 rounded-full">
                  ★ TOP
                </div>
              )}
              <div className="absolute bottom-3 inset-x-3 text-white">
                <p className="font-black text-sm leading-tight">{c.name}</p>
                <p className="text-[10px] opacity-80 mt-0.5">{c.disc}</p>
                <div className="flex items-center justify-between mt-2">
                  <span className="text-[10px] opacity-70">{c.subs} abos</span>
                  <span className="text-xs font-black">{c.price.toFixed(2)} €/mo</span>
                </div>
              </div>
            </div>
          </Link>
        ))}
      </div>

      {/* CTA BOTTOM */}
      <div className="mt-16 bg-gradient-to-br from-rose-500/20 to-transparent border border-rose-500/30 rounded-3xl p-8 text-center">
        <h3 className="text-2xl sm:text-3xl font-black mb-2">Et toi, quelle est ta passion ?</h3>
        <p className="text-white/70 mb-6 max-w-md mx-auto text-sm">
          Rejoins les Founding Unblurer et monétise ce que tu fais déjà.
        </p>
        <Link
          href="/mvp/waitlist"
          className="bg-rose-500 hover:bg-rose-600 text-white font-bold px-6 py-3 rounded-full text-sm transition inline-block"
        >
          Devenir Founding Unblurer
        </Link>
      </div>
    </div>
  );
}
