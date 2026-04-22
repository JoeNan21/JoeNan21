/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        base: '#0a0a0a',
        surface: '#111111',
        elevated: '#1a1a1a',
        line: '#2a2a2a',
        gold: '#c9a84c',
        'gold-dim': '#8c7434',
        teal: '#2a6b6b',
        'teal-dim': '#1c4a4a',
        ink: '#f0ede8',
        muted: '#9a9590',
        ok: '#22c55e',
        warn: '#f59e0b',
        bad: '#ef4444',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      borderRadius: {
        DEFAULT: '8px',
      },
    },
  },
  plugins: [],
}
