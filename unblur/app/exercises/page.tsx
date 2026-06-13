"use client";

import { useState, useMemo } from "react";
import Link from "next/link";
import {
  EXERCISES, MUSCLE_GROUPS, EQUIPMENTS, EXERCISE_CATEGORIES,
  type MuscleGroup, type Equipment, type ExerciseCategory, type Exercise,
} from "../../lib/exercises";
import { Search, Filter, ChevronRight, Dumbbell, Users } from "lucide-react";

export default function ExercisesPage() {
  const [q, setQ] = useState("");
  const [muscle, setMuscle] = useState<MuscleGroup | "ALL">("ALL");
  const [equipment, setEquipment] = useState<Equipment | "ALL">("ALL");
  const [category, setCategory] = useState<ExerciseCategory | "ALL">("ALL");

  const filtered = useMemo(() => {
    return EXERCISES.filter(e => {
      if (q && !e.name.toLowerCase().includes(q.toLowerCase()) && !e.alternativeNames?.some(n => n.toLowerCase().includes(q.toLowerCase()))) return false;
      if (muscle !== "ALL" && !e.primaryMuscles.includes(muscle) && !e.secondaryMuscles?.includes(muscle)) return false;
      if (equipment !== "ALL" && !e.equipment.includes(equipment)) return false;
      if (category !== "ALL" && e.category !== category) return false;
      return true;
    }).sort((a, b) => b.popularity - a.popularity);
  }, [q, muscle, equipment, category]);

  return (
    <div className="space-y-10 pb-12">
      {/* HERO */}
      <section className="pt-12">
        <p className="text-xs uppercase tracking-[0.28em] text-muted mb-4">Bibliothèque</p>
        <h1 className="text-4xl sm:text-6xl font-black tracking-tightest leading-[0.95]">
          Tous les exercices.<br />
          Toutes les machines.
        </h1>
        <p className="mt-6 text-lg text-muted max-w-2xl leading-snug">
          La référence francophone pour la musculation et le sport. Technique, erreurs, variantes, démonstrations des Unblurers.
        </p>
        <div className="mt-6 flex flex-wrap gap-3 text-xs text-muted">
          <span>· <strong className="text-foreground">{EXERCISES.length}</strong> exercices référencés</span>
          <span>· <strong className="text-foreground">{MUSCLE_GROUPS.length}</strong> groupes musculaires</span>
          <span>· <strong className="text-foreground">{EQUIPMENTS.length}</strong> types d'équipement</span>
          <span>· <strong className="text-foreground">{EXERCISES.reduce((s, e) => s + e.hasCreatorDemos, 0)}</strong> démos créateurs</span>
        </div>
      </section>

      {/* SEARCH + FILTERS */}
      <section className="space-y-3 border-y border-border py-6">
        <div className="flex items-center gap-3 rounded-2xl border border-border px-4 py-3">
          <Search size={16} className="text-muted" />
          <input
            value={q}
            onChange={e => setQ(e.target.value)}
            placeholder="Chercher un exercice ou une machine…"
            className="flex-1 bg-transparent outline-none text-sm"
          />
        </div>

        <div className="flex flex-wrap gap-2 items-center text-xs">
          <span className="inline-flex items-center gap-1 text-muted font-bold uppercase tracking-widest mr-2"><Filter size={11} /> Filtres</span>
          {/* Muscle */}
          <Chip active={muscle === "ALL"} onClick={() => setMuscle("ALL")}>Tous muscles</Chip>
          {MUSCLE_GROUPS.map(m => (
            <Chip key={m} active={muscle === m} onClick={() => setMuscle(m)}>{m}</Chip>
          ))}
        </div>
        <div className="flex flex-wrap gap-2 items-center text-xs">
          <Chip active={equipment === "ALL"} onClick={() => setEquipment("ALL")}>Tout équipement</Chip>
          {EQUIPMENTS.map(e => (
            <Chip key={e} active={equipment === e} onClick={() => setEquipment(e)}>{e}</Chip>
          ))}
        </div>
        <div className="flex flex-wrap gap-2 items-center text-xs">
          <Chip active={category === "ALL"} onClick={() => setCategory("ALL")}>Toutes catégories</Chip>
          {EXERCISE_CATEGORIES.map(c => (
            <Chip key={c} active={category === c} onClick={() => setCategory(c)}>{c}</Chip>
          ))}
        </div>
      </section>

      {/* RESULTS COUNT */}
      <p className="text-sm text-muted">
        <strong className="text-foreground">{filtered.length}</strong> exercice{filtered.length > 1 ? "s" : ""} trouvé{filtered.length > 1 ? "s" : ""}
      </p>

      {/* GRID */}
      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
        {filtered.map(e => <ExerciseCard key={e.id} ex={e} />)}
      </div>

      {filtered.length === 0 && (
        <div className="text-center py-16 text-muted">
          <p>Aucun exercice ne correspond. Élargis tes filtres.</p>
        </div>
      )}
    </div>
  );
}

function Chip({ children, active, onClick }: { children: any; active: boolean; onClick: () => void }) {
  return (
    <button onClick={onClick} className={`px-3 py-1.5 rounded-full text-xs font-bold transition ${active ? "bg-foreground text-surface" : "ring-1 ring-border hover:bg-overlay/5"}`}>
      {children}
    </button>
  );
}

function ExerciseCard({ ex }: { ex: Exercise }) {
  return (
    <Link href={`/exercises/${ex.id}`} className="group block rounded-3xl border border-border hover:border-foreground/40 p-5 transition">
      <div className="flex items-start justify-between mb-4">
        <span className="text-4xl">{ex.emoji}</span>
        <span className="text-[10px] uppercase tracking-widest font-bold text-muted">{ex.difficulty}</span>
      </div>

      <h3 className="font-black text-lg leading-tight">{ex.name}</h3>
      {ex.alternativeNames && ex.alternativeNames.length > 0 && (
        <p className="text-[11px] text-muted mt-0.5">{ex.alternativeNames.join(" · ")}</p>
      )}

      <p className="mt-3 text-sm text-muted line-clamp-2 leading-relaxed">{ex.shortDescription}</p>

      {/* Muscles */}
      <div className="mt-4 flex flex-wrap gap-1.5">
        {ex.primaryMuscles.slice(0, 3).map(m => (
          <span key={m} className="text-[10px] font-bold uppercase tracking-widest px-2 py-1 rounded-full bg-rose/10 text-rose">{m}</span>
        ))}
      </div>

      {/* Footer */}
      <div className="mt-4 pt-4 border-t border-border flex items-center justify-between text-[11px] text-muted">
        <span className="inline-flex items-center gap-1"><Dumbbell size={11} /> {ex.equipment[0]}</span>
        <span className="inline-flex items-center gap-1"><Users size={11} /> {ex.hasCreatorDemos} démos</span>
        <span className="font-mono tabular-nums">{ex.popularity}%</span>
      </div>
    </Link>
  );
}
