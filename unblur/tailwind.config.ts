import type { Config } from "tailwindcss";

export default {
  content: ["./app/**/*.{js,ts,jsx,tsx,mdx}", "./components/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        // Theme-driven (resolved via CSS vars)
        foreground: "rgb(var(--c-fg) / <alpha-value>)",
        overlay: "rgb(var(--c-overlay) / <alpha-value>)",
        surface: "rgb(var(--c-surface) / <alpha-value>)",
        border: "rgb(var(--c-border) / <alpha-value>)",
        muted: "rgb(var(--c-muted) / <alpha-value>)",
        rose: "rgb(var(--c-rose) / <alpha-value>)",
        sun: "rgb(var(--c-sun) / <alpha-value>)",
        sky: "rgb(var(--c-sky) / <alpha-value>)",
        violet: "rgb(var(--c-violet) / <alpha-value>)",
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
