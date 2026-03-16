/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        forest: {
          50: '#f1f8f2',
          100: '#dcf0de',
          200: '#bbe0bf',
          300: '#8dc994',
          400: '#5cad66',
          500: '#3a9145',
          600: '#2b7435',
          700: '#245d2c',
          800: '#1f4a25',
          900: '#1b3d20',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
};
