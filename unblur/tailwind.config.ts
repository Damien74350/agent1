import type { Config } from "tailwindcss";
import defaultColors from "tailwindcss/colors";

export default {
  content: ["./app/**/*.{js,ts,jsx,tsx,mdx}", "./components/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        // Full Tailwind palettes (for /mvp and any standard usage)
        rose: defaultColors.rose,
        sky: defaultColors.sky,
        violet: defaultColors.violet,
        emerald: defaultColors.emerald,
        amber: defaultColors.amber,
        zinc: defaultColors.zinc,
        fuchsia: defaultColors.fuchsia,
        indigo: defaultColors.indigo,
        purple: defaultColors.purple,
        lime: defaultColors.lime,
        teal: defaultColors.teal,
        cyan: defaultColors.cyan,
        orange: defaultColors.orange,
        red: defaultColors.red,
        pink: defaultColors.pink,
        // Theme-driven (resolved via CSS vars) — used by existing pages
        foreground: "rgb(var(--c-fg) / <alpha-value>)",
        overlay: "rgb(var(--c-overlay) / <alpha-value>)",
        surface: "rgb(var(--c-surface) / <alpha-value>)",
        border: "rgb(var(--c-border) / <alpha-value>)",
        muted: "rgb(var(--c-muted) / <alpha-value>)",
        sun: "rgb(var(--c-sun) / <alpha-value>)",
        success: "rgb(var(--c-success) / <alpha-value>)",
        danger: "rgb(var(--c-danger) / <alpha-value>)",
        // Convenience aliases used in existing code
        ink: "rgb(var(--c-fg) / <alpha-value>)",
        canvas: "var(--bg-base)",
        surfaceAlt: "#f4f4f5",
        warning: "#f59e0b",
      },
      fontFamily: {
        sans: ["-apple-system", "BlinkMacSystemFont", "ui-sans-serif", "system-ui", "Segoe UI", "Inter", "sans-serif"],
        display: ["-apple-system", "BlinkMacSystemFont", "ui-sans-serif", "system-ui", "Inter", "sans-serif"],
      },
      letterSpacing: {
        tighter: "-0.04em",
        tightest: "-0.06em",
      },
    },
  },
  plugins: [],
} satisfies Config;
