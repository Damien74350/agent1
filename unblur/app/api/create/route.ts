import { NextResponse } from 'next/server';
import { fetchProfile } from '@/lib/instagram';
import { db } from '@/lib/db';

export async function POST(req: Request) {
  try {
    const { handle } = await req.json();
    if (!handle || typeof handle !== 'string') {
      return NextResponse.json({ error: 'handle requis' }, { status: 400 });
    }
    const cleaned = handle.replace(/^@/, '').trim().toLowerCase();
    const existing = db.get(cleaned);
    if (existing) {
      return NextResponse.json({ creator: existing, existed: true });
    }
    const profile = await fetchProfile(cleaned);
    const creator = db.set({
      handle: profile.handle,
      displayName: profile.displayName,
      bio: profile.bio || 'Créateur unblur',
      profilePic: profile.profilePic,
      posts: profile.posts,
      priceCents: 999,
      currency: 'EUR',
      perks: [
        'Accès au feed complet (non flouté)',
        'Nouveaux posts en exclu',
        'Tu soutiens directement le créateur',
      ],
      createdAt: Date.now(),
    });
    return NextResponse.json({ creator, existed: false });
  } catch (e: any) {
    return NextResponse.json(
      { error: e?.message || 'Création impossible' },
      { status: 500 },
    );
  }
}
