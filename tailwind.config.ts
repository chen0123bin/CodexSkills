import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#0d1017",
        shell: "#131825",
        mist: "#8d98b3",
        line: "rgba(173, 186, 214, 0.14)",
        glow: "#9ae6b4",
        ember: "#f0b56f"
      },
      boxShadow: {
        panel: "0 24px 60px rgba(5, 10, 22, 0.28)"
      },
      fontFamily: {
        sans: ["Aptos", "\"Segoe UI Variable\"", "\"Segoe UI\"", "ui-sans-serif", "system-ui", "sans-serif"],
        mono: ["Consolas", "\"IBM Plex Mono\"", "\"SFMono-Regular\"", "ui-monospace", "monospace"]
      },
      keyframes: {
        rise: {
          "0%": {
            opacity: "0",
            transform: "translateY(16px)"
          },
          "100%": {
            opacity: "1",
            transform: "translateY(0)"
          }
        },
        drift: {
          "0%, 100%": {
            transform: "translateY(0px)"
          },
          "50%": {
            transform: "translateY(-6px)"
          }
        }
      },
      animation: {
        rise: "rise 700ms ease-out both",
        drift: "drift 7s ease-in-out infinite"
      }
    }
  },
  plugins: []
};

export default config;
