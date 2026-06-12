"use client";

import { useState } from "react";
import { CreatorCard } from "../../components/CreatorCard";
import { Pill } from "../../components/Card";
import { CREATORS, ALL_CATEGORIES } from "../../lib/mock";
import { Filter, Sparkles } from "lucide-react";
import type { Category } from "../../lib/types";

export default function DiscoverPage() {
  const [cat, setCat] = useState<Category | "ALL">("ALL");
  const [sort, setSort] = useState<"popular" | "rising" | "price-low" | "price-high">("popular");

  let list = cat === "ALL" ? CREATORS : CREATORS.filter(c => c.category === cat || c.subCategories.includes(cat));
  if (sort === "popular") list = [...list].sort((a, b) => b.subscribers - a.subscribers);
  if (sort === "rising") list = [...list].sort((a, b) => new Date(b.joinedAt).getTime() - new Date(a.joinedAt).getTime());
  if (sort === "price-low") list = [...list].sort((a, b) => a.monthlyPriceEUR - b.monthlyPriceEUR);
  if (sort === "price-high") list = [...list].sort((a, b) => b.monthlyPriceEUR - a.monthlyPriceEUR);

  return (
    <div className="space-y-6">
      <header>
        <Pill color="rose">Découvrir</Pill>
        <h1 className="mt-3 text-3xl sm:text-4xl font-black tracking-tight">
          Trouve ton <span className="rose-text">créateur</span>
        </h1>
        <p className="mt-2 text-muted">{CREATORS.length} créateurs · {CREATORS.reduce((s, c) => s + c.subscribers, 0).toLocaleString("fr-FR")} abonnements actifs</p>
      </header>

      <div className="flex flex-wrap gap-3">
        <div className="flex items-center gap-1 rounded-xl bg-overlay/5 p-1 ring-1 ring-overlay/10 overflow-x-auto scrollbar-thin">
          <Filter size={13} className="text-muted ml-2 shrink-0" />
          <button onClick={() => setCat("ALL")} className={`px-3 py-1.5 rounded-lg text-xs font-bold whitespace-nowrap ${cat === "ALL" ? "bg-rose text-black" : "text-muted hover:text-foreground"}`}>Toutes</button>
          {ALL_CATEGORIES.map(c => (
            <button key={c} onClick={() => setCat(c)} className={`px-3 py-1.5 rounded-lg text-xs font-bold whitespace-nowrap ${cat === c ? "bg-rose text-black" : "text-muted hover:text-foreground"}`}>{c}</button>
          ))}
        </div>
        <div className="flex items-center gap-1 rounded-xl bg-overlay/5 p-1 ring-1 ring-overlay/10">
          {([{ v: "popular", l: "Populaires" }, { v: "rising", l: "Émergents" }, { v: "price-low", l: "Prix ↑" }, { v: "price-high", l: "Prix ↓" }] as const).map(o => (
            <button key={o.v} onClick={() => setSort(o.v)} className={`px-3 py-1.5 rounded-lg text-xs font-bold ${sort === o.v ? "bg-sun text-black" : "text-muted hover:text-foreground"}`}>{o.l}</button>
          ))}
        </div>
      </div>

      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
        {list.map(c => <CreatorCard key={c.id} creator={c} />)}
      </div>

      {list.length === 0 && (
        <div className="text-center py-12 text-muted">
          <Sparkles size={28} className="mx-auto mb-3 text-rose" />
          <p>Aucun créateur dans cette catégorie pour l'instant.</p>
        </div>
      )}
    </div>
  );
}
