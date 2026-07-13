import { NextResponse } from 'next/server';
import { db } from '@/lib/db';

export async function POST(req: Request) {
  const body = await req.json();
  const { handle, priceCents, bio, displayName, perks, currency } = body;
  if (!handle) return NextResponse.json({ error: 'handle requis' }, { status: 400 });
  const c = db.get(handle);
  if (!c) return NextResponse.json({ error: 'créateur introuvable' }, { status: 404 });
  if (typeof priceCents === 'number') c.priceCents = priceCents;
  if (typeof bio === 'string') c.bio = bio;
  if (typeof displayName === 'string') c.displayName = displayName;
  if (Array.isArray(perks)) c.perks = perks;
  if (currency === 'EUR' || currency === 'USD' || currency === 'CHF') c.currency = currency;
  db.set(c);
  return NextResponse.json({ creator: c });
}
