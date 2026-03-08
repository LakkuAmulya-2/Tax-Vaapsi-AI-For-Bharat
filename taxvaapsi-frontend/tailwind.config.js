/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#fff1f3',
          100: '#ffe4e8',
          200: '#fecdd6',
          300: '#fda4b4',
          400: '#fb7a96',
          500: '#f43f6e',
          600: '#e11d48',
          700: '#be123c',
          800: '#9f1239',
          900: '#881337',
        },
        slate: {
          850: '#172033',
          950: '#0a0f1e',
        }
      },
      fontFamily: {
        sans: ['var(--font-sans)', 'system-ui'],
        display: ['var(--font-display)', 'system-ui'],
        mono: ['var(--font-mono)', 'monospace'],
      },
      animation: {
        'count-up': 'countUp 2s ease-out forwards',
        'pulse-slow': 'pulse 3s infinite',
        'slide-in': 'slideIn 0.5s ease-out',
        'fade-in': 'fadeIn 0.6s ease-out',
        'bounce-slow': 'bounce 2s infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
        'shimmer': 'shimmer 2s linear infinite',
      },
      keyframes: {
        countUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideIn: {
          '0%': { transform: 'translateX(-100%)', opacity: '0' },
          '100%': { transform: 'translateX(0)', opacity: '1' },
        },
        fadeIn: {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        glow: {
          '0%': { boxShadow: '0 0 5px #e11d48, 0 0 10px #e11d48' },
          '100%': { boxShadow: '0 0 20px #e11d48, 0 0 40px #e11d4840' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-1000px 0' },
          '100%': { backgroundPosition: '1000px 0' },
        }
      },
      backgroundImage: {
        'grid-pattern': "url(\"data:image/svg+xml,%3Csvg width='40' height='40' viewBox='0 0 40 40' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.03'%3E%3Cpath d='M0 40L40 0H20L0 20M40 40V20L20 40'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E\")",
      }
    },
  },
  plugins: [],
}
