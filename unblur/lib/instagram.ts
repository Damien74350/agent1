/** Instagram fetcher.
 *
 * Two modes:
 * - Production : pulls 9 last public posts via Apify's Instagram Scraper actor.
 *   Set APIFY_TOKEN in env vars to enable.
 * - Demo / fallback : returns a curated set of placeholder photos so the conf
 *   demo NEVER blocks on rate-limits or missing API tokens.
 */

export type Post = { id: string; url: string; caption?: string };
export type Profile = {
  handle: string;
  displayName: string;
  bio: string;
  profilePic: string;
  posts: Post[];
};

const PLACEHOLDER_POSTS: Post[] = [
  'photo-1539109136881-3be0616acf4b',
  'photo-1503342217505-b0a15ec3261c',
  'photo-1517694712202-14dd9538aa97',
  'photo-1517248135467-4c7edcad34c4',
  'photo-1483181957632-8bda974cbc91',
  'photo-1517423568366-8b83523034fd',
  'photo-1497515114629-f71d768fd07c',
  'photo-1493815793585-d94ccbc86df8',
  'photo-1452587925148-ce544e77e70d',
].map((id) => ({
  id,
  url: `https://images.unsplash.com/${id}?w=900&h=900&fit=crop&q=80`,
}));

const PLACEHOLDER_PROFILE_PIC =
  'https://images.unsplash.com/photo-1502685104226-ee32379fefbe?w=400&h=400&fit=crop&q=80';

export async function fetchProfile(handle: string): Promise<Profile> {
  const cleanHandle = handle.replace(/^@/, '').trim().toLowerCase();
  const token = process.env.APIFY_TOKEN;

  if (token) {
    try {
      return await fetchViaApify(cleanHandle, token);
    } catch (e) {
      console.warn('[unblur] Apify fetch failed, falling back to demo data:', e);
    }
  }

  // Demo fallback — always returns something pretty.
  return {
    handle: cleanHandle,
    displayName: prettify(cleanHandle),
    bio: 'Créateur · contenu exclusif',
    profilePic: PLACEHOLDER_PROFILE_PIC,
    posts: PLACEHOLDER_POSTS,
  };
}

async function fetchViaApify(handle: string, token: string): Promise<Profile> {
  // Apify "Instagram Scraper" actor — runs a one-shot, returns dataset items.
  const res = await fetch(
    `https://api.apify.com/v2/acts/apify~instagram-scraper/run-sync-get-dataset-items?token=${token}`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        usernames: [handle],
        resultsLimit: 9,
        addParentData: true,
      }),
    },
  );
  if (!res.ok) {
    throw new Error(`Apify ${res.status}`);
  }
  const items: any[] = await res.json();
  const profile = items[0]?.parentData ?? items[0] ?? {};
  const posts: Post[] = items
    .slice(0, 9)
    .filter((p) => p?.displayUrl || p?.thumbnailSrc)
    .map((p, i) => ({
      id: p?.id ?? String(i),
      url: p?.displayUrl ?? p?.thumbnailSrc,
      caption: p?.caption,
    }));
  return {
    handle,
    displayName: profile.fullName || prettify(handle),
    bio: profile.biography || '',
    profilePic: profile.profilePicUrlHD || profile.profilePicUrl || PLACEHOLDER_PROFILE_PIC,
    posts: posts.length > 0 ? posts : PLACEHOLDER_POSTS,
  };
}

function prettify(handle: string): string {
  return handle
    .replace(/[._-]+/g, ' ')
    .split(' ')
    .filter(Boolean)
    .map((w) => w[0].toUpperCase() + w.slice(1))
    .join(' ');
}
