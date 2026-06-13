"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { ChevronLeft, Video, Tv, Mic, MicOff, VideoOff, Settings, Play, Square, Circle, Image as ImageIcon, Type, MapPin, Wifi, Smile } from "lucide-react";

type Mode = "record" | "live";

export default function RecordPage() {
  const [mode, setMode] = useState<Mode>("record");
  const [recording, setRecording] = useState(false);
  const [seconds, setSeconds] = useState(0);
  const [audio, setAudio] = useState(true);
  const [video, setVideo] = useState(true);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [isPremium, setIsPremium] = useState(true);
  const videoRef = useRef<HTMLVideoElement>(null);

  // Simulated webcam (no actual permission flow — gradient bg + animated dot)
  useEffect(() => {
    if (!recording) { setSeconds(0); return; }
    const id = setInterval(() => setSeconds(s => s + 1), 1000);
    return () => clearInterval(id);
  }, [recording]);

  const mm = String(Math.floor(seconds / 60)).padStart(2, "0");
  const ss = String(seconds % 60).padStart(2, "0");

  return (
    <div className="space-y-6 pb-12">
      <Link href="/studio" className="inline-flex items-center gap-1 text-xs text-muted hover:text-foreground">
        <ChevronLeft size={14} /> Studio
      </Link>

      <header>
        <p className="text-xs uppercase tracking-[0.28em] text-muted mb-3">Caméra</p>
        <h1 className="text-3xl sm:text-5xl font-black tracking-tighter">Filmer maintenant</h1>
      </header>

      {/* Mode toggle */}
      <div className="inline-flex rounded-full border border-border p-1">
        <button onClick={() => setMode("record")} className={`px-5 py-2 rounded-full text-sm font-bold transition ${mode === "record" ? "bg-foreground text-surface" : "text-muted hover:text-foreground"}`}>
          <Video size={14} className="inline mr-2 -mt-0.5" />Enregistrer
        </button>
        <button onClick={() => setMode("live")} className={`px-5 py-2 rounded-full text-sm font-bold transition ${mode === "live" ? "bg-foreground text-surface" : "text-muted hover:text-foreground"}`}>
          <Tv size={14} className="inline mr-2 -mt-0.5" />Live direct
        </button>
      </div>

      <div className="grid lg:grid-cols-12 gap-6">
        {/* CAMERA preview */}
        <div className="lg:col-span-8 space-y-4">
          <div className="relative aspect-video rounded-3xl overflow-hidden border border-border" style={{ background: "linear-gradient(135deg, #1f1d2b, #3d3a52)" }}>
            {/* Faux feed video */}
            <div className="absolute inset-0 grid place-items-center text-surface/40">
              <div className="text-center">
                <Video size={48} className="mx-auto" />
                <p className="mt-3 text-sm font-bold">Aperçu caméra</p>
                <p className="text-xs opacity-70">1080p · 30fps · 5.2 Mbps</p>
              </div>
            </div>

            {/* HUD top */}
            <div className="absolute top-4 left-4 flex items-center gap-2">
              {recording && (
                <div className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-rose text-surface text-[11px] font-black uppercase tracking-widest">
                  <span className="w-1.5 h-1.5 rounded-full bg-surface live-dot" />
                  {mode === "live" ? "Live" : "REC"} {mm}:{ss}
                </div>
              )}
              {mode === "live" && (
                <div className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-foreground/50 backdrop-blur text-surface text-[11px] font-bold">
                  <Wifi size={11} /> {recording ? "184 viewers" : "Prêt"}
                </div>
              )}
            </div>

            {/* HUD bottom toggles */}
            <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex items-center gap-2">
              <button onClick={() => setAudio(!audio)} className={`w-11 h-11 rounded-full grid place-items-center backdrop-blur ${audio ? "bg-foreground/50 text-surface" : "bg-rose text-surface"}`}>
                {audio ? <Mic size={16} /> : <MicOff size={16} />}
              </button>
              <button onClick={() => setVideo(!video)} className={`w-11 h-11 rounded-full grid place-items-center backdrop-blur ${video ? "bg-foreground/50 text-surface" : "bg-rose text-surface"}`}>
                {video ? <Video size={16} /> : <VideoOff size={16} />}
              </button>
              {/* RECORD button */}
              <button onClick={() => setRecording(!recording)} className={`w-16 h-16 rounded-full grid place-items-center border-4 ${recording ? "border-rose bg-rose" : "border-surface bg-rose"} transition`}>
                {recording ? <Square size={20} className="text-surface" fill="currentColor" /> : <Circle size={28} className="text-surface" fill="currentColor" />}
              </button>
              <button className="w-11 h-11 rounded-full grid place-items-center bg-foreground/50 text-surface backdrop-blur">
                <Settings size={16} />
              </button>
            </div>
          </div>

          {/* Capacités */}
          <div className="grid grid-cols-3 gap-3 text-xs">
            <Cap icon={Smile} label="Filtres beauté" />
            <Cap icon={Type} label="Sous-titres auto" />
            <Cap icon={ImageIcon} label="Overlay image" />
            <Cap icon={MapPin} label="Géolocalisation" />
            <Cap icon={Wifi} label="Sauvegarde cloud" />
            <Cap icon={Settings} label="Qualité 4K dispo" />
          </div>
        </div>

        {/* SIDEBAR — publication */}
        <aside className="lg:col-span-4 space-y-4">
          <p className="text-xs uppercase tracking-[0.28em] text-muted">Détails de publication</p>

          <div className="rounded-2xl border border-border p-5 space-y-4">
            <div>
              <label className="text-[10px] uppercase tracking-widest font-bold text-muted">Titre</label>
              <input value={title} onChange={e => setTitle(e.target.value)} placeholder="Ex: Mobilité matin 25 min" className="mt-1 w-full bg-overlay/5 rounded-xl px-3 py-2.5 outline-none border border-border focus:border-foreground text-sm" />
            </div>
            <div>
              <label className="text-[10px] uppercase tracking-widest font-bold text-muted">Description</label>
              <textarea value={description} onChange={e => setDescription(e.target.value)} rows={4} placeholder="Pour qui, focus, équipement requis…" className="mt-1 w-full bg-overlay/5 rounded-xl px-3 py-2.5 outline-none border border-border focus:border-foreground text-sm resize-none" />
            </div>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-bold">Réservé aux abonnés</p>
                <p className="text-[11px] text-muted">{isPremium ? "Cette séance est verrouillée" : "Cette séance est gratuite"}</p>
              </div>
              <button onClick={() => setIsPremium(!isPremium)} className={`relative w-11 h-6 rounded-full transition ${isPremium ? "bg-foreground" : "bg-overlay/10"}`}>
                <span className={`absolute top-0.5 w-5 h-5 rounded-full bg-surface transition-all ${isPremium ? "left-5" : "left-0.5"}`} />
              </button>
            </div>
            <div>
              <label className="text-[10px] uppercase tracking-widest font-bold text-muted">Programme lié</label>
              <select className="mt-1 w-full bg-overlay/5 rounded-xl px-3 py-2.5 outline-none border border-border text-sm">
                <option>Aucun</option>
                <option>Premier pull-up en 12 semaines</option>
                <option>Mobilité hanches 30 jours</option>
              </select>
            </div>
          </div>

          <button className="w-full px-4 py-3 rounded-full bg-foreground text-surface font-bold disabled:opacity-50" disabled={!title}>
            {mode === "live" ? "Lancer le live" : "Publier le replay"}
          </button>
          <button className="w-full px-4 py-3 rounded-full border border-border font-bold text-sm">
            Sauvegarder en brouillon
          </button>

          <p className="text-[10px] text-muted text-center">Notification push envoyée automatiquement à tes 2 840 abonnés quand le contenu est publié.</p>
        </aside>
      </div>
    </div>
  );
}

function Cap({ icon: Icon, label }: { icon: any; label: string }) {
  return (
    <div className="rounded-xl border border-border px-3 py-2 flex items-center gap-2">
      <Icon size={13} className="text-muted" />
      <span className="text-[11px] font-semibold">{label}</span>
    </div>
  );
}
