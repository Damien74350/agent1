import Link from "next/link";
import { Card, Pill, Stat } from "../../components/Card";
import { ContentCard } from "../../components/ContentCard";
import { MY_SUBSCRIPTIONS, MY_FEED, findCreator } from "../../lib/mock";
import { compact, fmtEUR, relativeDate } from "../../lib/format";
import { Heart, Calendar, Tv, Coins } from "lucide-react";

export default function FeedPage() {
  const totalMonthly = MY_SUBSCRIPTIONS.reduce((s, x) => s + x.monthlyPrice, 0);
  const totalPaid = MY_SUBSCRIPTIONS.reduce((s, x) => s + x.totalPaid, 0);
  const totalWatched = MY_SUBSCRIPTIONS.reduce((s, x) => s + x.contentWatched, 0);

  return (
    <div className="space-y-6">
      <header>
        <Pill color="rose">Mon feed</Pill>
        <h1 className="mt-3 text-3xl sm:text-4xl font-black tracking-tight">
          Tes <span className="rose-text">{MY_SUBSCRIPTIONS.length} créateurs</span>, en un endroit
        </h1>
      </header>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <Stat icon={<Heart size={16} />} label="Abonnements actifs" value={MY_SUBSCRIPTIONS.length} />
        <Stat icon={<Coins size={16} />} label="Total mensuel" value={fmtEUR(totalMonthly)} hint="payé en début de mois" />
        <Stat icon={<Coins size={16} />} label="Payé depuis l'inscription" value={fmtEUR(totalPaid, 0)} hint="à des créateurs réels" />
        <Stat icon={<Calendar size={16} />} label="Contenus vus" value={totalWatched} hint="ce trimestre" trend={28.4} />
      </div>

      {/* Mes abonnements */}
      <Card title="Tes abonnements">
        <div className="space-y-2">
          {MY_SUBSCRIPTIONS.map(s => {
            const c = findCreator(s.creatorId)!;
            return (
              <Link key={s.creatorId} href={`/c/${c.id}`} className="block">
                <div className="flex items-center gap-3 rounded-xl bg-white/5 hover:bg-white/10 p-3 transition">
                  <div className="w-12 h-12 rounded-2xl grid place-items-center font-black text-black" style={{ background: c.banner }}>{c.avatar}</div>
                  <div className="flex-1 min-w-0">
                    <p className="font-bold truncate">{c.name}</p>
                    <p className="text-[11px] text-muted truncate">{c.handle} · abonné depuis {relativeDate(s.subscribedAt)}</p>
                  </div>
                  <div className="text-right">
                    <p className="font-black rose-text">{fmtEUR(s.monthlyPrice)}<span className="text-muted text-xs">/m</span></p>
                    <p className="text-[10px] text-muted">{s.contentWatched} contenus vus</p>
                  </div>
                </div>
              </Link>
            );
          })}
        </div>
      </Card>

      {/* Feed contenu */}
      <section>
        <header className="mb-4">
          <Pill color="sun">Nouveautés de tes créateurs</Pill>
          <h2 className="mt-2 text-2xl font-black">À découvrir maintenant</h2>
        </header>
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {MY_FEED.map(c => <ContentCard key={c.id} content={c} />)}
        </div>
      </section>
    </div>
  );
}
