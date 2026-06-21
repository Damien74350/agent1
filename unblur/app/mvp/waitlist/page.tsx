"use client";

import { useState } from "react";
import Link from "next/link";
import { Check, Sparkles, ArrowRight } from "lucide-react";

export default function Waitlist() {
  const [submitted, setSubmitted] = useState(false);
  const [data, setData] = useState({
    email: "",
    handle: "",
    discipline: "",
    followers: "",
  });
  const [position, setPosition] = useState<number | null>(null);

  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    const pos = 142 + Math.floor(Math.random() * 10);
    setPosition(pos);
    if (typeof window !== "undefined") {
      const existing = JSON.parse(localStorage.getItem("unblur_waitlist") || "[]");
      existing.push({ ...data, position: pos, date: new Date().toISOString() });
      localStorage.setItem("unblur_waitlist", JSON.stringify(existing));
    }
    setSubmitted(true);
  };

  if (submitted) {
    return (
      <div className="mx-auto max-w-lg px-6 py-16 text-center">
        <div className="w-24 h-24 rounded-full bg-rose-500/20 border border-rose-500/30 flex items-center justify-center mx-auto mb-6 animate-in zoom-in duration-500">
          <Sparkles className="w-12 h-12 text-rose-400" />
        </div>
        <p className="text-xs uppercase tracking-widest text-rose-400 font-bold mb-2">
          Bienvenue chez les pionniers
        </p>
        <h1 className="text-4xl font-black tracking-tight mb-3">Tu es Founding #{position}.</h1>
        <p className="text-white/70 mb-1">Ta place est réservée à vie.</p>
        <p className="text-rose-400 font-bold mb-8">Commission max 5% — à vie.</p>

        <div className="bg-gradient-to-br from-rose-500/10 to-transparent border border-rose-500/30 rounded-3xl p-6 mb-6 text-left">
          <p className="text-xs uppercase tracking-widest text-white/40 font-bold mb-3">Et ensuite ?</p>
          <ol className="space-y-3 text-sm">
            <li className="flex gap-3">
              <span className="w-6 h-6 rounded-full bg-rose-500 text-white font-black text-xs flex items-center justify-center shrink-0">1</span>
              <span>Tu reçois un email avec ton lien <strong>unblur.ch/{data.handle || "ton.pseudo"}</strong></span>
            </li>
            <li className="flex gap-3">
              <span className="w-6 h-6 rounded-full bg-rose-500 text-white font-black text-xs flex items-center justify-center shrink-0">2</span>
              <span>Accès à la bêta privée octobre 2026 (avant tout le monde)</span>
            </li>
            <li className="flex gap-3">
              <span className="w-6 h-6 rounded-full bg-rose-500 text-white font-black text-xs flex items-center justify-center shrink-0">3</span>
              <span>Onboarding personnel avec Damien (le fondateur)</span>
            </li>
          </ol>
        </div>

        <Link
          href="/mvp/profile/sarah-yoga"
          className="block w-full bg-white/5 hover:bg-white/10 text-white font-bold py-4 rounded-full text-base transition border border-white/10"
        >
          Voir à quoi ressemblera ton profil →
        </Link>

        <p className="mt-8 text-xs text-white/40">
          Reste {1000 - (position ?? 0)} places de Founding Unblurer.
        </p>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-xl px-4 sm:px-6 py-12">
      <p className="text-xs uppercase tracking-widest text-rose-500 font-bold mb-3">
        ⚠ 1000 places · pas une de plus
      </p>
      <h1 className="text-5xl sm:text-6xl font-black tracking-tighter leading-[0.95] mb-4">
        Founding<br />
        Unblurer.
      </h1>
      <p className="text-white/70 text-lg mb-2">
        Réserve ta place dans les <strong className="text-white">1000 premiers créateurs</strong> historiques d'unblur.
      </p>
      <p className="text-rose-400 font-bold mb-8">
        Commission max 5% à vie. Badge à vie. Boost algorithmique à vie.
      </p>

      <div className="mb-8 space-y-2">
        {[
          "Commission plancher 5% — à vie",
          "Badge Founding affiché sur ton profil",
          "Boost algorithmique +15% à vie",
          "Accès anticipé features (bêta privée octobre)",
          "Onboarding personnel avec Damien",
          "Communauté Founding privée + events",
        ].map((b) => (
          <p key={b} className="flex gap-3 text-sm">
            <Check className="w-5 h-5 text-rose-400 shrink-0" />
            <span>{b}</span>
          </p>
        ))}
      </div>

      <form onSubmit={submit} className="space-y-3 bg-white/5 border border-white/10 rounded-3xl p-6">
        <div>
          <label className="text-xs text-white/60 mb-1.5 block">Ton email</label>
          <input
            type="email"
            required
            placeholder="ton@email.com"
            value={data.email}
            onChange={(e) => setData({ ...data, email: e.target.value })}
            className="w-full bg-black/30 border border-white/10 rounded-2xl px-4 py-3 outline-none focus:border-rose-500 transition"
          />
        </div>
        <div>
          <label className="text-xs text-white/60 mb-1.5 block">Ton handle Instagram</label>
          <div className="bg-black/30 border border-white/10 rounded-2xl flex items-center px-4 py-3 focus-within:border-rose-500 transition">
            <span className="text-white/40 text-sm">@</span>
            <input
              type="text"
              required
              placeholder="ton.pseudo"
              value={data.handle}
              onChange={(e) => setData({ ...data, handle: e.target.value })}
              className="bg-transparent outline-none flex-1 ml-1"
            />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="text-xs text-white/60 mb-1.5 block">Discipline</label>
            <select
              required
              value={data.discipline}
              onChange={(e) => setData({ ...data, discipline: e.target.value })}
              className="w-full bg-black/30 border border-white/10 rounded-2xl px-4 py-3 outline-none focus:border-rose-500 transition appearance-none"
            >
              <option value="">Choisir</option>
              <option>Yoga / Pilates</option>
              <option>Crossfit / Muscu</option>
              <option>Running / Outdoor</option>
              <option>Méditation</option>
              <option>Coach sportif</option>
              <option>Lifestyle / Wellness</option>
              <option>Nutrition</option>
              <option>Autre</option>
            </select>
          </div>
          <div>
            <label className="text-xs text-white/60 mb-1.5 block">Followers Insta</label>
            <select
              required
              value={data.followers}
              onChange={(e) => setData({ ...data, followers: e.target.value })}
              className="w-full bg-black/30 border border-white/10 rounded-2xl px-4 py-3 outline-none focus:border-rose-500 transition appearance-none"
            >
              <option value="">Choisir</option>
              <option>0 - 1k</option>
              <option>1k - 5k</option>
              <option>5k - 25k</option>
              <option>25k - 100k</option>
              <option>100k +</option>
            </select>
          </div>
        </div>

        <button
          type="submit"
          className="w-full bg-rose-500 hover:bg-rose-600 text-white font-bold py-4 rounded-full text-base transition shadow-2xl shadow-rose-500/30 inline-flex items-center justify-center gap-2 mt-2"
        >
          Réserver ma place
          <ArrowRight className="w-4 h-4" />
        </button>
        <p className="text-[10px] text-white/40 text-center">
          Aucune carte requise. Aucun engagement. Annulable à tout moment.
        </p>
      </form>

      <div className="mt-8 flex items-center gap-3 justify-center text-xs text-white/40">
        <div className="flex -space-x-2">
          {["🧘‍♀️", "🏃‍♂️", "💪", "🧘‍♂️", "🏋️‍♀️"].map((e, i) => (
            <div key={i} className="w-7 h-7 rounded-full bg-gradient-to-br from-rose-500 to-purple-600 border-2 border-black flex items-center justify-center text-sm">
              {e}
            </div>
          ))}
        </div>
        <p>142 Founding réservées · 858 places restantes</p>
      </div>
    </div>
  );
}
