/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        display: ['"Playfair Display"', 'serif'],
        body: ['"DM Sans"', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
      colors: {
        cream: { 50: '#FDFAF4', 100: '#F9F2E3', 200: '#F2E4C4' },
        forest: { 400: '#5C8C5A', 500: '#3D6B3A', 600: '#2A4F28', 700: '#1A3318' },
        terracotta: { 400: '#E07B54', 500: '#C8603A', 600: '#A84A28' },
        charcoal: { 700: '#2C2C2C', 800: '#1C1C1C', 900: '#0F0F0F' },
      },
      animation: {
        'fade-up': 'fadeUp 0.6s ease forwards',
        'fade-in': 'fadeIn 0.4s ease forwards',
      },
      keyframes: {
        fadeUp: { from: { opacity: '0', transform: 'translateY(20px)' }, to: { opacity: '1', transform: 'translateY(0)' } },
        fadeIn: { from: { opacity: '0' }, to: { opacity: '1' } },
      },
    },
  },
  plugins: [],
}
