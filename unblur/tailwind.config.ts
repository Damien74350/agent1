import type { Config } from "tailwindcss";

export default {
  content: ["./app/**/*.{js,ts,jsx,tsx,mdx}", "./components/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        ink: "#0a0a0d",
        canvas: "#0f0f14",
        surface: "#16161d",
        surfaceAlt: "#1d1d26",
        border: "#2a2a36",
        // brand
        rose: "#ff2e7e",   // unblur signature
        sun: "#ffb347",
        sky: "#5eead4",
        violet: "#a78bfa",
        success: "#22c55e",
        warning: "#f59e0b",
        danger: "#ef4444",
        muted: "#8b8d97",
      },
      fontFamily: {
        sans: ["ui-sans-serif", "system-ui", "-apple-system", "Segoe UI", "Roboto", "Inter", "sans-serif"],
        display: ["ui-sans-serif", "system-ui", "Inter", "sans-serif"],
      },
      boxShadow: {
        glow: "0 10px 50px rgba(255, 46, 126, 0.30)",
        sun: "0 10px 50px rgba(255, 179, 71, 0.25)",
      },
    },
  },
  plugins: [],
} satisfies Config;
