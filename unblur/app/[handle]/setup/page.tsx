'use client';

import { useEffect, useState, use } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { Aurora } from '@/components/Aurora';
import { BlurredGrid } from '@/components/BlurredGrid';
import type { Creator } from '@/lib/db';

const PRICES = [499, 999, 1999, 4999];

export default function Setup({ params }: { params: Promise<{ handle: string }> }) {
  const router = useRouter();
  const { handle: rawHandle } = use(params);
  const handle = decodeURIComponent(rawHandle).replace(/^@/, '');
  const [creator, setCreator] = useState<Creator | null>(null);
  const [price, setPrice] = useState(999);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    (async () => {
      const res = await fetch('/api/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ handle }),
      });
      const j = await res.json();
      if (j?.creator) {
        setCreator(j.creator);
        setPrice(j.creator.priceCents);
      }
    })();
  }, [handle]);

  async function activate() {
    if (!creator) return;
    setSaving(true);
    await fetch('/api/update', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ handle, priceCents: price }),
    });
    router.push(`/@${handle}`);
  }

  return (
    <main className="relative min-h-screen overflow-hidden">
      <Aurora />
      <div className="relative z-10 mx-auto max-w-3xl px-6 py-14">
        <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
          <div className="mb-3 inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-1 text-[11px] font-bold uppercase tracking-widest text-accentSoft">
            <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-accent" /> Étape finale
          </div>
          <h1 className="text-4xl font-black tracking-tight sm:text-5xl">
            Choisis ton prix.<br />
            <span className="bg-gradient-to-br from-accent to-accentSoft bg-clip-text text-transparent">
              C'est tout.
            </span>
          </h1>
          <p className="mt-3 text-white/60">
            Ton compte sera live dans 5 secondes. Tu pourras tout changer après.
          </p>
        </motion.div>

        {!creator ? (
          <Skeleton />
        ) : (
          <>
            <motion.section
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.15 }}
              className="mt-8 rounded-3xl border border-white/10 bg-white/5 p-6 backdrop-blur"
            >
              <div className="flex items-center gap-4">
                <img
                  src={creator.profilePic}
                  alt={creator.displayName}
                  className="h-16 w-16 rounded-full border-2 border-accent object-cover"
                />
                <div>
                  <div className="text-xs uppercase tracking-widest text-white/40">Aperçu</div>
                  <div className="text-xl font-black">{creator.displayName}</div>
                  <div className="text-sm text-accentSoft">@{creator.handle}</div>
                </div>
              </div>

              <div className="mt-5">
                <BlurredGrid posts={creator.posts} blurred />
              </div>
            </motion.section>

            <motion.section
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="mt-6 rounded-3xl border border-white/10 bg-white/5 p-6 backdrop-blur"
            >
              <div className="text-xs uppercase tracking-widest text-white/40">Prix mensuel</div>
              <div className="mt-2 flex items-baseline gap-1">
                <span className="text-6xl font-black tabular-nums tracking-tight">
                  {(price / 100).toFixed(2).replace('.', ',')}
                </span>
                <span className="text-2xl font-bold text-white/50">€/mois</span>
              </div>

              <div className="mt-6 flex flex-wrap gap-2">
                {PRICES.map((p) => (
                  <button
                    key={p}
                    onClick={() => setPrice(p)}
                    className={`rounded-full border px-4 py-2 text-sm font-bold transition-all ${
                      price === p
                        ? 'border-accent bg-accent text-white shadow-[0_8px_24px_-8px_rgba(255,107,53,0.6)]'
                        : 'border-white/10 bg-white/5 text-white/70 hover:border-white/30'
                    }`}
                  >
                    {p / 100}€
                  </button>
                ))}
                <div className="ml-auto flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-2">
                  <span className="text-sm text-white/40">Custom</span>
                  <input
                    type="number"
                    value={price / 100}
                    min={1}
                    max={500}
                    onChange={(e) => setPrice(Math.max(1, Math.min(500, Number(e.target.value))) * 100)}
                    className="w-16 bg-transparent text-right text-sm font-bold focus:outline-none"
                  />
                  <span className="text-sm text-white/40">€</span>
                </div>
              </div>

              <p className="mt-4 text-xs text-white/40">
                Tu gardes 90 % · Stripe gère les paiements · Pas d'engagement
              </p>
            </motion.section>

            <motion.div
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.45 }}
              className="mt-6 flex flex-col gap-3 sm:flex-row"
            >
              <button
                onClick={activate}
                disabled={saving}
                className="group flex flex-1 items-center justify-center gap-2 rounded-2xl bg-accent px-6 py-4 text-base font-extrabold shadow-[0_12px_40px_-10px_rgba(255,107,53,0.7)] transition-all hover:scale-[1.01] active:scale-[0.99] disabled:opacity-50"
              >
                {saving ? 'Activation…' : 'Activer mon compte'}
                <span className="transition-transform group-hover:translate-x-0.5">→</span>
              </button>
            </motion.div>
          </>
        )}
      </div>
    </main>
  );
}

function Skeleton() {
  return (
    <div className="mt-8 space-y-4">
      <div className="h-44 animate-pulse rounded-3xl bg-white/5" />
      <div className="h-44 animate-pulse rounded-3xl bg-white/5" />
    </div>
  );
}
