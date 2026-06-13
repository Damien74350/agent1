"use client";

import Link from "next/link";
import { ME, MY_PAYOUTS } from "../../lib/mock";
import { compact, fmtEUR } from "../../lib/format";
import {
  Video, BookOpen, Lightbulb, Users, Megaphone, BarChart3, Coins,
  ArrowRight, Sparkles, Lock, MessageCircle, PenTool, Calendar, Bell, Image as ImageIcon,
} from "lucide-react";

export default function StudioPage() {
  const currentPayout = MY_PAYOUTS[0];
  const monthlyNet = ME.monthlyEarningsEUR * 0.80;

  return (
    <div className="space-y-16 pb-12">
      {/* HERO */}
      <section className="pt-12">
        <p className="text-xs uppercase tracking-[0.28em] text-muted mb-6">Studio Unblurer</p>
        <h1 className="text-4xl sm:text-6xl font-black tracking-tightest leading-[0.95]">
          Salut Louise.
        </h1>
        <p className="mt-4 text-lg text-muted max-w-2xl">
          Ton studio complet : filmer, écrire, animer ta communauté, gagner ta vie. Tout au même endroit.
        </p>

        {/* GO LIVE — bouton 1-clic ultra-visible */}
        <div className="mt-8 flex flex-wrap items-center gap-3">
          <Link href="/studio/record?live=1" className="inline-flex items-center gap-3 px-6 py-4 rounded-full bg-rose text-surface font-black text-base shadow-glow hover:scale-[1.02] transition">
            <span className="w-2.5 h-2.5 rounded-full bg-surface live-dot" />
            LANCER UN LIVE
            <span className="text-[10px] opacity-80 font-bold uppercase tracking-widest">1 clic</span>
          </Link>
          <Link href="/studio/record" className="inline-flex items-center gap-2 px-5 py-3 rounded-full border border-border hover:bg-overlay/5 font-semibold transition">
            <Video size={15} /> Filmer un replay
          </Link>
        </div>
      </section>

      {/* QUICK ACTIONS — les 6 outils principaux */}
      <section>
        <p className="text-xs uppercase tracking-[0.28em] text-muted mb-6">Que veux-tu faire maintenant ?</p>
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <StudioAction
            href="/studio/record"
            icon={Video}
            title="Filmer maintenant"
            desc="Lance ta caméra. Live ou enregistrement. Publication en 1 clic."
            badge="Le plus utilisé"
          />
          <StudioAction
            href="/studio/programs/new"
            icon={BookOpen}
            title="Écrire un programme"
            desc="Plan jour par jour. Cohorte privée. Pour TA communauté."
          />
          <StudioAction
            href="/studio/tips"
            icon={Lightbulb}
            title="Poster un tip"
            desc="Texte rapide, image, audio. Apparaît dans le feed des abonnés."
          />
          <StudioAction
            href="/studio/community"
            icon={Users}
            title="Animer ma communauté"
            desc="Chat privé groupe + DMs + channels par thème, comme WhatsApp."
            badge="🔥 Nouveau"
          />
          <StudioAction
            href="/studio/broadcast"
            icon={Megaphone}
            title="Envoyer une diffusion"
            desc="Push notification + email à tous tes abonnés en un coup."
          />
          <StudioAction
            href="/dashboard"
            icon={BarChart3}
            title="Voir mes stats"
            desc="Abonnés, revenus, watch time, engagement, churn."
          />
        </div>
      </section>

      {/* REVENUE — sobre, comme une banque */}
      <section className="border-y border-border py-10">
        <div className="grid lg:grid-cols-3 gap-8 items-center">
          <div>
            <p className="text-xs uppercase tracking-[0.28em] text-muted mb-3">Ce mois</p>
            <p className="text-4xl sm:text-5xl font-black tabular-nums tracking-tighter">{fmtEUR(monthlyNet, 0)}</p>
            <p className="text-sm text-muted mt-2">Net après 20% unblur · versement Stripe le 5 du mois</p>
          </div>
          <div className="grid grid-cols-3 gap-4 lg:col-span-2">
            <Mini label="Abonnés" value={compact(ME.subscribers)} />
            <Mini label="Suivers gratuits" value={compact(ME.freeFollowers)} />
            <Mini label="Note" value={ME.rating.toFixed(2) + " / 5"} />
          </div>
        </div>
      </section>

      {/* COMMUNITY TOOLS — détail des outils communauté */}
      <section>
        <p className="text-xs uppercase tracking-[0.28em] text-muted mb-3">Outils pour ta communauté</p>
        <h2 className="text-3xl sm:text-5xl font-black tracking-tighter mb-10">Anime, échange, fidélise.</h2>

        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-x-12 gap-y-10">
          {[
            { icon: MessageCircle, t: "Chat groupe privé", d: "Tous tes abonnés dans un canal type WhatsApp. Tu écris, ils répondent." },
            { icon: Bell, t: "Channels par thème", d: "#nutrition · #questions · #annonces. Chacun s'abonne aux sujets qui l'intéressent." },
            { icon: Users, t: "Lives interactifs", d: "Chat actif pendant tes lives, sondages instantanés, réactions emoji." },
            { icon: Calendar, t: "Calendrier collectif", d: "Tes prochains lives et programmes visibles pour tous. Inscriptions en 1 clic." },
            { icon: PenTool, t: "Form check vidéo", d: "Tes abonnés envoient leur vidéo, tu réponds en commenté ou en privé." },
            { icon: ImageIcon, t: "Galerie de progression", d: "Tes abonnés partagent leurs résultats. Toi tu likes, commentes, motives." },
          ].map(o => (
            <div key={o.t}>
              <o.icon size={20} className="mb-3" />
              <p className="font-bold text-lg">{o.t}</p>
              <p className="text-sm text-muted mt-1 leading-relaxed">{o.d}</p>
            </div>
          ))}
        </div>
      </section>

      {/* FUTURE — pub interne */}
      <section className="rounded-3xl border border-border p-8">
        <div className="flex items-start gap-4">
          <Sparkles size={20} className="text-rose shrink-0 mt-1" />
          <div className="flex-1">
            <div className="flex items-center gap-2">
              <p className="font-black text-lg">Boost ton profil — bientôt</p>
              <span className="inline-flex items-center gap-1 text-[10px] font-bold uppercase tracking-widest px-2 py-0.5 rounded-full bg-overlay/5 border border-border">
                <Lock size={9} /> 2027
              </span>
            </div>
            <p className="text-sm text-muted mt-1 max-w-2xl leading-relaxed">
              Quand la plateforme atteindra 100 000 abonnés cumulés, tu pourras promouvoir ton profil dans ta catégorie pour 50€/mois. Visibilité × 8. Bouton activable depuis ici.
            </p>
            <button disabled className="mt-3 inline-flex items-center gap-1.5 text-xs font-bold text-muted">
              Bientôt disponible
            </button>
          </div>
        </div>
      </section>

      {/* PAYOUT recap */}
      <section>
        <p className="text-xs uppercase tracking-[0.28em] text-muted mb-3">Historique versements</p>
        <div className="border-t border-border">
          {MY_PAYOUTS.map(p => (
            <div key={p.id} className="flex items-baseline justify-between py-4 border-b border-border">
              <div>
                <p className="font-bold">{p.periodLabel}</p>
                <p className="text-xs text-muted mt-0.5">Brut {fmtEUR(p.grossEUR, 0)} · Frais plateforme {fmtEUR(p.platformFeeEUR, 0)}</p>
              </div>
              <div className="text-right">
                <p className="font-black tabular-nums text-xl">{fmtEUR(p.netEUR, 0)}</p>
                <p className={`text-[10px] uppercase font-bold ${p.status === "paid" ? "text-success" : "text-muted"}`}>{p.status === "paid" ? "Versé" : "En cours"}</p>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}

function StudioAction({ href, icon: Icon, title, desc, badge }: { href: string; icon: any; title: string; desc: string; badge?: string }) {
  return (
    <Link href={href} className="group block rounded-3xl border border-border hover:border-foreground/40 p-6 transition">
      <div className="flex items-start justify-between">
        <Icon size={22} />
        {badge && <span className="text-[10px] uppercase tracking-widest font-bold text-rose">{badge}</span>}
      </div>
      <p className="mt-5 font-black text-lg">{title}</p>
      <p className="mt-1 text-sm text-muted leading-relaxed">{desc}</p>
      <p className="mt-4 inline-flex items-center gap-1 text-xs font-bold group-hover:underline">
        Ouvrir <ArrowRight size={12} />
      </p>
    </Link>
  );
}

function Mini({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-3xl sm:text-4xl font-black tabular-nums tracking-tighter">{value}</p>
      <p className="text-xs uppercase tracking-[0.18em] text-muted mt-2">{label}</p>
    </div>
  );
}
