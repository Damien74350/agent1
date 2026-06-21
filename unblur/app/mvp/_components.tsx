"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Home, User, Compass, MessageCircle, Plus } from "lucide-react";

export function MvpLogo({ size = "md", className = "" }: { size?: "sm" | "md" | "lg" | "xl"; className?: string }) {
  const sizes = {
    sm: "text-2xl",
    md: "text-4xl",
    lg: "text-6xl",
    xl: "text-9xl",
  };
  return (
    <span className={`font-black tracking-tighter inline-flex items-baseline ${sizes[size]} ${className}`}>
      <span className="text-white">u</span>
      <span className="text-rose-500">.</span>
    </span>
  );
}

export function MvpTopBar() {
  return (
    <header className="sticky top-0 z-50 bg-black/80 backdrop-blur-xl border-b border-white/10">
      <div className="mx-auto max-w-6xl px-4 sm:px-6 py-3 flex items-center justify-between">
        <Link href="/mvp" className="flex items-center">
          <MvpLogo size="md" />
        </Link>
        <nav className="hidden sm:flex items-center gap-7 text-sm font-medium text-white/70">
          <Link href="/mvp/feed" className="hover:text-white">Découvrir</Link>
          <Link href="/mvp/profile/sarah-yoga" className="hover:text-white">Profil démo</Link>
          <Link href="/mvp/onboarding" className="hover:text-white">Créateur</Link>
        </nav>
        <Link
          href="/mvp/waitlist"
          className="bg-rose-500 hover:bg-rose-600 text-white font-bold px-4 py-2 rounded-full text-sm transition"
        >
          Devenir Unblurer
        </Link>
      </div>
    </header>
  );
}

export function MvpBottomNav() {
  const pathname = usePathname();
  const items = [
    { href: "/mvp", icon: Home, label: "Accueil" },
    { href: "/mvp/feed", icon: Compass, label: "Explorer" },
    { href: "/mvp/studio", icon: Plus, label: "Créer" },
    { href: "/mvp/dashboard", icon: User, label: "Moi" },
  ];
  return (
    <nav className="fixed bottom-0 inset-x-0 sm:hidden z-50 bg-black/95 backdrop-blur-xl border-t border-white/10">
      <div className="grid grid-cols-4">
        {items.map(({ href, icon: Icon, label }) => {
          const active = pathname === href;
          return (
            <Link
              key={href}
              href={href}
              className={`flex flex-col items-center gap-1 py-3 ${
                active ? "text-rose-500" : "text-white/60"
              }`}
            >
              <Icon className="w-5 h-5" />
              <span className="text-[10px] font-medium">{label}</span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}

export function MvpFooter() {
  return (
    <footer className="border-t border-white/10 mt-32 py-12 text-center">
      <MvpLogo size="md" className="mb-3" />
      <p className="text-xs text-white/40">
        Démo interactive — © 2026 unblur — Antériorité INPI DSO2026022640
      </p>
    </footer>
  );
}
