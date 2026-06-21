import { MvpTopBar, MvpBottomNav, MvpFooter } from "./_components";

export default function MvpLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-black text-white antialiased">
      <MvpTopBar />
      <main className="pb-24 sm:pb-0">
        {children}
      </main>
      <MvpFooter />
      <MvpBottomNav />
    </div>
  );
}
