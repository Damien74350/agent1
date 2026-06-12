import Link from "next/link";
import { ArrowRight, Tv, BookOpen, MessageCircle, ChevronRight } from "lucide-react";
import { CreatorCard } from "../components/CreatorCard";
import { FEATURED_CREATORS, LIVE_NOW, ALL_CATEGORIES, platformTotals } from "../lib/mock";
import { compact, fmtEUR } from "../lib/format";

export default function Home() {
  const totals = platformTotals();
  const liveNow = LIVE_NOW.slice(0, 3);

  return (
    <div className="space-y-32 pb-12">
      {/* ─── HERO ─── */}
      <section className="pt-20 sm:pt-32">
        <p className="text-xs uppercase tracking-[0.28em] text-muted mb-8">unblur · bêta</p>
        <h1 className="text-5xl sm:text-7xl lg:text-[8rem] font-black tracking-tightest leading-[0.92] max-w-5xl">
          Le contenu,<br />sans le filtre.
        </h1>
        <p className="mt-10 text-xl sm:text-2xl text-muted max-w-2xl leading-snug">
          Abonne-toi à un <strong className="text-foreground">Unblurer</strong>. Lives en direct, programmes structurés, échanges privés. 80 % revient au créateur.
        </p>
        <div className="mt-12 flex flex-wrap gap-3">
          <Link href="/discover" className="inline-flex items-center gap-2 px-6 py-3 rounded-full bg-foreground text-surface font-semibold hover:opacity-90 transition">
            Découvrir les Unblurers <ArrowRight size={16} />
          </Link>
          <Link href="/become-creator" className="inline-flex items-center gap-2 px-6 py-3 rounded-full ring-1 ring-foreground/20 hover:bg-overlay/5 font-semibold transition">
            Devenir Unblurer
          </Link>
        </div>
      </section>

      {/* ─── DEFINITION ─── */}
      <section className="border-y border-border py-16">
        <p className="text-xs uppercase tracking-[0.28em] text-muted mb-4">Un Unblurer</p>
        <p className="text-3xl sm:text-5xl font-black tracking-tight leading-[1.1] max-w-4xl">
          Un créateur qui partage sa pratique <span className="text-muted">— sport, cuisine, art, musique, méthode —</span> sans filtre, en direct, avec sa communauté.
        </p>

        <div className="mt-16 grid sm:grid-cols-3 gap-10">
          <div>
            <Tv size={22} className="mb-3" />
            <p className="font-bold text-lg">Lives illimités</p>
            <p className="text-sm text-muted mt-1 leading-relaxed">Sessions en direct, sans limite de durée. Player intégré, chat actif, replays sauvegardés automatiquement.</p>
          </div>
          <div>
            <BookOpen size={22} className="mb-3" />
            <p className="font-bold text-lg">Programmes communauté</p>
            <p className="text-sm text-muted mt-1 leading-relaxed">Crée des parcours spécifiques à ta communauté. Plan jour par jour, cohorte privée, durée libre.</p>
          </div>
          <div>
            <MessageCircle size={22} className="mb-3" />
            <p className="font-bold text-lg">Échanges directs</p>
            <p className="text-sm text-muted mt-1 leading-relaxed">DMs chiffrés, feedback vidéo personnalisé, communauté privée. Tes abonnés te parlent vraiment.</p>
          </div>
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
          <p className="mt-3 text-muted">unblur démarre avec le sport et la remise en forme. Mais un Unblurer peut enseigner n'importe quoi.</p>
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
              OnlyFans : 80/20 mais image sulfureuse. Twitch : 50/50. Patreon : 88/12 mais zéro vidéo. unblur : la justice + l'authenticité, sur la qualité technique.
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

      {/* ─── CTA ─── */}
      <section className="text-center py-24">
        <p className="text-xs uppercase tracking-[0.28em] text-muted mb-4">Tu enseignes quelque chose ?</p>
        <h2 className="text-5xl sm:text-7xl font-black tracking-tightest leading-[0.95] max-w-3xl mx-auto">
          Deviens Unblurer.
        </h2>
        <p className="mt-6 text-xl text-muted max-w-xl mx-auto leading-snug">
          Lives. Programmes. Communauté. Stripe intégré. Tu gardes 80 %.
        </p>
        <Link href="/become-creator" className="mt-10 inline-flex items-center gap-2 px-8 py-4 rounded-full bg-foreground text-surface font-semibold hover:opacity-90 transition">
          Lancer mon studio <ChevronRight size={16} />
        </Link>
      </section>
    </div>
  );
}
