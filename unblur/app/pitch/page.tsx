"use client";

import { useEffect, useState, useCallback } from "react";
import Link from "next/link";
import { ChevronLeft, ChevronRight, X } from "lucide-react";

const SLIDES: ((key: number) => any)[] = [

  // ════════════════════════════════════
  // PART I — HOOK (slides 1-4)
  // ════════════════════════════════════

  // 1
  () => (
    <Slide bg="dark">
      <div className="text-center max-w-5xl mx-auto px-8">
        <p className="text-xs uppercase tracking-[0.5em] text-surface/40 mb-12">unblur · investor deck · juin 2026</p>
        <h1 className="text-[10rem] sm:text-[14rem] font-black tracking-tightest leading-[0.85] text-surface">
          unblur<span className="text-rose">.</span>
        </h1>
        <p className="mt-12 text-xl sm:text-3xl text-surface/70 tracking-tight max-w-3xl mx-auto leading-snug">
          L'écosystème mondial des créateurs sportifs.
        </p>
        <p className="mt-20 text-xs uppercase tracking-[0.4em] text-surface/30">
          Damien · Fondateur · damien@unblur.app
        </p>
      </div>
    </Slide>
  ),

  // 2 — Hook : le chiffre choc
  () => (
    <Slide bg="dark">
      <div className="max-w-6xl">
        <p className="text-xs uppercase tracking-[0.5em] text-surface/40 mb-12">Le marché</p>
        <h2 className="text-7xl sm:text-9xl font-black tracking-tightest leading-[0.9] text-surface">
          96 <span className="text-rose">milliards $</span>
        </h2>
        <p className="mt-12 text-3xl text-surface/70 max-w-3xl leading-snug">
          C'est la taille du marché mondial du fitness en ligne en 2026.<br />
          <span className="text-rose font-bold">Personne ne le sert correctement.</span>
        </p>
      </div>
    </Slide>
  ),

  // 3 — Pitch en 1 phrase
  () => (
    <Slide>
      <Eyebrow>Ce qu'est unblur en une phrase</Eyebrow>
      <Big>
        <Hl>TikTok + Twitch + OnlyFans + l'encyclopédie complète des exercices</Hl> — réunis sur une seule plateforme, focalisée sur le sport.
      </Big>
    </Slide>
  ),

  // 4 — Logo wall
  () => (
    <Slide>
      <Eyebrow>L'industrie qu'on remplace</Eyebrow>
      <Big>Une plateforme. <Hl>Quatre géants</Hl> en un.</Big>
      <div className="mt-16 grid sm:grid-cols-4 gap-6">
        {[
          { l: "TikTok", v: "1,5 Md utilisateurs", w: "Shorts vertical" },
          { l: "Twitch", v: "240 M utilisateurs", w: "Lives en direct" },
          { l: "OnlyFans", v: "220 M utilisateurs", w: "Abonnement direct" },
          { l: "Strong / Hevy", v: "10 M utilisateurs", w: "Bibliothèque exercices" },
        ].map((o, i) => (
          <div key={i} className="border-l-2 border-rose pl-5">
            <p className="text-[10px] uppercase tracking-widest font-black text-rose">{o.l}</p>
            <p className="mt-3 font-black text-xl">{o.v}</p>
            <p className="text-sm text-muted mt-2">{o.w}</p>
          </div>
        ))}
      </div>
      <p className="mt-12 text-2xl font-bold">Aucun de ces 4 géants n'est <Hl>focalisé sport et premium</Hl>.</p>
    </Slide>
  ),

  // ════════════════════════════════════
  // PART I-BIS — ORIGIN STORY
  // ════════════════════════════════════

  // 4-bis — D'où vient l'idée
  () => (
    <Slide bg="dark">
      <div className="max-w-5xl">
        <p className="text-xs uppercase tracking-[0.5em] text-surface/40 mb-12">L'origine du projet</p>
        <p className="text-base text-surface/40 italic mb-10">Salle de sport, Suisse romande, automne 2025.</p>
        <h2 className="text-4xl sm:text-6xl font-black tracking-tightest leading-[1.05] text-surface mb-12">
          Une cliente s'entraîne.<br />
          Physiquement <span className="text-rose">irréprochable</span>.<br />
          Pas coach. Juste passionnée.
        </h2>
        <p className="text-2xl text-surface/70 leading-snug max-w-3xl border-l-2 border-rose pl-6 italic">
          « Elle a un physique de dingue. Si elle avait une app, je m'entraînerais comme elle. »
        </p>
        <p className="mt-6 text-base text-surface/50">— Trois clientes différentes. Trois fois la même phrase. En trois semaines.</p>
        <p className="mt-16 text-3xl font-black text-surface">
          unblur est né <span className="text-rose">ce jour-là</span>.
        </p>
      </div>
    </Slide>
  ),

  // ════════════════════════════════════
  // PART II — PROBLEM (slides 5-7)
  // ════════════════════════════════════

  // 5 — Problème pain point créateur
  () => (
    <Slide>
      <Eyebrow>Problème — Côté créateur</Eyebrow>
      <Big>Un <Hl>passionné de sport</Hl> qui veut monétiser sa passion jongle entre <Hl>10 outils</Hl>, 4 commissions, 0 cohérence.</Big>
      <ul className="mt-12 grid grid-cols-2 gap-4 max-w-3xl text-base text-muted">
        {["Instagram (algo contre lui)", "YouTube (55/45)", "Twitch (50/50, gaming)", "Patreon (88/12, sans vidéo)", "OnlyFans (image sulfureuse)", "Calendly · Stripe · Discord · Notion · Mailchimp"].map(s => (
          <li key={s} className="flex items-baseline gap-2"><span className="text-rose">–</span> {s}</li>
        ))}
      </ul>
      <p className="mt-12 text-2xl font-bold"><Hl>95 % des créateurs sport abandonnent en 18 mois.</Hl></p>
      <p className="mt-4 text-sm text-muted italic">La cible primaire : les passionnés de sport — runners, crossfitteurs, grimpeurs, yogis, danseurs, kinés-étudiants. Les coachs pros sont évidemment les bienvenus aussi.</p>
    </Slide>
  ),

  // 6 — Problème côté abonné
  () => (
    <Slide>
      <Eyebrow>Problème — Côté abonné</Eyebrow>
      <Big>L'abonné cherche du <Hl>contenu authentique</Hl>. Il trouve de la pub et des filtres.</Big>
      <div className="mt-12 grid sm:grid-cols-3 gap-8 max-w-5xl">
        <Pain n="68%" l="des utilisateurs Insta fitness ne font confiance à 'aucun' créateur visible" />
        <Pain n="42%" l="abandonnent leur recherche après 3 vidéos non-pertinentes" />
        <Pain n="91%" l="souhaitent payer directement le créateur sans intermédiaire" />
      </div>
    </Slide>
  ),

  // 7 — Le vide à combler
  () => (
    <Slide bg="dark">
      <div className="text-center">
        <p className="text-xs uppercase tracking-[0.5em] text-surface/40 mb-12">Le constat</p>
        <h2 className="text-6xl sm:text-9xl font-black tracking-tightest leading-[0.9] text-surface">
          Il y a un<br />
          <span className="text-rose">trou de marché</span><br />
          de 12 milliards $<span className="text-rose">.</span>
        </h2>
        <p className="mt-12 text-xl text-surface/60">unblur va le combler.</p>
      </div>
    </Slide>
  ),

  // ════════════════════════════════════
  // PART III — MARKET (slides 8-10)
  // ════════════════════════════════════

  // 8 — TAM
  () => (
    <Slide>
      <Eyebrow>Marché total adressable (TAM)</Eyebrow>
      <Big>96 Mds $ — fitness mondial en ligne.</Big>
      <div className="mt-12 space-y-4 max-w-3xl text-base">
        <Row l="Apps fitness (Apple Fitness+, Peloton, Freeletics)" v="42 Mds $" />
        <Row l="Créateurs sport indépendants (passionnés + coachs)" v="28 Mds $" />
        <Row l="Programmes vidéo sport" v="16 Mds $" />
        <Row l="Communautés sportives premium" v="10 Mds $" />
        <Row l="Croissance annuelle" v="14 % CAGR" highlight />
      </div>
    </Slide>
  ),

  // 9 — SAM
  () => (
    <Slide>
      <Eyebrow>Marché adressable serviceable (SAM)</Eyebrow>
      <Big>12 Mds $ — passionnés de sport qui veulent monétiser <Hl>monde</Hl>.</Big>
      <div className="mt-12 grid sm:grid-cols-3 gap-6">
        <BigStat n="48 M" l="Passionnés sport actifs sur les réseaux (mondial)" />
        <BigStat n="180 M" l="Abonnés potentiels à un créateur sport" />
        <BigStat n="12 Mds $" l="Volume actuel mal capté par la concurrence" />
      </div>
      <p className="mt-8 text-sm text-muted italic">Sur ces 48 M, 2,4 M sont coachs pros et 45 M sont passionnés. unblur accueille les deux — la cible primaire est le passionné, qui est 20× plus nombreux.</p>
    </Slide>
  ),

  // 10 — SOM
  () => (
    <Slide>
      <Eyebrow>Notre cible serviceable (SOM)</Eyebrow>
      <Big>1,2 Mds €<br />Francophonie + anglo prioritaire.</Big>
      <div className="mt-12 space-y-3 max-w-3xl text-base">
        <Row l="🇨🇭 Suisse (an 1)" v="80 M €" />
        <Row l="🇫🇷 🇧🇪 🇨🇦 Francophonie complète (an 3)" v="420 M €" />
        <Row l="🇬🇧 🇺🇸 Anglo prioritaire (an 5)" v="700 M €" />
        <Row l="Total visé an 7" v="1,2 Mds €" highlight />
      </div>
      <p className="mt-10 text-base text-muted">Soit <Hl>10 %</Hl> de notre SAM. Hypothèses prudentes.</p>
    </Slide>
  ),

  // ════════════════════════════════════
  // PART IV — SOLUTION (slides 11-15)
  // ════════════════════════════════════

  // 11 — Solution 4-in-1
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

  // 12 — Product : landing
  () => (
    <Slide>
      <Eyebrow>Le produit · Page d'accueil</Eyebrow>
      <Big>Le visiteur comprend en <Hl>5 secondes</Hl>.</Big>
      <div className="mt-8 rounded-2xl overflow-hidden border border-border shadow-2xl max-w-6xl mx-auto">
        <img src="/screens/louise-profile.png" alt="Profil créateur" className="w-full block" />
      </div>
    </Slide>
  ),

  // 13 — Product : Studio créateur
  () => (
    <Slide>
      <Eyebrow>Le produit · Studio créateur</Eyebrow>
      <Big>Le créateur a tout dans <Hl>un seul écran</Hl>.</Big>
      <div className="mt-8 rounded-2xl overflow-hidden border border-border shadow-2xl max-w-6xl mx-auto">
        <img src="/screens/louise-studio.png" alt="Studio Louise" className="w-full block" />
      </div>
    </Slide>
  ),

  // 14 — Product : Live record
  () => (
    <Slide>
      <Eyebrow>Le produit · Caméra en 1 clic</Eyebrow>
      <Big>Le moment qui sépare un <Hl>amateur</Hl> d'un <Hl>professionnel</Hl>.</Big>
      <div className="mt-8 rounded-2xl overflow-hidden border border-border shadow-2xl max-w-6xl mx-auto">
        <img src="/screens/louise-record.png" alt="Studio record" className="w-full block" />
      </div>
    </Slide>
  ),

  // 15 — Product : Encyclopédie
  () => (
    <Slide>
      <Eyebrow>Le produit · Encyclopédie</Eyebrow>
      <Big>L'arme cachée — magnet <Hl>SEO mondial</Hl>.</Big>
      <p className="mt-6 text-lg text-muted max-w-3xl">500+ exercices à 18 mois. Référence francophone, puis anglo. Trafic organique massif.</p>
    </Slide>
  ),

  // ════════════════════════════════════
  // PART V — BUSINESS MODEL (slides 16-21)
  // ════════════════════════════════════

  // 16 — Algo intro
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

  // 17 — Commission dégressive
  () => (
    <Slide>
      <Eyebrow>Commission dégressive — unique au monde</Eyebrow>
      <div className="mt-8 max-w-3xl">
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

  // 18 — Bonus viralité
  () => (
    <Slide>
      <Eyebrow>Mécanique 1 — Bonus viralité</Eyebrow>
      <Big>Un Unblurer en parraine un autre ?<br />Il <Hl>économise 2 points</Hl> de commission pendant 3 mois.</Big>
      <p className="mt-12 text-xl text-muted max-w-3xl leading-relaxed">
        Les Unblurers font l'acquisition. Aucune team sales. Croissance virale gratuite à l'échelle mondiale.
      </p>
    </Slide>
  ),

  // 19 — Founding Unblurer
  () => (
    <Slide>
      <Eyebrow>Mécanique 2 — Founding Unblurer</Eyebrow>
      <Big>Les <Hl>100 premiers</Hl> signés en Suisse gardent leur grille à vie.</Big>
      <p className="mt-12 text-xl text-muted max-w-3xl leading-relaxed">
        Caste protégée qui défend unblur contre tous les nouveaux entrants. Stratégie Uber + Airbnb.
      </p>
    </Slide>
  ),

  // 20 — BREVET — Multiplicateur fidélité
  () => (
    <Slide bg="dark">
      <div className="max-w-5xl">
        <p className="text-xs uppercase tracking-[0.5em] text-rose mb-8">Mécanique 3 — Brevet mondial déposé</p>
        <h2 className="text-6xl sm:text-8xl font-black tracking-tightest leading-[0.92] text-surface">
          Multiplicateur de <span className="text-rose">fidélité abonné</span>.
        </h2>
        <p className="mt-12 text-xl text-surface/70 max-w-3xl leading-relaxed">
          Plus un abonné reste fidèle, <span className="text-rose font-black">moins on prend</span> sur lui. Plancher 5 %.
        </p>
        <p className="mt-6 text-base text-surface/60">Brevet européen "méthode mise en œuvre par ordinateur" · 20 ans · cabinet PI Zurich</p>
      </div>
    </Slide>
  ),

  // 21 — Palier sponsor
  () => (
    <Slide>
      <Eyebrow>Mécanique 4 — Palier sponsor</Eyebrow>
      <Big>À 20 000 €/mois, l'Unblurer débloque les <Hl>deals sponsors</Hl> orchestrés par unblur.</Big>
      <div className="mt-12 grid sm:grid-cols-3 gap-8 max-w-4xl">
        <Stat n="86 600 €" l="Un Unblurer top garde / mois" />
        <Stat n="23 400 €" l="unblur encaisse / mois" />
        <Stat n="× 200" l="top créateurs en année 4" />
      </div>
    </Slide>
  ),

  // ════════════════════════════════════
  // PART VI — STORY (Louise, slides 22-26)
  // ════════════════════════════════════

  // 22 — Louise présentation
  () => (
    <Slide>
      <Eyebrow>Exemple concret — Louise, 22 ans</Eyebrow>
      <div className="grid lg:grid-cols-2 gap-10 items-center">
        <div>
          <Big>Étudiante en kiné<br />à Lyon.</Big>
          <p className="mt-8 text-xl text-muted leading-relaxed max-w-xl">
            Avant unblur : 18 400 followers Insta, 0 € par mois.
          </p>
          <p className="mt-6 text-2xl font-black">Aujourd'hui :</p>
          <ul className="mt-3 space-y-1.5 text-lg">
            <li>→ 2 840 abonnés payants</li>
            <li>→ 9,90 €/mois</li>
            <li>→ <Hl>18 010 € NET ce mois</Hl></li>
          </ul>
        </div>
        <div className="rounded-2xl overflow-hidden border border-border shadow-2xl">
          <img src="/screens/louise-profile.png" alt="Profil Louise" className="w-full block" />
        </div>
      </div>
    </Slide>
  ),

  // 23 — Louise filme
  () => (
    <Slide>
      <Eyebrow>Étape 1 — Elle filme</Eyebrow>
      <div className="grid lg:grid-cols-12 gap-8 items-center">
        <div className="lg:col-span-5">
          <Big>1 clic.<br />Elle est <Hl>en direct</Hl>.</Big>
          <p className="mt-8 text-lg text-muted leading-relaxed">
            Aucun OBS. Aucun matos pro. Elle ouvre son téléphone. Sa caméra démarre. Ses 2 840 abonnés reçoivent un push.
          </p>
        </div>
        <div className="lg:col-span-7 rounded-2xl overflow-hidden border border-border shadow-2xl">
          <img src="/screens/louise-record.png" alt="Studio enregistrement" className="w-full block" />
        </div>
      </div>
    </Slide>
  ),

  // 24 — Louise anime
  () => (
    <Slide>
      <Eyebrow>Étape 2 — Elle anime</Eyebrow>
      <div className="grid lg:grid-cols-12 gap-8 items-center">
        <div className="lg:col-span-5">
          <Big>Communauté <Hl>WhatsApp</Hl>.<br />Privée. Chiffrée.</Big>
          <p className="mt-8 text-lg text-muted leading-relaxed">
            7 channels par thème. Ses abonnés se parlent. Elle modère, répond, encourage. Rétention naturelle.
          </p>
        </div>
        <div className="lg:col-span-7 rounded-2xl overflow-hidden border border-border shadow-2xl">
          <img src="/screens/louise-community.png" alt="Communauté" className="w-full block" />
        </div>
      </div>
    </Slide>
  ),

  // 25 — Louise gagne
  () => (
    <Slide>
      <Eyebrow>Étape 3 — Elle gagne sa vie</Eyebrow>
      <div className="grid lg:grid-cols-12 gap-8 items-center">
        <div className="lg:col-span-5">
          <Big><Hl>18 010 €</Hl><br />versés le 5<br />du mois prochain.</Big>
          <p className="mt-8 text-lg text-muted leading-relaxed">
            Stripe Connect automatique. Aucune négociation. Aucun intermédiaire. Aucune surprise.
          </p>
        </div>
        <div className="lg:col-span-7 rounded-2xl overflow-hidden border border-border shadow-2xl">
          <img src="/screens/louise-revenue.png" alt="Revenus" className="w-full block" />
        </div>
      </div>
    </Slide>
  ),

  // 26 — Multiplie par
  () => (
    <Slide bg="dark">
      <div className="text-center max-w-5xl mx-auto">
        <p className="text-xs uppercase tracking-[0.5em] text-surface/40 mb-12">Multiplie Louise par</p>
        <div className="grid sm:grid-cols-3 gap-12">
          <div>
            <p className="text-7xl sm:text-9xl font-black tracking-tightest text-rose">100</p>
            <p className="text-base text-surface/60 mt-3">en année 1<br /><span className="text-surface/40">Suisse</span></p>
          </div>
          <div>
            <p className="text-7xl sm:text-9xl font-black tracking-tightest text-rose">1 500</p>
            <p className="text-base text-surface/60 mt-3">en année 3<br /><span className="text-surface/40">Francophonie</span></p>
          </div>
          <div>
            <p className="text-7xl sm:text-9xl font-black tracking-tightest text-rose">8 000</p>
            <p className="text-base text-surface/60 mt-3">en année 5<br /><span className="text-surface/40">Anglo + monde</span></p>
          </div>
        </div>
      </div>
    </Slide>
  ),

  // ════════════════════════════════════
  // PART VII — COMPETITION (slides 27-29)
  // ════════════════════════════════════

  // 27 — Positionnement
  () => (
    <Slide>
      <Eyebrow>Positionnement</Eyebrow>
      <Big>Personne ne nous attaque <Hl>frontalement</Hl>.</Big>
      <div className="mt-10 max-w-5xl">
        <div className="grid grid-cols-12 gap-2 text-sm py-3 border-b border-border font-bold uppercase tracking-widest text-muted">
          <span className="col-span-3">Plateforme</span>
          <span className="col-span-2">Modèle</span>
          <span className="col-span-2">Focus sport</span>
          <span className="col-span-2">Live HD</span>
          <span className="col-span-3">Encyclopédie</span>
        </div>
        {[
          { p: "unblur", m: "Dégressif 80→95%", s: "✓ Pur", l: "✓", e: "✓ Référence", featured: true },
          { p: "OnlyFans", m: "Fixe 80/20", s: "Adulte dominant", l: "Partiel", e: "✕" },
          { p: "Twitch", m: "Fixe 50/50", s: "Gaming", l: "✓", e: "✕" },
          { p: "Patreon", m: "Fixe 88/12", s: "Multi-domaine", l: "✕", e: "✕" },
          { p: "Apple Fitness+", m: "Studio fermé", s: "✓ Sport", l: "Studio only", e: "✕" },
        ].map((r, i) => (
          <div key={i} className={`grid grid-cols-12 gap-2 text-base py-4 border-b border-border ${r.featured ? "font-black bg-rose/5" : ""}`}>
            <span className="col-span-3">{r.p}</span>
            <span className="col-span-2 text-muted">{r.m}</span>
            <span className="col-span-2 text-muted">{r.s}</span>
            <span className="col-span-2 text-muted">{r.l}</span>
            <span className="col-span-3 text-muted">{r.e}</span>
          </div>
        ))}
      </div>
    </Slide>
  ),

  // 28 — Slogan tueur
  () => (
    <Slide bg="dark">
      <div className="max-w-5xl">
        <p className="text-xs uppercase tracking-[0.5em] text-surface/40 mb-12">Le pitch one-liner</p>
        <p className="text-3xl sm:text-5xl font-black tracking-tighter leading-[1.2] text-surface">
          "Sur unblur, plus tu fais grandir la plateforme, moins tu nous paies.<br /><br />
          Plus tes abonnés te restent fidèles, moins on prend sur eux.<br /><br />
          Plus tu cartonnes, plus on te débloque des deals avec les marques.<br /><br />
          <span className="text-rose">Personne d'autre ne fait ça.</span>"
        </p>
      </div>
    </Slide>
  ),

  // 29 — Notre moat
  () => (
    <Slide>
      <Eyebrow>Notre fossé défensif</Eyebrow>
      <Big>5 raisons qui rendent unblur <Hl>inattaquable</Hl>.</Big>
      <ol className="mt-12 space-y-4 max-w-4xl text-lg">
        {[
          ["Modèle économique brevetable", "Multiplicateur de fidélité, méthode mise en œuvre par ordinateur, brevet EU 20 ans"],
          ["First-mover francophonie", "Personne ne nous précède. Lock-in culturel et SEO en 24 mois"],
          ["Encyclopédie SEO massive", "500+ exercices référencés. Magnet trafic gratuit. Aucun concurrent ne le construira"],
          ["Lock-in créateur", "Top Unblurers à 5% de commission. Partir leur coûte 25% de leur revenu"],
          ["Marque + statut social", "'Unblurer' devient un titre, comme YouTuber ou Influencer. Ownable mondialement"],
        ].map(([t, d], i) => (
          <li key={i} className="flex gap-5 items-baseline border-b border-border pb-4">
            <span className="text-4xl font-black text-rose tabular-nums shrink-0">{String(i + 1).padStart(2, "0")}</span>
            <div>
              <p className="font-black text-xl">{t}</p>
              <p className="text-muted text-sm mt-1">{d}</p>
            </div>
          </li>
        ))}
      </ol>
    </Slide>
  ),

  // ════════════════════════════════════
  // PART VIII — TRACTION & GTM (slides 30-32)
  // ════════════════════════════════════

  // 30 — Stratégie GTM
  () => (
    <Slide>
      <Eyebrow>Stratégie de lancement</Eyebrow>
      <Big>Suisse → Francophonie → Anglo → Monde.</Big>
      <div className="mt-12 space-y-6 max-w-4xl">
        {[
          { phase: "Phase 1", when: "T3 2026", w: "🇨🇭 Suisse romande", goal: "30 Unblurers · 3 000 abonnés" },
          { phase: "Phase 2", when: "T1 2027", w: "🌍 Francophonie (300 M)", goal: "300 Unblurers · 60 000 abonnés" },
          { phase: "Phase 3", when: "T1 2028", w: "🇬🇧 🇺🇸 Anglo", goal: "1 500 Unblurers · 500 000 abonnés" },
          { phase: "Phase 4", when: "2029+",   w: "🌐 Monde + extension", goal: "8 000+ Unblurers" },
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

  // 30-bis — Distribution : on n'invente pas la roue (Linktree playbook)
  () => (
    <Slide bg="dark">
      <div className="max-w-6xl">
        <p className="text-xs uppercase tracking-[0.5em] text-surface/40 mb-12">Distribution · acquisition créatrices</p>
        <h2 className="text-5xl sm:text-7xl font-black tracking-tightest leading-[1] text-surface mb-8">
          On n'invente <span className="text-rose">pas la roue</span>.<br />
          On reprend la méthode <span className="text-rose">Linktree</span>.
        </h2>
        <p className="text-xl text-surface/70 mb-12 max-w-4xl leading-relaxed">
          Chaque Unblurer reçoit un lien unique <span className="font-mono text-rose">unblur.app/louise</span> qu'elle colle dans sa bio Instagram. Une action. Une seule fois. Acquisition mondiale, gratuite, permanente.
        </p>

        <div className="grid sm:grid-cols-4 gap-6 mb-12">
          {[
            { v: "50 M+", l: "utilisateurs Linktree dans le monde" },
            { v: "1,3 Md $", l: "valorisation Linktree (Série C 2022)" },
            { v: "25 M $", l: "ARR Linktree — preuve que le modèle marche" },
            { v: "16 000", l: "signups/jour au pic — adoption fulgurante" },
          ].map((s, i) => (
            <div key={i} className="border-l-2 border-rose pl-5">
              <p className="text-4xl font-black tracking-tighter text-surface tabular-nums">{s.v}</p>
              <p className="text-xs text-surface/60 mt-2 leading-relaxed">{s.l}</p>
            </div>
          ))}
        </div>

        <div className="grid sm:grid-cols-2 gap-8 max-w-5xl">
          <div className="p-6 rounded-2xl border border-surface/20">
            <p className="text-xs uppercase tracking-widest text-rose font-bold mb-3">Ce que fait Linktree</p>
            <ul className="text-sm text-surface/70 space-y-2">
              <li>→ 1 lien dans la bio Insta</li>
              <li>→ Page agrégateur de liens</li>
              <li>→ Modèle horizontal, tous secteurs</li>
              <li>→ <strong className="text-surface">Pas de monétisation native</strong></li>
            </ul>
          </div>
          <div className="p-6 rounded-2xl bg-surface text-foreground">
            <p className="text-xs uppercase tracking-widest text-rose font-bold mb-3">Ce que fait unblur en plus</p>
            <ul className="text-sm space-y-2">
              <li>→ 1 lien dans la bio Insta</li>
              <li>→ Page créatrice <strong>brandée + transactionnelle</strong></li>
              <li>→ Modèle vertical <strong>focalisé sport</strong></li>
              <li>→ <strong className="text-rose">Paywall + lives + communauté intégrés</strong></li>
            </ul>
          </div>
        </div>

        <p className="mt-10 text-base text-surface/60 italic max-w-4xl">
          Linktree = distribution sans monétisation. OnlyFans = monétisation sans distribution propre. unblur = les deux dans une seule URL.
        </p>
      </div>
    </Slide>
  ),

  // 31 — Traction actuelle
  () => (
    <Slide>
      <Eyebrow>Traction actuelle</Eyebrow>
      <Big>Avant même le 1er € levé.</Big>
      <div className="mt-12 grid sm:grid-cols-2 gap-6 max-w-5xl">
        {[
          ["Démo cliquable en ligne", "13 écrans fonctionnels publics", "✓ Live"],
          ["Brevet déposé", "Multiplicateur fidélité abonné", "✓ Cabinet Zurich"],
          ["Marque protégée", "unblur + Unblurer", "✓ Suisse + EU + US"],
          ["Lettres d'intention", "15 créateurs sport romands en attente", "→ En cours"],
          ["Sponsors approchés", "Mammut, On Running, Migros", "→ Discussions"],
          ["Encyclopédie", "24 exercices techniques en ligne", "→ 500 cible"],
        ].map(([t, d, status], i) => (
          <div key={i} className="border-l-2 border-rose pl-5 py-3">
            <p className="font-black text-lg">{t}</p>
            <p className="text-sm text-muted">{d}</p>
            <p className="text-xs uppercase tracking-widest font-bold text-rose mt-2">{status}</p>
          </div>
        ))}
      </div>
    </Slide>
  ),

  // 32 — Roadmap 24 mois
  () => (
    <Slide>
      <Eyebrow>Roadmap 24 mois</Eyebrow>
      <div className="mt-10 space-y-5 max-w-5xl">
        {[
          { m: "Mois 1-3",  e: "MVP technique (auth, paywall, lives, DMs)" },
          { m: "Mois 4",    e: "Bêta privée — 5 Unblurers Suisse romande" },
          { m: "Mois 5-6",  e: "Pré-seed levé · 30 Unblurers actifs" },
          { m: "Mois 7-9",  e: "Ouverture publique CH · campagne presse" },
          { m: "Mois 10-12", e: "100 Unblurers · 1ère deal sponsor Mammut" },
          { m: "Mois 13-18", e: "Expansion France + Belgique · Seed 3M" },
          { m: "Mois 19-24", e: "Québec + Maroc · 500 Unblurers · marge positive" },
        ].map((r, i) => (
          <div key={i} className="grid grid-cols-12 gap-4 items-baseline py-4 border-b border-border">
            <span className="col-span-3 text-xs uppercase tracking-widest font-bold text-rose">{r.m}</span>
            <span className="col-span-9 text-lg">{r.e}</span>
          </div>
        ))}
      </div>
    </Slide>
  ),

  // ════════════════════════════════════
  // PART IX — FINANCIALS (slides 33-35)
  // ════════════════════════════════════

  // 33 — Unit economics
  () => (
    <Slide>
      <Eyebrow>Unit economics</Eyebrow>
      <Big>Le LTV/CAC qui fait rêver.</Big>
      <div className="mt-12 grid sm:grid-cols-2 gap-12 max-w-5xl">
        <div>
          <p className="text-xs uppercase tracking-widest text-rose font-bold mb-4">Par Unblurer</p>
          <Row l="CAC (acquisition créateur)" v="180 €" />
          <Row l="ARPU moyen (abonnés × prix)" v="3 200 €/mois" />
          <Row l="Commission unblur moyenne" v="18 %" />
          <Row l="Revenu net unblur" v="576 €/mois" />
          <Row l="Durée de vie créateur" v="38 mois" highlight />
          <Row l="LTV créateur" v="21 880 €" highlight />
        </div>
        <div>
          <p className="text-xs uppercase tracking-widest text-rose font-bold mb-4">Ratios</p>
          <Row l="LTV / CAC" v="121×" highlight />
          <Row l="Payback" v="0,3 mois" highlight />
          <Row l="Marge brute" v="78 %" />
          <Row l="Churn créateur an 1" v="4 %" />
          <Row l="Churn créateur an 3" v="2 %" />
          <Row l="NPS attendu" v="68" />
        </div>
      </div>
    </Slide>
  ),

  // 34 — ARR trajectory
  () => (
    <Slide>
      <Eyebrow>Trajectoire ARR — base prudente</Eyebrow>
      <Big>De rentable en An 1 à <Hl>pré-licorne en An 7</Hl>.</Big>
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

  // 35 — Multiple revenues
  () => (
    <Slide>
      <Eyebrow>4 lignes de revenu</Eyebrow>
      <Big>Pas une, <Hl>quatre</Hl> sources de revenus en année 5.</Big>
      <div className="mt-12 space-y-4 max-w-4xl text-base">
        <Row l="1. Commission abonnements (cœur)" v="14,4 M €/an" />
        <Row l="2. Deals sponsors orchestrés" v="2,0 M €/an" />
        <Row l="3. Boost interne (pub créateur)" v="0,8 M €/an" />
        <Row l="4. Programmes premium + certifications" v="1,2 M €/an" />
        <Row l="Total ARR an 5" v="18,4 M €" highlight />
      </div>
      <p className="mt-10 text-base text-muted">Diversification = résilience. Aucun pilier ne porte la totalité.</p>
    </Slide>
  ),

  // ════════════════════════════════════
  // PART IX-BIS — EVOLUTION V2-V3
  // ════════════════════════════════════

  // 35-bis — Le moteur intelligent (v2-v3)
  () => (
    <Slide bg="dark">
      <div className="max-w-6xl">
        <p className="text-xs uppercase tracking-[0.5em] text-surface/40 mb-12">Évolution v2-v3 · post-MVP</p>
        <h2 className="text-5xl sm:text-7xl font-black tracking-tightest leading-[1] text-surface mb-8">
          Le <span className="text-rose">moteur intelligent</span> unblur.
        </h2>
        <p className="text-xl text-surface/70 mb-12 max-w-3xl leading-relaxed">
          L'abonnée note la difficulté perçue de chaque séance. L'algorithme construit sa courbe de progression. La séance la plus dure reste floutée tant que les paliers intermédiaires ne sont pas validés.
        </p>
        <div className="grid sm:grid-cols-3 gap-6">
          {[
            { t: "Sécurité abonnée", d: "L'algo empêche l'accès à un contenu trop difficile. Zéro blessure. Zéro frustration." },
            { t: "Rétention massive", d: "12 séances dans une progression de 6 mois au lieu d'une consommation flash." },
            { t: "Barrière concurrence", d: "Un moteur de reco fitness-aware = 6-18 mois d'avance technique." },
          ].map((b, i) => (
            <div key={i} className="border-l-2 border-rose pl-5">
              <p className="text-xs uppercase tracking-widest text-rose font-bold mb-2">{b.t}</p>
              <p className="text-base text-surface/70 leading-relaxed">{b.d}</p>
            </div>
          ))}
        </div>
        <p className="mt-12 text-xs uppercase tracking-[0.4em] text-rose">Brevet n°3 en réserve sur cette mécanique</p>
      </div>
    </Slide>
  ),

  // ════════════════════════════════════
  // PART X — IP (portfolio complet)
  // ════════════════════════════════════

  // 36 — Portefeuille IP
  () => (
    <Slide>
      <Eyebrow>Portefeuille de propriété intellectuelle</Eyebrow>
      <Big>3 <Hl>brevets</Hl>. 6 <Hl>marques</Hl>. 20 ans de protection.</Big>

      <div className="mt-10 grid sm:grid-cols-2 gap-10 max-w-6xl">
        <div>
          <p className="text-xs uppercase tracking-widest text-rose font-bold mb-4">Les 3 brevets européens</p>
          <div className="space-y-4">
            {[
              { n: "01", t: "Commission dégressive viralisable", s: "Déposé", d: "Multiplicateur de fidélité abonné + paliers de revenu + parrainage croisé" },
              { n: "02", t: "Défloutage par l'effort physique", s: "À déposer", d: "Méthode de défloutage d'un contenu selon l'accomplissement d'une séance + re-floutage post-usage" },
              { n: "03", t: "Reco fitness avec protection progression", s: "v2-v3", d: "Algo de recommandation personnalisée basé sur la difficulté perçue et la progression cumulative" },
            ].map((b) => (
              <div key={b.n} className="border-l-2 border-rose pl-4 pb-2">
                <div className="flex items-baseline gap-3">
                  <span className="text-xs font-mono text-rose tabular-nums">{b.n}</span>
                  <p className="font-black text-base">{b.t}</p>
                  <span className="text-[10px] uppercase tracking-widest text-muted ml-auto">{b.s}</span>
                </div>
                <p className="text-xs text-muted mt-1 leading-relaxed">{b.d}</p>
              </div>
            ))}
          </div>
        </div>

        <div>
          <p className="text-xs uppercase tracking-widest text-rose font-bold mb-4">Les 6 marques déposées</p>
          <div className="space-y-3">
            {[
              { n: "unblur",          s: "Déposée", z: "CH + EU + US",      d: "Marque verbale + figurative" },
              { n: "Unblurer",        s: "Déposée", z: "CH + EU + US",      d: "Titre du créateur (comme YouTuber)" },
              { n: "unblurée",        s: "À déposer", z: "EU",              d: "Verbe d'usage de l'abonnée" },
              { n: "Founding Unblurer", s: "À déposer", z: "EU + US",       d: "Statut des 100 premiers créateurs" },
              { n: "déflou / défloutage", s: "À étudier", z: "EU",          d: "Vocabulaire propriétaire de la marque" },
              { n: "u.",              s: "À déposer", z: "CH + EU + US",    d: "Signature visuelle (point rouge)" },
            ].map((m) => (
              <div key={m.n} className="flex items-baseline gap-2 text-xs">
                <p className="font-black text-sm w-40 truncate">{m.n}</p>
                <span className="text-[9px] uppercase tracking-widest text-muted">{m.s}</span>
                <span className="text-[9px] uppercase tracking-widest text-muted ml-auto">{m.z}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <p className="mt-10 text-base text-muted italic">+ Trade secret sur les paramètres exacts des algorithmes — protection illimitée.</p>
    </Slide>
  ),

  // ════════════════════════════════════
  // PART XI — VISION (slides 37-38)
  // ════════════════════════════════════

  // 37 — Impact monde
  () => (
    <Slide bg="dark">
      <div className="max-w-5xl">
        <p className="text-xs uppercase tracking-[0.5em] text-surface/40 mb-12">Mon impact</p>
        <h2 className="text-6xl sm:text-7xl font-black tracking-tightest leading-[1] text-surface mb-12">
          Je libère les <span className="text-rose">créateurs sportifs</span>.
        </h2>
        <ul className="space-y-4 text-xl text-surface/70 leading-relaxed">
          <li>→ Une étudiante en kiné peut vivre de sa passion dès le 1er jour.</li>
          <li>→ Un boxeur en fin de carrière transmet sans passer par une fédération.</li>
          <li>→ Une mère solo poste 20 min/jour et touche son public mondial.</li>
          <li>→ Un kiné de quartier devient référence francophone d'une discipline.</li>
          <li>→ Les marques accèdent à un canal mesurable et propre.</li>
          <li>→ Les abonnés trouvent enfin le contenu qu'ils cherchaient sans algorithme.</li>
        </ul>
      </div>
    </Slide>
  ),

  // 38 — Vision 2030 + exit
  () => (
    <Slide>
      <Eyebrow>Vision 2030 · Stratégie de sortie</Eyebrow>
      <Big>Référence mondiale du savoir-faire sportif.</Big>
      <div className="mt-12 grid sm:grid-cols-2 gap-12 max-w-5xl">
        <div>
          <p className="text-xs uppercase tracking-widest text-rose font-bold mb-3">2030 — métriques</p>
          <ul className="space-y-3 text-lg text-muted leading-relaxed">
            <li>→ 50 000 Unblurers dans le monde</li>
            <li>→ 5 millions d'abonnés actifs</li>
            <li>→ 40+ pays</li>
            <li>→ ARR &gt; 200 M €</li>
            <li>→ Valorisation 1,5 - 2 Mds €</li>
          </ul>
        </div>
        <div>
          <p className="text-xs uppercase tracking-widest text-rose font-bold mb-3">Stratégies de sortie possibles</p>
          <ul className="space-y-3 text-lg text-muted leading-relaxed">
            <li>→ Rachat Decathlon (canal créateur intégré)</li>
            <li>→ Rachat Meta (Reels fitness)</li>
            <li>→ Rachat Apple (Fitness+ open creator)</li>
            <li>→ <Hl>IPO indépendante</Hl> Nasdaq ou Euronext</li>
          </ul>
        </div>
      </div>
    </Slide>
  ),

  // ════════════════════════════════════
  // PART XII — ASK (slide 39)
  // ════════════════════════════════════

  // 39 — Ask
  () => (
    <Slide bg="dark">
      <div className="max-w-5xl">
        <p className="text-xs uppercase tracking-[0.5em] text-surface/40 mb-8">Ce que je lève</p>
        <h2 className="text-7xl sm:text-9xl font-black tracking-tightest leading-[0.92] text-surface">
          800 k <span className="text-rose">CHF</span>
        </h2>
        <p className="mt-8 text-2xl text-surface/70">Pré-seed · 18 mois de runway</p>

        <div className="mt-12 grid sm:grid-cols-2 gap-12">
          <div>
            <p className="text-xs uppercase tracking-widest text-rose font-bold mb-4">Allocation</p>
            <ul className="space-y-2 text-base text-surface/70">
              <li>→ 60 % — Développement produit (MVP + équipe tech)</li>
              <li>→ 20 % — Acquisition 30 premiers Unblurers</li>
              <li>→ 10 % — Marketing & presse Suisse romande</li>
              <li>→ 10 % — Légal, brevet, assurance, runway</li>
            </ul>
          </div>
          <div>
            <p className="text-xs uppercase tracking-widest text-rose font-bold mb-4">Objectifs à 18 mois</p>
            <ul className="space-y-2 text-base text-surface/70">
              <li>→ 100 Unblurers actifs</li>
              <li>→ ARR 240 k€ (rentable)</li>
              <li>→ Brevet validé</li>
              <li>→ Prêt pour Seed 3 M CHF</li>
            </ul>
          </div>
        </div>
      </div>
    </Slide>
  ),

  // ════════════════════════════════════
  // PART XIII — CLOSING (slide 40)
  // ════════════════════════════════════

  // 40 — Closing — c'est ouf
  () => (
    <Slide bg="dark">
      <div className="text-center max-w-6xl mx-auto">
        <p className="text-xs uppercase tracking-[0.5em] text-surface/40 mb-12">En résumé</p>
        <h2 className="text-6xl sm:text-[10rem] font-black tracking-tightest leading-[0.88] text-surface">
          Marché 96 Mds.<br />
          Trou de 12 Mds.<br />
          Brevet déposé.<br />
          <span className="text-rose">Démo live.</span>
        </h2>
        <p className="mt-16 text-2xl sm:text-4xl text-surface/80 font-bold max-w-4xl mx-auto leading-snug">
          La seule question qui reste : <Hl>tu montes ou pas ?</Hl>
        </p>
        <p className="mt-16 text-xs uppercase tracking-[0.4em] text-surface/30">
          unblur-app.vercel.app · damien@unblur.app
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
      <div key={idx} className="absolute inset-0 animate-[fadeIn_0.4s_ease-out] overflow-y-auto">
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
        <div className="flex gap-0.5 px-3 py-2 rounded-full bg-surface/80 backdrop-blur ring-1 ring-border max-w-[50vw] overflow-hidden">
          {SLIDES.map((_, i) => (
            <button key={i} onClick={() => setIdx(i)} className={`h-1.5 rounded-full transition-all ${i === idx ? "bg-foreground w-4" : "bg-foreground/20 w-1"}`} />
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
    <div className={`min-h-screen grid place-items-center px-12 sm:px-20 py-12 ${bg === "dark" ? "bg-foreground text-surface" : "bg-canvas text-foreground"}`} style={bg === "light" ? { background: "var(--bg-base)" } : {}}>
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

function BigStat({ n, l }: { n: string; l: string }) {
  return (
    <div className="border-l-2 border-rose pl-5">
      <p className="text-4xl sm:text-5xl font-black tabular-nums tracking-tighter">{n}</p>
      <p className="text-sm text-muted mt-3 leading-snug">{l}</p>
    </div>
  );
}

function Pain({ n, l }: { n: string; l: string }) {
  return (
    <div>
      <p className="text-5xl sm:text-7xl font-black tracking-tighter text-rose">{n}</p>
      <p className="text-sm text-muted mt-3 leading-snug">{l}</p>
    </div>
  );
}

function Row({ l, v, highlight }: { l: string; v: string; highlight?: boolean }) {
  return (
    <div className={`flex items-baseline justify-between py-3 border-b border-border ${highlight ? "font-black" : ""}`}>
      <span className={highlight ? "" : "text-muted"}>{l}</span>
      <span className={`font-mono tabular-nums ${highlight ? "text-rose text-xl" : ""}`}>{v}</span>
    </div>
  );
}
