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
      <Big>Bienvenue.<br />Voici ce que je veux construire <Hl>avec toi</Hl>.</Big>
      <p className="mt-12 text-xl text-muted max-w-3xl leading-relaxed">
        Je vais te montrer le concept, l'architecture, et la stack que j'envisage. Puis on discute du périmètre du MVP, des choix technos, et de comment on travaille ensemble.
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
      <Eyebrow>Stack technique proposée</Eyebrow>
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
      <p className="mt-10 text-base text-muted italic">Tout est négociable. C'est ton terrain.</p>
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

  // 7 — MVP scope (priorités)
  () => (
    <Slide>
      <Eyebrow>MVP en 12 semaines</Eyebrow>
      <Big>Le strict minimum pour signer 30 créateurs.</Big>
      <ol className="mt-12 space-y-3 max-w-4xl text-lg">
        {[
          ["S1-2", "Auth + onboarding créateur + KYC Stripe"],
          ["S2-4", "Paywall Stripe Connect · webhooks · payouts auto"],
          ["S4-7", "Lives Mux + chat Pusher + replays auto"],
          ["S7-9", "DMs + canal communautaire privé"],
          ["S9-12", "Page profil créateur + paywall + smoke-testing"],
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
      <Eyebrow>3 décisions techniques à prendre ensemble</Eyebrow>
      <ol className="mt-10 space-y-6 max-w-4xl text-lg">
        {[
          ["Streaming vidéo", "Mux (rapide, cher) · Livepeer (web3) · LiveKit (open source)"],
          ["Persistance", "Neon Postgres serverless · Supabase · Railway"],
          ["Paiements", "Stripe Connect Express · Stripe Connect Standard · Lemon Squeezy"],
        ].map(([t, opts], i) => (
          <li key={i} className="border-l-2 border-rose pl-5">
            <p className="font-black text-xl">{t}</p>
            <p className="text-base text-muted mt-2">{opts}</p>
          </li>
        ))}
      </ol>
      <p className="mt-10 text-base text-muted italic">Mes hypothèses : Mux + Neon + Stripe Express. Tu valides ?</p>
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

  // 11 — Budget développement
  () => (
    <Slide>
      <Eyebrow>Budget MVP estimé</Eyebrow>
      <Big>Combien pour livrer en 12 semaines ?</Big>
      <div className="mt-12 max-w-3xl space-y-3">
        <Row l="Développement (toi)" v="60-100 k CHF" />
        <Row l="Infrastructure cloud (Vercel + Neon + Mux + Stripe)" v="800 CHF/mois" />
        <Row l="Design polish + assets" v="6 k CHF" />
        <Row l="Tests + QA" v="3 k CHF" />
        <Row l="Légal + CGU + brevet" v="15 k CHF" />
        <Row l="Total MVP 12 semaines" v="84-124 k CHF" highlight />
      </div>
      <p className="mt-8 text-base text-muted">Sur les 800 k CHF du pré-seed, tu dois représenter ~15 % du budget total.</p>
    </Slide>
  ),

  // 12 — Modalités de collaboration
  () => (
    <Slide>
      <Eyebrow>Comment tu rejoins l'aventure</Eyebrow>
      <Big>3 options. <Hl>À toi de choisir.</Hl></Big>
      <div className="grid sm:grid-cols-3 gap-6 mt-12">
        {[
          { t: "A · Co-fondatrice technique", s: "2-3 k CHF/mois", e: "12-20 % equity vesting 4 ans", who: "Tu crois fort au projet" },
          { t: "B · Lead Dev salariée", s: "8-10 k CHF/mois", e: "Stock options après 12 mois", who: "Tu veux sécuriser" },
          { t: "C · Freelance MVP forfait", s: "60-100 k CHF forfait", e: "Pas d'engagement long-terme", who: "Tu veux tester d'abord" },
        ].map((o, i) => (
          <div key={i} className={`p-6 rounded-3xl ${i === 0 ? "bg-foreground text-surface" : "border border-border"}`}>
            <p className="text-2xl font-black mb-4">{o.t}</p>
            <p className="text-xs uppercase tracking-widest font-bold opacity-70">Rémunération</p>
            <p className="mt-1 font-bold">{o.s}</p>
            <p className="mt-4 text-xs uppercase tracking-widest font-bold opacity-70">Equity</p>
            <p className="mt-1 font-bold">{o.e}</p>
            <p className="mt-6 text-xs opacity-60 italic">{o.who}</p>
          </div>
        ))}
      </div>
    </Slide>
  ),

  // 13 — Mon rôle
  () => (
    <Slide>
      <Eyebrow>Mon rôle vs ton rôle</Eyebrow>
      <Big>Moi la <Hl>vision</Hl>.<br />Toi le <Hl>code</Hl>.</Big>
      <div className="mt-12 grid sm:grid-cols-2 gap-8 max-w-5xl">
        <div className="p-8 rounded-3xl border border-border">
          <p className="text-xs uppercase tracking-[0.3em] text-rose font-bold mb-4">Moi — Damien</p>
          <ul className="space-y-2 text-base text-muted">
            <li>→ Concept, naming, branding</li>
            <li>→ Modèle économique, brevet</li>
            <li>→ Recrutement créateurs</li>
            <li>→ Levée de fonds, presse</li>
            <li>→ Deals sponsors</li>
            <li>→ Stratégie pays par pays</li>
          </ul>
        </div>
        <div className="p-8 rounded-3xl bg-foreground text-surface">
          <p className="text-xs uppercase tracking-[0.3em] text-rose font-bold mb-4">Toi — la codeuse</p>
          <ul className="space-y-2 text-base text-surface/70">
            <li>→ MVP en 12 semaines</li>
            <li>→ Stack technique solide</li>
            <li>→ Architecture scalable</li>
            <li>→ Sécurité + RGPD</li>
            <li>→ Tu construis ce que je vois</li>
            <li>→ Tu raffines techniquement</li>
          </ul>
        </div>
      </div>
    </Slide>
  ),

  // 14 — Calendrier
  () => (
    <Slide>
      <Eyebrow>Calendrier que je tiens</Eyebrow>
      <div className="mt-10 space-y-8 max-w-4xl">
        <div>
          <p className="text-rose font-black text-6xl tracking-tighter">Lundi 15 juin</p>
          <p className="mt-2 text-lg text-muted">Aujourd'hui · on aligne la vision et le scope</p>
        </div>
        <div>
          <p className="text-rose font-black text-6xl tracking-tighter">Fin juin</p>
          <p className="mt-2 text-lg text-muted">Décision sur la modalité de collaboration · contrat signé</p>
        </div>
        <div>
          <p className="text-rose font-black text-6xl tracking-tighter">Début juillet</p>
          <p className="mt-2 text-lg text-muted">Démarrage MVP · Sprint 0</p>
        </div>
        <div>
          <p className="text-foreground font-black text-6xl tracking-tighter">Fin août</p>
          <p className="mt-2 text-lg text-muted">Bêta privée · 5 Unblurers tests</p>
        </div>
        <div>
          <p className="text-foreground font-black text-6xl tracking-tighter">Octobre</p>
          <p className="mt-2 text-lg text-muted">Ouverture publique Suisse romande</p>
        </div>
      </div>
    </Slide>
  ),

  // 15 — Décisions à prendre aujourd'hui
  () => (
    <Slide>
      <Eyebrow>Ce qu'on décide ensemble aujourd'hui</Eyebrow>
      <ol className="mt-12 space-y-5 max-w-4xl text-xl">
        {[
          "Faisabilité du MVP en 12 semaines · avec 1 dev senior",
          "Choix techno : Mux ou alternative ? Persistance ? Auth ?",
          "Budget MVP : 60-100 k CHF, on confirme l'enveloppe ?",
          "Modalité de collaboration : Option A, B ou C ?",
          "Timing du démarrage : début juillet, on tient ?",
        ].map((q, i) => (
          <li key={i} className="flex gap-5 items-baseline">
            <span className="text-4xl font-black text-rose tabular-nums">{String(i + 1).padStart(2, "0")}</span>
            <span>{q}</span>
          </li>
        ))}
      </ol>
    </Slide>
  ),

  // 16 — Pourquoi je veux toi
  () => (
    <Slide bg="dark">
      <div className="max-w-5xl">
        <p className="text-xs uppercase tracking-[0.5em] text-surface/40 mb-12">Pourquoi je viens te voir</p>
        <h2 className="text-5xl sm:text-7xl font-black tracking-tightest leading-[1.02] text-surface mb-12">
          Parce que tu sais construire des choses qui <span className="text-rose">scalent</span>.
        </h2>
        <p className="text-xl text-surface/70 leading-relaxed max-w-3xl">
          Je sais convaincre des créateurs, lever de l'argent, écrire un brevet, vendre à des sponsors. Mais sans toi, ce projet reste une démo Vercel. Avec toi, il devient l'infrastructure du sport en ligne francophone.
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
          On en parle<span className="text-rose">.</span>
        </h2>
        <p className="mt-16 text-2xl text-surface/60 max-w-2xl mx-auto leading-snug">
          Tu poses tes questions. Tu donnes ton avis sur la stack. On regarde ensemble ce qui te va.
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
