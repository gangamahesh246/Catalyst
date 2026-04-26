/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        cream: {
          50: "#fbfaf3",
          100: "#f7f5ed",
          200: "#efebd9",
          300: "#e3dfcf",
        },
        olive: {
          50: "#f4f6ec",
          100: "#e6ecd3",
          200: "#cdd9a8",
          300: "#b1c181",
          400: "#92a35e",
          500: "#75884a",
          600: "#5b6c39",
          700: "#475430",
          800: "#3a4427",
          900: "#2c331e",
        },
        ink: {
          900: "#181b14",
          700: "#3a3e34",
          500: "#6b6f60",
          400: "#8b8f80",
        },
      },
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
        display: ["Fraunces", "Georgia", "serif"],
      },
      boxShadow: {
        card: "0 1px 2px rgba(20,25,15,0.04), 0 8px 24px rgba(20,25,15,0.06)",
        cardHover: "0 1px 2px rgba(20,25,15,0.05), 0 16px 36px rgba(20,25,15,0.10)",
      },
      animation: {
        marquee: "marquee 40s linear infinite",
      },
      keyframes: {
        marquee: {
          "0%": { transform: "translateX(0)" },
          "100%": { transform: "translateX(-50%)" },
        },
      },
    },
  },
  plugins: [],
};
