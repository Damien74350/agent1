import Link from "next/link";
import { Card, Pill } from "../../components/Card";
import { CREATORS } from "../../lib/mock";
import { compact, fmtEUR } from "../../lib/format";
import { Calendar, CheckCircle2, Lock, Sparkles, Users, Clock } from "lucide-react";

const PROGRAMS = [
  { id: "pg_1", creatorId: "c_louise", title: "Premier pull-up en 12 semaines", weeks: 12, sessionsPerWeek: 4, level: "Débutant",   priceEUR: 49, subs: 1240, included: true,  cover: "linear-gradient(135deg, #ff2e7e, #ffb347)" },
  { id: "pg_2", creatorId: "c_marko",  title: "Marathon sub 4h",                weeks: 16, sessionsPerWeek: 5, level: "Intermédiaire", priceEUR: 89, subs: 2840, included: true,  cover: "linear-gradient(135deg, #5eead4, #5b9eff)" },
  { id: "pg_3", creatorId: "c_amira",  title: "Posture parfaite — 8 semaines", weeks: 8,  sessionsPerWeek: 3, level: "Débutant",     priceEUR: 39, subs: 4120, included: true,  cover: "linear-gradient(135deg, #a78bfa, #ff2e7e)" },
  { id: "pg_4", creatorId: "c_jules",  title: "Calisthenics fondations 8 sem", weeks: 8,  sessionsPerWeek: 4, level: "Débutant",     priceEUR: 29, subs: 480,  included: false, cover: "linear-gradient(135deg, #5eead4, #ffb347)" },
  { id: "pg_5", creatorId: "c_theo",   title: "Force 5/3/1 — 12 semaines",      weeks: 12, sessionsPerWeek: 4, level: "Avancé",       priceEUR: 69, subs: 920,  included: false, cover: "linear-gradient(135deg, #ffb347, #ff2e7e)" },
  { id: "pg_6", creatorId: "c_chloé",  title: "6a → 7b en 12 mois",            weeks: 52, sessionsPerWeek: 3, level: "Intermédiaire", priceEUR: 129,subs: 280,  included: false, cover: "linear-gradient(135deg, #a78bfa, #ffb347)" },
];

export default function ProgramsPage() {
  return (
    <div className="space-y-6">
      <header>
        <Pill color="violet">Programmes</Pill>
        <h1 className="mt-3 text-3xl sm:text-4xl font-black tracking-tight">
          Des parcours <span className="rose-text">structurés</span>, semaine après semaine
        </h1>
        <p className="mt-2 text-muted text-sm">Inclus dans ton abonnement créateur. Ou achetables à l'unité.</p>
      </header>

      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
        {PROGRAMS.map(pg => {
          const c = CREATORS.find(x => x.id === pg.creatorId)!;
          return (
            <Link href={`/c/${c.id}`} key={pg.id} className="block group">
              <article className="rounded-2xl overflow-hidden ring-1 ring-overlay/10 hover:ring-rose/40 transition glass">
                <div className="relative h-44" style={{ background: pg.cover }}>
                  <div className="absolute inset-0 grain opacity-30" />
                  <div className="absolute top-3 left-3 flex flex-wrap gap-1.5">
                    <Pill color="violet">Programme</Pill>
                    <Pill color="sky">{pg.level}</Pill>
                  </div>
                  <div className="absolute bottom-3 right-3">
                    {pg.included ? (
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-success/90 text-foreground text-[10px] font-black">
                        <CheckCircle2 size={10} /> Inclus
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-black/70 backdrop-blur text-[10px] font-black">
                        <Lock size={10} /> Premium
                      </span>
                    )}
                  </div>
                </div>
                <div className="p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <div className="w-8 h-8 rounded-lg grid place-items-center font-black text-black text-xs" style={{ background: c.banner }}>{c.avatar}</div>
                    <div className="min-w-0">
                      <p className="text-xs font-bold truncate">{c.name}</p>
                      <p className="text-[10px] text-muted truncate">{c.handle}</p>
                    </div>
                  </div>
                  <h3 className="font-black">{pg.title}</h3>

                  <div className="mt-3 grid grid-cols-3 gap-2 text-[10px] text-muted">
                    <div className="rounded-lg bg-overlay/5 p-2 text-center">
                      <p>Durée</p>
                      <p className="font-bold text-foreground mt-0.5">{pg.weeks} sem</p>
                    </div>
                    <div className="rounded-lg bg-overlay/5 p-2 text-center">
                      <p>Par sem</p>
                      <p className="font-bold text-foreground mt-0.5">{pg.sessionsPerWeek}×</p>
                    </div>
                    <div className="rounded-lg bg-overlay/5 p-2 text-center">
                      <p>Élèves</p>
                      <p className="font-bold text-foreground mt-0.5">{compact(pg.subs)}</p>
                    </div>
                  </div>

                  <div className="mt-4 flex items-center justify-between">
                    <p className="font-black rose-text text-xl">{fmtEUR(pg.priceEUR, 0)}</p>
                    <button className="px-3 py-1.5 rounded-lg rose-gradient text-black text-xs font-black">
                      {pg.included ? "Démarrer" : "Acheter"}
                    </button>
                  </div>
                </div>
              </article>
            </Link>
          );
        })}
      </div>

      <Card title="Comment fonctionnent les programmes" subtitle="Structurés, vivants, garantis">
        <div className="grid sm:grid-cols-3 gap-4">
          {[
            { icon: Calendar, t: "Plan jour par jour", d: "Tu reçois ta séance du jour le matin. Pas de navigation, juste play." },
            { icon: Users, t: "Cohorte privée", d: "Un Discord par programme. Tu progresses avec 200-2000 autres élèves." },
            { icon: Sparkles, t: "Form check inclus", d: "Tu envoies une vidéo, le créateur ou son assistant te corrige." },
          ].map(o => (
            <div key={o.t} className="rounded-xl bg-overlay/5 p-4">
              <o.icon size={20} className="text-rose mb-2" />
              <p className="font-bold">{o.t}</p>
              <p className="text-xs text-muted mt-1">{o.d}</p>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
