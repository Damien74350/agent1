import Link from "next/link";
import type { Content } from "../lib/types";
import { findCreator } from "../lib/mock";
import { compact, relativeDate } from "../lib/format";
import { Lock, Play, Heart, MessageCircle, Clock, Tv } from "lucide-react";
import { Pill } from "./Card";

export function ContentCard({ content }: { content: Content }) {
  const creator = findCreator(content.creatorId);
  if (!creator) return null;
  return (
    <Link href={`/c/${creator.id}`} className="group block">
      <article className="rounded-2xl overflow-hidden ring-1 ring-white/10 hover:ring-rose/40 transition">
        <div className="relative aspect-video" style={{ background: content.thumbnail }}>
          <div className="absolute inset-0 grain opacity-30" />
          <div className="absolute inset-0 grid place-items-center text-6xl">{content.thumbnailEmoji}</div>
          <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/90 to-transparent p-3 pt-10">
            <div className="flex items-center gap-2 text-[10px]">
              {content.type === "live" && (
                <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded bg-rose text-white font-black uppercase">
                  <Tv size={9} /> Live
                </span>
              )}
              {content.type === "program" && <Pill color="violet">Programme</Pill>}
              {content.type === "video" && <Pill color="sun">Vidéo</Pill>}
              {content.durationMin && (
                <span className="inline-flex items-center gap-0.5 text-white/80">
                  <Clock size={9} /> {content.durationMin}min
                </span>
              )}
            </div>
          </div>
          {content.isPremium && (
            <div className="absolute top-2 right-2 w-8 h-8 rounded-lg bg-black/60 backdrop-blur grid place-items-center">
              <Lock size={14} className="text-rose" />
            </div>
          )}
          <div className="absolute inset-0 grid place-items-center opacity-0 group-hover:opacity-100 transition">
            <div className="w-14 h-14 rounded-full rose-gradient grid place-items-center shadow-glow">
              <Play size={22} className="text-black ml-1" fill="currentColor" />
            </div>
          </div>
        </div>
        <div className="p-3 glass">
          <p className="font-bold text-sm line-clamp-1">{content.title}</p>
          <div className="mt-1 flex items-center gap-2 text-[11px] text-muted">
            <span className="font-semibold text-white/80">{creator.handle}</span>
            <span>·</span>
            <span>{relativeDate(content.publishedAt)}</span>
          </div>
          <div className="mt-2 flex items-center gap-3 text-[10px] text-muted">
            <span>{compact(content.views)} vues</span>
            <span className="inline-flex items-center gap-0.5"><Heart size={9} /> {compact(content.likes)}</span>
            <span className="inline-flex items-center gap-0.5"><MessageCircle size={9} /> {compact(content.comments)}</span>
            <span className="ml-auto text-[9px] uppercase font-bold">{content.difficulty}</span>
          </div>
        </div>
      </article>
    </Link>
  );
}
