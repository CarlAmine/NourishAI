/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        forest: {
          50: '#f1f8f2', 100: '#dcf0de', 200: '#bbe0bf', 300: '#8dc994',
          400: '#5cad66', 500: '#3a9145', 600: '#2b7435', 700: '#245d2c',
          800: '#1f4a25', 900: '#1b3d20',
        },
        terracotta: {
          50: '#fdf3ef', 100: '#fae4da', 200: '#f5c9b4', 300: '#eeaa8b',
          400: '#e07b54', 500: '#c8603a', 600: '#a8482a', 700: '#8a3820',
          800: '#6f2c18', 900: '#5a2313',
        },
        cream: {
          50: '#fdfaf4', 100: '#faf5e8', 200: '#f2e4c4', 300: '#e8d09e',
          400: '#d9b878', 500: '#c9a055',
        },
        charcoal: {
          700: '#4a4a4a', 800: '#2c2c2c', 900: '#1a1a1a',
        },
      },
      fontFamily: {
        display: ['Georgia', 'serif'],
        body: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
    },
  },
  plugins: [],
}
