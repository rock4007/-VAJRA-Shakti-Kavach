import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./hooks/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#111111",
        sand: "#f7f2e8",
        ember: "#ef5a29",
        moss: "#6a8c69",
        ocean: "#0f4c5c"
      },
      fontFamily: {
        display: ["Space Grotesk", "sans-serif"],
        body: ["IBM Plex Sans", "sans-serif"],
        mono: ["IBM Plex Mono", "monospace"]
      },
      boxShadow: {
        panel: "0 10px 30px rgba(17, 17, 17, 0.12)"
      }
    }
  },
  plugins: []
};

export default config;
