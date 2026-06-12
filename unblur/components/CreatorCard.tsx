import Link from "next/link";
import type { Creator } from "../lib/types";
import { compact, fmtEUR } from "../lib/format";
import { Users, Star, Zap, Tv } from "lucide-react";
import { Pill } from "./Card";

const TIER_COLOR: Record<string, "rose" | "sun" | "sky" | "violet"> = {
  Rising: "sky",
  Trusted: "sun",
  Pro: "rose",
  Elite: "violet",
};

export function CreatorCard({ creator, compactMode = false }: { creator: Creator; compactMode?: boolean }) {
  return (
    <Link href={`/c/${creator.id}`} className="group block">
      <article className="rounded-2xl overflow-hidden ring-1 ring-overlay/10 hover:ring-rose/40 transition glass">
        {/* Banner */}
        <div className="relative h-32 sm:h-40" style={{ background: creator.banner }}>
          <div />
          {creator.isLive && (
            <div className="absolute top-3 left-3 inline-flex items-center gap-1.5 px-2 py-1 rounded-full bg-foreground/80 backdrop-blur text-surface text-[10px] font-black uppercase tracking-widest">
              <span className="w-2 h-2 rounded-full bg-rose live-dot" />
              Live · {compact(creator.liveViewers ?? 0)}
            </div>
          )}
          <div className="absolute top-3 right-3">
            <Pill color={TIER_COLOR[creator.tier]}>{creator.tier}</Pill>
          </div>
          <div className="absolute -bottom-7 left-4 w-14 h-14 rounded-2xl grid place-items-center text-black font-black text-xl ring-4 ring-canvas" style={{ background: creator.banner }}>
            {creator.avatar}
          </div>
        </div>

        <div className="p-4 pt-9">
          <div className="flex items-baseline justify-between gap-2">
            <div className="min-w-0">
              <p className="font-black truncate">{creator.name}</p>
              <p className="text-xs text-muted truncate">{creator.handle}</p>
            </div>
            <div className="text-right shrink-0">
              <p className="font-black rose-text text-lg">{fmtEUR(creator.monthlyPriceEUR)}</p>
              <p className="text-[10px] text-muted">/mois</p>
            </div>
          </div>

          <p className="mt-2 text-xs text-foreground/65 line-clamp-2">{creator.tagline}</p>

          <div className="mt-3 pt-3 border-t border-overlay/5 flex items-center justify-between text-[11px] text-muted">
            <span className="inline-flex items-center gap-1"><Users size={11} /> {compact(creator.subscribers)} subs</span>
            <span className="inline-flex items-center gap-1 text-sun"><Star size={11} fill="currentColor" /> {creator.rating.toFixed(2)}</span>
            <span>{creator.countryFlag}</span>
          </div>

          {!compactMode && (
            <button className="mt-3 w-full px-3 py-2 rounded-lg rose-gradient text-black font-bold text-xs flex items-center justify-center gap-1.5 shadow-glow opacity-90 group-hover:opacity-100">
              <Zap size={13} /> S'abonner — {fmtEUR(creator.monthlyPriceEUR)}/mois
            </button>
          )}
        </div>
      </article>
    </Link>
  );
}
