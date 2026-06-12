import { CreatorCard } from "../../components/CreatorCard";
import { Pill, Card } from "../../components/Card";
import { LIVE_NOW, CREATORS } from "../../lib/mock";
import { Tv, Clock, Calendar } from "lucide-react";

export default function LivePage() {
  const live = LIVE_NOW;
  const scheduledNext = CREATORS.filter(c => !c.isLive).slice(0, 4);

  return (
    <div className="space-y-6">
      <header>
        <Pill color="rose"><span className="w-2 h-2 rounded-full bg-rose live-dot mr-1" />Lives</Pill>
        <h1 className="mt-3 text-3xl sm:text-4xl font-black tracking-tight">
          <span className="rose-text">{live.length} créateurs</span> en direct maintenant
        </h1>
        <p className="mt-2 text-muted">Rejoins une séance, pose tes questions en chat.</p>
      </header>

      {live.length > 0 && (
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {live.map(c => <CreatorCard key={c.id} creator={c} />)}
        </div>
      )}

      <Card title="Programmés bientôt" subtitle="N'oublie pas de t'abonner">
        <div className="space-y-2">
          {scheduledNext.map((c, i) => (
            <div key={c.id} className="flex items-center gap-3 rounded-xl bg-white/5 p-3">
              <div className="w-10 h-10 rounded-xl grid place-items-center font-black text-black text-xs" style={{ background: c.banner }}>{c.avatar}</div>
              <div className="flex-1 min-w-0">
                <p className="font-bold text-sm truncate">{c.name}</p>
                <p className="text-[11px] text-muted truncate">{c.tagline}</p>
              </div>
              <div className="text-right">
                <p className="text-xs font-bold inline-flex items-center gap-1"><Calendar size={10} /> Dans {(i + 1) * 3}h</p>
                <p className="text-[10px] text-muted">Durée prévue : {30 + i * 15}min</p>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
