/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#0F172A',
        surface: '#1E293B',
        'surface-raised': '#334155',
        border: '#475569',
        primary: '#2563EB',
        'primary-hover': '#1D4ED8',
        secondary: '#7C3AED',
        'risk-safe': '#22C55E',
        'risk-low': '#84CC16',
        'risk-moderate': '#EAB308',
        'risk-high': '#F97316',
        'risk-critical': '#EF4444',
      },
    },
  },
  plugins: [],
}
