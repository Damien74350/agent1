"use client";

import { useEffect, useRef, useState } from "react";
import { useParams, notFound } from "next/navigation";
import Link from "next/link";
import { Pill } from "../../../components/Card";
import { findCreator } from "../../../lib/mock";
import { compact, fmtEUR } from "../../../lib/format";
import { Heart, Send, Smile, Share2, Lock, ChevronLeft, Users, Eye, Gift, Sparkles, Zap, MessageCircle, Pause, Play, Volume2, Maximize2 } from "lucide-react";

const SEED_CHATS = [
  { user: "alex_92", msg: "Salutttt 💪", sub: true, color: "#5eead4" },
  { user: "marathon_inès", msg: "première fois en live, je test !", sub: false, color: "#a78bfa" },
  { user: "léa.bx", msg: "tu peux montrer la position des épaules ?", sub: true, color: "#fcd34d" },
  { user: "fitkim", msg: "OMGGG cette session 🔥🔥", sub: true, color: "#ff2e7e" },
  { user: "warrior_théo", msg: "merci pour la méthode 🙏", sub: true, color: "#ffb347" },
  { user: "mama_fit", msg: "j'arrive de Lyon!", sub: false, color: "#5b9eff" },
  { user: "yoga_maya", msg: "❤️❤️❤️", sub: true, color: "#a78bfa" },
  { user: "running_dad", msg: "tu peux refaire avec une bande?", sub: true, color: "#10b981" },
  { user: "chloe.climb", msg: "trop bon le tempo respiration", sub: true, color: "#fcd34d" },
  { user: "calistarter", msg: "première séance, on lâche rien !", sub: false, color: "#fb7185" },
  { user: "noah_box", msg: "💯", sub: true, color: "#ff2e7e" },
  { user: "kine_marie", msg: "questions à la fin ?", sub: true, color: "#5eead4" },
  { user: "iron_louis", msg: "wahou 312 viewers 🚀", sub: true, color: "#ffb347" },
  { user: "soft_lily", msg: "merci pour la modif chaise!", sub: true, color: "#a78bfa" },
];

export default function LiveRoom() {
  const params = useParams();
  const id = params?.id as string;
  const creator = findCreator(id);
  if (!creator) notFound();

  const [chat, setChat] = useState(SEED_CHATS.slice(0, 6));
  const [subscribed, setSubscribed] = useState(false);
  const [input, setInput] = useState("");
  const [viewers, setViewers] = useState(creator.liveViewers ?? 312);
  const chatRef = useRef<HTMLDivElement>(null);

  // simulate chat stream
  useEffect(() => {
    const id = setInterval(() => {
      setChat(prev => {
        const next = SEED_CHATS[Math.floor(Math.random() * SEED_CHATS.length)];
        const updated = [...prev, { ...next, key: Date.now() } as any].slice(-20);
        setTimeout(() => chatRef.current?.scrollTo({ top: 99999, behavior: "smooth" }), 50);
        return updated;
      });
      setViewers(v => Math.max(120, v + Math.floor(Math.random() * 10) - 4));
    }, 2200);
    return () => clearInterval(id);
  }, []);

  function send() {
    if (!input.trim()) return;
    setChat(prev => [...prev, { user: "toi", msg: input, sub: subscribed, color: "#ff2e7e", key: Date.now() } as any].slice(-20));
    setInput("");
    setTimeout(() => chatRef.current?.scrollTo({ top: 99999, behavior: "smooth" }), 50);
  }

  return (
    <div className="space-y-4 -mx-4 sm:-mx-6 lg:-mx-8 px-4 sm:px-6 lg:px-8">
      <Link href={`/c/${creator.id}`} className="inline-flex items-center gap-1 text-xs text-muted hover:text-foreground">
        <ChevronLeft size={14} /> Retour au profil
      </Link>

      <div className="grid lg:grid-cols-12 gap-4">
        {/* VIDEO PLAYER */}
        <div className="lg:col-span-8 space-y-3">
          <div className="relative aspect-video rounded-2xl overflow-hidden ring-1 ring-rose/40 shadow-glow" style={{ background: creator.banner }}>
            <div />
            {/* Live UI */}
            <div className="absolute top-3 left-3 inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-foreground/80 backdrop-blur text-xs font-black uppercase tracking-widest">
              <span className="w-2 h-2 rounded-full bg-rose live-dot" /> LIVE
            </div>
            <div className="absolute top-3 right-3 inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-foreground/80 backdrop-blur text-xs font-bold">
              <Eye size={11} /> {compact(viewers)}
            </div>
            {/* Faux centre player */}
            <div className="absolute inset-0 grid place-items-center">
              <div className="w-20 h-20 rounded-full bg-foreground/40 backdrop-blur grid place-items-center">
                <Pause size={32} className="text-foreground" />
              </div>
            </div>
            {/* Controls */}
            <div className="absolute inset-x-0 bottom-0 p-3 bg-gradient-to-t from-black/90 to-transparent">
              <div className="flex items-center gap-3 text-foreground">
                <Pause size={16} />
                <Volume2 size={16} />
                <div className="flex-1 h-1 bg-overlay/30 rounded-full">
                  <div className="h-full w-1/3 rose-gradient rounded-full" />
                </div>
                <span className="text-xs font-mono">23:14 / LIVE</span>
                <Maximize2 size={16} />
              </div>
            </div>
          </div>

          {/* Title & creator strip */}
          <div className="glass rounded-2xl p-4">
            <div className="flex items-center justify-between gap-3">
              <div className="flex items-center gap-3 min-w-0">
                <Link href={`/c/${creator.id}`} className="w-12 h-12 rounded-2xl grid place-items-center font-black text-black shrink-0" style={{ background: creator.banner }}>
                  {creator.avatar}
                </Link>
                <div className="min-w-0">
                  <Link href={`/c/${creator.id}`} className="font-black truncate hover:underline">{creator.name}</Link>
                  <p className="text-xs text-muted truncate">{creator.handle} · <Pill color="rose">{creator.tier}</Pill></p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <button className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg bg-overlay/10 hover:bg-overlay/20 text-xs font-bold">
                  <Heart size={13} /> Suivre
                </button>
                <button className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg bg-overlay/10 hover:bg-overlay/20 text-xs font-bold">
                  <Share2 size={13} /> Partager
                </button>
              </div>
            </div>

            <p className="mt-3 font-bold">{creator.liveTitle ?? "Live en direct"}</p>
            <p className="text-xs text-muted mt-1">{creator.tagline}</p>

            {!subscribed && (
              <div className="mt-4 rounded-2xl rose-gradient text-black p-4 flex items-center gap-3">
                <Lock size={20} />
                <div className="flex-1">
                  <p className="font-black">Tu suis Louise gratuitement</p>
                  <p className="text-xs opacity-80">Abonne-toi pour : chat actif · replays · programmes · DMs</p>
                </div>
                <button onClick={() => setSubscribed(true)} className="px-4 py-2 rounded-lg bg-black text-foreground font-bold text-xs">
                  S'abonner {fmtEUR(creator.monthlyPriceEUR)}
                </button>
              </div>
            )}
          </div>

          {/* RELATED LIVES */}
          <div>
            <p className="text-[10px] uppercase tracking-widest text-muted font-bold mb-2">À regarder ensuite</p>
            <div className="grid sm:grid-cols-2 gap-3">
              {[1, 2].map(i => (
                <div key={i} className="rounded-xl glass p-3 flex items-center gap-3">
                  <div className="w-16 h-10 rounded-md grid place-items-center text-xs font-black text-black shrink-0" style={{ background: "linear-gradient(135deg, #a78bfa, #5eead4)" }}>
                    PLAY
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-xs font-bold truncate">Replay : mobilité 25 min</p>
                    <p className="text-[10px] text-muted truncate">il y a 3 jours · 1.2k vues</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* CHAT */}
        <aside className="lg:col-span-4 glass rounded-2xl flex flex-col h-[70vh]">
          <header className="px-4 py-3 border-b border-overlay/10 flex items-center justify-between">
            <p className="font-bold text-sm flex items-center gap-1.5">
              <MessageCircle size={14} className="text-rose" />
              Chat live · {chat.length}
            </p>
            <div className="flex gap-2">
              <Pill color="rose"><Users size={9} className="mr-0.5" />{compact(viewers)}</Pill>
            </div>
          </header>

          <div ref={chatRef} className="flex-1 overflow-y-auto scrollbar-thin px-3 py-2 space-y-1.5">
            {chat.map((c, i) => (
              <div key={i} className="flex items-baseline gap-1.5 text-xs leading-snug">
                <span className="font-black truncate" style={{ color: c.color }}>{c.user}</span>
                {c.sub && <Sparkles size={9} className="text-rose shrink-0" />}
                <span className="text-foreground/85 break-words">{c.msg}</span>
              </div>
            ))}
          </div>

          <footer className="border-t border-overlay/10 p-3">
            <div className="flex items-center gap-2">
              <input
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={e => e.key === "Enter" && send()}
                placeholder={subscribed ? "Écris ton message…" : "Abonne-toi pour parler"}
                disabled={!subscribed}
                className="flex-1 bg-overlay/10 rounded-lg px-3 py-2 text-sm outline-none ring-1 ring-overlay/10 focus:ring-rose/40 disabled:opacity-50"
              />
              <button className="p-2 rounded-lg hover:bg-overlay/10"><Smile size={16} /></button>
              <button onClick={send} disabled={!subscribed} className="p-2 rounded-lg rose-gradient text-black disabled:opacity-40">
                <Send size={14} />
              </button>
            </div>
            <div className="mt-2 flex items-center gap-2 flex-wrap">
              {["❤️", "🔥", "💪", "👏", "✨"].map(e => (
                <button key={e} className="px-2 py-1 rounded-lg bg-overlay/10 hover:bg-overlay/20 text-sm">{e}</button>
              ))}
              <button className="inline-flex items-center gap-1 px-2 py-1 rounded-lg bg-rose/10 ring-1 ring-rose/30 text-rose text-[10px] font-bold ml-auto">
                <Gift size={11} /> Tip
              </button>
            </div>
          </footer>
        </aside>
      </div>
    </div>
  );
}
