"use client";

import { useState } from "react";
import { useParams, notFound } from "next/navigation";
import Link from "next/link";
import { Pill } from "../../../components/Card";
import { ContentCard } from "../../../components/ContentCard";
import { findContent, findCreator, contentsForCreator } from "../../../lib/mock";
import { compact, fmtEUR, relativeDate } from "../../../lib/format";
import { Heart, Share2, Bookmark, ChevronLeft, ThumbsUp, MessageCircle, Lock, Play, Pause, Volume2, Maximize2, Sparkles, Send, MoreVertical } from "lucide-react";

const FAKE_COMMENTS = [
  { user: "léa.bx", avatar: "LB", time: "2h", msg: "Top séance, j'ai bien transpiré 💦 Merci Louise.", likes: 24, color: "#fcd34d" },
  { user: "fitkim", avatar: "FK", time: "5h", msg: "La progression sur le dos est dingue. J'ai senti chaque muscle.", likes: 18, color: "#ff2e7e" },
  { user: "warrior_théo", avatar: "WT", time: "8h", msg: "Question : on peut faire ça tous les jours ou il faut alterner ?", likes: 12, color: "#ffb347" },
  { user: "mama_fit", avatar: "MF", time: "1j", msg: "Première semaine et déjà des résultats. ❤️", likes: 31, color: "#5b9eff" },
  { user: "alex_92", avatar: "A9", time: "1j", msg: "Petit feedback : la transition était un peu rapide à 12min, sinon parfait.", likes: 8, color: "#5eead4" },
];

export default function WatchPage() {
  const params = useParams();
  const id = params?.id as string;
  const content = findContent(id);
  if (!content) notFound();
  const creator = findCreator(content.creatorId)!;
  const related = contentsForCreator(creator.id).filter(c => c.id !== content.id).slice(0, 4);

  const [subscribed, setSubscribed] = useState(!content.isPremium);
  const [liked, setLiked] = useState(false);
  const [saved, setSaved] = useState(false);
  const [commentInput, setCommentInput] = useState("");

  return (
    <div className="space-y-4 -mx-4 sm:-mx-6 lg:-mx-8 px-4 sm:px-6 lg:px-8">
      <Link href={`/c/${creator.id}`} className="inline-flex items-center gap-1 text-xs text-muted hover:text-white">
        <ChevronLeft size={14} /> {creator.name}
      </Link>

      <div className="grid lg:grid-cols-12 gap-6">
        {/* MAIN */}
        <div className="lg:col-span-8 space-y-5">
          {/* Player */}
          <div className="relative aspect-video rounded-2xl overflow-hidden ring-1 ring-overlay/10" style={{ background: content.thumbnail }}>
            <div className="absolute inset-0 grain opacity-30" />
            <div className="absolute inset-0 grid place-items-center text-7xl opacity-50">{content.thumbnailEmoji}</div>

            {!subscribed ? (
              <div className="absolute inset-0 grid place-items-center bg-black/60 backdrop-blur">
                <div className="text-center max-w-xs px-4">
                  <Lock size={32} className="text-rose mx-auto mb-3" />
                  <p className="font-black text-xl">Contenu premium</p>
                  <p className="text-xs text-muted mt-1">Abonne-toi à {creator.name.split(" ")[0]} pour débloquer cette séance + tout son catalogue.</p>
                  <button onClick={() => setSubscribed(true)} className="mt-4 inline-flex items-center gap-2 px-5 py-2.5 rounded-xl rose-gradient text-black font-black shadow-glow">
                    <Sparkles size={16} /> S'abonner · {fmtEUR(creator.monthlyPriceEUR)}/mois
                  </button>
                </div>
              </div>
            ) : (
              <>
                <div className="absolute inset-0 grid place-items-center">
                  <div className="w-20 h-20 rounded-full rose-gradient grid place-items-center shadow-glow">
                    <Play size={28} className="text-black ml-1" fill="currentColor" />
                  </div>
                </div>
                <div className="absolute inset-x-0 bottom-0 p-3 bg-gradient-to-t from-black/90 to-transparent">
                  <div className="flex items-center gap-3 text-white">
                    <Play size={16} />
                    <Volume2 size={16} />
                    <div className="flex-1 h-1 bg-overlay/30 rounded-full">
                      <div className="h-full w-1/4 rose-gradient rounded-full" />
                    </div>
                    <span className="text-xs font-mono">5:32 / {content.durationMin}:00</span>
                    <Maximize2 size={16} />
                  </div>
                </div>
              </>
            )}
          </div>

          {/* Title + actions */}
          <div>
            <div className="flex flex-wrap items-center gap-2 text-[11px]">
              <Pill color={content.type === "live" ? "rose" : content.type === "program" ? "violet" : "sun"}>
                {content.type === "live" ? "Live" : content.type === "program" ? "Programme" : "Vidéo"}
              </Pill>
              <Pill color="sky">{content.difficulty}</Pill>
              <span className="text-muted">{content.durationMin}min · {compact(content.views)} vues · {relativeDate(content.publishedAt)}</span>
            </div>
            <h1 className="mt-2 text-2xl sm:text-3xl font-black tracking-tight">{content.title}</h1>

            <div className="mt-4 flex flex-wrap items-center gap-2">
              <button onClick={() => setLiked(!liked)} className={`inline-flex items-center gap-1.5 px-3 py-2 rounded-lg text-xs font-bold ${liked ? "bg-rose text-black" : "bg-overlay/10 hover:bg-overlay/20"}`}>
                <ThumbsUp size={13} /> {compact(content.likes + (liked ? 1 : 0))}
              </button>
              <button onClick={() => setSaved(!saved)} className={`inline-flex items-center gap-1.5 px-3 py-2 rounded-lg text-xs font-bold ${saved ? "bg-sun text-black" : "bg-overlay/10 hover:bg-overlay/20"}`}>
                <Bookmark size={13} /> Sauver
              </button>
              <button className="inline-flex items-center gap-1.5 px-3 py-2 rounded-lg bg-overlay/10 hover:bg-overlay/20 text-xs font-bold">
                <Share2 size={13} /> Partager
              </button>
              <button className="ml-auto p-2 rounded-lg hover:bg-overlay/10"><MoreVertical size={16} /></button>
            </div>
          </div>

          {/* Creator strip */}
          <div className="glass rounded-2xl p-4 flex items-center gap-3">
            <Link href={`/c/${creator.id}`} className="w-12 h-12 rounded-2xl grid place-items-center font-black text-black shrink-0" style={{ background: creator.banner }}>
              {creator.avatar}
            </Link>
            <div className="flex-1 min-w-0">
              <Link href={`/c/${creator.id}`} className="font-black hover:underline">{creator.name}</Link>
              <p className="text-xs text-muted">{compact(creator.subscribers)} abonnés · {creator.handle}</p>
            </div>
            {subscribed ? (
              <Pill color="success">Abonné</Pill>
            ) : (
              <button onClick={() => setSubscribed(true)} className="px-4 py-2 rounded-lg rose-gradient text-black text-xs font-black">
                S'abonner
              </button>
            )}
          </div>

          {/* Description */}
          <div className="glass rounded-2xl p-4">
            <p className="text-sm">{content.description}</p>
            <div className="mt-3 flex flex-wrap gap-1.5 text-[10px]">
              {["#calisthenics", "#mobility", "#débutant", "#sans-matériel"].map(t => (
                <span key={t} className="text-rose font-bold">{t}</span>
              ))}
            </div>
          </div>

          {/* Comments */}
          <div className="glass rounded-2xl p-4">
            <p className="font-bold flex items-center gap-2"><MessageCircle size={14} className="text-rose" /> {compact(content.comments)} commentaires</p>

            <div className="mt-3 flex items-center gap-2">
              <div className="w-9 h-9 rounded-full grid place-items-center font-black text-black text-xs" style={{ background: "linear-gradient(135deg, #ff2e7e, #ffb347)" }}>DR</div>
              <input
                value={commentInput}
                onChange={e => setCommentInput(e.target.value)}
                placeholder="Ajouter un commentaire publique…"
                className="flex-1 bg-overlay/10 rounded-lg px-3 py-2 text-sm outline-none ring-1 ring-overlay/10 focus:ring-rose/40"
              />
              <button className="p-2 rounded-lg rose-gradient text-black"><Send size={14} /></button>
            </div>

            <ul className="mt-4 space-y-4">
              {FAKE_COMMENTS.map(c => (
                <li key={c.user} className="flex items-start gap-3">
                  <div className="w-9 h-9 rounded-full grid place-items-center font-black text-black text-xs shrink-0" style={{ background: c.color }}>{c.avatar}</div>
                  <div className="flex-1 min-w-0">
                    <p className="text-xs"><span className="font-bold">{c.user}</span> <span className="text-muted">· il y a {c.time}</span></p>
                    <p className="mt-0.5 text-sm">{c.msg}</p>
                    <div className="mt-1 flex items-center gap-3 text-[11px] text-muted">
                      <button className="inline-flex items-center gap-1 hover:text-rose"><ThumbsUp size={11} /> {c.likes}</button>
                      <button className="hover:text-rose">Répondre</button>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* SIDEBAR */}
        <aside className="lg:col-span-4 space-y-4">
          <p className="text-[10px] uppercase tracking-widest text-muted font-bold">Autres séances de {creator.name.split(" ")[0]}</p>
          {related.map(c => <ContentCard key={c.id} content={c} />)}
        </aside>
      </div>
    </div>
  );
}
