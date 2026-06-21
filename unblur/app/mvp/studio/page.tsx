"use client";

import Link from "next/link";
import { useState } from "react";
import { Upload, Image as ImageIcon, Video, Mic, Sparkles, ArrowLeft, Check, Lock, Eye } from "lucide-react";

export default function Studio() {
  const [step, setStep] = useState<"choose" | "blur" | "publish" | "done">("choose");
  const [blurLevel, setBlurLevel] = useState(28);
  const [title, setTitle] = useState("Yoga matinal vitalité");
  const [selectedFormat, setSelectedFormat] = useState<"vinyasa" | "yin" | "power" | null>(null);

  if (step === "done") {
    return (
      <div className="mx-auto max-w-md px-6 py-16 text-center">
        <div className="w-24 h-24 rounded-full bg-emerald-500/20 border border-emerald-500/30 flex items-center justify-center mx-auto mb-6">
          <Check className="w-12 h-12 text-emerald-400" />
        </div>
        <h1 className="text-4xl font-black tracking-tight mb-3">Publié !</h1>
        <p className="text-white/60 mb-2">Ton contenu est en ligne sur ton profil.</p>
        <p className="text-rose-400 font-bold mb-8">unblur.ch/sarah.yoga</p>
        <div className="space-y-3">
          <Link href="/mvp/profile/sarah-yoga" className="block w-full bg-rose-500 hover:bg-rose-600 text-white font-bold py-4 rounded-full text-base transition">
            Voir mon profil
          </Link>
          <Link href="/mvp/dashboard" className="block w-full bg-white/5 hover:bg-white/10 text-white font-bold py-4 rounded-full text-base transition border border-white/10">
            Retour au dashboard
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-2xl px-4 sm:px-6 py-8">
      <Link
        href="/mvp/dashboard"
        className="text-white/40 hover:text-white text-sm inline-flex items-center gap-1 mb-6"
      >
        <ArrowLeft className="w-4 h-4" />
        Dashboard
      </Link>

      {step === "choose" && (
        <>
          <h1 className="text-4xl font-black tracking-tight mb-2">Nouveau contenu.</h1>
          <p className="text-white/60 mb-8">Vidéo, photo, audio. Le studio s'occupe du reste.</p>

          {/* UPLOAD ZONE */}
          <button
            onClick={() => setStep("blur")}
            className="w-full bg-gradient-to-br from-white/5 to-white/0 border-2 border-dashed border-white/20 hover:border-rose-500/50 rounded-3xl p-12 text-center transition group"
          >
            <Upload className="w-12 h-12 text-white/30 group-hover:text-rose-400 transition mx-auto mb-4" />
            <p className="font-bold text-lg mb-1">Glisser ou cliquer pour uploader</p>
            <p className="text-sm text-white/40">MP4, MOV, JPG, PNG, MP3 · Max 4 Go</p>
          </button>

          {/* FORMAT QUICK PICKS */}
          <p className="text-xs uppercase tracking-widest text-white/40 font-bold mt-8 mb-3">
            Format rapide
          </p>
          <div className="grid grid-cols-3 gap-3">
            {[
              { icon: Video, label: "Séance", desc: "Vidéo longue", id: "vinyasa" },
              { icon: ImageIcon, label: "Story", desc: "24h éphémère", id: "yin" },
              { icon: Mic, label: "Audio", desc: "Méditation", id: "power" },
            ].map((f) => (
              <button
                key={f.label}
                onClick={() => {
                  setSelectedFormat(f.id as any);
                  setStep("blur");
                }}
                className="aspect-square bg-white/5 hover:bg-white/10 border border-white/10 rounded-2xl flex flex-col items-center justify-center gap-1 p-3 transition"
              >
                <f.icon className="w-6 h-6 text-rose-400 mb-1" />
                <p className="font-bold text-sm">{f.label}</p>
                <p className="text-[10px] text-white/40">{f.desc}</p>
              </button>
            ))}
          </div>

          {/* IA SUGGESTION */}
          <div className="mt-8 bg-gradient-to-br from-violet-500/10 to-transparent border border-violet-500/30 rounded-2xl p-5">
            <p className="text-xs uppercase tracking-widest text-violet-400 font-bold mb-2 flex items-center gap-2">
              <Sparkles className="w-3 h-3" />
              Mode IA (Q2 2027)
            </p>
            <p className="text-sm text-white/80 mb-1 font-bold">
              Optimisation automatique
            </p>
            <p className="text-xs text-white/60">
              L'IA coupe les temps morts, ajoute sous-titres, suggère musique, color grading et stratégie de floutage optimale.
            </p>
          </div>
        </>
      )}

      {step === "blur" && (
        <>
          <h1 className="text-4xl font-black tracking-tight mb-2">Stratégie de flou.</h1>
          <p className="text-white/60 mb-8">C'est ta marque. C'est ton talent. Ajuste l'intensité.</p>

          {/* PREVIEW */}
          <div className="relative aspect-[9/16] sm:aspect-video rounded-3xl overflow-hidden bg-gradient-to-br from-amber-500 via-rose-600 to-purple-700 max-w-md mx-auto mb-6">
            <div
              className="absolute inset-0 transition-all duration-300"
              style={{ filter: `blur(${blurLevel}px)`, transform: `scale(${1 + blurLevel / 200})` }}
            >
              <div className="absolute inset-0 flex items-center justify-center text-white text-center p-8">
                <div>
                  <div className="text-8xl sm:text-9xl mb-3">🧘‍♀️</div>
                  <p className="text-xl font-black">{title}</p>
                </div>
              </div>
            </div>
            {blurLevel > 5 && (
              <div className="absolute bottom-4 inset-x-4 flex items-center justify-center pointer-events-none">
                <div className="bg-black/60 backdrop-blur-xl border border-white/20 rounded-full px-4 py-2 flex items-center gap-2">
                  <Lock className="w-3.5 h-3.5 text-rose-400" />
                  <span className="text-xs font-bold">Réservé aux abonnés</span>
                </div>
              </div>
            )}
          </div>

          {/* SLIDER */}
          <div className="bg-white/5 border border-white/10 rounded-2xl p-5 mb-4">
            <div className="flex items-center justify-between mb-3">
              <label className="text-xs uppercase tracking-widest text-white/60 font-bold">
                Intensité du flou
              </label>
              <span className="font-bold text-rose-400">{blurLevel}px</span>
            </div>
            <input
              type="range"
              min="0"
              max="60"
              value={blurLevel}
              onChange={(e) => setBlurLevel(parseInt(e.target.value))}
              className="w-full accent-rose-500"
            />
            <div className="flex justify-between text-[10px] text-white/40 mt-2">
              <span>Visible (gratuit)</span>
              <span>Flou max (paywall)</span>
            </div>
          </div>

          {/* STRATÉGIES */}
          <p className="text-xs uppercase tracking-widest text-white/40 font-bold mb-3">
            Stratégies préréglées
          </p>
          <div className="grid grid-cols-2 gap-3 mb-8">
            {[
              { label: "Paywall classique", desc: "Flou total", val: 40 },
              { label: "Teaser 10s + flou", desc: "Création d'envie", val: 28 },
              { label: "Flou par zone", desc: "Visage flou seulement", val: 20 },
              { label: "Adversarial anti-IA", desc: "Brevet 00 — Q1 2027", val: 35 },
            ].map((s) => (
              <button
                key={s.label}
                onClick={() => setBlurLevel(s.val)}
                className="text-left bg-white/5 hover:bg-white/10 border border-white/10 hover:border-rose-500/30 rounded-2xl p-4 transition"
              >
                <p className="font-bold text-sm">{s.label}</p>
                <p className="text-xs text-white/50 mt-0.5">{s.desc}</p>
              </button>
            ))}
          </div>

          <div className="flex gap-3">
            <button
              onClick={() => setStep("choose")}
              className="px-5 bg-white/5 hover:bg-white/10 text-white/70 font-bold py-4 rounded-full transition border border-white/10"
            >
              <ArrowLeft className="w-4 h-4" />
            </button>
            <button
              onClick={() => setStep("publish")}
              className="flex-1 bg-rose-500 hover:bg-rose-600 text-white font-bold py-4 rounded-full text-base transition shadow-xl shadow-rose-500/20"
            >
              Continuer
            </button>
          </div>
        </>
      )}

      {step === "publish" && (
        <>
          <h1 className="text-4xl font-black tracking-tight mb-2">Publier.</h1>
          <p className="text-white/60 mb-8">Dernières infos avant publication.</p>

          <div className="space-y-4 mb-8">
            <div>
              <label className="text-xs text-white/60 mb-1.5 block">Titre</label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="w-full bg-white/5 border border-white/10 rounded-2xl px-4 py-3 outline-none focus:border-rose-500 transition"
              />
            </div>
            <div>
              <label className="text-xs text-white/60 mb-1.5 block">Description</label>
              <textarea
                rows={3}
                defaultValue="Séance complète pour démarrer la journée en douceur. Vinyasa fluide, focus respiration. 30 min."
                className="w-full bg-white/5 border border-white/10 rounded-2xl px-4 py-3 outline-none focus:border-rose-500 transition resize-none text-sm"
              />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-xs text-white/60 mb-1.5 block">Durée</label>
                <div className="bg-white/5 border border-white/10 rounded-2xl px-4 py-3 font-medium">30 min</div>
              </div>
              <div>
                <label className="text-xs text-white/60 mb-1.5 block">Niveau</label>
                <div className="bg-white/5 border border-white/10 rounded-2xl px-4 py-3 font-medium">Tous niveaux</div>
              </div>
            </div>
          </div>

          {/* ACCÈS */}
          <p className="text-xs uppercase tracking-widest text-white/40 font-bold mb-3">
            Qui peut voir
          </p>
          <div className="space-y-2 mb-8">
            <AccessOption
              title="Tous les abonnés"
              desc="Accessible avec ton abonnement 9,90€/mois"
              selected
            />
            <AccessOption
              title="Tier Premium uniquement"
              desc="Multi-tier à venir Q1 2027"
            />
            <AccessOption
              title="Programme premium 49€"
              desc="Vente one-shot, accès à vie"
            />
          </div>

          <div className="flex gap-3">
            <button
              onClick={() => setStep("blur")}
              className="px-5 bg-white/5 hover:bg-white/10 text-white/70 font-bold py-4 rounded-full transition border border-white/10"
            >
              <ArrowLeft className="w-4 h-4" />
            </button>
            <button
              onClick={() => setStep("done")}
              className="flex-1 bg-rose-500 hover:bg-rose-600 text-white font-bold py-4 rounded-full text-base transition shadow-xl shadow-rose-500/20"
            >
              Publier maintenant
            </button>
          </div>
        </>
      )}
    </div>
  );
}

function AccessOption({ title, desc, selected }: { title: string; desc: string; selected?: boolean }) {
  return (
    <div
      className={`p-4 rounded-2xl border flex items-center gap-3 cursor-pointer ${
        selected ? "bg-rose-500/10 border-rose-500/40" : "bg-white/5 border-white/10 hover:bg-white/10"
      }`}
    >
      <div className={`w-5 h-5 rounded-full border-2 ${selected ? "bg-rose-500 border-rose-500" : "border-white/30"} flex items-center justify-center`}>
        {selected && <Check className="w-3 h-3 text-white" />}
      </div>
      <div className="flex-1">
        <p className="font-bold text-sm">{title}</p>
        <p className="text-xs text-white/50">{desc}</p>
      </div>
    </div>
  );
}
