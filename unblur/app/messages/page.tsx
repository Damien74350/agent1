"use client";

import { useState, useEffect, useRef } from "react";
import { Card, Pill } from "../../components/Card";
import { CREATORS } from "../../lib/mock";
import { relativeDate } from "../../lib/format";
import { Send, Search, Image as ImageIcon, Sparkles, Mic, Plus } from "lucide-react";

type Thread = {
  creatorId: string;
  lastMsg: string;
  lastAt: string;
  unread: number;
};

const THREADS: Thread[] = [
  { creatorId: "c_amira", lastMsg: "Super ta progression sur le pont !", lastAt: new Date(Date.now() - 5 * 60_000).toISOString(), unread: 2 },
  { creatorId: "c_marko", lastMsg: "On essaie 8x800 mardi prochain ?", lastAt: new Date(Date.now() - 2 * 3600_000).toISOString(), unread: 0 },
  { creatorId: "c_louise", lastMsg: "Le form check est upload, regarde !", lastAt: new Date(Date.now() - 1 * 86400000).toISOString(), unread: 1 },
  { creatorId: "c_karim", lastMsg: "Tu m'as bluffé hier. On garde le rythme.", lastAt: new Date(Date.now() - 3 * 86400000).toISOString(), unread: 0 },
  { creatorId: "c_naima", lastMsg: "On se voit en live ce soir ?", lastAt: new Date(Date.now() - 5 * 86400000).toISOString(), unread: 0 },
];

const DEFAULT_CONV = [
  { from: "creator", msg: "Salut Damien ! J'ai vu ta vidéo de form check 👀", at: "10:32" },
  { from: "creator", msg: "Le coude part trop vers l'extérieur sur le dip. Essaie de coller au max au tronc.", at: "10:33" },
  { from: "me", msg: "Ah ok merci !! Je le sentais bizarre mais je voyais pas pourquoi", at: "10:35" },
  { from: "me", msg: "Je peux te renvoyer une vidéo demain pour vérifier ?", at: "10:35" },
  { from: "creator", msg: "Bien sûr, envoie quand tu veux. Et essaie le drill mobilité épaules juste avant.", at: "10:38" },
  { from: "creator", msg: "Bonne journée 💪", at: "10:38" },
];

export default function MessagesPage() {
  const [activeId, setActiveId] = useState<string>(THREADS[0].creatorId);
  const active = CREATORS.find(c => c.id === activeId)!;
  const [conv, setConv] = useState(DEFAULT_CONV);
  const [input, setInput] = useState("");
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => { ref.current?.scrollTo({ top: 99999, behavior: "smooth" }); }, [conv]);

  function send() {
    if (!input.trim()) return;
    setConv(c => [...c, { from: "me", msg: input, at: new Date().toLocaleTimeString("fr-FR", { hour: "2-digit", minute: "2-digit" }) }]);
    setInput("");
  }

  return (
    <div className="space-y-4">
      <header>
        <Pill color="rose">Messages</Pill>
        <h1 className="mt-3 text-3xl sm:text-4xl font-black tracking-tight">Tes <span className="rose-text">conversations</span></h1>
        <p className="mt-2 text-muted text-sm">Les abonnements donnent accès à la messagerie privée des créateurs.</p>
      </header>

      <div className="grid lg:grid-cols-12 gap-4 h-[68vh]">
        {/* THREADS list */}
        <aside className="lg:col-span-4 glass rounded-2xl flex flex-col">
          <header className="p-3 border-b border-overlay/10">
            <div className="flex items-center gap-2 rounded-xl bg-overlay/10 px-3 py-2 ring-1 ring-overlay/10">
              <Search size={13} className="text-muted" />
              <input placeholder="Chercher une conversation…" className="bg-transparent outline-none flex-1 text-sm" />
            </div>
          </header>

          <ul className="flex-1 overflow-y-auto scrollbar-thin">
            {THREADS.map(t => {
              const c = CREATORS.find(x => x.id === t.creatorId)!;
              const isActive = t.creatorId === activeId;
              return (
                <li key={t.creatorId}>
                  <button onClick={() => setActiveId(t.creatorId)} className={`w-full flex items-start gap-3 p-3 transition text-left ${isActive ? "bg-rose/10 ring-1 ring-rose/30" : "hover:bg-overlay/5"}`}>
                    <div className="relative shrink-0">
                      <div className="w-12 h-12 rounded-2xl grid place-items-center font-black text-black" style={{ background: c.banner }}>{c.avatar}</div>
                      {c.isLive && <span className="absolute -bottom-0.5 -right-0.5 px-1.5 py-0.5 rounded-full bg-rose text-[8px] font-black text-white">LIVE</span>}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-baseline justify-between gap-1">
                        <p className="text-sm font-bold truncate">{c.name}</p>
                        <span className="text-[10px] text-muted shrink-0">{relativeDate(t.lastAt)}</span>
                      </div>
                      <p className="text-[11px] text-muted truncate">{t.lastMsg}</p>
                    </div>
                    {t.unread > 0 && <span className="w-5 h-5 rounded-full rose-gradient text-black text-[10px] font-black grid place-items-center shrink-0">{t.unread}</span>}
                  </button>
                </li>
              );
            })}
          </ul>
        </aside>

        {/* CONVERSATION */}
        <section className="lg:col-span-8 glass rounded-2xl flex flex-col">
          <header className="p-3 border-b border-overlay/10 flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl grid place-items-center font-black text-black text-xs" style={{ background: active.banner }}>{active.avatar}</div>
            <div className="flex-1 min-w-0">
              <p className="font-bold truncate">{active.name}</p>
              <p className="text-[11px] text-muted truncate">{active.handle} · {active.tier}</p>
            </div>
            <Pill color="rose">Abonnée</Pill>
          </header>

          <div ref={ref} className="flex-1 overflow-y-auto scrollbar-thin p-4 space-y-3">
            {conv.map((m, i) => (
              <div key={i} className={`flex ${m.from === "me" ? "justify-end" : "justify-start"}`}>
                <div className={`max-w-[70%] rounded-2xl px-3 py-2 ${m.from === "me" ? "rose-gradient text-black" : "bg-overlay/10"}`}>
                  <p className="text-sm">{m.msg}</p>
                  <p className={`text-[10px] mt-1 ${m.from === "me" ? "text-black/60" : "text-muted"}`}>{m.at}</p>
                </div>
              </div>
            ))}

            <div className="flex justify-center pt-2">
              <span className="text-[10px] text-muted">Conversation chiffrée · privée entre toi et {active.name.split(" ")[0]}</span>
            </div>
          </div>

          <footer className="p-3 border-t border-overlay/10">
            <div className="flex items-center gap-2">
              <button className="p-2 rounded-lg hover:bg-overlay/10"><Plus size={16} /></button>
              <button className="p-2 rounded-lg hover:bg-overlay/10"><ImageIcon size={16} /></button>
              <input
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={e => e.key === "Enter" && send()}
                placeholder="Écris à Amira…"
                className="flex-1 bg-overlay/10 rounded-lg px-3 py-2 text-sm outline-none ring-1 ring-overlay/10 focus:ring-rose/40"
              />
              <button className="p-2 rounded-lg hover:bg-overlay/10"><Mic size={16} /></button>
              <button onClick={send} className="p-2 rounded-lg rose-gradient text-black"><Send size={14} /></button>
            </div>
            <p className="mt-2 text-[10px] text-muted text-center">Réponse moyenne d'Amira : 4h · Les créateurs Elite répondent dans 24h</p>
          </footer>
        </section>
      </div>
    </div>
  );
}
