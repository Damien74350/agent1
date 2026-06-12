import Link from "next/link";
import { Play, Sparkles, Tv, Zap, Users, ArrowRight, Star, Lock, Heart, Crown, TrendingUp } from "lucide-react";
import { Pill, Card } from "../components/Card";
import { CreatorCard } from "../components/CreatorCard";
import { ContentCard } from "../components/ContentCard";
import { FEATURED_CREATORS, TRENDING_CREATORS, RISING_CREATORS, LIVE_NOW, CONTENTS, ALL_CATEGORIES, platformTotals, CREATORS } from "../lib/mock";
import { compact, fmtEUR } from "../lib/format";

export default function Home() {
  const totals = platformTotals();
  const liveNow = LIVE_NOW.slice(0, 3);
  const recentContent = CONTENTS.slice(0, 4);

  return (
    <div className="space-y-16">
      {/* HERO */}
      <section className="relative pt-6 sm:pt-10 pb-4 -mx-4 sm:-mx-6 px-4 sm:px-6 lg:-mx-8 lg:px-8">
        <div className="grid lg:grid-cols-12 gap-10 items-center">
          <div className="lg:col-span-7">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-rose/10 ring-1 ring-rose/30 text-rose text-xs font-black uppercase tracking-[0.18em] mb-6">
              <Sparkles size={12} /> Le Twitch du sport — bêta
            </div>
            <h1 className="text-5xl sm:text-7xl lg:text-8xl font-black tracking-tight leading-[0.95]">
              <span className="rose-text">unblur.</span><br />
              Le vrai entraînement,<br />
              sans filtre.
            </h1>
            <p className="mt-6 text-lg sm:text-xl text-white/70 max-w-2xl">
              Abonne-toi à tes créateurs préférés. Ils fixent leur prix. Tu as accès à leurs lives, programmes, vidéos exclusives.
              <strong className="text-white"> Le créateur garde 80%</strong> — la rémunération la plus juste du marché.
            </p>

            <div className="mt-8 flex flex-wrap gap-3">
              <Link href="/discover" className="inline-flex items-center gap-2 px-6 py-3.5 rounded-xl rose-gradient text-black font-black shadow-glow">
                <Sparkles size={18} /> Découvrir
                <ArrowRight size={16} />
              </Link>
              <Link href="/become-creator" className="inline-flex items-center gap-2 px-6 py-3.5 rounded-xl bg-white/5 ring-1 ring-white/10 hover:bg-white/10 font-bold">
                <Zap size={18} /> Devenir créateur
              </Link>
            </div>

            <div className="mt-12 grid grid-cols-2 sm:grid-cols-4 gap-6 max-w-2xl">
              <div>
                <p className="text-3xl sm:text-4xl font-black rose-text">{compact(totals.totalCreators * 280)}</p>
                <p className="text-xs text-white/60 mt-1">créateurs sur la plateforme</p>
              </div>
              <div>
                <p className="text-3xl sm:text-4xl font-black">{compact(totals.totalSubs * 12)}</p>
                <p className="text-xs text-white/60 mt-1">abonnés actifs</p>
              </div>
              <div>
                <p className="text-3xl sm:text-4xl font-black">80%</p>
                <p className="text-xs text-white/60 mt-1">au créateur, toujours</p>
              </div>
              <div>
                <p className="text-3xl sm:text-4xl font-black rose-text">{fmtEUR(totals.creatorPayout * 12, 0)}</p>
                <p className="text-xs text-white/60 mt-1">reversé aux créateurs</p>
              </div>
            </div>
          </div>

          {/* Hero card preview */}
          <div className="lg:col-span-5 relative">
            <div className="glass-strong rounded-3xl overflow-hidden shadow-glow">
              {liveNow[0] && (
                <div className="relative aspect-video unblur-in" style={{ background: liveNow[0].banner }}>
                  <div className="absolute inset-0 grain opacity-30" />
                  <div className="absolute top-3 left-3 inline-flex items-center gap-1.5 px-2 py-1 rounded-full bg-black/70 backdrop-blur text-[10px] font-black uppercase tracking-widest text-white">
                    <span className="w-2 h-2 rounded-full bg-rose live-dot" /> Live · {compact(liveNow[0].liveViewers ?? 0)}
                  </div>
                  <div className="absolute inset-0 grid place-items-center">
                    <div className="w-16 h-16 rounded-full rose-gradient grid place-items-center shadow-glow">
                      <Play size={26} className="text-black ml-1" fill="currentColor" />
                    </div>
                  </div>
                </div>
              )}
              <div className="p-5">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 rounded-2xl grid place-items-center font-black text-black" style={{ background: liveNow[0]?.banner }}>
                    {liveNow[0]?.avatar}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-black truncate">{liveNow[0]?.name}</p>
                    <p className="text-xs text-muted truncate">{liveNow[0]?.handle}</p>
                  </div>
                  <Pill color="rose">{liveNow[0]?.tier}</Pill>
                </div>
                <p className="mt-3 font-bold text-sm">{liveNow[0]?.liveTitle}</p>
                <button className="mt-4 w-full px-4 py-2.5 rounded-xl rose-gradient text-black font-black text-sm shadow-glow">
                  Rejoindre — {fmtEUR(liveNow[0]?.monthlyPriceEUR ?? 9.9)}/mois
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* LIVE NOW */}
      <section>
        <header className="flex items-end justify-between mb-5">
          <div>
            <Pill color="rose"><span className="w-2 h-2 rounded-full bg-rose live-dot mr-1" />Live maintenant</Pill>
            <h2 className="mt-2 text-2xl sm:text-3xl font-black">En direct — rejoins la séance</h2>
          </div>
          <Link href="/live" className="text-sm text-rose font-bold hover:underline">Tout voir →</Link>
        </header>
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {liveNow.map(c => <CreatorCard key={c.id} creator={c} />)}
        </div>
      </section>

      {/* FEATURED */}
      <section>
        <header className="mb-5">
          <Pill color="sun">À la une cette semaine</Pill>
          <h2 className="mt-2 text-2xl sm:text-3xl font-black">4 créateurs qui cartonnent</h2>
        </header>
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-5">
          {FEATURED_CREATORS.map(c => <CreatorCard key={c.id} creator={c} compactMode />)}
        </div>
      </section>

      {/* CATEGORIES */}
      <section>
        <header className="mb-5">
          <Pill color="sky">Toutes les disciplines</Pill>
          <h2 className="mt-2 text-2xl sm:text-3xl font-black">Trouve ta discipline</h2>
        </header>
        <div className="flex flex-wrap gap-2">
          {ALL_CATEGORIES.map(cat => (
            <Link key={cat} href={`/discover?cat=${cat}`} className="px-4 py-2 rounded-xl bg-white/5 ring-1 ring-white/10 hover:bg-rose/10 hover:ring-rose/30 transition text-sm font-bold">
              {cat}
            </Link>
          ))}
        </div>
      </section>

      {/* WHY IT WORKS */}
      <section className="rounded-3xl glass-strong p-8 sm:p-12">
        <div className="text-center max-w-2xl mx-auto mb-8">
          <Pill color="rose">Le deal</Pill>
          <h2 className="mt-3 text-3xl sm:text-4xl font-black">80% au créateur. Toujours.</h2>
          <p className="mt-3 text-white/70">
            OnlyFans : 80/20 mais image sulfureuse. Twitch : 50/50. YouTube : algorithme.
            Patreon : 88/12 mais zéro vidéo. unblur : <strong className="text-white">la justice + la qualité technique</strong>.
          </p>
        </div>
        <div className="grid sm:grid-cols-3 gap-4">
          {[
            { icon: Crown, title: "80/20 le plus juste", text: "Tu fixes ton prix. Tu touches 80%. On gère tout : paiement, hébergement, support." },
            { icon: Tv, title: "Live + Replay + Programme", text: "Sessions en direct, replays toujours dispos, programmes structurés. Tout un studio dans un onglet." },
            { icon: Lock, title: "Paywall propre", text: "Stripe sous le capot. Tes abonnés paient avec Apple Pay, virement, CB. Aucun abus possible." },
          ].map(o => (
            <div key={o.title} className="rounded-2xl bg-white/5 ring-1 ring-white/10 p-5">
              <o.icon size={22} className="text-rose mb-2" />
              <p className="font-bold">{o.title}</p>
              <p className="text-xs text-muted mt-1">{o.text}</p>
            </div>
          ))}
        </div>
      </section>

      {/* TRENDING CONTENT */}
      <section>
        <header className="mb-5 flex items-end justify-between">
          <div>
            <Pill color="violet">Trending</Pill>
            <h2 className="mt-2 text-2xl sm:text-3xl font-black">Le contenu qui buzz</h2>
          </div>
          <Link href="/discover" className="text-sm text-rose font-bold hover:underline">Explorer →</Link>
        </header>
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-5">
          {recentContent.map(c => <ContentCard key={c.id} content={c} />)}
        </div>
      </section>

      {/* CTA FINAL */}
      <section className="relative rounded-3xl ring-1 ring-rose/30 p-10 sm:p-16 text-center overflow-hidden">
        <div className="absolute inset-0 rose-gradient opacity-[0.12]" />
        <div className="absolute inset-0 grain opacity-25" />
        <div className="relative max-w-3xl mx-auto">
          <Crown className="mx-auto text-rose" size={36} />
          <h2 className="mt-5 text-4xl sm:text-6xl font-black tracking-tight leading-[1.05]">
            Tu enseignes ?<br />
            <span className="rose-text">Vis de ta passion.</span>
          </h2>
          <p className="mt-5 text-white/70 text-lg max-w-xl mx-auto">
            Une étudiante en kiné gagne <strong className="text-white">{fmtEUR(CREATORS[0].monthlyEarningsEUR * 0.8, 0)}</strong> ce mois sur unblur. Sans agent, sans contrat.
            Lance ton abonnement en 10 minutes.
          </p>
          <div className="mt-8 flex flex-wrap gap-3 justify-center">
            <Link href="/become-creator" className="inline-flex items-center gap-2 px-6 py-3.5 rounded-xl rose-gradient text-black font-black shadow-glow">
              <Sparkles size={18} /> Devenir créateur
            </Link>
            <Link href="/discover" className="inline-flex items-center gap-2 px-6 py-3.5 rounded-xl bg-white/10 ring-1 ring-white/20 font-bold">
              <Heart size={18} /> Découvrir les créateurs
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
