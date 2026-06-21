"use client";

import Link from "next/link";
import { useState, useEffect } from "react";
import { Check, Eye, Lock, MapPin, MessageCircle, Star, Users, Sparkles, ArrowRight, Play } from "lucide-react";

const SESSIONS = [
  { id: 1, emoji: "🧘‍♀️", title: "Yoga matinal vitalité", duration: "30 min", level: "Tous niveaux", gradient: "from-amber-500 via-rose-500 to-purple-600" },
  { id: 2, emoji: "🌅", title: "Flow Sunrise complet", duration: "45 min", level: "Intermédiaire", gradient: "from-orange-400 via-pink-500 to-purple-600" },
  { id: 3, emoji: "🔥", title: "Power Vinyasa", duration: "60 min", level: "Avancé", gradient: "from-rose-600 via-fuchsia-600 to-violet-700" },
  { id: 4, emoji: "🌙", title: "Yin Yoga sommeil", duration: "20 min", level: "Tous niveaux", gradient: "from-indigo-700 via-purple-700 to-rose-700" },
  { id: 5, emoji: "💪", title: "Renforcement pelvic floor", duration: "25 min", level: "Tous niveaux", gradient: "from-emerald-500 via-teal-500 to-cyan-600" },
  { id: 6, emoji: "🌿", title: "Méditation guidée", duration: "15 min", level: "Tous niveaux", gradient: "from-lime-500 via-emerald-500 to-teal-600" },
];

export default function SarahProfile() {
  const [subscribed, setSubscribed] = useState(false);
  const [showPaywall, setShowPaywall] = useState(false);

  useEffect(() => {
    if (typeof window !== "undefined") {
      setSubscribed(localStorage.getItem("unblur_sub_sarah") === "1");
    }
  }, []);

  const subscribe = () => {
    setSubscribed(true);
    localStorage.setItem("unblur_sub_sarah", "1");
    setShowPaywall(false);
  };

  const unsubscribe = () => {
    setSubscribed(false);
    localStorage.removeItem("unblur_sub_sarah");
  };

  return (
    <div className="mx-auto max-w-3xl">
      {/* COVER */}
      <div className="relative h-48 sm:h-64 bg-gradient-to-br from-rose-500 via-fuchsia-600 to-purple-700 overflow-hidden">
        <div className="absolute inset-0 opacity-30" style={{
          backgroundImage: "radial-gradient(circle at 30% 50%, white 0%, transparent 50%), radial-gradient(circle at 70% 80%, white 0%, transparent 50%)"
        }} />
      </div>

      {/* PROFIL HEADER */}
      <div className="px-4 sm:px-6 -mt-16 sm:-mt-20 relative">
        <div className="flex items-end justify-between gap-3">
          <div className="w-32 h-32 sm:w-40 sm:h-40 rounded-3xl bg-gradient-to-br from-orange-400 via-pink-500 to-rose-600 border-4 border-black flex items-center justify-center text-7xl sm:text-8xl shadow-2xl">
            🧘‍♀️
          </div>
          {subscribed ? (
            <button
              onClick={unsubscribe}
              className="bg-white/10 hover:bg-white/20 text-white text-sm font-bold px-5 py-2.5 rounded-full transition"
            >
              ✓ Abonné · Annuler
            </button>
          ) : (
            <button
              onClick={() => setShowPaywall(true)}
              className="bg-rose-500 hover:bg-rose-600 text-white text-sm font-bold px-5 py-2.5 rounded-full transition shadow-lg shadow-rose-500/30"
            >
              S'abonner · 9,90 €/mois
            </button>
          )}
        </div>

        <div className="mt-5">
          <div className="flex items-center gap-2 mb-1">
            <h1 className="text-3xl font-black tracking-tight">Sarah Yoga</h1>
            <span className="text-rose-400 text-xs font-black bg-rose-500/10 px-2 py-0.5 rounded-full border border-rose-500/30">
              ✦ Founding
            </span>
          </div>
          <p className="text-white/60 text-sm flex items-center gap-2">
            @sarah.yoga
            <span className="text-white/30">·</span>
            <MapPin className="w-3 h-3" />
            Genève
          </p>
          <p className="mt-4 text-white/80 max-w-lg">
            Coach yoga & wellness — guidée par le flow et le respect du corps. Vinyasa, Yin, méditation. Programmes 4 à 12 semaines. 🌿
          </p>

          <div className="mt-4 flex items-center gap-5 text-sm">
            <div>
              <p className="font-black text-lg">847</p>
              <p className="text-white/50 text-xs">abonnés</p>
            </div>
            <div>
              <p className="font-black text-lg">42</p>
              <p className="text-white/50 text-xs">séances</p>
            </div>
            <div>
              <p className="font-black text-lg flex items-center gap-1">4.9 <Star className="w-4 h-4 fill-amber-400 text-amber-400" /></p>
              <p className="text-white/50 text-xs">avis</p>
            </div>
          </div>
        </div>

        {/* STATUS BAR */}
        {subscribed && (
          <div className="mt-6 bg-emerald-500/10 border border-emerald-500/30 rounded-2xl p-4 flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-emerald-500/20 flex items-center justify-center">
              <Check className="w-5 h-5 text-emerald-400" />
            </div>
            <div>
              <p className="font-bold text-emerald-400 text-sm">Tu es abonné·e</p>
              <p className="text-xs text-white/60">Accès complet à tous les contenus de Sarah Yoga</p>
            </div>
          </div>
        )}

        {/* SÉANCES */}
        <div className="mt-10">
          <div className="flex items-center justify-between mb-5">
            <h2 className="text-2xl font-black tracking-tight">Séances</h2>
            <span className="text-xs text-white/40">{SESSIONS.length} contenus</span>
          </div>

          <div className="grid sm:grid-cols-2 gap-4">
            {SESSIONS.map((session) => (
              <SessionCard
                key={session.id}
                session={session}
                unlocked={subscribed}
                onLockedClick={() => setShowPaywall(true)}
              />
            ))}
          </div>
        </div>

        {/* CHAT */}
        <div className="mt-10 bg-white/5 border border-white/10 rounded-3xl p-6">
          <div className="flex items-center gap-3 mb-4">
            <MessageCircle className="w-5 h-5 text-rose-400" />
            <h3 className="font-black text-lg">Chat direct avec Sarah</h3>
          </div>
          {subscribed ? (
            <div>
              <p className="text-sm text-white/70 mb-4">Tu peux échanger directement avec Sarah pour ajuster tes séances, poser tes questions, partager tes ressentis.</p>
              <button className="w-full bg-rose-500 hover:bg-rose-600 text-white font-bold py-3 rounded-full text-sm transition">
                Écrire à Sarah
              </button>
            </div>
          ) : (
            <p className="text-sm text-white/60">🔒 Réservé aux abonnés</p>
          )}
        </div>

        {/* RECOMMANDATIONS */}
        <div className="mt-10 mb-12">
          <h2 className="text-2xl font-black tracking-tight mb-1">Tu pourrais aimer</h2>
          <p className="text-white/40 text-sm mb-5">Algorithme méritocratique — qualité du contenu = mise en avant</p>
          <div className="grid grid-cols-3 gap-3">
            {[
              { e: "🏃‍♀️", n: "Léa Run", b: "+ Founding" },
              { e: "💪", n: "CrossFit Pat", b: "Coach" },
              { e: "🧘‍♂️", n: "Mindful Tom", b: "+ Founding" },
            ].map((c) => (
              <Link
                key={c.n}
                href="#"
                className="aspect-square rounded-2xl bg-white/5 hover:bg-white/10 border border-white/10 flex flex-col items-center justify-center text-center p-3 transition"
              >
                <span className="text-4xl mb-2">{c.e}</span>
                <span className="text-xs font-bold">{c.n}</span>
                <span className="text-[10px] text-rose-400 mt-1">{c.b}</span>
              </Link>
            ))}
          </div>
        </div>
      </div>

      {/* PAYWALL MODAL */}
      {showPaywall && (
        <Paywall onClose={() => setShowPaywall(false)} onSubscribe={subscribe} />
      )}
    </div>
  );
}

function SessionCard({
  session,
  unlocked,
  onLockedClick,
}: {
  session: typeof SESSIONS[0];
  unlocked: boolean;
  onLockedClick: () => void;
}) {
  return (
    <button
      onClick={!unlocked ? onLockedClick : undefined}
      className="text-left group"
    >
      <div className="relative aspect-[4/5] rounded-3xl overflow-hidden cursor-pointer">
        <div
          className={`absolute inset-0 bg-gradient-to-br ${session.gradient} transition-all duration-700 ease-out`}
          style={{
            filter: unlocked ? "blur(0px)" : "blur(28px) saturate(1.2)",
            transform: unlocked ? "scale(1)" : "scale(1.1)",
          }}
        >
          <div className="absolute inset-0 flex items-center justify-center text-9xl">
            {session.emoji}
          </div>
        </div>

        {!unlocked && (
          <div className="absolute inset-0 flex flex-col items-center justify-center bg-black/30 backdrop-blur-sm">
            <Lock className="w-8 h-8 text-white mb-3" />
            <p className="text-white font-bold text-sm">Déflouter</p>
            <p className="text-white/70 text-xs mt-1">Abonnement 9,90 €/mois</p>
          </div>
        )}

        {unlocked && (
          <>
            <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-transparent to-transparent" />
            <div className="absolute bottom-0 inset-x-0 p-4 text-white">
              <p className="text-xs opacity-80 mb-1">{session.duration} · {session.level}</p>
              <p className="font-black text-base">{session.title}</p>
            </div>
            <div className="absolute top-3 right-3 w-10 h-10 rounded-full bg-white/20 backdrop-blur flex items-center justify-center group-hover:bg-white/40 transition">
              <Play className="w-4 h-4 fill-white text-white" />
            </div>
          </>
        )}
      </div>
      {!unlocked && (
        <p className="mt-2 text-xs text-white/40 truncate">{session.duration} · {session.title}</p>
      )}
    </button>
  );
}

function Paywall({ onClose, onSubscribe }: { onClose: () => void; onSubscribe: () => void }) {
  const [step, setStep] = useState<"choose" | "pay">("choose");

  return (
    <div
      className="fixed inset-0 z-50 bg-black/80 backdrop-blur-xl flex items-end sm:items-center justify-center p-0 sm:p-4 animate-in fade-in duration-200"
      onClick={onClose}
    >
      <div
        className="bg-zinc-900 border border-white/10 rounded-t-3xl sm:rounded-3xl w-full sm:max-w-md max-h-[90vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        {step === "choose" ? (
          <div className="p-6 sm:p-8">
            <div className="w-12 h-1.5 bg-white/20 rounded-full mx-auto mb-6 sm:hidden" />
            <div className="w-16 h-16 rounded-2xl bg-rose-500/20 border border-rose-500/30 flex items-center justify-center mb-5">
              <Lock className="w-8 h-8 text-rose-400" />
            </div>
            <h3 className="text-2xl font-black tracking-tight mb-2">
              Soutenir Sarah Yoga
            </h3>
            <p className="text-white/60 text-sm mb-6">
              Accède à toutes ses séances, en exclusivité.
            </p>

            <div className="space-y-3 mb-6">
              <Plan
                title="Abonnement mensuel"
                price="9,90 €"
                period="/mois"
                badge="POPULAIRE"
                features={[
                  "Toutes les séances de Sarah",
                  "Chat direct avec elle",
                  "Stories quotidiennes",
                  "Annulable à tout moment",
                ]}
                onClick={() => setStep("pay")}
              />
              <Plan
                title="Programme one-shot"
                price="49 €"
                period="à vie"
                features={[
                  "1 programme complet 4 semaines",
                  "Accès à vie",
                  "Pas d'abonnement",
                ]}
                onClick={() => setStep("pay")}
                muted
              />
            </div>

            <p className="text-xs text-white/40 text-center">
              95% de ce que tu payes va directement à Sarah (Founding Unblurer).
            </p>
          </div>
        ) : (
          <div className="p-6 sm:p-8">
            <div className="w-12 h-1.5 bg-white/20 rounded-full mx-auto mb-6 sm:hidden" />
            <h3 className="text-2xl font-black tracking-tight mb-1">
              Paiement
            </h3>
            <p className="text-white/60 text-sm mb-6">Sécurisé par Stripe</p>

            <div className="space-y-4">
              <FakeInput label="Email" value="ton-email@gmail.com" />
              <FakeInput label="Numéro de carte" value="4242 4242 4242 4242" cardIcon />
              <div className="grid grid-cols-2 gap-3">
                <FakeInput label="MM / AA" value="12 / 28" />
                <FakeInput label="CVC" value="123" />
              </div>

              <button
                onClick={onSubscribe}
                className="w-full bg-rose-500 hover:bg-rose-600 text-white font-black py-4 rounded-2xl text-base transition shadow-2xl shadow-rose-500/30 mt-2"
              >
                Payer 9,90 € — S'abonner
              </button>
              <p className="text-xs text-white/40 text-center">
                Démo : aucun paiement réel ne sera prélevé.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function Plan({
  title,
  price,
  period,
  features,
  onClick,
  badge,
  muted,
}: {
  title: string;
  price: string;
  period: string;
  features: string[];
  onClick: () => void;
  badge?: string;
  muted?: boolean;
}) {
  return (
    <button
      onClick={onClick}
      className={`w-full text-left p-5 rounded-2xl border transition ${
        muted
          ? "bg-white/5 border-white/10 hover:border-white/20"
          : "bg-gradient-to-br from-rose-500/10 to-transparent border-rose-500/30 hover:border-rose-500/60"
      }`}
    >
      <div className="flex items-baseline justify-between mb-3">
        <p className="font-black">{title}</p>
        {badge && (
          <span className="text-[10px] font-black text-rose-400 bg-rose-500/10 px-2 py-0.5 rounded-full border border-rose-500/30">
            {badge}
          </span>
        )}
      </div>
      <p className="text-3xl font-black">
        {price}
        <span className="text-sm font-medium text-white/40 ml-1">{period}</span>
      </p>
      <ul className="mt-3 space-y-1.5">
        {features.map((f) => (
          <li key={f} className="text-xs text-white/70 flex gap-2">
            <Check className="w-3.5 h-3.5 text-emerald-400 shrink-0" /> {f}
          </li>
        ))}
      </ul>
    </button>
  );
}

function FakeInput({ label, value, cardIcon }: { label: string; value: string; cardIcon?: boolean }) {
  return (
    <div>
      <label className="text-xs text-white/60 mb-1 block">{label}</label>
      <div className="bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-sm font-medium flex items-center justify-between">
        <span>{value}</span>
        {cardIcon && <span className="text-xs text-white/40">VISA</span>}
      </div>
    </div>
  );
}
