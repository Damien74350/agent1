'use client';

import { useEffect, useState, use } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useSearchParams } from 'next/navigation';
import { Aurora } from '@/components/Aurora';
import { BlurredGrid } from '@/components/BlurredGrid';
import type { Creator } from '@/lib/db';

export default function Profile({ params }: { params: Promise<{ handle: string }> }) {
  const { handle: rawHandle } = use(params);
  const handle = decodeURIComponent(rawHandle).replace(/^@/, '');
  const search = useSearchParams();
  const isUnlocked = !!search.get('unblur');
  const [creator, setCreator] = useState<Creator | null>(null);
  const [loading, setLoading] = useState(false);
  const [origin, setOrigin] = useState('');

  useEffect(() => {
    setOrigin(window.location.origin);
    (async () => {
      const res = await fetch('/api/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ handle }),
      });
      const j = await res.json();
      if (j?.creator) setCreator(j.creator);
    })();
  }, [handle]);

  async function subscribe() {
    setLoading(true);
    const res = await fetch('/api/checkout', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ handle }),
    });
    const j = await res.json();
    if (j?.url) window.location.href = j.url;
    else setLoading(false);
  }

  if (!creator) {
    return (
      <main className="relative min-h-screen overflow-hidden">
        <Aurora />
        <div className="relative z-10 mx-auto max-w-3xl px-6 py-14">
          <div className="h-44 animate-pulse rounded-3xl bg-white/5" />
        </div>
      </main>
    );
  }

  const price = (creator.priceCents / 100).toFixed(2).replace('.', ',');
  const shareUrl = `${origin}/@${creator.handle}`;

  return (
    <main className="relative min-h-screen overflow-hidden">
      <Aurora />
      <div className="relative z-10 mx-auto max-w-3xl px-6 py-10 sm:py-14">
        <motion.header
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex flex-col items-center gap-4 text-center"
        >
          <img
            src={creator.profilePic}
            alt={creator.displayName}
            className="h-28 w-28 rounded-full border-4 border-accent object-cover shadow-[0_12px_40px_-10px_rgba(255,107,53,0.7)]"
          />
          <div>
            <div className="text-3xl font-black tracking-tight">{creator.displayName}</div>
            <div className="text-accentSoft">@{creator.handle}</div>
          </div>
          {creator.bio && <p className="max-w-md text-white/70">{creator.bio}</p>}
        </motion.header>

        <motion.section
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.15 }}
          className="mt-10 rounded-3xl border border-white/10 bg-white/5 p-4 backdrop-blur sm:p-6"
        >
          <div className="mb-4 flex items-center justify-between">
            <div className="text-xs uppercase tracking-widest text-white/40">Feed</div>
            <div className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-[11px] font-bold uppercase tracking-widest text-accentSoft">
              {isUnlocked ? 'Débloqué' : 'Verrouillé'}
            </div>
          </div>
          <BlurredGrid posts={creator.posts} blurred={!isUnlocked} />
        </motion.section>

        <AnimatePresence>
          {!isUnlocked && (
            <motion.section
              initial={{ opacity: 0, y: 22 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              transition={{ delay: 0.3 }}
              className="mt-6 rounded-3xl border border-accent/30 bg-gradient-to-br from-accent/15 via-white/5 to-white/0 p-6 backdrop-blur"
            >
              <div className="flex flex-col gap-5 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <div className="text-xs uppercase tracking-widest text-accentSoft">Abonnement mensuel</div>
                  <div className="mt-1 flex items-baseline gap-1">
                    <span className="text-5xl font-black tabular-nums tracking-tight">{price}</span>
                    <span className="text-xl font-bold text-white/50">€/mois</span>
                  </div>
                  <ul className="mt-3 space-y-1 text-sm text-white/70">
                    {creator.perks.map((p) => (
                      <li key={p} className="flex items-center gap-2">
                        <span className="text-mint">✓</span> {p}
                      </li>
                    ))}
                  </ul>
                </div>
                <button
                  onClick={subscribe}
                  disabled={loading}
                  className="group flex items-center justify-center gap-2 rounded-2xl bg-accent px-7 py-4 text-base font-extrabold shadow-[0_14px_40px_-10px_rgba(255,107,53,0.7)] transition-all hover:scale-[1.02] active:scale-[0.98] disabled:opacity-50"
                >
                  {loading ? 'Redirection…' : 'Débloquer tout'}
                  <span className="transition-transform group-hover:translate-x-0.5">→</span>
                </button>
              </div>
            </motion.section>
          )}
        </AnimatePresence>

        {isUnlocked && (
          <motion.section
            initial={{ opacity: 0, y: 22 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-6 rounded-3xl border border-mint/30 bg-mint/10 p-6 backdrop-blur"
          >
            <div className="text-center">
              <div className="text-3xl">🎉</div>
              <div className="mt-2 text-xl font-black">Bienvenue dans le club</div>
              <div className="mt-1 text-sm text-white/70">
                Tu as accès à l'intégralité du feed de @{creator.handle}. Profite.
              </div>
            </div>
          </motion.section>
        )}

        <motion.section
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="mt-6 rounded-3xl border border-white/10 bg-white/5 p-5 backdrop-blur"
        >
          <div className="text-xs uppercase tracking-widest text-white/40">Partage ta page</div>
          <div className="mt-2 flex items-center gap-2 rounded-xl bg-black/40 px-3 py-2.5 font-mono text-sm text-white/80">
            <span className="truncate">{shareUrl}</span>
            <button
              onClick={() => navigator.clipboard?.writeText(shareUrl)}
              className="ml-auto shrink-0 rounded-md border border-white/10 bg-white/10 px-2 py-1 text-xs font-bold hover:bg-white/20"
            >
              Copier
            </button>
          </div>
        </motion.section>

        <footer className="mt-12 text-center text-xs text-white/30">
          Propulsé par <span className="font-bold text-white/60">unblur</span>
        </footer>
      </div>
    </main>
  );
}
