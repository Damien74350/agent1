import { NextResponse } from 'next/server';
import Stripe from 'stripe';
import { db } from '@/lib/db';

const stripeKey = process.env.STRIPE_SECRET_KEY;

export async function POST(req: Request) {
  const { handle } = await req.json();
  const creator = db.get(handle);
  if (!creator) return NextResponse.json({ error: 'créateur introuvable' }, { status: 404 });

  // Conference-demo fallback when no Stripe key is configured:
  // skip the real checkout, just return a success URL that auto-unblurs.
  if (!stripeKey) {
    const origin = new URL(req.url).origin;
    return NextResponse.json({
      url: `${origin}/@${creator.handle}?unblur=demo`,
      mode: 'demo',
    });
  }

  const stripe = new Stripe(stripeKey);
  const origin = new URL(req.url).origin;
  const session = await stripe.checkout.sessions.create({
    mode: 'subscription',
    line_items: [
      {
        price_data: {
          currency: creator.currency.toLowerCase(),
          recurring: { interval: 'month' },
          product_data: {
            name: `Abonnement à @${creator.handle}`,
            description: `Accès au feed complet de ${creator.displayName}`,
          },
          unit_amount: creator.priceCents,
        },
        quantity: 1,
      },
    ],
    success_url: `${origin}/@${creator.handle}?unblur=success`,
    cancel_url: `${origin}/@${creator.handle}`,
    metadata: { handle: creator.handle },
  });

  return NextResponse.json({ url: session.url, mode: 'stripe' });
}
