import { Card, Pill, Stat } from "../../components/Card";
import { ContentCard } from "../../components/ContentCard";
import { ME, MY_CONTENTS, MY_PAYOUTS } from "../../lib/mock";
import { compact, fmtEUR } from "../../lib/format";
import { Users, Coins, TrendingUp, Tv, Sparkles, Heart, MessageCircle, Eye, CheckCircle2, Clock, Settings, Upload, Send } from "lucide-react";

export default function DashboardPage() {
  const currentPayout = MY_PAYOUTS[0];
  const lastPayout = MY_PAYOUTS[1];
  const monthlyGross = ME.monthlyEarningsEUR;
  const monthlyNet = monthlyGross * 0.80;
  const totalNet = ME.totalEarningsEUR * 0.80;

  return (
    <div className="space-y-6">
      <header className="flex flex-col lg:flex-row lg:items-end justify-between gap-4">
        <div>
          <Pill color="rose">Studio créateur</Pill>
          <h1 className="mt-3 text-3xl sm:text-4xl font-black tracking-tight">
            Salut <span className="rose-text">Louise</span> ✨
          </h1>
          <p className="mt-2 text-muted">Ton mois est en route. Voici ta machine.</p>
        </div>
        <div className="flex gap-2">
          <button className="inline-flex items-center gap-1.5 px-3 py-2 rounded-lg rose-gradient text-black text-sm font-bold shadow-glow">
            <Upload size={14} /> Uploader
          </button>
          <button className="inline-flex items-center gap-1.5 px-3 py-2 rounded-lg bg-rose/15 text-rose ring-1 ring-rose/30 text-sm font-bold">
            <Tv size={14} /> Lancer un live
          </button>
        </div>
      </header>

      {/* KPIs */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <Stat icon={<Coins size={16} />} label="Mois en cours · brut" value={fmtEUR(monthlyGross, 0)} hint="objectif 25k €" trend={12.4} />
        <Stat icon={<Coins size={16} />} label="Mois en cours · NET (80%)" value={fmtEUR(monthlyNet, 0)} hint="versé en début juillet" trend={12.4} />
        <Stat icon={<Users size={16} />} label="Abonnés actifs" value={compact(ME.subscribers)} hint={`+ ${compact(ME.freeFollowers)} followers gratuits`} trend={8.2} />
        <Stat icon={<TrendingUp size={16} />} label="Revenus à vie · NET" value={fmtEUR(totalNet, 0)} hint="depuis ton inscription" />
      </div>

      {/* PAYOUT EN COURS */}
      <Card title="Versement en cours" subtitle="Stripe — virement automatique le 5 du mois suivant" right={<Pill color="success">{currentPayout.status === "pending" ? "en cours" : currentPayout.status}</Pill>}>
        <div className="grid sm:grid-cols-3 gap-3">
          <div className="rounded-xl bg-white/5 p-4">
            <p className="text-[10px] uppercase text-muted">Brut généré</p>
            <p className="text-2xl font-black mt-1">{fmtEUR(currentPayout.grossEUR, 0)}</p>
          </div>
          <div className="rounded-xl bg-white/5 p-4">
            <p className="text-[10px] uppercase text-muted">Frais plateforme (20%)</p>
            <p className="text-2xl font-black mt-1 text-muted">- {fmtEUR(currentPayout.platformFeeEUR, 0)}</p>
          </div>
          <div className="rounded-xl bg-rose/10 ring-1 ring-rose/30 p-4">
            <p className="text-[10px] uppercase text-rose font-bold">NET pour toi</p>
            <p className="text-2xl font-black rose-text mt-1">{fmtEUR(currentPayout.netEUR, 0)}</p>
          </div>
        </div>

        <div className="mt-4 pt-4 border-t border-white/10">
          <p className="text-[10px] uppercase tracking-wider text-muted font-bold mb-2">Historique versements</p>
          <table className="w-full text-sm">
            <thead className="text-[10px] uppercase text-muted">
              <tr className="text-left">
                <th className="py-1.5">Période</th>
                <th className="text-right">Brut</th>
                <th className="text-right">Net</th>
                <th className="text-right">Status</th>
              </tr>
            </thead>
            <tbody>
              {MY_PAYOUTS.slice(1).map(p => (
                <tr key={p.id} className="border-t border-white/5">
                  <td className="py-2 font-semibold">{p.periodLabel}</td>
                  <td className="text-right">{fmtEUR(p.grossEUR, 0)}</td>
                  <td className="text-right font-bold rose-text">{fmtEUR(p.netEUR, 0)}</td>
                  <td className="text-right text-[10px] uppercase font-bold text-success">{p.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      {/* ENGAGEMENT */}
      <div className="grid lg:grid-cols-3 gap-6">
        <Card title="Engagement cette semaine" subtitle="Tes contenus performent">
          <div className="space-y-3">
            {[
              { label: "Vues totales", value: compact(MY_CONTENTS.reduce((s, c) => s + c.views, 0)), icon: Eye },
              { label: "Likes reçus", value: compact(MY_CONTENTS.reduce((s, c) => s + c.likes, 0)), icon: Heart },
              { label: "Commentaires", value: compact(MY_CONTENTS.reduce((s, c) => s + c.comments, 0)), icon: MessageCircle },
              { label: "Watch time moyen", value: "18 min", icon: Clock },
            ].map(o => (
              <div key={o.label} className="flex items-center justify-between rounded-xl bg-white/5 px-3 py-2.5">
                <div className="flex items-center gap-2 text-sm">
                  <o.icon size={14} className="text-rose" />
                  <span>{o.label}</span>
                </div>
                <span className="font-black">{o.value}</span>
              </div>
            ))}
          </div>
        </Card>

        <Card className="lg:col-span-2" title="Tes contenus" subtitle={`${MY_CONTENTS.length} publiés`} right={<button className="text-xs font-bold text-rose hover:underline">Nouveau →</button>}>
          <div className="grid sm:grid-cols-3 gap-4">
            {MY_CONTENTS.map(c => <ContentCard key={c.id} content={c} />)}
          </div>
        </Card>
      </div>

      {/* GROWTH SUGGESTIONS */}
      <Card title="Boost ta croissance" subtitle="Suggestions personnalisées">
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {[
            { icon: Tv, title: "Lance un live cette semaine", desc: "Tes derniers lives ont eu +180 nouveaux abonnés. Reconduit le mardi à 18h.", color: "rose" as const },
            { icon: Send, title: "Réponds aux 12 messages en attente", desc: "Les créateurs qui répondent dans 24h gardent 22% plus d'abonnés.", color: "sun" as const },
            { icon: Sparkles, title: "Crée un programme 8 semaines", desc: "Les programmes structurés convertissent 3× plus que les vidéos isolées.", color: "violet" as const },
            { icon: Heart, title: "Lance un challenge gratuit", desc: "Attire 1500+ nouveaux followers en 7 jours pour ensuite les convertir.", color: "sky" as const },
            { icon: Settings, title: "Active l'abonnement annuel", desc: "Les créateurs avec offre annuelle gagnent 38% en moyenne.", color: "rose" as const },
            { icon: Users, title: "Collab avec @marko.run", desc: "Audience complémentaire. Croisement chiffré : +840 abonnés probables.", color: "sun" as const },
          ].map(o => (
            <button key={o.title} className="text-left rounded-xl bg-white/5 ring-1 ring-white/10 p-4 hover:ring-rose/30 transition">
              <o.icon size={18} className={`text-${o.color} mb-2`} />
              <p className="font-bold text-sm">{o.title}</p>
              <p className="text-[11px] text-muted mt-1">{o.desc}</p>
            </button>
          ))}
        </div>
      </Card>
    </div>
  );
}
