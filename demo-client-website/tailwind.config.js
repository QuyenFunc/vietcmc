/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Professional Dark Theme (Zinc/Slate based)
        dark: {
          primary: '#09090b', // Zinc 950
          secondary: '#18181b', // Zinc 900
          tertiary: '#27272a', // Zinc 800
          quaternary: '#3f3f46', // Zinc 700
          border: '#27272a', // Zinc 800
          text: {
            primary: '#f4f4f5', // Zinc 100
            secondary: '#a1a1aa', // Zinc 400
            tertiary: '#71717a', // Zinc 500
            quaternary: '#52525b', // Zinc 600
          }
        },
        // Professional Accent - Indigo/Violet
        accent: {
          primary: '#6366f1', // Indigo 500
          secondary: '#4f46e5', // Indigo 600
          tertiary: '#4338ca', // Indigo 700
          subtle: 'rgba(99, 102, 241, 0.1)',
        },
        // Status colors - Refined
        status: {
          success: '#10b981', // Emerald 500
          warning: '#f59e0b', // Amber 500
          error: '#ef4444', // Red 500
          info: '#3b82f6', // Blue 500
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      boxShadow: {
        'sm': '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
        'md': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
        'lg': '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
        'xl': '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
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
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
      },
    },
  },
  plugins: [],
}

