import type { Metadata } from "next";
import "./globals.css";
import { TopNav } from "../components/TopNav";

export const metadata: Metadata = {
  title: "unblur — Le contenu sans le filtre",
  description: "Abonne-toi à un Unblurer. Lives en direct, programmes communauté, échanges privés. 80% revient au créateur.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fr">
      <body className="min-h-screen antialiased">
        <TopNav />
        <main className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 pb-24 pt-6">
          {children}
        </main>
        <footer className="border-t border-border mt-16 py-8 text-center text-xs text-muted">
          <p>© {new Date().getFullYear()} unblur — Sans filtres. Sans pub. Juste l'entraînement.</p>
        </footer>
      </body>
    </html>
  );
}
