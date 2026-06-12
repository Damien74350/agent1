"use client";

import { useState } from "react";
import Link from "next/link";
import { Card, Pill, Stat } from "../../components/Card";
import { CREATORS } from "../../lib/mock";
import { fmtEUR } from "../../lib/format";
import { Sparkles, Zap, ArrowRight, Crown, Tv, Coins, CheckCircle2, TrendingUp, Heart } from "lucide-react";

export default function BecomeCreatorPage() {
  const [subscribers, setSubscribers] = useState(500);
  const [price, setPrice] = useState(9.90);
  const gross = subscribers * price;
  const net = gross * 0.80;
  const yearlyNet = net * 12;

  return (
    <div className="space-y-16">
      {/* HERO */}
      <section className="relative rounded-3xl overflow-hidden ring-1 ring-rose/30 p-6 sm:p-14 text-center">
        <div className="absolute inset-0 rose-gradient opacity-[0.12]" />
        <div />
        <div className="relative max-w-4xl mx-auto">
          <Pill color="rose">Devenir créateur</Pill>
          <h1 className="mt-4 text-4xl sm:text-7xl font-black tracking-tight leading-[1.02]">
            Vis de ton <span className="rose-text">expertise sport.</span>
          </h1>
          <p className="mt-6 text-lg sm:text-xl text-foreground/70 max-w-2xl mx-auto">
            Tu connais quelque chose que les autres veulent apprendre. unblur te donne tout l'écosystème : paywall, lives, replays, paiements.
            Tu gardes <strong className="text-foreground">80%</strong>. On gère le reste.
          </p>
          <div className="mt-8 flex flex-wrap gap-3 justify-center">
            <button className="inline-flex items-center gap-2 px-6 py-3.5 rounded-xl rose-gradient text-black font-black shadow-glow">
              <Sparkles size={18} /> Créer mon compte créateur
            </button>
          </div>
        </div>
      </section>

      {/* CALCULATEUR */}
      <section>
        <header className="mb-8 text-center">
          <Pill color="sun">Simulateur</Pill>
          <h2 className="mt-3 text-3xl sm:text-5xl font-black">Combien tu pourrais gagner ?</h2>
          <p className="mt-3 text-foreground/70 max-w-2xl mx-auto">Bouge les curseurs. Vois ton revenu.</p>
        </header>

        <Card className="max-w-3xl mx-auto">
          <div className="space-y-6">
            <div>
              <div className="flex items-baseline justify-between mb-2">
                <label className="text-sm font-bold">Tes abonnés actifs</label>
                <span className="font-black text-2xl rose-text">{subscribers.toLocaleString("fr-FR")}</span>
              </div>
              <input type="range" min="50" max="10000" step="50" value={subscribers} onChange={e => setSubscribers(+e.target.value)} className="w-full accent-rose" />
              <div className="flex justify-between text-[10px] text-muted mt-1">
                <span>50</span><span>5 000</span><span>10 000</span>
              </div>
            </div>
            <div>
              <div className="flex items-baseline justify-between mb-2">
                <label className="text-sm font-bold">Ton prix mensuel</label>
                <span className="font-black text-2xl rose-text">{fmtEUR(price)}</span>
              </div>
              <input type="range" min="2.99" max="49.90" step="1" value={price} onChange={e => setPrice(+e.target.value)} className="w-full accent-rose" />
              <div className="flex justify-between text-[10px] text-muted mt-1">
                <span>2,99 €</span><span>24,90 €</span><span>49,90 €</span>
              </div>
            </div>

            <div className="rounded-2xl rose-gradient p-6 text-black">
              <p className="text-xs font-bold uppercase tracking-widest opacity-80">Ton revenu NET</p>
              <p className="text-5xl font-black mt-1">{fmtEUR(net, 0)}<span className="text-xl font-normal">/mois</span></p>
              <p className="text-sm mt-2 opacity-90">soit {fmtEUR(yearlyNet, 0)} sur l'année (après 20% unblur)</p>
            </div>

            <div className="grid grid-cols-3 gap-3 text-center text-xs">
              <div className="rounded-xl bg-overlay/5 p-3">
                <p className="text-muted">Brut généré</p>
                <p className="font-black mt-1">{fmtEUR(gross, 0)}</p>
              </div>
              <div className="rounded-xl bg-overlay/5 p-3">
                <p className="text-muted">unblur prend</p>
                <p className="font-black mt-1 text-muted">-{fmtEUR(gross * 0.20, 0)}</p>
              </div>
              <div className="rounded-xl bg-rose/10 ring-1 ring-rose/30 p-3">
                <p className="text-rose font-bold">TU TOUCHES</p>
                <p className="font-black mt-1 rose-text">{fmtEUR(net, 0)}</p>
              </div>
            </div>
          </div>
        </Card>
      </section>

      {/* COMPARAISON */}
      <section>
        <header className="mb-8 text-center">
          <Pill color="violet">Comparatif</Pill>
          <h2 className="mt-3 text-3xl sm:text-4xl font-black">unblur vs le marché</h2>
        </header>

        <div className="grid sm:grid-cols-3 gap-4">
          {[
            { name: "unblur", split: "80 / 20", color: "rose-text", featured: true, pros: ["Live + Replay + Programme", "Stripe intégré", "Aucun frais caché", "Image propre & sport"] },
            { name: "OnlyFans", split: "80 / 20", color: "text-foreground", pros: ["Same split"], cons: ["Image sulfureuse", "Marques fuient"] },
            { name: "Twitch", split: "50 / 50", color: "text-foreground", pros: ["Audience massive"], cons: ["50% de marge", "Gaming-centric"] },
            { name: "Patreon", split: "88 / 12", color: "text-foreground", pros: ["Meilleur split"], cons: ["Pas de live propre", "Pas focus sport"] },
            { name: "Apple Fitness+", split: "Salarié", color: "text-foreground", pros: ["Production studio"], cons: ["Tu n'es pas créateur indep", "Tu as un patron"] },
          ].slice(0, 3).map(o => (
            <div key={o.name} className={`rounded-2xl p-5 ring-1 ${o.featured ? "ring-rose/40 shadow-glow bg-rose/5" : "ring-overlay/10 bg-overlay/5"}`}>
              {o.featured && <Pill color="rose">Le meilleur deal</Pill>}
              <p className={`mt-2 text-2xl font-black ${o.color}`}>{o.name}</p>
              <p className="text-sm text-muted">{o.split} créateur/plateforme</p>
              <ul className="mt-3 space-y-1.5 text-xs">
                {o.pros.map(p => (
                  <li key={p} className="flex items-center gap-2"><CheckCircle2 size={12} className="text-success" />{p}</li>
                ))}
                {o.cons?.map(c => (
                  <li key={c} className="flex items-center gap-2 text-muted"><span className="w-3 text-center">✕</span>{c}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </section>

      {/* TOUS LES OUTILS */}
      <section>
        <header className="mb-8 text-center">
          <Pill color="rose">Ton studio inclus</Pill>
          <h2 className="mt-3 text-3xl sm:text-4xl font-black">Tout ce dont tu as besoin</h2>
        </header>
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {[
            { icon: Tv, t: "Live HD intégré", d: "Pas besoin d'OBS. Tu cliques, tu streames depuis ton tel ou ordi." },
            { icon: Coins, t: "Paiements Stripe", d: "CB, Apple Pay, SEPA. Virement le 5 du mois suivant. Auto." },
            { icon: TrendingUp, t: "Analytics propres", d: "Vues, taux de complétion, churn, conversion. Aucune surprise." },
            { icon: Crown, t: "Niveaux d'abos", d: "Free + Mensuel + Annuel + Pack programme. Multi-tier inclus." },
            { icon: Heart, t: "DMs & communauté", d: "Tes abonnés te parlent. Tu réponds. Une vraie relation." },
            { icon: Sparkles, t: "Suggestions IA", d: "On te dit quoi poster, quand, à qui. Tu ne navigues pas dans le brouillard." },
            { icon: Zap, t: "Page profil belle", d: "Aucun code requis. Banner, story, certifs, contenu — c'est prêt." },
            { icon: CheckCircle2, t: "Modération assurée", d: "On gère les trolls, les abus, les remboursements. Tu te concentres sur ton métier." },
          ].map(o => (
            <div key={o.t} className="rounded-2xl bg-overlay/5 ring-1 ring-overlay/10 p-5">
              <o.icon size={20} className="text-rose mb-2" />
              <p className="font-bold">{o.t}</p>
              <p className="text-xs text-muted mt-1">{o.d}</p>
            </div>
          ))}
        </div>
      </section>

      {/* TESTIMONIALS */}
      <section>
        <header className="mb-8 text-center">
          <Pill color="sky">Témoignages</Pill>
          <h2 className="mt-3 text-3xl sm:text-4xl font-black">Ce qu'ils en disent</h2>
        </header>
        <div className="grid sm:grid-cols-3 gap-5">
          {CREATORS.slice(0, 3).map(c => (
            <div key={c.id} className="rounded-2xl glass p-5 ring-1 ring-overlay/10">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-2xl grid place-items-center font-black text-black" style={{ background: c.banner }}>{c.avatar}</div>
                <div className="min-w-0">
                  <p className="font-black truncate">{c.name}</p>
                  <p className="text-xs text-muted truncate">{c.handle}</p>
                </div>
              </div>
              <p className="mt-4 text-sm italic text-foreground/80 line-clamp-3">"{c.story}"</p>
              <p className="mt-4 font-black rose-text">{fmtEUR(c.monthlyEarningsEUR * 0.8, 0)}/mois</p>
            </div>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section className="text-center py-8">
        <Link href="/dashboard" className="inline-flex items-center gap-2 px-8 py-4 rounded-xl rose-gradient text-black font-black shadow-glow">
          <Sparkles size={20} /> Lancer mon studio
          <ArrowRight size={18} />
        </Link>
        <p className="mt-3 text-xs text-muted">Gratuit. Aucune carte requise. Tu peux activer ton abonnement quand tu veux.</p>
      </section>
    </div>
  );
}
