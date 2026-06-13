"use client";

import { useEffect, useState, useCallback } from "react";
import Link from "next/link";
import { ChevronLeft, ChevronRight, X } from "lucide-react";

const SLIDES: ((key: number) => any)[] = [

  // 1 — Cover
  () => (
    <Slide bg="dark">
      <div className="text-center max-w-5xl mx-auto">
        <p className="text-xs uppercase tracking-[0.5em] text-surface/40 mb-12">unblur · pitch technique · 15 juin 2026</p>
        <h1 className="text-[8rem] sm:text-[12rem] font-black tracking-tightest leading-[0.85] text-surface">
          unblur<span className="text-rose">.</span>
        </h1>
        <p className="mt-12 text-xl sm:text-3xl text-surface/70 tracking-tight max-w-3xl mx-auto leading-snug">
          Pour la rencontre avec ma future codeuse.
        </p>
      </div>
    </Slide>
  ),

  // 2 — Bienvenue
  () => (
    <Slide>
      <Eyebrow>Avant tout</Eyebrow>
      <Big>Bienvenue.<br />Voici ce que <Hl>je construis</Hl>.</Big>
      <p className="mt-12 text-xl text-muted max-w-3xl leading-relaxed">
        Je vais te montrer le concept, l'architecture, la stack. Pas de pitch commercial, pas de chiffres. Juste un produit que personne au monde n'a encore osé faire.
      </p>
    </Slide>
  ),

  // 3 — Le concept
  () => (
    <Slide>
      <Eyebrow>Le concept</Eyebrow>
      <Big><Hl>TikTok + Twitch + OnlyFans + Encyclopédie</Hl> du sport.</Big>
      <p className="mt-10 text-xl text-muted max-w-3xl leading-relaxed">
        Un coach sport indépendant a aujourd'hui 10 outils éclatés. unblur lui donne un seul écran. Il garde 80 % minimum. Brevet déposé sur la mécanique économique.
      </p>
    </Slide>
  ),

  // 4 — Démo live
  () => (
    <Slide>
      <Eyebrow>La démo est en ligne</Eyebrow>
      <Big>15 routes fonctionnelles.<br />Voilà ce qu'on veut produire <Hl>en code réel</Hl>.</Big>
      <div className="mt-12 grid sm:grid-cols-2 gap-4 max-w-4xl">
        {[
          ["/", "Accueil — dual écosystème"],
          ["/discover", "Catalogue créateurs filtrable"],
          ["/c/[id]", "Profil créateur + paywall Stripe"],
          ["/live/[id]", "Live room chat actif"],
          ["/watch/[id]", "Player vidéo + commentaires"],
          ["/studio", "Hub créateur"],
          ["/studio/record", "Caméra navigateur"],
          ["/studio/community", "Canal privé style WhatsApp"],
          ["/messages", "DMs créateur↔fan"],
          ["/exercises", "Bibliothèque 24 exercices"],
          ["/shorts", "Feed vertical TikTok"],
          ["/programs", "Programmes structurés"],
        ].map(([r, d], i) => (
          <div key={i} className="flex items-baseline gap-3">
            <code className="text-rose font-mono text-sm">{r}</code>
            <span className="text-muted text-sm">{d}</span>
          </div>
        ))}
      </div>
      <p className="mt-8 text-base text-muted italic">unblur-app.vercel.app</p>
    </Slide>
  ),

  // 5 — Stack proposée
  () => (
    <Slide>
      <Eyebrow>Stack technique</Eyebrow>
      <Big>Pragmatique. <Hl>Speed-to-market</Hl>.</Big>
      <div className="mt-12 grid sm:grid-cols-2 gap-8 max-w-5xl">
        <div>
          <p className="text-xs uppercase tracking-widest text-rose font-bold mb-4">Front</p>
          <ul className="space-y-2 text-lg">
            <li>→ Next.js 14 App Router</li>
            <li>→ TypeScript strict</li>
            <li>→ Tailwind CSS</li>
            <li>→ React Server Components</li>
            <li>→ Vercel (déjà en place)</li>
          </ul>
        </div>
        <div>
          <p className="text-xs uppercase tracking-widest text-rose font-bold mb-4">Back</p>
          <ul className="space-y-2 text-lg">
            <li>→ PostgreSQL + Prisma</li>
            <li>→ Clerk pour l'auth</li>
            <li>→ Stripe Connect Express</li>
            <li>→ Mux pour live + replays</li>
            <li>→ Pusher Channels pour chat</li>
            <li>→ Cloudinary pour médias</li>
          </ul>
        </div>
      </div>
    </Slide>
  ),

  // 6 — Architecture
  () => (
    <Slide>
      <Eyebrow>Architecture haute-niveau</Eyebrow>
      <div className="mt-8 max-w-5xl space-y-4 text-base">
        <ArchRow l="Client (web + mobile-web)" t="Next.js 14, Tailwind" c="rose" />
        <ArchRow l="API (route handlers)" t="Server actions Next, Edge runtime" c="sun" />
        <ArchRow l="Auth" t="Clerk · JWT · OAuth Google/Apple" c="sky" />
        <ArchRow l="Persistance" t="PostgreSQL hébergé Neon · Prisma ORM" c="violet" />
        <ArchRow l="Vidéo live + replay" t="Mux Direct Upload · Mux Live · ABR streaming" c="rose" />
        <ArchRow l="Paiements + payouts" t="Stripe Connect Express · webhooks signés HMAC" c="sun" />
        <ArchRow l="Real-time" t="Pusher Channels (commencer) → Soketi self-hosted (scale)" c="sky" />
        <ArchRow l="Stockage" t="Cloudinary pour avatars + thumbnails · CloudFront pour vidéo" c="violet" />
      </div>
    </Slide>
  ),

  // 7 — Roadmap produit
  () => (
    <Slide>
      <Eyebrow>Roadmap produit</Eyebrow>
      <Big>Les briques à construire <Hl>par ordre d'impact</Hl>.</Big>
      <ol className="mt-12 space-y-3 max-w-4xl text-lg">
        {[
          ["01", "Auth + onboarding créateur + KYC Stripe"],
          ["02", "Paywall Stripe Connect · webhooks · payouts auto"],
          ["03", "Lives Mux + chat Pusher + replays auto"],
          ["04", "DMs + canal communautaire privé"],
          ["05", "Page profil créateur + paywall · ouverture publique"],
        ].map(([s, t], i) => (
          <li key={i} className="grid grid-cols-12 gap-4 items-baseline py-3 border-b border-border">
            <span className="col-span-2 font-mono text-rose">{s}</span>
            <span className="col-span-10 font-semibold">{t}</span>
          </li>
        ))}
      </ol>
    </Slide>
  ),

  // 8 — Anti-roadmap
  () => (
    <Slide>
      <Eyebrow>Ce qu'on NE fait PAS dans le MVP</Eyebrow>
      <Big>Le piège qui tue les startups :<br /><Hl>faire trop, trop tôt</Hl>.</Big>
      <div className="mt-12 grid sm:grid-cols-2 gap-x-12 gap-y-3 max-w-4xl text-base">
        {[
          ["Shorts vidéo TikTok-style", "v2 — mois 4-6"],
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

  // 9 — Décisions techniques
  () => (
    <Slide>
      <Eyebrow>Les 3 vrais choix techno</Eyebrow>
      <Big>Tout le reste découle de ça.</Big>
      <ol className="mt-10 space-y-6 max-w-4xl text-lg">
        {[
          ["Streaming vidéo", "Mux (rapide) · Livepeer (web3) · LiveKit (open source)"],
          ["Persistance", "Neon Postgres serverless · Supabase · Railway"],
          ["Paiements", "Stripe Connect Express · Stripe Connect Standard · Lemon Squeezy"],
        ].map(([t, opts], i) => (
          <li key={i} className="border-l-2 border-rose pl-5">
            <p className="font-black text-xl">{t}</p>
            <p className="text-base text-muted mt-2">{opts}</p>
          </li>
        ))}
      </ol>
      <p className="mt-10 text-base text-muted italic">Mon hypothèse : Mux + Neon + Stripe Express. Ouvert au débat.</p>
    </Slide>
  ),

  // 10 — Considérations légales
  () => (
    <Slide>
      <Eyebrow>Considérations légales · à anticiper</Eyebrow>
      <Big>Le risque qu'on sous-estime tous : <Hl>la responsabilité</Hl>.</Big>
      <ul className="mt-12 space-y-3 max-w-4xl text-lg">
        <li>→ <strong>Conformité Suisse</strong> : TVA 8,1 %, IDE, CGU robustes, LPD</li>
        <li>→ <strong>RGPD</strong> à partir de 5 000 utilisateurs (DPO requis)</li>
        <li>→ <strong>Responsabilité contenu créateur</strong> : disclaimer santé/sport sur chaque programme, assurance RC pro 6 k CHF/an</li>
        <li>→ <strong>Modération</strong> avant publication des programmes structurés</li>
        <li>→ <strong>Conformité PCI-DSS</strong> via Stripe (delegation totale)</li>
      </ul>
    </Slide>
  ),

  // 11 — Pourquoi c'est révolutionnaire
  () => (
    <Slide bg="dark">
      <Eyebrow>Pourquoi c'est révolutionnaire</Eyebrow>
      <h2 className="text-4xl sm:text-6xl lg:text-7xl font-black tracking-tightest leading-[1.02] text-surface">
        Personne au monde n'a fait <Hl>les quatre à la fois</Hl>.
      </h2>
      <div className="mt-12 grid sm:grid-cols-2 gap-x-12 gap-y-8 max-w-5xl">
        <div>
          <p className="text-xs uppercase tracking-widest text-rose font-bold mb-2">Feed vertical</p>
          <p className="text-lg text-surface/70">Les Shorts TikTok du sport. Acquisition virale.</p>
        </div>
        <div>
          <p className="text-xs uppercase tracking-widest text-rose font-bold mb-2">Live 1 clic</p>
          <p className="text-lg text-surface/70">Twitch sans la complexité. Caméra navigateur.</p>
        </div>
        <div>
          <p className="text-xs uppercase tracking-widest text-rose font-bold mb-2">Paywall créateur</p>
          <p className="text-lg text-surface/70">OnlyFans sans le sulfureux. Abonnement direct.</p>
        </div>
        <div>
          <p className="text-xs uppercase tracking-widest text-rose font-bold mb-2">Encyclopédie</p>
          <p className="text-lg text-surface/70">500+ exercices. Magnet SEO mondial.</p>
        </div>
      </div>
    </Slide>
  ),

  // 12 — Le défi technique
  () => (
    <Slide>
      <Eyebrow>Le défi technique</Eyebrow>
      <Big>Faire tenir <Hl>4 produits</Hl> sur un seul écran.<br />Sans que ça rame.</Big>
      <ul className="mt-12 space-y-4 max-w-4xl text-lg">
        <li>→ <strong>Latence live &lt; 3 s</strong> sur connexion 4G moyenne</li>
        <li>→ <strong>Scroll infini Shorts</strong> à 60 fps avec préchargement vidéo</li>
        <li>→ <strong>Paywall instantané</strong> sans rechargement de page</li>
        <li>→ <strong>Chat temps réel</strong> jusqu'à 5 000 viewers simultanés</li>
        <li>→ <strong>Replays auto</strong> générés dans la minute qui suit le live</li>
        <li>→ <strong>Search exercices</strong> &lt; 100 ms full-text</li>
      </ul>
      <p className="mt-10 text-base text-muted italic">C'est ce qui rend le produit défendable face aux clones.</p>
    </Slide>
  ),

  // 13 — Le brevet
  () => (
    <Slide>
      <Eyebrow>Le moat technique</Eyebrow>
      <Big>Un <Hl>brevet européen</Hl> sur l'algorithme.</Big>
      <div className="mt-12 max-w-4xl space-y-6 text-lg">
        <p className="text-muted leading-relaxed">
          Méthode mise en œuvre par ordinateur qui ajuste dynamiquement la commission selon trois axes :
        </p>
        <ul className="space-y-3 pl-6">
          <li>→ Paliers de revenu du créateur (commission dégressive 30 → 5 %)</li>
          <li>→ Durée cumulative de fidélité de chaque abonné individuel</li>
          <li>→ Système de parrainage croisé entre créateurs</li>
        </ul>
        <p className="text-muted leading-relaxed">
          C'est un algorithme spécifique, brevetable selon l'EPO. Cabinet PI Zurich. Code source = forteresse.
        </p>
      </div>
    </Slide>
  ),

  // 14 — Ce qui existe déjà
  () => (
    <Slide>
      <Eyebrow>L'état du produit aujourd'hui</Eyebrow>
      <Big>Ce n'est pas une <Hl>idée</Hl>. C'est une <Hl>démo</Hl>.</Big>
      <ul className="mt-12 space-y-3 max-w-4xl text-lg">
        <li>→ <strong>15 routes Next.js</strong> entièrement fonctionnelles en production sur Vercel</li>
        <li>→ <strong>Design system complet</strong> · variables CSS · typographie éditoriale</li>
        <li>→ <strong>24 exercices documentés</strong> avec filtres muscle / équipement / catégorie</li>
        <li>→ <strong>Feed Shorts vertical</strong> style TikTok, scroll fluide</li>
        <li>→ <strong>Studio créateur</strong> · record · communauté · programmes</li>
        <li>→ <strong>Pitch deck VC</strong> de 40 slides en code, accessible publiquement</li>
        <li>→ <strong>Marques déposées</strong> (CH + EU + US) · brevet en cours de dépôt</li>
      </ul>
    </Slide>
  ),

  // 15 — Ce qu'il reste à construire
  () => (
    <Slide>
      <Eyebrow>Ce qu'il reste à construire</Eyebrow>
      <Big>Le passage de <Hl>démo</Hl> à <Hl>plateforme</Hl>.</Big>
      <ul className="mt-12 space-y-3 max-w-4xl text-lg">
        <li>→ Backend persistant (Postgres + Prisma)</li>
        <li>→ Auth réelle (Clerk + KYC créateur)</li>
        <li>→ Paiements + payouts (Stripe Connect Express)</li>
        <li>→ Vidéo live native (Mux + Pusher)</li>
        <li>→ Replays automatiques</li>
        <li>→ Webhooks signés, sécurité, observabilité</li>
        <li>→ Migration des mocks vers la vraie API</li>
      </ul>
    </Slide>
  ),

  // 16 — La vision technique
  () => (
    <Slide bg="dark">
      <div className="max-w-5xl">
        <p className="text-xs uppercase tracking-[0.5em] text-surface/40 mb-12">La vision technique</p>
        <h2 className="text-5xl sm:text-7xl font-black tracking-tightest leading-[1.02] text-surface mb-12">
          Construire l'<span className="text-rose">infrastructure</span><br />du sport en ligne francophone.
        </h2>
        <p className="text-xl text-surface/70 leading-relaxed max-w-3xl">
          Pas une app de plus. Une couche de base sur laquelle des milliers de coachs vont vivre. Avec une qualité d'exécution qui force le respect — au niveau Apple, pas au niveau startup MVP.
        </p>
      </div>
    </Slide>
  ),

  // 17 — Closing
  () => (
    <Slide bg="dark">
      <div className="text-center max-w-5xl mx-auto">
        <p className="text-xs uppercase tracking-[0.5em] text-surface/40 mb-12">Maintenant</p>
        <h2 className="text-6xl sm:text-9xl font-black tracking-tightest leading-[0.9] text-surface">
          Tes questions<span className="text-rose">.</span>
        </h2>
        <p className="mt-16 text-2xl text-surface/60 max-w-2xl mx-auto leading-snug">
          Architecture, stack, choix techniques. Tout est ouvert au débat.
        </p>
        <p className="mt-12 text-xs uppercase tracking-[0.5em] text-surface/30">
          unblur-app.vercel.app · damien@unblur.app
        </p>
      </div>
    </Slide>
  ),

  // 18 — Annexe : screenshots de la démo
  () => (
    <Slide>
      <Eyebrow>Annexe — Démo cliquable</Eyebrow>
      <Big>Tu peux explorer chaque écran avant lundi.</Big>
      <div className="mt-12 max-w-3xl text-lg space-y-2">
        <Row l="Accueil" v="/" />
        <Row l="Catalogue créateurs" v="/discover" />
        <Row l="Profil créateur (Louise)" v="/c/c_louise" />
        <Row l="Live room" v="/live/c_louise" />
        <Row l="Studio créateur" v="/studio" />
        <Row l="Caméra live" v="/studio/record" />
        <Row l="Communauté WhatsApp-like" v="/studio/community" />
        <Row l="Bibliothèque exercices" v="/exercises" />
        <Row l="Shorts TikTok-like" v="/shorts" />
        <Row l="Pitch deck VC complet" v="/pitch" />
      </div>
      <p className="mt-10 text-base text-muted italic">Tout est dans `unblur-app.vercel.app`. Code source sur github.com/Damien74350/agent1, dossier `unblur`.</p>
    </Slide>
  ),
];

export default function PitchTechPage() {
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
    <div className="fixed inset-0 overflow-hidden" style={{ background: "var(--bg-base)" }}>
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
        <div className="flex gap-1 px-3 py-2 rounded-full bg-surface/80 backdrop-blur ring-1 ring-border">
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
    <div className={`min-h-screen grid place-items-center px-12 sm:px-20 py-12 ${bg === "dark" ? "bg-foreground text-surface" : "text-foreground"}`} style={bg === "light" ? { background: "var(--bg-base)" } : {}}>
      <div className="w-full max-w-7xl">{children}</div>
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
function Row({ l, v, highlight }: { l: string; v: string; highlight?: boolean }) {
  return (
    <div className={`flex items-baseline justify-between py-3 border-b border-border ${highlight ? "font-black" : ""}`}>
      <span className={highlight ? "" : "text-muted"}>{l}</span>
      <span className={`font-mono tabular-nums ${highlight ? "text-rose text-xl" : ""}`}>{v}</span>
    </div>
  );
}
function ArchRow({ l, t, c }: { l: string; t: string; c: string }) {
  return (
    <div className="grid grid-cols-12 gap-4 items-baseline py-3 border-b border-border">
      <div className={`col-span-1 h-3 rounded-full bg-${c}`} />
      <span className="col-span-4 font-black">{l}</span>
      <span className="col-span-7 text-muted font-mono text-sm">{t}</span>
    </div>
  );
}
