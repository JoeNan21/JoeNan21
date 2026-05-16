/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        navy: {
          DEFAULT: '#0D1B2A',
          900: '#0D1B2A',
          800: '#142A3E',
          700: '#1C3A55',
        },
        ochre: {
          DEFAULT: '#C9882E',
          600: '#B0741F',
          400: '#DCA757',
        },
        sand: {
          DEFAULT: '#F7F3EE',
          dark: '#EBE3D7',
        },
        terracotta: {
          DEFAULT: '#A0522D',
        },
        ink: '#1A1A1A',
      },
      fontFamily: {
        display: ['"Playfair Display"', 'Georgia', 'serif'],
        serif: ['"Source Serif Pro"', 'Georgia', 'serif'],
        sans: ['"DM Sans"', 'system-ui', 'sans-serif'],
      },
      maxWidth: {
        prose: '68ch',
      },
      keyframes: {
        fadeUp: {
          '0%': { opacity: '0', transform: 'translateY(8px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
      },
      animation: {
        fadeUp: 'fadeUp 0.5s ease-out forwards',
        fadeIn: 'fadeIn 0.4s ease-out forwards',
      },
    },
  },
  plugins: [],
};
