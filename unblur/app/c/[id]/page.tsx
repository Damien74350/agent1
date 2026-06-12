"use client";

import { useState } from "react";
import { useParams, notFound } from "next/navigation";
import { Card, Pill } from "../../../components/Card";
import { ContentCard } from "../../../components/ContentCard";
import { findCreator, contentsForCreator } from "../../../lib/mock";
import { compact, fmtEUR } from "../../../lib/format";
import { Star, Users, MessageCircle, Lock, Zap, Award, CheckCircle2, X, MapPin, Calendar, Tv } from "lucide-react";

export default function CreatorPage() {
  const params = useParams();
  const id = params?.id as string;
  const creator = findCreator(id);
  const [subscribed, setSubscribed] = useState(false);
  const [showPaywall, setShowPaywall] = useState(false);

  if (!creator) {
    notFound();
  }

  const contents = contentsForCreator(creator.id);
  const yearlyDiscount = creator.yearlyPriceEUR ? Math.round((1 - creator.yearlyPriceEUR / (creator.monthlyPriceEUR * 12)) * 100) : 0;

  return (
    <div className="space-y-6">
      {/* BANNER */}
      <section className="relative h-48 sm:h-72 rounded-3xl overflow-hidden ring-1 ring-overlay/10" style={{ background: creator.banner }}>
        <div />
        {creator.isLive && (
          <div className="absolute top-4 left-4 inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-foreground/80 backdrop-blur text-xs font-black uppercase tracking-widest text-foreground">
            <span className="w-2 h-2 rounded-full bg-rose live-dot" />
            Live · {compact(creator.liveViewers ?? 0)} viewers
          </div>
        )}
      </section>

      {/* IDENTITY */}
      <section className="-mt-20 relative px-4 sm:px-8">
        <div className="flex flex-col lg:flex-row gap-6 items-start">
          <div className="w-28 h-28 rounded-3xl grid place-items-center text-black font-black text-4xl ring-4 ring-canvas" style={{ background: creator.banner }}>
            {creator.avatar}
          </div>
          <div className="flex-1">
            <div className="flex flex-wrap items-center gap-2">
              <h1 className="text-3xl sm:text-4xl font-black">{creator.name}</h1>
              <Pill color="rose">{creator.tier}</Pill>
              {creator.certifications.length > 0 && (
                <Pill color="sky"><CheckCircle2 size={9} className="mr-1" />Vérifié</Pill>
              )}
            </div>
            <p className="text-muted">{creator.handle}</p>
            <p className="mt-2 text-sm text-foreground/70 italic">"{creator.tagline}"</p>
            <div className="mt-3 flex flex-wrap items-center gap-3 text-xs text-muted">
              <span className="inline-flex items-center gap-1"><MapPin size={11} /> {creator.city}, {creator.country} {creator.countryFlag}</span>
              <span>·</span>
              <span className="inline-flex items-center gap-1"><Users size={11} /> {compact(creator.subscribers)} abonnés</span>
              <span>·</span>
              <span className="inline-flex items-center gap-1 text-sun"><Star size={11} fill="currentColor" /> {creator.rating.toFixed(2)}</span>
              <span>·</span>
              <span className="inline-flex items-center gap-1"><Calendar size={11} /> rejoint en {new Date(creator.joinedAt).toLocaleDateString("fr-FR", { month: "short", year: "numeric" })}</span>
            </div>
          </div>

          {/* SUBSCRIBE CTA */}
          <div className="w-full lg:w-80 shrink-0 glass-strong rounded-2xl p-5 shadow-glow">
            {subscribed ? (
              <div className="text-center">
                <CheckCircle2 size={32} className="text-success mx-auto mb-2" />
                <p className="font-black">Tu es abonné(e) ✨</p>
                <p className="text-xs text-muted mt-1">Tout le contenu est débloqué.</p>
                <button onClick={() => setSubscribed(false)} className="mt-3 text-xs text-muted hover:underline">Se désabonner</button>
              </div>
            ) : (
              <>
                <p className="text-[10px] uppercase tracking-wider text-muted font-bold">Abonnement</p>
                <p className="font-black rose-text text-4xl mt-1">{fmtEUR(creator.monthlyPriceEUR)}<span className="text-sm text-muted font-normal"> /mois</span></p>
                {creator.yearlyPriceEUR && (
                  <p className="text-xs text-muted mt-1">ou {fmtEUR(creator.yearlyPriceEUR)}/an · économie {yearlyDiscount}%</p>
                )}
                <ul className="mt-4 space-y-1.5 text-xs">
                  <li className="flex items-center gap-2"><CheckCircle2 size={12} className="text-rose" /> Lives & replays illimités</li>
                  <li className="flex items-center gap-2"><CheckCircle2 size={12} className="text-rose" /> Programmes structurés</li>
                  <li className="flex items-center gap-2"><CheckCircle2 size={12} className="text-rose" /> Communauté privée</li>
                  <li className="flex items-center gap-2"><CheckCircle2 size={12} className="text-rose" /> Form check vidéo</li>
                  <li className="flex items-center gap-2"><CheckCircle2 size={12} className="text-rose" /> Annulation 1 clic</li>
                </ul>
                <button onClick={() => setShowPaywall(true)} className="mt-4 w-full px-4 py-3 rounded-xl rose-gradient text-black font-black shadow-glow inline-flex items-center justify-center gap-2">
                  <Zap size={16} /> S'abonner
                </button>
                <p className="text-[10px] text-muted text-center mt-2">80% va à {creator.name.split(" ")[0]}, 20% à unblur</p>
              </>
            )}
          </div>
        </div>
      </section>

      {/* STORY */}
      <Card title="Son histoire">
        <p className="text-sm text-foreground/80 leading-relaxed">{creator.story}</p>
        {creator.certifications.length > 0 && (
          <div className="mt-4 flex flex-wrap gap-1.5">
            {creator.certifications.map(c => (
              <span key={c} className="inline-flex items-center gap-1 rounded-full bg-sky/10 ring-1 ring-sky/30 px-3 py-1 text-xs font-semibold text-sky">
                <Award size={11} /> {c}
              </span>
            ))}
          </div>
        )}
      </Card>

      {/* CONTENT */}
      <section>
        <header className="mb-4">
          <Pill color="rose">Contenu</Pill>
          <h2 className="mt-2 text-2xl font-black">{contents.length} séances disponibles</h2>
          <p className="text-xs text-muted">{contents.filter(c => !c.isPremium).length} gratuites · {contents.filter(c => c.isPremium).length} pour abonnés</p>
        </header>
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {contents.map(c => <ContentCard key={c.id} content={c} />)}
        </div>
      </section>

      {/* PAYWALL MODAL */}
      {showPaywall && (
        <div className="fixed inset-0 z-50 grid place-items-center bg-overlay/60 backdrop-blur-sm p-4" onClick={() => setShowPaywall(false)}>
          <div className="glass-strong rounded-3xl p-6 max-w-md w-full" onClick={e => e.stopPropagation()}>
            <div className="flex items-center justify-between">
              <p className="text-[10px] uppercase tracking-widest text-rose font-bold">Tu rejoins</p>
              <button onClick={() => setShowPaywall(false)} className="p-1 rounded-lg hover:bg-overlay/10"><X size={18} /></button>
            </div>
            <div className="mt-4 flex items-center gap-3">
              <div className="w-14 h-14 rounded-2xl grid place-items-center font-black text-black text-xl" style={{ background: creator.banner }}>{creator.avatar}</div>
              <div>
                <p className="font-black text-lg">{creator.name}</p>
                <p className="text-xs text-muted">{creator.handle}</p>
              </div>
            </div>
            <div className="mt-5 space-y-2">
              <button className="w-full text-left rounded-xl bg-overlay/5 ring-1 ring-rose/30 p-4 hover:ring-rose/60 transition">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-bold">Mensuel</p>
                    <p className="text-xs text-muted">Annule quand tu veux</p>
                  </div>
                  <p className="font-black rose-text text-xl">{fmtEUR(creator.monthlyPriceEUR)}</p>
                </div>
              </button>
              {creator.yearlyPriceEUR && (
                <button className="w-full text-left rounded-xl bg-rose/10 ring-1 ring-rose/40 p-4 hover:ring-rose/60 transition relative">
                  <span className="absolute -top-2 -right-2 px-2 py-0.5 rounded-full rose-gradient text-black text-[10px] font-black uppercase">Économie {yearlyDiscount}%</span>
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-bold">Annuel</p>
                      <p className="text-xs text-muted">2 mois offerts</p>
                    </div>
                    <p className="font-black rose-text text-xl">{fmtEUR(creator.yearlyPriceEUR)}</p>
                  </div>
                </button>
              )}
            </div>
            <button onClick={() => { setSubscribed(true); setShowPaywall(false); }} className="mt-5 w-full px-4 py-3 rounded-xl rose-gradient text-black font-black shadow-glow">
              Confirmer · paiement sécurisé Stripe
            </button>
            <p className="text-[10px] text-muted text-center mt-3">Apple Pay · CB · SEPA · Confirmation immédiate</p>
          </div>
        </div>
      )}
    </div>
  );
}
