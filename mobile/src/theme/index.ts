/** Calo brand system — shared across the app. */

export const colors = {
  primary: '#1F4E79', // deep blue
  primaryDark: '#163A5A',
  accent: '#E07B00', // orange
  accentSoft: '#F4A24C',
  success: '#3FA34D',
  danger: '#D9534F',
  bg: '#0E1A26', // dark app background
  bgElevated: '#16273A',
  card: '#1B2E44',
  text: '#F4F7FB',
  textMuted: '#9DB0C4',
  border: '#274058',
  bubbleUser: '#E07B00',
  bubbleCalo: '#1B2E44',
  white: '#FFFFFF',
} as const;

export const spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  xxl: 48,
} as const;

export const radius = {
  sm: 8,
  md: 14,
  lg: 22,
  pill: 999,
} as const;

export const font = {
  h1: { fontSize: 30, fontWeight: '800' as const, color: colors.text },
  h2: { fontSize: 22, fontWeight: '700' as const, color: colors.text },
  h3: { fontSize: 17, fontWeight: '700' as const, color: colors.text },
  body: { fontSize: 16, fontWeight: '400' as const, color: colors.text },
  small: { fontSize: 13, fontWeight: '400' as const, color: colors.textMuted },
} as const;
