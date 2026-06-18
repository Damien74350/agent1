import type { Config } from 'tailwindcss';

const config: Config = {
  content: ['./app/**/*.{ts,tsx}', './components/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        bg: '#08090C',
        surface: '#15171D',
        surfaceHi: '#1B1E26',
        accent: '#FF6B35',
        accentSoft: '#FFB694',
        mint: '#10D9A0',
        violet: '#A78BFA',
        muted: '#A1A1AA',
        dim: '#52525B',
      },
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui'],
      },
      animation: {
        'aurora-1': 'aurora1 18s ease-in-out infinite',
        'aurora-2': 'aurora2 22s ease-in-out infinite',
        'fade-in-up': 'fadeInUp 0.6s ease-out',
      },
      keyframes: {
        aurora1: {
          '0%, 100%': { transform: 'translate(-10%, -10%) scale(1)' },
          '50%': { transform: 'translate(10%, 10%) scale(1.1)' },
        },
        aurora2: {
          '0%, 100%': { transform: 'translate(20%, 10%) scale(1)' },
          '50%': { transform: 'translate(-10%, -10%) scale(1.15)' },
        },
        fadeInUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
    },
  },
  plugins: [],
};

export default config;
