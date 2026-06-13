import Link from "next/link";
import { ArrowRight, Tv, BookOpen, MessageCircle, ChevronRight, Users, Sparkles } from "lucide-react";
import { CreatorCard } from "../components/CreatorCard";
import { FEATURED_CREATORS, LIVE_NOW, ALL_CATEGORIES, platformTotals } from "../lib/mock";
import { compact, fmtEUR } from "../lib/format";

export default function Home() {
  const totals = platformTotals();
  const liveNow = LIVE_NOW.slice(0, 3);

  return (
    <div className="space-y-32 pb-12">
      {/* ─── HERO POSITIONING ─── */}
      <section className="pt-20 sm:pt-28">
        <p className="text-xs uppercase tracking-[0.28em] text-muted mb-8">unblur · bêta · 🇨🇭 → 🌍 francophone → monde</p>
        <h1 className="text-5xl sm:text-7xl lg:text-[7.5rem] font-black tracking-tightest leading-[0.92] max-w-5xl">
          L'écosystème<br />
          des créateurs sportifs.
        </h1>
        <p className="mt-10 text-xl sm:text-2xl text-muted max-w-2xl leading-snug">
          <strong className="text-foreground">TikTok</strong> pour les shorts. <strong className="text-foreground">Twitch</strong> pour les lives. <strong className="text-foreground">OnlyFans</strong> pour la rémunération. <strong className="text-foreground">L'encyclopédie</strong> des exercices.
        </p>
        <p className="mt-4 text-base text-muted max-w-2xl">
          80 % du revenu va au créateur. Toujours. Lancement Suisse puis tous les pays francophones.
        </p>
      </section>

      {/* ─── 3-IN-1 — mention explicite ─── */}
      <section className="border-y border-border py-12">
        <p className="text-xs uppercase tracking-[0.28em] text-muted mb-6">unblur, c'est quatre plateformes dans une</p>
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-10">
          <div>
            <p className="text-[11px] uppercase tracking-widest font-black text-rose mb-2">TikTok</p>
            <p className="font-black text-2xl tracking-tight">Shorts gratuits</p>
            <p className="text-sm text-muted mt-2 leading-relaxed">Vertical, 15-60s. Tips, motivation, behind-the-scenes.</p>
          </div>
          <div>
            <p className="text-[11px] uppercase tracking-widest font-black text-rose mb-2">Twitch</p>
            <p className="font-black text-2xl tracking-tight">Lives en direct</p>
            <p className="text-sm text-muted mt-2 leading-relaxed">Sessions illimitées, chat actif. Live en 1 clic depuis le compte créateur.</p>
          </div>
          <div>
            <p className="text-[11px] uppercase tracking-widest font-black text-rose mb-2">OnlyFans</p>
            <p className="font-black text-2xl tracking-tight">Abonnement direct</p>
            <p className="text-sm text-muted mt-2 leading-relaxed">Tu fixes ton prix. Tu gardes 80 %. Sans algorithme.</p>
          </div>
          <div>
            <p className="text-[11px] uppercase tracking-widest font-black text-rose mb-2">Encyclopédie</p>
            <p className="font-black text-2xl tracking-tight">Tous les exercices</p>
            <p className="text-sm text-muted mt-2 leading-relaxed">Bibliothèque complète : machines, exercices, technique, démos. La référence francophone.</p>
          </div>
        </div>
      </section>

      {/* ─── DUAL CHOICE — 2 chemins clairs ─── */}
      <section>
        <p className="text-xs uppercase tracking-[0.28em] text-muted mb-6">Tu es là pour</p>
        <div className="grid lg:grid-cols-2 gap-6">
          {/* CHOICE 1 — SUIVRE UN CRÉATEUR */}
          <Link href="/discover" className="group block rounded-3xl border border-border hover:border-foreground/40 p-8 sm:p-10 transition relative overflow-hidden">
            <div className="flex items-start justify-between mb-8">
              <Users size={28} />
              <span className="text-[10px] uppercase tracking-widest font-bold text-muted">01 / Abonné</span>
            </div>
            <h2 className="text-3xl sm:text-5xl font-black tracking-tighter leading-[1.05]">
              Suivre un<br />créateur.
            </h2>
            <p className="mt-6 text-base text-muted leading-relaxed max-w-md">
              Abonne-toi à un Unblurer. Accès aux lives, replays, programmes structurés, communauté privée et DMs directs.
            </p>
            <div className="mt-8 inline-flex items-center gap-1.5 font-bold text-sm">
              Découvrir les Unblurers <ArrowRight size={14} className="group-hover:translate-x-1 transition" />
            </div>
          </Link>

          {/* CHOICE 2 — DEVENIR CRÉATEUR */}
          <Link href="/become-creator" className="group block rounded-3xl bg-foreground text-surface p-8 sm:p-10 transition relative overflow-hidden hover:opacity-95">
            <div className="flex items-start justify-between mb-8">
              <Sparkles size={28} />
              <span className="text-[10px] uppercase tracking-widest font-bold opacity-60">02 / Créateur</span>
            </div>
            <h2 className="text-3xl sm:text-5xl font-black tracking-tighter leading-[1.05]">
              Devenir<br />Unblurer.
            </h2>
            <p className="mt-6 text-base opacity-75 leading-relaxed max-w-md">
              Filme-toi. Crée des programmes pour TA communauté. Anime un canal privé façon WhatsApp. Tu fixes le prix, tu gardes 80 %.
            </p>
            <div className="mt-8 inline-flex items-center gap-1.5 font-bold text-sm">
              Lancer mon studio <ArrowRight size={14} className="group-hover:translate-x-1 transition" />
            </div>
          </Link>
        </div>
      </section>

      {/* ─── DEFINITION UNBLURER ─── */}
      <section className="border-y border-border py-16">
        <p className="text-xs uppercase tracking-[0.28em] text-muted mb-4">Un Unblurer</p>
        <p className="text-2xl sm:text-4xl font-black tracking-tight leading-[1.15] max-w-4xl">
          Un créateur qui partage sa pratique <span className="text-muted">— sport, cuisine, art, musique, méthode —</span> sans filtre, en direct, avec sa communauté.
        </p>

        <div className="mt-16 grid sm:grid-cols-3 gap-10">
          <Feature icon={Tv}            t="Lives illimités"       d="Sessions en direct sans limite de durée. Player intégré, chat actif, replays sauvegardés." />
          <Feature icon={BookOpen}      t="Programmes communauté" d="Crée des parcours pour TA communauté. Plan jour par jour, cohorte privée." />
          <Feature icon={MessageCircle} t="Canal privé groupe"    d="Comme WhatsApp : channels par thème, DMs, voix, sondages. Tes abonnés te parlent vraiment." />
        </div>
      </section>

      {/* ─── LIVE NOW ─── */}
      <section>
        <header className="flex items-end justify-between mb-10">
          <div>
            <p className="text-xs uppercase tracking-[0.28em] text-muted mb-3">En direct</p>
            <h2 className="text-3xl sm:text-5xl font-black tracking-tighter">{liveNow.length} sessions live</h2>
          </div>
          <Link href="/live" className="text-sm font-semibold underline underline-offset-4">Tout voir</Link>
        </header>
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {liveNow.map(c => <CreatorCard key={c.id} creator={c} />)}
        </div>
      </section>

      {/* ─── FEATURED ─── */}
      <section>
        <header className="mb-10">
          <p className="text-xs uppercase tracking-[0.28em] text-muted mb-3">À découvrir</p>
          <h2 className="text-3xl sm:text-5xl font-black tracking-tighter">Quatre Unblurers cette semaine</h2>
        </header>
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {FEATURED_CREATORS.map(c => <CreatorCard key={c.id} creator={c} compactMode />)}
        </div>
      </section>

      {/* ─── CATEGORIES ─── */}
      <section>
        <header className="mb-10">
          <p className="text-xs uppercase tracking-[0.28em] text-muted mb-3">Tous les domaines</p>
          <h2 className="text-3xl sm:text-5xl font-black tracking-tighter">Sport. Et bien au-delà.</h2>
          <p className="mt-3 text-muted">unblur démarre avec le sport et la remise en forme. Un Unblurer peut enseigner n'importe quel domaine.</p>
        </header>
        <div className="flex flex-wrap gap-2">
          {[...ALL_CATEGORIES, "Cuisine", "Musique", "Méthode", "Art", "Productivité", "Langues"].map(cat => (
            <Link key={cat} href={`/discover?cat=${cat}`} className="px-4 py-2 rounded-full ring-1 ring-foreground/15 hover:bg-foreground hover:text-surface text-sm font-semibold transition">
              {cat}
            </Link>
          ))}
        </div>
      </section>

      {/* ─── DEAL ─── */}
      <section className="border-y border-border py-20">
        <div className="grid lg:grid-cols-2 gap-12 items-start">
          <div>
            <p className="text-xs uppercase tracking-[0.28em] text-muted mb-3">Le deal</p>
            <h2 className="text-4xl sm:text-6xl font-black tracking-tighter leading-[1.05]">80 % au créateur.</h2>
            <p className="mt-6 text-lg text-muted max-w-md leading-relaxed">
              OnlyFans : 80/20 mais image sulfureuse. Twitch : 50/50. Patreon : 88/12 mais zéro vidéo. unblur : la justice, l'authenticité, et le sérieux du sport et de la pratique.
            </p>
          </div>
          <div className="space-y-px text-lg">
            {[
              { l: "unblur", v: "80 / 20", featured: true },
              { l: "OnlyFans", v: "80 / 20" },
              { l: "Patreon", v: "88 / 12" },
              { l: "Twitch", v: "50 / 50" },
              { l: "YouTube", v: "55 / 45" },
            ].map(o => (
              <div key={o.l} className={`flex items-baseline justify-between py-4 border-b border-border ${o.featured ? "font-black text-2xl" : "text-muted"}`}>
                <span>{o.l}</span>
                <span className="font-mono tabular-nums">{o.v}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ─── METRICS ─── */}
      <section>
        <div className="grid sm:grid-cols-4 gap-8 border-b border-border pb-12">
          <div>
            <p className="text-4xl sm:text-6xl font-black tracking-tighter">{compact(totals.totalCreators * 280)}</p>
            <p className="text-xs uppercase tracking-[0.18em] text-muted mt-3">Unblurers actifs</p>
          </div>
          <div>
            <p className="text-4xl sm:text-6xl font-black tracking-tighter">{compact(totals.totalSubs * 12)}</p>
            <p className="text-xs uppercase tracking-[0.18em] text-muted mt-3">Abonnés</p>
          </div>
          <div>
            <p className="text-4xl sm:text-6xl font-black tracking-tighter">80 %</p>
            <p className="text-xs uppercase tracking-[0.18em] text-muted mt-3">Au créateur, toujours</p>
          </div>
          <div>
            <p className="text-4xl sm:text-6xl font-black tracking-tighter">{fmtEUR(totals.creatorPayout * 12, 0)}</p>
            <p className="text-xs uppercase tracking-[0.18em] text-muted mt-3">Reversé aux Unblurers</p>
          </div>
        </div>
      </section>

      {/* ─── CTA FINAL — re-affirme les 2 chemins ─── */}
      <section className="text-center py-24">
        <p className="text-xs uppercase tracking-[0.28em] text-muted mb-4">Choisis ton côté</p>
        <h2 className="text-5xl sm:text-7xl font-black tracking-tightest leading-[0.95] max-w-3xl mx-auto">
          Suis. Ou crée.
        </h2>
        <p className="mt-6 text-xl text-muted max-w-xl mx-auto leading-snug">
          Les deux côtés d'un même écosystème.
        </p>
        <div className="mt-10 flex flex-wrap gap-3 justify-center">
          <Link href="/discover" className="inline-flex items-center gap-2 px-8 py-4 rounded-full border border-foreground/20 hover:bg-overlay/5 font-semibold transition">
            Découvrir les Unblurers
          </Link>
          <Link href="/become-creator" className="inline-flex items-center gap-2 px-8 py-4 rounded-full bg-foreground text-surface font-semibold hover:opacity-90 transition">
            Devenir Unblurer <ChevronRight size={16} />
          </Link>
        </div>
      </section>
    </div>
  );
}

function Feature({ icon: Icon, t, d }: { icon: any; t: string; d: string }) {
  return (
    <div>
      <Icon size={22} className="mb-3" />
      <p className="font-bold text-lg">{t}</p>
      <p className="text-sm text-muted mt-1 leading-relaxed">{d}</p>
    </div>
  );
}
