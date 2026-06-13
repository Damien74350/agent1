"use client";

import { useEffect, useState, useCallback } from "react";
import Link from "next/link";
import { ChevronLeft, ChevronRight, X } from "lucide-react";

const SLIDES: ((key: number) => any)[] = [
  // 1 — Cover
  () => (
    <Slide bg="dark">
      <div className="text-center max-w-5xl mx-auto px-8">
        <p className="text-xs uppercase tracking-[0.5em] text-surface/40 mb-12">unblur · pitch deck · juin 2026</p>
        <h1 className="text-[10rem] sm:text-[14rem] font-black tracking-tightest leading-[0.85] text-surface">
          unblur<span className="text-rose">.</span>
        </h1>
        <p className="mt-12 text-xl sm:text-3xl text-surface/70 tracking-tight max-w-3xl mx-auto leading-snug">
          L'écosystème des créateurs sportifs.<br />
          <span className="text-surface/40">TikTok + Twitch + OnlyFans + Encyclopédie.</span>
        </p>
        <p className="mt-16 text-xs uppercase tracking-[0.4em] text-surface/30">
          Présentation à ma codeuse · 15 juin 2026
        </p>
      </div>
    </Slide>
  ),

  // 2 — Le pitch en une phrase
  () => (
    <Slide>
      <Eyebrow>La phrase qui résume tout</Eyebrow>
      <Big>
        unblur est <Hl>la première plateforme</Hl> qui combine TikTok, Twitch, OnlyFans et une encyclopédie complète des exercices, focalisée sur le sport, où le créateur devient <Hl>de plus en plus riche</Hl> à mesure qu'il fait grandir la plateforme.
      </Big>
    </Slide>
  ),

  // 3 — Le problème
  () => (
    <Slide>
      <Eyebrow>Problème</Eyebrow>
      <Big>Un coach sport doit jongler entre <Hl>10 outils</Hl>, 4 commissions différentes, et 0 cohérence.</Big>
      <ul className="mt-12 grid grid-cols-2 gap-4 max-w-3xl text-base text-muted">
        {["Instagram (algo contre lui)", "YouTube (55/45)", "Twitch (50/50)", "Patreon (88/12, pas de vidéo)", "OnlyFans (image sulfureuse)", "Calendly, Stripe, Discord, Notion, Mailchimp"].map(s => (
          <li key={s} className="flex items-baseline gap-2"><span className="text-rose">–</span> {s}</li>
        ))}
      </ul>
      <p className="mt-12 text-2xl font-bold">95 % des créateurs sport abandonnent en 18 mois.</p>
    </Slide>
  ),

  // 4 — La solution
  () => (
    <Slide>
      <Eyebrow>Solution — 4 dimensions, 1 plateforme</Eyebrow>
      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-8 mt-12">
        {[
          { l: "TikTok", t: "Shorts gratuits", d: "Vertical 15-60s. L'entonnoir d'acquisition." },
          { l: "Twitch", t: "Lives en 1 clic", d: "Sessions illimitées, chat, replays auto." },
          { l: "OnlyFans", t: "Abonnement direct", d: "Le créateur fixe son prix. Garde jusqu'à 95%." },
          { l: "Encyclopédie", t: "Bibliothèque", d: "Tous les exercices, machines, techniques. Magnet SEO." },
        ].map(o => (
          <div key={o.l} className="border-l-2 border-rose pl-5">
            <p className="text-[10px] uppercase tracking-widest font-black text-rose">{o.l}</p>
            <p className="mt-3 font-black text-2xl">{o.t}</p>
            <p className="mt-2 text-sm text-muted leading-relaxed">{o.d}</p>
          </div>
        ))}
      </div>
    </Slide>
  ),

  // 5 — Le naming
  () => (
    <Slide>
      <Eyebrow>Naming</Eyebrow>
      <Big>Les créateurs sont des <Hl>Unblurers</Hl>.</Big>
      <ul className="mt-12 space-y-3 text-xl text-muted">
        <li>— Court. 8 lettres.</li>
        <li>— Ownable. Aucun acteur ne l'utilise.</li>
        <li>— Multilingue. FR · EN · DE · IT.</li>
        <li>— Statut social. "Je suis Unblurer."</li>
        <li>— Brevetable comme marque.</li>
      </ul>
    </Slide>
  ),

  // 6 — Business model — intro
  () => (
    <Slide bg="dark">
      <div className="text-center">
        <p className="text-xs uppercase tracking-[0.5em] text-surface/40 mb-8">Notre algorithme économique</p>
        <h2 className="text-7xl sm:text-9xl font-black tracking-tightest leading-[0.9] text-surface">
          Plus tu fais<br /><span className="text-rose">grandir</span> la plateforme,<br />moins tu nous paies.
        </h2>
      </div>
    </Slide>
  ),

  // 7 — Paliers commission
  () => (
    <Slide>
      <Eyebrow>Commission dégressive</Eyebrow>
      <Big>Personne ne fait ça aujourd'hui.</Big>
      <div className="mt-12 max-w-3xl">
        {[
          { range: "0 – 1 000 €", us: 30, them: 70 },
          { range: "1 001 – 5 000 €", us: 20, them: 80 },
          { range: "5 001 – 20 000 €", us: 12, them: 88 },
          { range: "20 001 – 100 000 €", us: 8, them: 92 },
          { range: "100 000 € +", us: 5, them: 95 },
        ].map((p, i) => (
          <div key={i} className="grid grid-cols-3 items-baseline py-5 border-b border-border">
            <p className="text-base font-semibold text-muted">{p.range}/mois</p>
            <p className="text-center text-sm text-muted">unblur prend <span className="text-foreground font-black">{p.us}%</span></p>
            <p className="text-right text-3xl font-black tabular-nums">{p.them}%</p>
          </div>
        ))}
      </div>
    </Slide>
  ),

  // 8 — Mécanique 1 — bonus viralité
  () => (
    <Slide>
      <Eyebrow>Mécanique 1 — Bonus viralité</Eyebrow>
      <Big>Tu parraines un Unblurer qui cartonne ?<br />Tu <Hl>économises 2 points</Hl> de commission pendant 3 mois.</Big>
      <p className="mt-12 text-xl text-muted max-w-3xl leading-relaxed">
        Tes Unblurers font l'acquisition à ta place. Tu n'as plus besoin de team sales. Croissance virale gratuite.
      </p>
    </Slide>
  ),

  // 9 — Mécanique 2 — Founding
  () => (
    <Slide>
      <Eyebrow>Mécanique 2 — Founding Unblurer</Eyebrow>
      <Big>Les <Hl>100 premiers</Hl> signés en Suisse romande gardent à vie leur grille actuelle, même si la commission de base augmente plus tard.</Big>
      <p className="mt-12 text-xl text-muted max-w-3xl leading-relaxed">
        C'est ce qu'Uber a fait avec ses premiers chauffeurs. Une caste protégée qui te défend toute leur carrière contre les nouveaux entrants.
      </p>
    </Slide>
  ),

  // 10 — Mécanique 3 — fidélité (LE brevet)
  () => (
    <Slide bg="dark">
      <div className="max-w-5xl">
        <p className="text-xs uppercase tracking-[0.5em] text-rose mb-8">Mécanique 3 — Brevetable</p>
        <h2 className="text-6xl sm:text-8xl font-black tracking-tightest leading-[0.92] text-surface">
          Multiplicateur de <span className="text-rose">fidélité abonné</span>.
        </h2>
        <p className="mt-12 text-xl text-surface/70 max-w-3xl leading-relaxed">
          Pour chaque abonné qui reste plus de 12 mois chez un créateur, la commission unblur sur cet abonné précis <span className="text-rose font-black">baisse de 1 point par année supplémentaire</span>, jusqu'à un plancher de 5%.
        </p>
        <ul className="mt-10 space-y-2 text-base text-surface/60">
          <li>→ Le créateur a un intérêt direct à fidéliser long-terme</li>
          <li>→ Nous, nous avons un intérêt à ce qu'il les fidélise</li>
          <li>→ Brevet européen "méthode mise en œuvre par ordinateur"</li>
          <li>→ Cabinet PI suisse, budget 12 000 CHF, protection 20 ans</li>
        </ul>
      </div>
    </Slide>
  ),

  // 11 — Palier sponsor
  () => (
    <Slide>
      <Eyebrow>Mécanique 4 — Palier sponsor</Eyebrow>
      <Big>À 20 000 €/mois, l'Unblurer débloque les <Hl>deals sponsors</Hl> orchestrés par unblur.</Big>
      <p className="mt-10 text-xl text-muted leading-relaxed max-w-3xl">
        Decathlon, On Running, Mammut, Lululemon paient pour accéder au top 5%. unblur prend 30%, l'Unblurer 70% — en plus de son revenu abonnés.
      </p>
      <div className="mt-12 grid sm:grid-cols-3 gap-8 max-w-4xl">
        <Stat n="86 600 €" l="Karim garde / mois" />
        <Stat n="23 400 €" l="unblur encaisse / mois" />
        <Stat n="× 200" l="top créateurs en année 4" />
      </div>
    </Slide>
  ),

  // 12 — Le slogan
  () => (
    <Slide bg="dark">
      <div className="max-w-5xl">
        <p className="text-xs uppercase tracking-[0.5em] text-surface/40 mb-12">Le pitch one-liner</p>
        <p className="text-3xl sm:text-5xl font-black tracking-tighter leading-[1.15] text-surface">
          "Sur unblur, plus tu fais grandir la plateforme, moins tu nous paies.<br /><br />
          Plus tes abonnés te restent fidèles, moins on prend sur eux.<br /><br />
          Plus tu cartonnes, plus on te débloque des deals avec les marques.<br /><br />
          <span className="text-rose">Personne d'autre ne fait ça.</span>"
        </p>
      </div>
    </Slide>
  ),

  // 13 — Roadmap géographique
  () => (
    <Slide>
      <Eyebrow>Stratégie géographique</Eyebrow>
      <Big>Suisse → Francophonie → Anglo → Monde.</Big>
      <div className="mt-12 space-y-6 max-w-4xl">
        {[
          { phase: "Phase 1", when: "T3 2026", w: "🇨🇭 Suisse romande", goal: "30 Unblurers · 3 000 abonnés en 6 mois" },
          { phase: "Phase 2", when: "T1 2027", w: "🌍 Francophonie (300 M)", goal: "300 Unblurers · 60 000 abonnés" },
          { phase: "Phase 3", when: "T1 2028", w: "🇬🇧 🇺🇸 Anglo", goal: "1 500 Unblurers · 500 000 abonnés" },
          { phase: "Phase 4", when: "2029+",   w: "🌐 Monde + extension cuisine/art/musique", goal: "8 000+ Unblurers" },
        ].map((p, i) => (
          <div key={i} className="grid grid-cols-12 gap-4 items-baseline py-4 border-b border-border">
            <p className="col-span-2 text-xs uppercase tracking-widest font-bold text-rose">{p.phase}</p>
            <p className="col-span-2 text-sm text-muted">{p.when}</p>
            <p className="col-span-4 font-black text-xl">{p.w}</p>
            <p className="col-span-4 text-sm text-muted text-right">{p.goal}</p>
          </div>
        ))}
      </div>
    </Slide>
  ),

  // 14 — MVP technique
  () => (
    <Slide>
      <Eyebrow>MVP technique — 12 semaines</Eyebrow>
      <Big>Le strict minimum pour signer 30 créateurs et générer du chiffre.</Big>
      <ol className="mt-12 space-y-3 max-w-4xl text-lg">
        {[
          { s: "S1-2", t: "Auth + profil créateur", stack: "Clerk, PostgreSQL + Prisma" },
          { s: "S2-4", t: "Paywall Stripe Connect 80/20", stack: "Stripe Connect Express, webhooks signés" },
          { s: "S4-7", t: "Lives — le cœur du produit", stack: "Mux (recommandé) vs Livepeer vs LiveKit" },
          { s: "S7-9", t: "DMs + canal communautaire", stack: "Pusher Channels ou Soketi" },
          { s: "S9-12", t: "Replays + bibliothèque vidéo", stack: "Cloudinary + transcodage" },
        ].map((o, i) => (
          <li key={i} className="grid grid-cols-12 gap-4 items-baseline py-3 border-b border-border">
            <span className="col-span-1 font-mono text-sm text-rose">{o.s}</span>
            <span className="col-span-5 font-bold">{o.t}</span>
            <span className="col-span-6 text-sm text-muted">{o.stack}</span>
          </li>
        ))}
      </ol>
    </Slide>
  ),

  // 15 — Anti-roadmap
  () => (
    <Slide>
      <Eyebrow>Anti-roadmap — ce qu'on NE fait PAS</Eyebrow>
      <Big>Ce qui te tue, c'est ce que tu fais en trop.<br />Pas ce que tu ne fais pas.</Big>
      <div className="mt-12 grid sm:grid-cols-2 gap-x-12 gap-y-4 max-w-4xl">
        {[
          ["Shorts vidéo", "v2 — mois 4-6"],
          ["Bibliothèque exercices complète", "v2 — mois 4-7"],
          ["Programmes structurés avancés", "v2 — mois 6-8"],
          ["App mobile native iOS/Android", "v3 — mois 12+"],
          ["Boost interne (pub créateur)", "2027+"],
          ["Deals sponsors orchestrés", "2028"],
          ["Marketplace équipement", "2029"],
          ["API publique B2B", "2029+"],
        ].map(([t, when], i) => (
          <div key={i} className="flex items-baseline gap-3">
            <span className="text-rose">✕</span>
            <div>
              <p className="font-bold">{t}</p>
              <p className="text-xs text-muted">{when}</p>
            </div>
          </div>
        ))}
      </div>
    </Slide>
  ),

  // 16 — Trajectoire financière
  () => (
    <Slide>
      <Eyebrow>Trajectoire financière</Eyebrow>
      <Big>De rentable en année 1<br />à <Hl>pré-licorne en année 7</Hl>.</Big>
      <div className="mt-12 grid sm:grid-cols-4 gap-6 max-w-5xl">
        {[
          { y: "An 1", arr: "240 k€",  zone: "Suisse", what: "100 Unblurers · équilibre" },
          { y: "An 3", arr: "2,4 M€",  zone: "Francophonie", what: "1 500 Unblurers · marge 1,2 M" },
          { y: "An 5", arr: "17 M€",   zone: "Anglo", what: "8 000 Unblurers · marge 5 M" },
          { y: "An 7", arr: "80-100 M€", zone: "Monde", what: "Valo 640-800 M · pré-licorne" },
        ].map((s, i) => (
          <div key={i} className={`p-6 rounded-3xl ${i === 3 ? "bg-foreground text-surface" : "border border-border"}`}>
            <p className={`text-xs uppercase tracking-widest font-bold ${i === 3 ? "text-rose" : "text-rose"}`}>{s.y}</p>
            <p className="mt-3 text-3xl font-black tabular-nums tracking-tighter">{s.arr}</p>
            <p className="text-[10px] uppercase tracking-widest mt-1 opacity-70">ARR · {s.zone}</p>
            <p className={`mt-4 text-xs ${i === 3 ? "text-surface/70" : "text-muted"} leading-relaxed`}>{s.what}</p>
          </div>
        ))}
      </div>
    </Slide>
  ),

  // 17 — Levée de fonds
  () => (
    <Slide>
      <Eyebrow>Levée de fonds prévisionnelle</Eyebrow>
      <Big>3 tours sur 5 ans.</Big>
      <div className="mt-12 space-y-6 max-w-4xl">
        {[
          { t: "Pré-seed", w: "maintenant", a: "500-800 k CHF", use: "MVP · recrutement Suisse · runway 18 mois", who: "Investiere, Verve, Innosuisse, FONGIT" },
          { t: "Seed",     w: "+18 mois",   a: "3 M CHF",        use: "Internationalisation francophone · équipe 15", who: "Speedinvest, Index Ventures, Heartcore" },
          { t: "Series A", w: "+36 mois",   a: "15 M CHF",       use: "Anglo + monde", who: "Atomico, Accel, a16z creator economy fund" },
        ].map((r, i) => (
          <div key={i} className="grid grid-cols-12 gap-4 items-baseline py-4 border-b border-border">
            <p className="col-span-2 text-xs uppercase tracking-widest font-bold text-rose">{r.t}</p>
            <p className="col-span-2 text-sm text-muted">{r.w}</p>
            <p className="col-span-2 font-black text-xl">{r.a}</p>
            <p className="col-span-3 text-sm text-muted">{r.use}</p>
            <p className="col-span-3 text-xs text-muted text-right">{r.who}</p>
          </div>
        ))}
      </div>
    </Slide>
  ),

  // 18 — Ce qu'on attend de la codeuse
  () => (
    <Slide>
      <Eyebrow>Ce qu'on te demande</Eyebrow>
      <Big>3 décisions à prendre ensemble lundi.</Big>
      <ol className="mt-12 space-y-6 max-w-4xl text-xl">
        <li className="flex gap-5 items-baseline"><span className="text-4xl font-black text-rose tabular-nums">01</span> <span>Faisabilité technique du MVP en 12 semaines avec 1 dev senior ?</span></li>
        <li className="flex gap-5 items-baseline"><span className="text-4xl font-black text-rose tabular-nums">02</span> <span>Choix techno définitifs : Mux ou alternative ? Persistance ? Auth ?</span></li>
        <li className="flex gap-5 items-baseline"><span className="text-4xl font-black text-rose tabular-nums">03</span> <span>Modalité de collaboration : co-fondatrice equity, salariée senior, ou freelance forfait ?</span></li>
      </ol>
    </Slide>
  ),

  // 19 — Options collaboration
  () => (
    <Slide>
      <Eyebrow>3 options sur la table</Eyebrow>
      <div className="grid sm:grid-cols-3 gap-6 mt-12">
        {[
          { t: "A · Co-fondatrice", s: "2-3 k CHF/mois", e: "12-20% equity vesting 4 ans", who: "Si tu crois fort au projet" },
          { t: "B · Salariée senior", s: "8-10 k CHF/mois", e: "Stock options après 12 mois", who: "Si tu veux sécuriser" },
          { t: "C · Freelance MVP", s: "60-100 k CHF forfait", e: "Pas d'engagement long-terme", who: "Si tu veux tester d'abord" },
        ].map((o, i) => (
          <div key={i} className={`p-6 rounded-3xl ${i === 0 ? "bg-foreground text-surface" : "border border-border"}`}>
            <p className="text-2xl font-black mb-4">{o.t}</p>
            <p className="text-sm opacity-70 uppercase tracking-widest font-bold">Rémunération</p>
            <p className="mt-1 font-bold">{o.s}</p>
            <p className="mt-4 text-sm opacity-70 uppercase tracking-widest font-bold">Equity</p>
            <p className="mt-1 font-bold">{o.e}</p>
            <p className="mt-6 text-xs opacity-60 italic">{o.who}</p>
          </div>
        ))}
      </div>
    </Slide>
  ),

  // 20 — Timing
  () => (
    <Slide>
      <Eyebrow>Timing impératif</Eyebrow>
      <div className="mt-8 space-y-12 max-w-4xl">
        <div>
          <p className="text-rose font-black text-7xl tracking-tighter tabular-nums">Août 2026</p>
          <p className="mt-3 text-xl text-muted">Bêta privée avec 5 Unblurers tests en Suisse romande</p>
        </div>
        <div>
          <p className="text-rose font-black text-7xl tracking-tighter tabular-nums">Octobre 2026</p>
          <p className="mt-3 text-xl text-muted">Ouverture publique Suisse romande</p>
        </div>
        <div>
          <p className="text-foreground font-black text-7xl tracking-tighter tabular-nums">T1 2027</p>
          <p className="mt-3 text-xl text-muted">Démarrage Francophonie</p>
        </div>
      </div>
    </Slide>
  ),

  // 21 — Closing
  () => (
    <Slide bg="dark">
      <div className="text-center max-w-5xl mx-auto">
        <p className="text-xs uppercase tracking-[0.5em] text-surface/40 mb-12">Pour conclure</p>
        <h2 className="text-6xl sm:text-9xl font-black tracking-tightest leading-[0.9] text-surface">
          On construit<br /><span className="text-rose">la licorne</span><br />ensemble<span className="text-rose">.</span>
        </h2>
        <p className="mt-16 text-2xl text-surface/60 max-w-2xl mx-auto leading-snug">
          La démo est en ligne. Le concept est verrouillé. Le brevet est prêt à déposer. Il manque juste ton code.
        </p>
        <p className="mt-12 text-xs uppercase tracking-[0.5em] text-surface/30">
          unblur-app.vercel.app · Damien74350/agent1 · branche main
        </p>
      </div>
    </Slide>
  ),
];

export default function PitchPage() {
  const [idx, setIdx] = useState(0);

  const next = useCallback(() => setIdx(i => Math.min(SLIDES.length - 1, i + 1)), []);
  const prev = useCallback(() => setIdx(i => Math.max(0, i - 1)), []);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "ArrowRight" || e.key === " " || e.key === "PageDown") { e.preventDefault(); next(); }
      else if (e.key === "ArrowLeft" || e.key === "PageUp") { e.preventDefault(); prev(); }
      else if (e.key === "Home") setIdx(0);
      else if (e.key === "End") setIdx(SLIDES.length - 1);
      else if (e.key === "Escape") {} // could close fullscreen
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [next, prev]);

  const Slide = SLIDES[idx];

  return (
    <div className="fixed inset-0 bg-canvas overflow-hidden" style={{ background: "var(--bg-base)" }}>
      <div key={idx} className="absolute inset-0 animate-[fadeIn_0.4s_ease-out]">
        {Slide(idx)}
      </div>

      {/* Controls */}
      <div className="absolute top-4 right-4 flex items-center gap-2 z-50">
        <span className="text-xs font-mono tabular-nums px-3 py-1.5 rounded-full bg-surface/80 backdrop-blur ring-1 ring-border">
          {String(idx + 1).padStart(2, "0")} / {String(SLIDES.length).padStart(2, "0")}
        </span>
        <Link href="/" className="p-1.5 rounded-full bg-surface/80 backdrop-blur ring-1 ring-border hover:opacity-90">
          <X size={14} />
        </Link>
      </div>

      <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex items-center gap-3 z-50">
        <button onClick={prev} disabled={idx === 0} className="p-3 rounded-full bg-surface/80 backdrop-blur ring-1 ring-border hover:opacity-90 disabled:opacity-30">
          <ChevronLeft size={18} />
        </button>
        <div className="flex gap-1 px-3 py-2 rounded-full bg-surface/80 backdrop-blur ring-1 ring-border max-w-[40vw] overflow-hidden">
          {SLIDES.map((_, i) => (
            <button key={i} onClick={() => setIdx(i)} className={`h-1.5 rounded-full transition-all ${i === idx ? "bg-foreground w-6" : "bg-foreground/20 w-1.5"}`} />
          ))}
        </div>
        <button onClick={next} disabled={idx === SLIDES.length - 1} className="p-3 rounded-full bg-surface/80 backdrop-blur ring-1 ring-border hover:opacity-90 disabled:opacity-30">
          <ChevronRight size={18} />
        </button>
      </div>

      <div className="absolute bottom-4 right-4 text-[10px] text-muted font-mono z-50">
        ← → · espace · home · end
      </div>

      <style jsx global>{`
        @keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
      `}</style>
    </div>
  );
}

// ─── COMPOSANTS PRIMITIFS DE SLIDE ───

function Slide({ children, bg = "light" }: { children: React.ReactNode; bg?: "light" | "dark" }) {
  return (
    <div className={`absolute inset-0 grid place-items-center px-12 sm:px-20 ${bg === "dark" ? "bg-foreground text-surface" : "bg-canvas text-foreground"}`} style={bg === "light" ? { background: "var(--bg-base)" } : {}}>
      <div className="w-full max-w-7xl">
        {children}
      </div>
    </div>
  );
}

function Eyebrow({ children }: { children: React.ReactNode }) {
  return <p className="text-xs uppercase tracking-[0.4em] text-rose font-bold mb-6">{children}</p>;
}

function Big({ children }: { children: React.ReactNode }) {
  return <h2 className="text-4xl sm:text-6xl lg:text-7xl font-black tracking-tightest leading-[1.02]">{children}</h2>;
}

function Hl({ children }: { children: React.ReactNode }) {
  return <span className="text-rose">{children}</span>;
}

function Stat({ n, l }: { n: string; l: string }) {
  return (
    <div>
      <p className="text-4xl sm:text-6xl font-black tabular-nums tracking-tighter">{n}</p>
      <p className="text-xs uppercase tracking-widest text-muted font-bold mt-3">{l}</p>
    </div>
  );
}
