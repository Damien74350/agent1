/** In-memory creator store. Replace with Postgres/Supabase before scale. */

export type Creator = {
  handle: string;
  displayName: string;
  bio: string;
  profilePic: string;
  posts: { id: string; url: string; caption?: string }[];
  priceCents: number;
  currency: 'EUR' | 'USD' | 'CHF';
  perks: string[];
  createdAt: number;
};

declare global {
  // eslint-disable-next-line no-var
  var __unblurStore: Map<string, Creator> | undefined;
}

function getStore(): Map<string, Creator> {
  if (!globalThis.__unblurStore) {
    globalThis.__unblurStore = new Map();
  }
  return globalThis.__unblurStore;
}

export const db = {
  get(handle: string): Creator | undefined {
    return getStore().get(handle.toLowerCase());
  },
  set(c: Creator): Creator {
    getStore().set(c.handle.toLowerCase(), c);
    return c;
  },
  all(): Creator[] {
    return Array.from(getStore().values());
  },
};
