"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { ChevronLeft, Hash, Megaphone, Send, Smile, Plus, Image as ImageIcon, Mic, Search, Users, Pin, Settings } from "lucide-react";

type Channel = { id: string; name: string; emoji?: string; unread?: number; pinned?: boolean; description: string };

const CHANNELS: Channel[] = [
  { id: "general",    name: "général",     emoji: "👋", description: "Discussion libre de la communauté", pinned: true, unread: 4 },
  { id: "annonces",   name: "annonces",    emoji: "📢", description: "Mes nouveautés, événements, lives", pinned: true },
  { id: "questions",  name: "questions",   emoji: "❓", description: "Tes questions, je réponds", unread: 12 },
  { id: "nutrition",  name: "nutrition",   emoji: "🥗", description: "Recettes, conseils, plans" },
  { id: "progres",    name: "progrès",     emoji: "💪", description: "Partagez vos résultats avant/après" },
  { id: "form-check", name: "form-check",  emoji: "🎥", description: "Envoyez vos vidéos pour correction" },
  { id: "challenges", name: "challenges",  emoji: "🏆", description: "Mini-défis hebdo entre abonnés" },
];

const FAKE_MESSAGES = [
  { user: "léa.bx",      avatar: "LB", time: "9:42",  msg: "Salutttt ! Hâte du live de ce soir 🔥",    color: "#fcd34d" },
  { user: "fitkim",      avatar: "FK", time: "9:45",  msg: "Question : pour la mobilité hanches, j'ai mal au pli de l'aine, c'est normal ?", color: "#ff2e7e" },
  { user: "Louise",      avatar: "LC", time: "9:48",  msg: "@fitkim normal au début, c'est un point qui se débloque. Reste 30 sec par côté, respiration longue.", color: "#10b981", me: true },
  { user: "warrior_théo",avatar: "WT", time: "9:52",  msg: "🙏 J'avais la même question",                color: "#ffb347" },
  { user: "mama_fit",    avatar: "MF", time: "10:01", msg: "J'ai fait la séance de hier — première fois que j'arrive à toucher mes pieds en 10 ans 😭",  color: "#5b9eff" },
  { user: "Louise",      avatar: "LC", time: "10:03", msg: "@mama_fit !!!!! C'est exactement ce que je voulais entendre 🥹 BRAVO", color: "#10b981", me: true },
  { user: "alex_92",     avatar: "A9", time: "10:15", msg: "Vidéo form-check envoyée dans le channel dédié, merci d'avance",  color: "#5eead4" },
];

export default function CommunityPage() {
  const [active, setActive] = useState<Channel>(CHANNELS[0]);
  const [conv, setConv] = useState(FAKE_MESSAGES);
  const [input, setInput] = useState("");
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => { ref.current?.scrollTo({ top: 99999, behavior: "smooth" }); }, [conv]);

  function send() {
    if (!input.trim()) return;
    setConv(c => [...c, { user: "Louise", avatar: "LC", time: new Date().toLocaleTimeString("fr-FR", { hour: "2-digit", minute: "2-digit" }), msg: input, color: "#10b981", me: true }]);
    setInput("");
  }

  return (
    <div className="space-y-4 pb-12">
      <Link href="/studio" className="inline-flex items-center gap-1 text-xs text-muted hover:text-foreground">
        <ChevronLeft size={14} /> Studio
      </Link>

      <header>
        <p className="text-xs uppercase tracking-[0.28em] text-muted mb-3">Communauté</p>
        <h1 className="text-3xl sm:text-5xl font-black tracking-tighter">Ton canal privé</h1>
        <p className="mt-2 text-muted">2 840 membres dans ton canal · 7 channels actifs</p>
      </header>

      <div className="grid lg:grid-cols-12 gap-4 h-[70vh]">
        {/* CHANNEL LIST */}
        <aside className="lg:col-span-3 rounded-2xl border border-border flex flex-col">
          <header className="p-3 border-b border-border">
            <div className="flex items-center gap-2 rounded-xl bg-overlay/5 px-3 py-2 border border-border">
              <Search size={13} className="text-muted" />
              <input placeholder="Chercher..." className="bg-transparent outline-none flex-1 text-sm" />
            </div>
            <button className="mt-2 w-full inline-flex items-center justify-center gap-1.5 text-xs font-bold text-muted hover:text-foreground py-2">
              <Plus size={13} /> Créer un channel
            </button>
          </header>

          <ul className="flex-1 overflow-y-auto scrollbar-thin p-2">
            {CHANNELS.map(ch => {
              const isActive = ch.id === active.id;
              return (
                <li key={ch.id}>
                  <button onClick={() => setActive(ch)} className={`w-full text-left rounded-lg px-3 py-2 flex items-center gap-2 transition ${isActive ? "bg-foreground text-surface" : "hover:bg-overlay/5"}`}>
                    <span className="text-base shrink-0">{ch.emoji}</span>
                    <span className="text-sm font-semibold truncate flex-1">{ch.name}</span>
                    {ch.pinned && <Pin size={11} className={isActive ? "text-surface/60" : "text-muted"} />}
                    {ch.unread && <span className={`text-[10px] font-black px-1.5 rounded-full ${isActive ? "bg-surface text-foreground" : "bg-rose text-surface"}`}>{ch.unread}</span>}
                  </button>
                </li>
              );
            })}
          </ul>

          <footer className="p-3 border-t border-border text-[10px] text-muted text-center">
            Canal chiffré · seuls tes abonnés peuvent y accéder
          </footer>
        </aside>

        {/* CONVERSATION */}
        <section className="lg:col-span-9 rounded-2xl border border-border flex flex-col">
          <header className="p-4 border-b border-border flex items-center justify-between">
            <div className="flex items-center gap-3">
              <span className="text-2xl">{active.emoji}</span>
              <div>
                <p className="font-black text-lg">#{active.name}</p>
                <p className="text-xs text-muted">{active.description}</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <button className="px-3 py-1.5 rounded-full border border-border text-xs font-bold inline-flex items-center gap-1.5">
                <Megaphone size={11} /> Annonce groupée
              </button>
              <button className="p-2 rounded-lg hover:bg-overlay/5"><Users size={16} /></button>
              <button className="p-2 rounded-lg hover:bg-overlay/5"><Settings size={16} /></button>
            </div>
          </header>

          <div ref={ref} className="flex-1 overflow-y-auto scrollbar-thin p-4 space-y-3">
            {conv.map((m, i) => (
              <div key={i} className={`flex gap-3 ${m.me ? "flex-row-reverse" : ""}`}>
                <div className="w-9 h-9 rounded-full grid place-items-center text-xs font-black shrink-0" style={{ background: m.color, color: "#fff" }}>{m.avatar}</div>
                <div className={`max-w-[65%] ${m.me ? "items-end" : ""}`}>
                  <div className={`flex items-baseline gap-2 mb-0.5 ${m.me ? "justify-end" : ""}`}>
                    <span className="text-xs font-black">{m.user}</span>
                    {m.me && <span className="text-[9px] font-bold uppercase tracking-widest px-1.5 py-0.5 rounded bg-foreground text-surface">Créatrice</span>}
                    <span className="text-[10px] text-muted">{m.time}</span>
                  </div>
                  <div className={`rounded-2xl px-3 py-2 ${m.me ? "bg-foreground text-surface" : "bg-overlay/5"}`}>
                    <p className="text-sm">{m.msg}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>

          <footer className="p-3 border-t border-border">
            <div className="flex items-center gap-2">
              <button className="p-2 rounded-lg hover:bg-overlay/5"><Plus size={16} /></button>
              <button className="p-2 rounded-lg hover:bg-overlay/5"><ImageIcon size={16} /></button>
              <input
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={e => e.key === "Enter" && send()}
                placeholder={`Écrire dans #${active.name}…`}
                className="flex-1 bg-overlay/5 rounded-full px-4 py-2 text-sm outline-none border border-border focus:border-foreground"
              />
              <button className="p-2 rounded-lg hover:bg-overlay/5"><Smile size={16} /></button>
              <button className="p-2 rounded-lg hover:bg-overlay/5"><Mic size={16} /></button>
              <button onClick={send} className="p-2 rounded-full bg-foreground text-surface"><Send size={14} /></button>
            </div>
            <p className="mt-2 text-[10px] text-muted text-center">Réactions emoji · vocal · pinned messages · sondages — comme WhatsApp, premium</p>
          </footer>
        </section>
      </div>
    </div>
  );
}
