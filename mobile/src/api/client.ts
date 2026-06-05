/** Thin typed client for the Calo backend `/app/*` JSON API. */
import Constants from 'expo-constants';

const BASE_URL: string =
  (Constants.expoConfig?.extra as any)?.apiBaseUrl ??
  'https://coachwarrior-production.up.railway.app';

export type PublicUser = {
  id: string;
  name?: string;
  sex?: string;
  age?: number;
  height_cm?: number;
  weight_kg?: number;
  target_weight_kg?: number;
  goal?: string;
  activity_level?: string;
  daily_calories?: number;
  daily_protein_g?: number;
  daily_carbs_g?: number;
  daily_fat_g?: number;
  onboarding_complete?: boolean;
};

export type ChatMedia = { url: string; caption: string };
export type ChatResponse = { reply: string; tool_calls: string[]; media: ChatMedia[] };
export type Progress = {
  weights: { kg: number; at: string }[];
  today: { consumed_kcal: number; target_kcal: number; remaining_kcal: number | null };
  meals_today: number;
};

let authToken: string | null = null;
let onUnauthorized: (() => void) | null = null;

export function setToken(token: string | null) {
  authToken = token;
}

/** Wire a callback fired on 401 so the AuthProvider can auto-sign-out. */
export function setUnauthorizedHandler(cb: (() => void) | null) {
  onUnauthorized = cb;
}

async function request<T>(path: string, opts: RequestInit = {}): Promise<T> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(opts.headers as Record<string, string>),
  };
  if (authToken) headers['Authorization'] = `Bearer ${authToken}`;

  let res: Response;
  try {
    res = await fetch(`${BASE_URL}${path}`, { ...opts, headers });
  } catch {
    throw new ApiError('Connexion impossible. Vérifie ton réseau.', 0);
  }
  if (!res.ok) {
    let detail = `HTTP ${res.status}`;
    try {
      const body = await res.json();
      detail = body?.detail ?? detail;
    } catch {}
    if (res.status === 401 && onUnauthorized) onUnauthorized();
    throw new ApiError(detail, res.status);
  }
  return (await res.json()) as T;
}

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

export const api = {
  authStart: (phone: string) =>
    request<{ sent: boolean; dev_hint: string | null }>('/app/auth/start', {
      method: 'POST',
      body: JSON.stringify({ phone }),
    }),

  authVerify: (phone: string, code: string) =>
    request<{ token: string; user: PublicUser }>('/app/auth/verify', {
      method: 'POST',
      body: JSON.stringify({ phone, code }),
    }),

  me: () => request<{ user: PublicUser }>('/app/me'),
  profile: () => request<{ user: PublicUser }>('/app/profile'),
  progress: () => request<Progress>('/app/progress'),

  chat: (text: string, imageBase64?: string) =>
    request<ChatResponse>('/app/chat', {
      method: 'POST',
      body: JSON.stringify({
        text,
        image_base64: imageBase64 ?? null,
        image_media_type: 'image/jpeg',
      }),
    }),
};

export { BASE_URL };
