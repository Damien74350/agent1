"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Logo } from "./Logo";
import { Search, Home, Compass, Tv, Library, BarChart3, BookOpen, MessageCircle, PlaySquare } from "lucide-react";

const NAV = [
  { href: "/", label: "Accueil", icon: Home },
  { href: "/discover", label: "Découvrir", icon: Compass },
  { href: "/shorts", label: "Shorts", icon: PlaySquare },
  { href: "/live", label: "Live", icon: Tv },
  { href: "/programs", label: "Programmes", icon: BookOpen },
  { href: "/feed", label: "Mon feed", icon: Library },
  { href: "/messages", label: "Messages", icon: MessageCircle },
  { href: "/studio", label: "Studio", icon: BarChart3 },
];

export function TopNav() {
  const pathname = usePathname() || "/";
  return (
    <header className="sticky top-0 z-40 border-b border-border bg-canvas/80 backdrop-blur">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="h-14 flex items-center justify-between gap-4">
          <Link href="/" className="flex items-center gap-2 shrink-0">
            <Logo />
          </Link>
          <div className="hidden md:flex items-center gap-2 flex-1 max-w-xl">
            <div className="flex items-center gap-2 rounded-xl bg-overlay/5 ring-1 ring-overlay/10 px-3 py-2 flex-1">
              <Search size={14} className="text-muted" />
              <input placeholder="Cherche un créateur, une discipline…" className="bg-transparent outline-none flex-1 text-sm" />
            </div>
          </div>
          <nav className="hidden md:flex items-center gap-1 overflow-x-auto scrollbar-thin">
            {NAV.map(({ href, label, icon: Icon }) => {
              const active = pathname === href || (href !== "/" && pathname.startsWith(href));
              return (
                <Link key={href} href={href} className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm font-medium whitespace-nowrap transition ${active ? "bg-rose/15 text-rose ring-1 ring-rose/30" : "text-muted hover:text-foreground hover:bg-overlay/5"}`}>
                  <Icon size={15} />
                  {label}
                </Link>
              );
            })}
          </nav>
          <Link href="/become-creator" className="hidden sm:inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-bold rose-gradient text-black shadow-glow">
            Devenir créateur
          </Link>
        </div>
        <nav className="md:hidden flex items-center gap-1 overflow-x-auto scrollbar-thin pb-2 -mx-1 px-1">
          {NAV.map(({ href, label, icon: Icon }) => {
            const active = pathname === href || (href !== "/" && pathname.startsWith(href));
            return (
              <Link key={href} href={href} className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium whitespace-nowrap transition ${active ? "bg-rose/15 text-rose ring-1 ring-rose/30" : "text-muted hover:text-foreground"}`}>
                <Icon size={14} />
                {label}
              </Link>
            );
          })}
        </nav>
      </div>
    </header>
  );
}
