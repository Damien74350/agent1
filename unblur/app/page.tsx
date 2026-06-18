'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import { Aurora } from '@/components/Aurora';

export default function Landing() {
  const router = useRouter();
  const [handle, setHandle] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function start() {
    const cleaned = handle.replace(/^@/, '').trim().toLowerCase();
    if (!cleaned) {
      setError('Mets ton @ Instagram');
      return;
    }
    setError(null);
    setLoading(true);
    try {
      const res = await fetch('/api/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ handle: cleaned }),
      });
      if (!res.ok) {
        const j = await res.json().catch(() => ({}));
        throw new Error(j?.error || 'Création impossible');
      }
      router.push(`/@${cleaned}/setup`);
    } catch (e: any) {
      setError(e?.message || 'Une erreur est survenue');
      setLoading(false);
    }
  }

  return (
    <main className="relative min-h-screen overflow-hidden">
      <Aurora />

      <div className="relative z-10 flex min-h-screen flex-col items-center justify-center px-6 py-20">
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, ease: 'easeOut' }}
          className="mx-auto w-full max-w-2xl text-center"
        >
          <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-4 py-1.5 text-xs font-semibold uppercase tracking-widest text-accentSoft backdrop-blur">
            <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-accent" />
            Lance ton compte en 60 secondes
          </div>

          <h1 className="text-balance bg-gradient-to-br from-white via-white to-white/60 bg-clip-text text-5xl font-black leading-[1.05] tracking-tight text-transparent sm:text-7xl">
            Transforme ton Insta
            <br />
            en <span className="bg-gradient-to-br from-accent via-accentSoft to-accent bg-clip-text text-transparent">revenu mensuel</span>.
          </h1>

          <p className="mx-auto mt-6 max-w-xl text-balance text-lg text-white/70 sm:text-xl">
            unblur duplique ton compte, floute ton feed, et tes followers paient
            pour le voir en clair. Sans changer ce que tu publies déjà.
          </p>

          <div className="mx-auto mt-10 max-w-md">
            <div className="flex items-center gap-2 rounded-2xl border border-white/10 bg-white/5 p-2 backdrop-blur transition-all focus-within:border-accent">
              <span className="pl-3 text-2xl font-black text-white/40">@</span>
              <input
                value={handle}
                onChange={(e) => setHandle(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && start()}
                placeholder="ton_pseudo_insta"
                autoFocus
                className="min-w-0 flex-1 bg-transparent px-2 py-3 text-lg font-semibold text-white placeholder-white/30 focus:outline-none"
              />
              <button
                onClick={start}
                disabled={loading}
                className="group relative inline-flex items-center justify-center gap-2 overflow-hidden rounded-xl bg-accent px-5 py-3 text-sm font-bold text-white shadow-[0_8px_30px_-8px_rgba(255,107,53,0.6)] transition-all hover:scale-[1.02] active:scale-[0.98] disabled:opacity-50"
              >
                {loading ? (
                  <>
                    <Spinner /> Création
                  </>
                ) : (
                  <>
                    Démarrer
                    <Arrow />
                  </>
                )}
              </button>
            </div>
            <AnimatePresence>
              {error && (
                <motion.p
                  initial={{ opacity: 0, y: -6 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0 }}
                  className="mt-3 text-sm font-semibold text-rose-400"
                >
                  {error}
                </motion.p>
              )}
            </AnimatePresence>
          </div>

          <ul className="mx-auto mt-10 flex max-w-xl flex-wrap items-center justify-center gap-x-6 gap-y-2 text-sm text-white/50">
            <li className="flex items-center gap-2">
              <Dot /> 0% lock-in
            </li>
            <li className="flex items-center gap-2">
              <Dot /> Tu gardes 90% des revenus
            </li>
            <li className="flex items-center gap-2">
              <Dot /> Paiement par Stripe
            </li>
          </ul>
        </motion.div>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5, duration: 0.8 }}
          className="mt-24 grid w-full max-w-5xl grid-cols-1 gap-4 sm:grid-cols-3"
        >
          <Feature
            icon="✨"
            title="Import en 30 sec"
            body="Tape ton @, on récupère tes 9 dernières photos publiques et on les floute."
          />
          <Feature
            icon="💸"
            title="Tu fixes ton prix"
            body="€5 à €99/mois, change quand tu veux. Pas d'engagement, pas de paperasse."
          />
          <Feature
            icon="📈"
            title="Tu communiques"
            body="Lien à partager partout. Tes followers existants = ton premier revenu."
          />
        </motion.div>
      </div>
    </main>
  );
}

function Feature({ icon, title, body }: { icon: string; title: string; body: string }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/5 p-6 backdrop-blur transition-all hover:border-white/20 hover:bg-white/10">
      <div className="text-3xl">{icon}</div>
      <h3 className="mt-3 text-lg font-extrabold tracking-tight">{title}</h3>
      <p className="mt-1 text-sm text-white/60">{body}</p>
    </div>
  );
}

function Spinner() {
  return (
    <span className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-white/40 border-t-white" />
  );
}

function Arrow() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" className="transition-transform group-hover:translate-x-0.5">
      <path d="M5 12h14m0 0l-6-6m6 6l-6 6" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

function Dot() {
  return <span className="h-1.5 w-1.5 rounded-full bg-mint" />;
}
