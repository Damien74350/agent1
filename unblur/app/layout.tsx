import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'unblur · transforme ton Instagram en revenu en 60 secondes',
  description:
    'unblur duplique ton compte Instagram, floute ton feed et le transforme en page d\'abonnement. Tes followers paient pour voir tes contenus en clair.',
  metadataBase: new URL('https://unblur.app'),
  openGraph: {
    title: 'unblur',
    description: 'Transforme ton Instagram en revenu en 60 secondes.',
    type: 'website',
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fr">
      <head>
        <link
          rel="preconnect"
          href="https://rsms.me/"
        />
        <link rel="stylesheet" href="https://rsms.me/inter/inter.css" />
      </head>
      <body className="min-h-screen bg-bg text-white font-sans antialiased">{children}</body>
    </html>
  );
}
