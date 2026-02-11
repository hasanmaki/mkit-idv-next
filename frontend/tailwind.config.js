/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./app.js",
    "./src/**/*.{html,js}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#6366f1', // Indigo 500
        secondary: '#a855f7', // Purple 500
        dark: '#0f172a', // Slate 900
        darker: '#020617', // Slate 950
        surface: '#1e293b', // Slate 800
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-out',
        'slide-up': 'slideUp 0.5s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
      }
    },
  },
  plugins: [],
}
