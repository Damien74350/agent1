import Link from "next/link";
import type { Creator } from "../lib/types";
import { compact, fmtEUR } from "../lib/format";
import { Users } from "lucide-react";

export function CreatorCard({ creator, compactMode = false }: { creator: Creator; compactMode?: boolean }) {
  return (
    <Link href={`/c/${creator.id}`} className="group block">
      <article className="rounded-3xl bg-surface border border-border hover:border-foreground/30 transition p-6 h-full flex flex-col">
        <div className="flex items-start justify-between mb-5">
          <div className="w-14 h-14 rounded-full grid place-items-center font-black text-base text-surface" style={{ background: "rgb(var(--c-fg))" }}>
            {creator.avatar}
          </div>
          {creator.isLive ? (
            <span className="inline-flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-widest">
              <span className="w-1.5 h-1.5 rounded-full bg-rose live-dot" />
              Live
            </span>
          ) : (
            <span className="text-[10px] font-bold uppercase tracking-widest text-muted">{creator.tier}</span>
          )}
        </div>

        <h3 className="font-black text-xl tracking-tight">{creator.name}</h3>
        <p className="text-sm text-muted">{creator.handle}</p>

        <p className="mt-4 text-sm leading-relaxed line-clamp-2 flex-1">{creator.tagline}</p>

        <div className="mt-6 pt-5 border-t border-border flex items-baseline justify-between">
          <div className="flex items-center gap-3 text-xs text-muted">
            <span className="inline-flex items-center gap-1"><Users size={11} /> {compact(creator.subscribers)}</span>
            <span>·</span>
            <span>{creator.country}</span>
          </div>
          <div className="text-right">
            <span className="font-black text-lg tabular-nums">{fmtEUR(creator.monthlyPriceEUR)}</span>
            <span className="text-muted text-xs"> /mois</span>
          </div>
        </div>
      </article>
    </Link>
  );
}
