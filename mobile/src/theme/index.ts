/** Calo design system — refonte 2026, vibe American startup tech.
 *
 * Direction : noir profond, surface en niveaux de gris, UN accent vibrant
 * (coral), un secondaire (mint pour le positif), typographie ultra-display.
 * Inspirations : Linear, Vercel, Whoop, Cal AI, Stripe.
 */

export const colors = {
  // Surfaces (true black with a hair of warmth)
  bg: '#08090C',
  bgElevated: '#101116',
  card: '#15171D',
  cardHi: '#1B1E26',

  // Accent (the Calo signature)
  accent: '#FF6B35', // vibrant coral
  accentSoft: '#FFB694',
  accentDeep: '#E2511A',

  // Secondary (positives, progress)
  mint: '#10D9A0',
  violet: '#A78BFA',

  // Status
  success: '#10D9A0',
  warning: '#F59E0B',
  danger: '#FF5470',

  // Text
  text: '#FAFAFA',
  textMuted: '#A1A1AA',
  textDim: '#52525B',

  // Borders & overlays — hairline glass
  border: 'rgba(255,255,255,0.07)',
  borderStrong: 'rgba(255,255,255,0.12)',
  glassOverlay: 'rgba(255,255,255,0.04)',

  // Chat bubbles
  bubbleUser: '#FF6B35',
  bubbleCalo: '#15171D',

  // Compatibility aliases (some legacy refs still use these names)
  primary: '#FF6B35',
  primaryDeep: '#E2511A',

  white: '#FFFFFF',
  black: '#000000',
} as const;

export const spacing = {
  xs: 4,
  sm: 8,
  md: 14,
  lg: 20,
  xl: 28,
  xxl: 40,
  hero: 56,
} as const;

export const radius = {
  sm: 10,
  md: 16,
  lg: 22,
  xl: 30,
  pill: 999,
} as const;

export const font = {
  hero: { fontSize: 48, fontWeight: '900' as const, color: colors.text, letterSpacing: -2 },
  display: { fontSize: 34, fontWeight: '900' as const, color: colors.text, letterSpacing: -1 },
  h1: { fontSize: 28, fontWeight: '800' as const, color: colors.text, letterSpacing: -0.5 },
  h2: { fontSize: 22, fontWeight: '700' as const, color: colors.text },
  h3: { fontSize: 17, fontWeight: '700' as const, color: colors.text },
  body: { fontSize: 16, fontWeight: '500' as const, color: colors.text, lineHeight: 23 },
  bodyStrong: { fontSize: 16, fontWeight: '700' as const, color: colors.text },
  small: { fontSize: 13, fontWeight: '500' as const, color: colors.textMuted, lineHeight: 19 },
  micro: { fontSize: 11, fontWeight: '800' as const, color: colors.textMuted, letterSpacing: 1.4, textTransform: 'uppercase' as const },
} as const;

export const shadow = {
  soft: {
    shadowColor: '#000',
    shadowOpacity: 0.5,
    shadowRadius: 18,
    shadowOffset: { width: 0, height: 8 },
    elevation: 8,
  },
  glow: {
    shadowColor: colors.accent,
    shadowOpacity: 0.45,
    shadowRadius: 24,
    shadowOffset: { width: 0, height: 8 },
    elevation: 10,
  },
  glowMint: {
    shadowColor: colors.mint,
    shadowOpacity: 0.35,
    shadowRadius: 20,
    shadowOffset: { width: 0, height: 6 },
    elevation: 8,
  },
} as const;
