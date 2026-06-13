"use client";

import { useParams, notFound } from "next/navigation";
import Link from "next/link";
import { findExercise, EXERCISES } from "../../../lib/exercises";
import { CREATORS } from "../../../lib/mock";
import { ChevronLeft, Dumbbell, Users, Play, AlertTriangle, CheckCircle2, Sparkles, Timer } from "lucide-react";

export default function ExerciseDetail() {
  const params = useParams();
  const ex = findExercise(params?.id as string);
  if (!ex) notFound();

  // 3 créateurs avec démos
  const demoCreators = CREATORS.slice(0, ex.hasCreatorDemos > 0 ? Math.min(ex.hasCreatorDemos, 3) : 0);
  const related = EXERCISES.filter(e => e.id !== ex.id && e.primaryMuscles.some(m => ex.primaryMuscles.includes(m))).slice(0, 3);

  return (
    <div className="space-y-12 pb-12">
      <Link href="/exercises" className="inline-flex items-center gap-1 text-xs text-muted hover:text-foreground">
        <ChevronLeft size={14} /> Bibliothèque
      </Link>

      {/* HERO */}
      <header>
        <div className="flex items-center gap-2 mb-4">
          <span className="text-xs uppercase tracking-[0.28em] text-muted">{ex.category}</span>
          <span className="text-xs uppercase tracking-[0.28em] text-muted">·</span>
          <span className="text-xs uppercase tracking-[0.28em] text-muted">{ex.difficulty}</span>
        </div>
        <div className="flex items-start gap-6">
          <span className="text-7xl sm:text-8xl">{ex.emoji}</span>
          <div className="flex-1">
            <h1 className="text-4xl sm:text-6xl font-black tracking-tightest leading-[0.95]">{ex.name}</h1>
            {ex.alternativeNames && ex.alternativeNames.length > 0 && (
              <p className="mt-2 text-muted">{ex.alternativeNames.join(" · ")}</p>
            )}
            <p className="mt-4 text-lg leading-relaxed max-w-2xl">{ex.shortDescription}</p>
          </div>
        </div>
      </header>

      {/* QUICK INFO */}
      <section className="grid sm:grid-cols-4 gap-4 border-y border-border py-6">
        <Info label="Muscles principaux" value={ex.primaryMuscles.join(", ")} />
        <Info label="Équipement" value={ex.equipment.join(", ")} />
        {ex.recommendedSets && <Info label="Volume conseillé" value={ex.recommendedSets} />}
        {ex.caloriesPerHour && <Info label="Brûlé / heure" value={`~${ex.caloriesPerHour} kcal`} />}
        {!ex.caloriesPerHour && <Info label="Popularité" value={`${ex.popularity}/100`} />}
      </section>

      {/* CRÉATEUR DEMOS */}
      {demoCreators.length > 0 && (
        <section>
          <div className="flex items-end justify-between mb-6">
            <div>
              <p className="text-xs uppercase tracking-[0.28em] text-muted mb-2">Démonstrations</p>
              <h2 className="text-2xl sm:text-4xl font-black tracking-tighter">{ex.hasCreatorDemos} Unblurers le montrent</h2>
            </div>
            <Link href="/discover" className="text-sm font-semibold underline underline-offset-4">Tous les Unblurers</Link>
          </div>
          <div className="grid sm:grid-cols-3 gap-4">
            {demoCreators.map(c => (
              <Link key={c.id} href={`/c/${c.id}`} className="group block rounded-3xl border border-border hover:border-foreground/40 p-5 transition">
                <div className="aspect-video rounded-xl mb-4 relative grid place-items-center" style={{ background: c.banner }}>
                  <div className="w-14 h-14 rounded-full bg-surface/20 backdrop-blur grid place-items-center">
                    <Play size={22} className="text-surface ml-1" fill="currentColor" />
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-9 h-9 rounded-full grid place-items-center font-black text-xs bg-foreground text-surface">{c.avatar}</div>
                  <div className="min-w-0">
                    <p className="font-bold text-sm truncate">{c.name}</p>
                    <p className="text-[11px] text-muted truncate">{c.handle}</p>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </section>
      )}

      {/* TECHNIQUE */}
      <section>
        <p className="text-xs uppercase tracking-[0.28em] text-muted mb-3">Technique</p>
        <h2 className="text-2xl sm:text-4xl font-black tracking-tighter mb-6">{ex.technique.length} clés d'exécution</h2>
        <ol className="space-y-3">
          {ex.technique.map((t, i) => (
            <li key={i} className="flex gap-4 p-4 rounded-2xl border border-border">
              <span className="font-black text-2xl text-rose tabular-nums">{String(i + 1).padStart(2, "0")}</span>
              <span className="flex-1 leading-relaxed pt-1">{t}</span>
            </li>
          ))}
        </ol>
      </section>

      {/* MISTAKES */}
      <section>
        <p className="text-xs uppercase tracking-[0.28em] text-muted mb-3">Erreurs courantes</p>
        <h2 className="text-2xl sm:text-4xl font-black tracking-tighter mb-6">À éviter absolument</h2>
        <ul className="grid sm:grid-cols-2 gap-3">
          {ex.mistakes.map((m, i) => (
            <li key={i} className="flex gap-3 p-4 rounded-2xl border border-border">
              <AlertTriangle size={18} className="text-rose shrink-0 mt-0.5" />
              <span className="text-sm leading-relaxed">{m}</span>
            </li>
          ))}
        </ul>
      </section>

      {/* VARIATIONS */}
      {ex.variations && ex.variations.length > 0 && (
        <section>
          <p className="text-xs uppercase tracking-[0.28em] text-muted mb-3">Variantes</p>
          <h2 className="text-2xl sm:text-4xl font-black tracking-tighter mb-6">{ex.variations.length} variations à connaître</h2>
          <div className="flex flex-wrap gap-2">
            {ex.variations.map(v => (
              <span key={v} className="px-4 py-2 rounded-full ring-1 ring-border text-sm font-semibold">{v}</span>
            ))}
          </div>
        </section>
      )}

      {/* RELATED */}
      {related.length > 0 && (
        <section className="border-t border-border pt-12">
          <p className="text-xs uppercase tracking-[0.28em] text-muted mb-3">À découvrir</p>
          <h2 className="text-2xl sm:text-3xl font-black tracking-tighter mb-6">Exercices similaires</h2>
          <div className="grid sm:grid-cols-3 gap-4">
            {related.map(r => (
              <Link key={r.id} href={`/exercises/${r.id}`} className="block p-5 rounded-3xl border border-border hover:border-foreground/40 transition">
                <span className="text-3xl">{r.emoji}</span>
                <p className="mt-3 font-black">{r.name}</p>
                <p className="text-xs text-muted mt-1 line-clamp-2">{r.shortDescription}</p>
              </Link>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}

function Info({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-[10px] uppercase tracking-[0.18em] text-muted font-bold mb-1">{label}</p>
      <p className="text-sm font-semibold leading-snug">{value}</p>
    </div>
  );
}
