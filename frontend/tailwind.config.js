/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        display: ['Space Grotesk', 'Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      colors: {
        background: '#060B14',
        surface: '#0A1628',
        'surface-raised': '#0F1F35',
        'surface-high': '#162840',
        border: '#1A3050',
        'border-bright': '#1E4060',
        primary: '#06B6D4',
        'primary-hover': '#0891B2',
        'primary-dim': '#0E7490',
        'risk-safe': '#22C55E',
        'risk-low': '#84CC16',
        'risk-moderate': '#F59E0B',
        'risk-high': '#F97316',
        'risk-critical': '#EF4444',
        'cyber-cyan': '#06B6D4',
        'cyber-blue': '#3B82F6',
        'cyber-purple': '#8B5CF6',
        'threat-green': '#10B981',
        'threat-amber': '#F59E0B',
        'threat-red': '#EF4444',
      },
      keyframes: {
        'pulse-slow': {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.4' },
        },
        'pulse-ring': {
          '0%': { transform: 'scale(0.8)', opacity: '1' },
          '100%': { transform: 'scale(2.2)', opacity: '0' },
        },
        'scan-line': {
          '0%': { top: '0%' },
          '100%': { top: '100%' },
        },
        'glow-pulse': {
          '0%, 100%': { boxShadow: '0 0 8px rgba(6,182,212,0.3)' },
          '50%': { boxShadow: '0 0 20px rgba(6,182,212,0.7)' },
        },
        'float': {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-6px)' },
        },
        'shimmer': {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
        'fade-in-up': {
          '0%': { opacity: '0', transform: 'translateY(16px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        'counter': {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        'node-drift': {
          '0%, 100%': { transform: 'translate(0, 0)' },
          '33%': { transform: 'translate(4px, -6px)' },
          '66%': { transform: 'translate(-4px, 4px)' },
        },
      },
      animation: {
        'pulse-slow': 'pulse-slow 2.5s ease-in-out infinite',
        'pulse-ring': 'pulse-ring 1.5s cubic-bezier(0.215, 0.61, 0.355, 1) infinite',
        'scan-line': 'scan-line 2s linear infinite',
        'glow-pulse': 'glow-pulse 3s ease-in-out infinite',
        'float': 'float 4s ease-in-out infinite',
        'shimmer': 'shimmer 2.5s linear infinite',
        'fade-in-up': 'fade-in-up 0.5s ease-out forwards',
        'node-drift': 'node-drift 8s ease-in-out infinite',
      },
      backgroundImage: {
        'grid-pattern': "linear-gradient(rgba(6,182,212,0.04) 1px, transparent 1px), linear-gradient(90deg, rgba(6,182,212,0.04) 1px, transparent 1px)",
        'radial-glow': 'radial-gradient(ellipse at center, rgba(6,182,212,0.08) 0%, transparent 70%)',
      },
      backgroundSize: {
        'grid': '40px 40px',
      },
    },
  },
  plugins: [],
}
