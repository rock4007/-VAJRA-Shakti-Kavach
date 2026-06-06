import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        signal: {
          ink: "#0D1B2A",
          mint: "#6FFFE9",
          amber: "#FFB703",
          cloud: "#E0FBFC"
        }
      }
    }
  },
  plugins: []
};

export default config;
