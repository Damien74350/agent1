"use client";

import { useState } from "react";
import Link from "next/link";
import { ArrowRight, ArrowLeft, Check, Camera, Lock, Sparkles, AtSign } from "lucide-react";

const DISCIPLINES = ["Yoga", "Pilates", "Crossfit", "Musculation", "Running", "Cyclisme", "Boxe", "Danse", "HIIT", "Méditation", "Mobilité", "Nutrition"];

export default function Onboarding() {
  const [step, setStep] = useState(0);
  const [data, setData] = useState({
    handle: "",
    name: "",
    bio: "",
    disciplines: [] as string[],
    price: 9.9,
  });

  const totalSteps = 5;
  const progress = ((step + 1) / totalSteps) * 100;

  const next = () => setStep((s) => Math.min(s + 1, totalSteps - 1));
  const prev = () => setStep((s) => Math.max(s - 1, 0));

  const finish = () => {
    if (typeof window !== "undefined") {
      localStorage.setItem("unblur_creator", JSON.stringify(data));
      window.location.href = "/mvp/dashboard";
    }
  };

  return (
    <div className="mx-auto max-w-xl px-4 sm:px-6 py-12">
      {/* Progress */}
      <div className="mb-10">
        <div className="flex items-center justify-between mb-2">
          <p className="text-xs uppercase tracking-widest text-white/40 font-bold">
            Étape {step + 1} sur {totalSteps}
          </p>
          <p className="text-xs text-white/40">{Math.round(progress)}%</p>
        </div>
        <div className="h-1 bg-white/10 rounded-full overflow-hidden">
          <div
            className="h-full bg-rose-500 transition-all duration-500"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* Steps */}
      {step === 0 && (
        <Step
          title="Bienvenue."
          subtitle="2 minutes et ton compte unblur est prêt à monétiser."
          accent="Tu vas pouvoir gagner de l'argent dès aujourd'hui."
        >
          <ul className="space-y-3 mb-8 text-sm text-white/70">
            <li className="flex gap-3 items-start">
              <Check className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
              <span>Gratuit — tu ne payes rien à unblur tant que tu ne gagnes pas un euro</span>
            </li>
            <li className="flex gap-3 items-start">
              <Check className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
              <span>Commission 5% (Founding Unblurer) — à vie pour les 1000 premiers</span>
            </li>
            <li className="flex gap-3 items-start">
              <Check className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
              <span>Tu gardes Instagram — unblur s'ajoute, ne remplace rien</span>
            </li>
            <li className="flex gap-3 items-start">
              <Check className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
              <span>Premier virement sous 7 jours après ton premier abonné</span>
            </li>
          </ul>
          <PrimaryButton onClick={next}>Commencer</PrimaryButton>
        </Step>
      )}

      {step === 1 && (
        <Step
          title="Ton @handle."
          subtitle="C'est ton URL unique. Reprends celle de ton Instagram, c'est plus simple à partager."
        >
          <div className="bg-white/5 border border-white/10 rounded-2xl flex items-center px-4 py-3 mb-3">
            <span className="text-white/40 text-sm whitespace-nowrap">unblur.ch/</span>
            <input
              type="text"
              autoFocus
              placeholder="ton.pseudo"
              value={data.handle}
              onChange={(e) => setData({ ...data, handle: e.target.value.toLowerCase().replace(/[^a-z0-9.]/g, "") })}
              className="bg-transparent outline-none flex-1 font-bold"
            />
            {data.handle && (
              <Check className="w-5 h-5 text-emerald-400" />
            )}
          </div>
          {data.handle && (
            <p className="text-xs text-emerald-400 mb-6">
              ✓ Ton lien : <strong>unblur.ch/{data.handle}</strong>
            </p>
          )}
          <div className="flex gap-3">
            <SecondaryButton onClick={prev}>Retour</SecondaryButton>
            <PrimaryButton onClick={next} disabled={!data.handle}>
              Continuer
            </PrimaryButton>
          </div>
        </Step>
      )}

      {step === 2 && (
        <Step title="Présente-toi." subtitle="Ton nom affiché et 1-2 phrases de bio.">
          <div className="space-y-4 mb-6">
            <div>
              <label className="text-xs text-white/60 mb-1.5 block">Nom affiché</label>
              <input
                type="text"
                placeholder="Sarah Yoga"
                value={data.name}
                onChange={(e) => setData({ ...data, name: e.target.value })}
                className="w-full bg-white/5 border border-white/10 rounded-2xl px-4 py-3 outline-none focus:border-rose-500 transition"
              />
            </div>
            <div>
              <label className="text-xs text-white/60 mb-1.5 block">Bio (2 phrases max)</label>
              <textarea
                rows={3}
                placeholder="Coach yoga & wellness. Vinyasa, Yin, méditation. Genève."
                value={data.bio}
                onChange={(e) => setData({ ...data, bio: e.target.value })}
                className="w-full bg-white/5 border border-white/10 rounded-2xl px-4 py-3 outline-none focus:border-rose-500 transition resize-none"
              />
            </div>
          </div>
          <div className="flex gap-3">
            <SecondaryButton onClick={prev}>Retour</SecondaryButton>
            <PrimaryButton onClick={next} disabled={!data.name}>Continuer</PrimaryButton>
          </div>
        </Step>
      )}

      {step === 3 && (
        <Step title="Tes disciplines." subtitle="Sélectionne celles qui te représentent. Tu peux en choisir plusieurs.">
          <div className="flex flex-wrap gap-2 mb-6">
            {DISCIPLINES.map((d) => {
              const active = data.disciplines.includes(d);
              return (
                <button
                  key={d}
                  onClick={() => {
                    setData({
                      ...data,
                      disciplines: active
                        ? data.disciplines.filter((x) => x !== d)
                        : [...data.disciplines, d],
                    });
                  }}
                  className={`px-4 py-2 rounded-full text-sm font-medium transition ${
                    active
                      ? "bg-rose-500 text-white"
                      : "bg-white/5 hover:bg-white/10 text-white/70 border border-white/10"
                  }`}
                >
                  {active && "✓ "}{d}
                </button>
              );
            })}
          </div>
          <div className="flex gap-3">
            <SecondaryButton onClick={prev}>Retour</SecondaryButton>
            <PrimaryButton onClick={next} disabled={data.disciplines.length === 0}>
              Continuer
            </PrimaryButton>
          </div>
        </Step>
      )}

      {step === 4 && (
        <Step title="Ton prix mensuel." subtitle="Combien tes vrais fans payent par mois pour ton contenu ?">
          <div className="bg-gradient-to-br from-rose-500/20 to-transparent border border-rose-500/30 rounded-3xl p-8 mb-6 text-center">
            <p className="text-7xl font-black mb-2">{data.price.toFixed(2)} €</p>
            <p className="text-white/60 text-sm">par mois</p>
            <input
              type="range"
              min="5"
              max="49.9"
              step="0.1"
              value={data.price}
              onChange={(e) => setData({ ...data, price: parseFloat(e.target.value) })}
              className="w-full mt-6 accent-rose-500"
            />
            <div className="flex justify-between text-xs text-white/40 mt-2">
              <span>5 €</span>
              <span>49,90 €</span>
            </div>
          </div>

          <div className="bg-emerald-500/10 border border-emerald-500/30 rounded-2xl p-4 mb-6">
            <p className="text-xs uppercase tracking-widest text-emerald-400 font-bold mb-1">
              Estimation revenus
            </p>
            <p className="text-sm text-white/80">
              Avec <strong>200 abonnés</strong> (3% de 6 000 followers) :
            </p>
            <p className="text-3xl font-black text-emerald-400 mt-1">
              {Math.round(data.price * 200 * 0.95)} € / mois net
            </p>
          </div>

          <div className="flex gap-3">
            <SecondaryButton onClick={prev}>Retour</SecondaryButton>
            <PrimaryButton onClick={finish}>
              Créer mon compte
              <ArrowRight className="w-4 h-4 ml-2 inline" />
            </PrimaryButton>
          </div>
        </Step>
      )}
    </div>
  );
}

function Step({
  title,
  subtitle,
  accent,
  children,
}: {
  title: string;
  subtitle: string;
  accent?: string;
  children: React.ReactNode;
}) {
  return (
    <div className="animate-in fade-in slide-in-from-bottom-3 duration-300">
      <h1 className="text-4xl font-black tracking-tight mb-3">{title}</h1>
      <p className="text-white/70 mb-2">{subtitle}</p>
      {accent && (
        <p className="text-rose-400 font-bold text-sm mb-6">{accent}</p>
      )}
      <div className="mt-6">{children}</div>
    </div>
  );
}

function PrimaryButton({
  onClick,
  children,
  disabled,
}: {
  onClick: () => void;
  children: React.ReactNode;
  disabled?: boolean;
}) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className="flex-1 bg-rose-500 hover:bg-rose-600 disabled:bg-white/5 disabled:text-white/30 text-white font-bold py-4 rounded-full text-base transition shadow-xl shadow-rose-500/20 disabled:shadow-none"
    >
      {children}
    </button>
  );
}

function SecondaryButton({ onClick, children }: { onClick: () => void; children: React.ReactNode }) {
  return (
    <button
      onClick={onClick}
      className="px-6 bg-white/5 hover:bg-white/10 text-white/70 font-bold py-4 rounded-full text-base transition border border-white/10"
    >
      <ArrowLeft className="w-4 h-4 inline" />
    </button>
  );
}
