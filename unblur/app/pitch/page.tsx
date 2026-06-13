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
          L'écosystème mondial des créateurs sportifs.
        </p>
      </div>
    </Slide>
  ),

  // 2 — Pitch en 1 phrase
  () => (
    <Slide>
      <Eyebrow>Ce que c'est</Eyebrow>
      <Big>
        unblur, c'est <Hl>TikTok + Twitch + OnlyFans + l'encyclopédie complète des exercices</Hl> — réunis sur une seule plateforme, focalisée sur le sport et la pratique sérieuse.
      </Big>
    </Slide>
  ),

  // 3 — Le problème
  () => (
    <Slide>
      <Eyebrow>Le problème mondial</Eyebrow>
      <Big>Un coach sport jongle entre <Hl>10 outils</Hl>, 4 commissions, et 0 cohérence.</Big>
      <ul className="mt-12 grid grid-cols-2 gap-4 max-w-3xl text-base text-muted">
        {["Instagram (algo contre lui)", "YouTube (55/45)", "Twitch (50/50, gaming)", "Patreon (88/12, sans vidéo)", "OnlyFans (image sulfureuse)", "Calendly · Stripe · Discord · Notion · Mailchimp"].map(s => (
          <li key={s} className="flex items-baseline gap-2"><span className="text-rose">–</span> {s}</li>
        ))}
      </ul>
      <p className="mt-12 text-2xl font-bold">Résultat : <Hl>95 % des créateurs sport abandonnent en 18 mois.</Hl></p>
    </Slide>
  ),

  // 4 — Solution
  () => (
    <Slide>
      <Eyebrow>La solution — 4 dimensions, 1 plateforme</Eyebrow>
      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-8 mt-12">
        {[
          { l: "TikTok", t: "Shorts gratuits", d: "Vertical 15-60s. L'entonnoir d'acquisition mondial." },
          { l: "Twitch", t: "Lives en 1 clic", d: "Sessions illimitées, chat actif, replays auto." },
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

  // 5 — Naming
  () => (
    <Slide>
      <Eyebrow>Le créateur a un nom</Eyebrow>
      <Big>Il s'appelle <Hl>Unblurer</Hl>.</Big>
      <ul className="mt-12 space-y-3 text-xl text-muted">
        <li>— Court. 8 lettres. Mémorisable.</li>
        <li>— Ownable. Aucun acteur ne l'utilise.</li>
        <li>— Multilingue. FR · EN · DE · IT · ES.</li>
        <li>— Statut social. "Je suis Unblurer."</li>
        <li>— Brevetable comme marque mondiale.</li>
      </ul>
    </Slide>
  ),

  // 6 — Intro algo (dark)
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

  // 7 — Commission dégressive
  () => (
    <Slide>
      <Eyebrow>Commission dégressive — unique au monde</Eyebrow>
      <Big>Personne ne fait ça aujourd'hui.</Big>
      <div className="mt-12 max-w-3xl">
        {[
          { range: "0 – 1 000 €",       us: 30, them: 70 },
          { range: "1 001 – 5 000 €",   us: 20, them: 80 },
          { range: "5 001 – 20 000 €",  us: 12, them: 88 },
          { range: "20 001 – 100 000 €", us: 8, them: 92 },
          { range: "100 000 € +",        us: 5, them: 95 },
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

  // 8 — Bonus viralité
  () => (
    <Slide>
      <Eyebrow>Mécanique 1 — Bonus viralité</Eyebrow>
      <Big>Un Unblurer en parraine un autre ?<br />Il <Hl>économise 2 points</Hl> de commission pendant 3 mois.</Big>
      <p className="mt-12 text-xl text-muted max-w-3xl leading-relaxed">
        Les Unblurers font l'acquisition à ma place. Aucune équipe sales. Croissance virale mondiale gratuite.
      </p>
    </Slide>
  ),

  // 9 — Founding Unblurer
  () => (
    <Slide>
      <Eyebrow>Mécanique 2 — Founding Unblurer</Eyebrow>
      <Big>Les <Hl>100 premiers signés en Suisse</Hl> gardent leur grille à vie, même si la commission de base augmente plus tard.</Big>
      <p className="mt-12 text-xl text-muted max-w-3xl leading-relaxed">
        Comme Uber avec ses premiers chauffeurs, Airbnb avec ses premiers hôtes. Une caste protégée qui défend la plateforme contre les nouveaux entrants.
      </p>
    </Slide>
  ),

  // 10 — Brevetable — multiplicateur fidélité (dark)
  () => (
    <Slide bg="dark">
      <div className="max-w-5xl">
        <p className="text-xs uppercase tracking-[0.5em] text-rose mb-8">Mécanique 3 — Brevet mondial déposé</p>
        <h2 className="text-6xl sm:text-8xl font-black tracking-tightest leading-[0.92] text-surface">
          Multiplicateur de <span className="text-rose">fidélité abonné</span>.
        </h2>
        <p className="mt-12 text-xl text-surface/70 max-w-3xl leading-relaxed">
          Pour chaque abonné qui reste plus de 12 mois chez un créateur, ma commission sur cet abonné précis <span className="text-rose font-black">baisse de 1 point par année supplémentaire</span>, plancher à 5%.
        </p>
        <ul className="mt-10 space-y-2 text-base text-surface/60">
          <li>→ Le créateur a un intérêt direct à fidéliser long-terme</li>
          <li>→ Nous avons intérêt à ce qu'il les fidélise</li>
          <li>→ Brevet européen "méthode mise en œuvre par ordinateur"</li>
          <li>→ Cabinet PI suisse · 12 000 CHF · 20 ans de protection</li>
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
        Decathlon, On Running, Mammut, Lululemon paient unblur pour accéder au top 5%. Je prends 30%, l'Unblurer 70% — en plus de son revenu abonnés.
      </p>
      <div className="mt-12 grid sm:grid-cols-3 gap-8 max-w-4xl">
        <Stat n="86 600 €" l="Un Unblurer top garde / mois" />
        <Stat n="23 400 €" l="unblur encaisse / mois" />
        <Stat n="× 200" l="top créateurs en année 4" />
      </div>
    </Slide>
  ),

  // 12 — Slogan (dark)
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

  // 13 — Bibliothèque exercices (SEO magnet)
  () => (
    <Slide>
      <Eyebrow>L'arme cachée — l'Encyclopédie</Eyebrow>
      <Big>La bibliothèque de <Hl>tous les exercices</Hl> et <Hl>toutes les machines</Hl> du sport.</Big>
      <div className="mt-12 grid sm:grid-cols-3 gap-8 max-w-5xl">
        <div>
          <p className="text-5xl font-black tracking-tighter">500+</p>
          <p className="text-xs uppercase tracking-widest text-muted font-bold mt-3">Exercices référencés à 18 mois</p>
        </div>
        <div>
          <p className="text-5xl font-black tracking-tighter">15</p>
          <p className="text-xs uppercase tracking-widest text-muted font-bold mt-3">Groupes musculaires</p>
        </div>
        <div>
          <p className="text-5xl font-black tracking-tighter">M+</p>
          <p className="text-xs uppercase tracking-widest text-muted font-bold mt-3">Recherches Google captables/an</p>
        </div>
      </div>
      <p className="mt-12 text-lg text-muted max-w-3xl leading-relaxed">
        Magnet SEO massif gratuit. Outil quotidien que les sportifs ouvrent en salle, même sans abonnement. Funnel parfait vers la conversion premium. Fossé défensif que TikTok, Twitch, OnlyFans ne peuvent pas copier.
      </p>
    </Slide>
  ),

  // 14 — Roadmap géographique
  () => (
    <Slide>
      <Eyebrow>Stratégie mondiale</Eyebrow>
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

  // 15 — Trajectoire financière
  () => (
    <Slide>
      <Eyebrow>Trajectoire financière</Eyebrow>
      <Big>Rentable en année 1.<br /><Hl>Pré-licorne en année 7.</Hl></Big>
      <div className="mt-12 grid sm:grid-cols-4 gap-6 max-w-5xl">
        {[
          { y: "An 1", arr: "240 k€",   zone: "Suisse",       what: "100 Unblurers · équilibre" },
          { y: "An 3", arr: "2,4 M€",   zone: "Francophonie", what: "1 500 Unblurers · marge 1,2 M" },
          { y: "An 5", arr: "17 M€",    zone: "Anglo",        what: "8 000 Unblurers · marge 5 M" },
          { y: "An 7", arr: "80-100 M€",zone: "Monde",        what: "Valo 640-800 M · pré-licorne" },
        ].map((s, i) => (
          <div key={i} className={`p-6 rounded-3xl ${i === 3 ? "bg-foreground text-surface" : "border border-border"}`}>
            <p className="text-xs uppercase tracking-widest font-bold text-rose">{s.y}</p>
            <p className="mt-3 text-3xl font-black tabular-nums tracking-tighter">{s.arr}</p>
            <p className="text-[10px] uppercase tracking-widest mt-1 opacity-70">ARR · {s.zone}</p>
            <p className={`mt-4 text-xs ${i === 3 ? "text-surface/70" : "text-muted"} leading-relaxed`}>{s.what}</p>
          </div>
        ))}
      </div>
    </Slide>
  ),

  // 16 — Propriété intellectuelle
  () => (
    <Slide>
      <Eyebrow>Propriété intellectuelle</Eyebrow>
      <Big>Ma forteresse juridique mondiale.</Big>
      <div className="mt-12 space-y-5 max-w-4xl text-lg">
        {[
          { t: "Marque 'unblur'", w: "IPI Suisse · EUIPO · USPTO", c: "Protection mondiale" },
          { t: "Marque 'Unblurer'", w: "Idem · trio mondial", c: "Le mot devient mon territoire" },
          { t: "Brevet européen", w: "Multiplicateur de fidélité", c: "Méthode mise en œuvre par ordinateur · 20 ans" },
          { t: "Trade secret", w: "Paramètres exacts de la formule", c: "Protection illimitée tant que confidentiel" },
        ].map((r, i) => (
          <div key={i} className="grid grid-cols-12 gap-4 items-baseline py-4 border-b border-border">
            <p className="col-span-4 font-black text-xl">{r.t}</p>
            <p className="col-span-4 text-sm text-muted">{r.w}</p>
            <p className="col-span-4 text-sm text-muted text-right">{r.c}</p>
          </div>
        ))}
      </div>
    </Slide>
  ),

  // 17 — Levée de fonds prévisionnelle
  () => (
    <Slide>
      <Eyebrow>Levée de fonds</Eyebrow>
      <Big>3 tours sur 5 ans pour conquérir le monde.</Big>
      <div className="mt-12 space-y-6 max-w-4xl">
        {[
          { t: "Pré-seed", w: "T3 2026", a: "500-800 k CHF", use: "MVP · 30 premiers Unblurers · runway 18 mois" },
          { t: "Seed",     w: "T1 2028", a: "3 M CHF",       use: "Internationalisation francophone · équipe 15" },
          { t: "Series A", w: "T1 2029", a: "15 M CHF",      use: "Conquête anglo + monde" },
        ].map((r, i) => (
          <div key={i} className="grid grid-cols-12 gap-4 items-baseline py-4 border-b border-border">
            <p className="col-span-2 text-xs uppercase tracking-widest font-bold text-rose">{r.t}</p>
            <p className="col-span-2 text-sm text-muted">{r.w}</p>
            <p className="col-span-3 font-black text-2xl">{r.a}</p>
            <p className="col-span-5 text-sm text-muted">{r.use}</p>
          </div>
        ))}
      </div>
    </Slide>
  ),

  // 18 — Ce que j'apporte au monde
  () => (
    <Slide bg="dark">
      <div className="max-w-5xl">
        <p className="text-xs uppercase tracking-[0.5em] text-surface/40 mb-12">Mon impact sur le monde</p>
        <h2 className="text-6xl sm:text-7xl font-black tracking-tightest leading-[1] text-surface mb-12">
          Je libère les <span className="text-rose">créateurs sportifs</span>.
        </h2>
        <ul className="space-y-4 text-xl text-surface/70 leading-relaxed">
          <li>→ Une étudiante en kiné peut vivre de son expertise dès le 1er jour.</li>
          <li>→ Un boxeur en fin de carrière transmet sans passer par une fédération.</li>
          <li>→ Une mère solo poste 20 min/jour et touche son public mondial.</li>
          <li>→ Un kiné de quartier devient référence francophone d'une discipline.</li>
          <li>→ Les marques accèdent à un canal mesurable et propre.</li>
          <li>→ Les abonnés trouvent enfin le contenu qu'ils cherchaient sans algorithme.</li>
        </ul>
      </div>
    </Slide>
  ),

  // 19 — Vision 2030
  () => (
    <Slide>
      <Eyebrow>Ma vision pour 2030</Eyebrow>
      <Big>unblur devient la <Hl>référence mondiale</Hl> du savoir-faire sportif.</Big>
      <div className="mt-12 grid sm:grid-cols-2 gap-12 max-w-5xl">
        <div>
          <p className="text-xs uppercase tracking-widest text-rose font-bold mb-3">D'ici 2030</p>
          <ul className="space-y-3 text-lg text-muted leading-relaxed">
            <li>→ 50 000 Unblurers dans le monde</li>
            <li>→ 5 millions d'abonnés actifs</li>
            <li>→ Présence dans 40+ pays</li>
            <li>→ Encyclopédie de 2 000 exercices</li>
            <li>→ La plateforme que Decathlon rachète, ou qu'on IPO</li>
          </ul>
        </div>
        <div>
          <p className="text-xs uppercase tracking-widest text-rose font-bold mb-3">Au-delà du sport</p>
          <ul className="space-y-3 text-lg text-muted leading-relaxed">
            <li>→ Extension cuisine, art, musique, méthode</li>
            <li>→ Le modèle s'étend à tout savoir-faire enseignable</li>
            <li>→ unblur devient le synonyme mondial de "créateur authentique"</li>
            <li>→ Le mot "Unblurer" entre dans les dictionnaires</li>
          </ul>
        </div>
      </div>
    </Slide>
  ),

  // 20 — Timing
  () => (
    <Slide>
      <Eyebrow>Le calendrier que je tiens</Eyebrow>
      <div className="mt-8 space-y-12 max-w-4xl">
        <div>
          <p className="text-rose font-black text-7xl tracking-tighter tabular-nums">Août 2026</p>
          <p className="mt-3 text-xl text-muted">Bêta privée · 5 Unblurers tests en Suisse romande</p>
        </div>
        <div>
          <p className="text-rose font-black text-7xl tracking-tighter tabular-nums">Octobre 2026</p>
          <p className="mt-3 text-xl text-muted">Ouverture publique Suisse romande</p>
        </div>
        <div>
          <p className="text-foreground font-black text-7xl tracking-tighter tabular-nums">2027</p>
          <p className="mt-3 text-xl text-muted">Lancement francophonie complète</p>
        </div>
        <div>
          <p className="text-foreground font-black text-7xl tracking-tighter tabular-nums">2030</p>
          <p className="mt-3 text-xl text-muted">Référence mondiale du savoir-faire sportif</p>
        </div>
      </div>
    </Slide>
  ),

  // 21 — Closing — ma promesse
  () => (
    <Slide bg="dark">
      <div className="text-center max-w-5xl mx-auto">
        <p className="text-xs uppercase tracking-[0.5em] text-surface/40 mb-12">Ma promesse</p>
        <h2 className="text-6xl sm:text-9xl font-black tracking-tightest leading-[0.9] text-surface">
          unblur<span className="text-rose">.</span><br />
          La plateforme<br />
          que <span className="text-rose">le sport</span><br />
          mérite<span className="text-rose">.</span>
        </h2>
        <p className="mt-16 text-2xl text-surface/60 max-w-2xl mx-auto leading-snug">
          Le concept est prêt. Le brevet est prêt. La démo est en ligne.<br />
          <span className="text-surface/90 font-bold">Je vais le construire.</span>
        </p>
        <p className="mt-12 text-xs uppercase tracking-[0.5em] text-surface/30">
          unblur-app.vercel.app
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
