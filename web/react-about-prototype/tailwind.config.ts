import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        background: "#050914",
        foreground: "#eef5ff",
        muted: "#a7b4cc",
        panel: "#0a111d",
        border: "rgba(145, 170, 208, 0.16)",
      },
      boxShadow: {
        ai: "0 18px 56px rgba(0, 0, 0, 0.38)",
        glow: "0 0 42px rgba(102, 88, 255, 0.2)",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        display: ["Sora", "Inter", "system-ui", "sans-serif"],
      },
      backgroundImage: {
        "ai-gradient": "linear-gradient(135deg, #8a5bff 0%, #469bff 52%, #34d7ff 100%)",
      },
    },
  },
  plugins: [],
} satisfies Config;
