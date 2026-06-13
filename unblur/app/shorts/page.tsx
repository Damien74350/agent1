"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { CREATORS, CONTENTS } from "../../lib/mock";
import { compact } from "../../lib/format";
import { Heart, MessageCircle, Share2, Music, Lock, Play, Volume2, VolumeX, ChevronUp, Bookmark } from "lucide-react";

// Filtre des shorts: 6 contenus avec créateurs
const SHORTS = CONTENTS.slice(0, 6).map(c => {
  const creator = CREATORS.find(x => x.id === c.creatorId)!;
  return { ...c, creator };
});

export default function ShortsPage() {
  const [idx, setIdx] = useState(0);
  const [muted, setMuted] = useState(true);
  const containerRef = useRef<HTMLDivElement>(null);

  function next() { setIdx(i => Math.min(SHORTS.length - 1, i + 1)); }
  function prev() { setIdx(i => Math.max(0, i - 1)); }

  return (
    <div className="-mx-4 sm:-mx-6 lg:-mx-8 -mt-6">
      <header className="px-4 sm:px-6 lg:px-8 py-6">
        <p className="text-xs uppercase tracking-[0.28em] text-muted">Shorts</p>
        <h1 className="text-2xl sm:text-4xl font-black tracking-tighter">Vertical · 15-60s · gratuit</h1>
      </header>

      <div className="flex justify-center pb-12">
        {/* Phone-like vertical canvas */}
        <div className="relative w-full max-w-[420px] aspect-[9/16] rounded-3xl overflow-hidden bg-foreground" ref={containerRef}>
          {SHORTS.map((short, i) => (
            <ShortItem
              key={short.id}
              short={short}
              visible={i === idx}
              muted={muted}
              onMute={() => setMuted(!muted)}
              onNext={next}
              onPrev={prev}
            />
          ))}

          {/* Pagination dots */}
          <div className="absolute right-2 top-1/2 -translate-y-1/2 flex flex-col gap-1 z-30">
            {SHORTS.map((_, i) => (
              <button key={i} onClick={() => setIdx(i)} className={`w-1 rounded-full transition-all ${i === idx ? "bg-surface h-6" : "bg-surface/40 h-2"}`} />
            ))}
          </div>

          {/* Up nav */}
          <button onClick={prev} disabled={idx === 0} className="absolute top-4 left-1/2 -translate-x-1/2 w-10 h-10 rounded-full bg-surface/10 backdrop-blur grid place-items-center text-surface disabled:opacity-30 z-30">
            <ChevronUp size={18} />
          </button>
        </div>
      </div>

      <section className="px-4 sm:px-6 lg:px-8 pb-12 max-w-2xl mx-auto text-center space-y-4">
        <p className="text-sm text-muted leading-relaxed">
          Les Unblurers postent des shorts gratuits — extraits, tips, motivation, behind-the-scenes.
          Si tu accroches, abonne-toi pour débloquer leurs lives et programmes complets.
        </p>
        <Link href="/discover" className="inline-flex items-center gap-2 px-6 py-3 rounded-full bg-foreground text-surface font-semibold">
          Voir tous les Unblurers
        </Link>
      </section>
    </div>
  );
}

function ShortItem({ short, visible, muted, onMute, onNext, onPrev }: { short: any; visible: boolean; muted: boolean; onMute: () => void; onNext: () => void; onPrev: () => void }) {
  const [liked, setLiked] = useState(false);
  const [saved, setSaved] = useState(false);

  if (!visible) return null;

  return (
    <div className="absolute inset-0" style={{ background: short.thumbnail }}>
      {/* Faux video background */}
      <div className="absolute inset-0 grid place-items-center text-9xl opacity-30 text-surface">{short.thumbnailEmoji}</div>

      {/* Center play */}
      <div className="absolute inset-0 grid place-items-center pointer-events-none">
        <div className="w-20 h-20 rounded-full bg-surface/15 backdrop-blur grid place-items-center">
          <Play size={32} className="text-surface ml-1" fill="currentColor" />
        </div>
      </div>

      {/* Premium lock overlay */}
      {short.isPremium && (
        <div className="absolute top-16 right-3 z-20">
          <div className="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-full bg-foreground/60 backdrop-blur text-surface text-[10px] font-black uppercase tracking-widest">
            <Lock size={10} /> Premium
          </div>
        </div>
      )}

      {/* Mute toggle */}
      <button onClick={onMute} className="absolute top-4 right-3 z-20 w-10 h-10 rounded-full bg-surface/15 backdrop-blur grid place-items-center text-surface">
        {muted ? <VolumeX size={16} /> : <Volume2 size={16} />}
      </button>

      {/* Tap zones for nav */}
      <button onClick={onPrev} className="absolute top-0 left-0 w-1/3 h-1/2 z-10" />
      <button onClick={onNext} className="absolute bottom-0 right-0 w-2/3 h-2/3 z-10" />

      {/* Bottom info */}
      <div className="absolute inset-x-0 bottom-0 p-4 z-20 pointer-events-none">
        <div className="flex items-end justify-between gap-3">
          {/* LEFT — creator + caption */}
          <div className="flex-1 min-w-0 text-surface pointer-events-auto">
            <Link href={`/c/${short.creator.id}`} className="inline-flex items-center gap-2 mb-2">
              <div className="w-10 h-10 rounded-full grid place-items-center font-black text-xs bg-surface text-foreground">{short.creator.avatar}</div>
              <div>
                <p className="text-sm font-black">{short.creator.handle}</p>
                <p className="text-[10px] opacity-80">{short.creator.tagline}</p>
              </div>
              <button className="ml-2 px-3 py-1 rounded-full text-[11px] font-bold bg-rose text-surface">S'abonner</button>
            </Link>
            <p className="text-sm font-bold mb-1 line-clamp-2">{short.title}</p>
            <p className="text-xs opacity-90 line-clamp-2 leading-snug">{short.description}</p>
            <div className="mt-2 flex items-center gap-1.5 text-[11px] opacity-90">
              <Music size={11} />
              <span className="truncate">Son original — {short.creator.name}</span>
            </div>
          </div>

          {/* RIGHT — actions verticales */}
          <div className="flex flex-col items-center gap-4 pointer-events-auto">
            <ActionBtn icon={Heart} count={compact(short.likes + (liked ? 1 : 0))} active={liked} onClick={() => setLiked(!liked)} />
            <ActionBtn icon={MessageCircle} count={compact(short.comments)} />
            <ActionBtn icon={Bookmark} count={short.isPremium ? "Lock" : "Save"} active={saved} onClick={() => setSaved(!saved)} />
            <ActionBtn icon={Share2} count="Partager" />
          </div>
        </div>
      </div>
    </div>
  );
}

function ActionBtn({ icon: Icon, count, active = false, onClick }: { icon: any; count: string; active?: boolean; onClick?: () => void }) {
  return (
    <button onClick={onClick} className="flex flex-col items-center gap-1 text-surface">
      <div className={`w-12 h-12 rounded-full grid place-items-center backdrop-blur ${active ? "bg-rose" : "bg-surface/15"}`}>
        <Icon size={20} fill={active ? "currentColor" : "none"} />
      </div>
      <span className="text-[10px] font-bold">{count}</span>
    </button>
  );
}
