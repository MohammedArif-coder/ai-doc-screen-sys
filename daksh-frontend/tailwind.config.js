/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        bg: {
          DEFAULT: '#F5F7FA',
          dark: '#0B1220'
        },
        surface: {
          DEFAULT: '#FFFFFF',
          dark: '#121B2E',
          raised: '#FFFFFF',
          'raised-dark': '#16223A'
        },
        border: {
          DEFAULT: '#E3E7EE',
          dark: '#233150'
        },
        ink: {
          DEFAULT: '#101828',
          dark: '#E7ECF5'
        },
        muted: {
          DEFAULT: '#5B6472',
          dark: '#8B96AC'
        },
        brand: {
          50: '#EEF3FB',
          100: '#D6E2F3',
          300: '#7EA0D6',
          500: '#2F5DA8',
          700: '#1B3B72',
          900: '#0F2547'
        },
        engine: {
          DEFAULT: '#0E7C7B',
          light: '#E4F4F3',
          dark: '#0A5F5E'
        },
        success: { DEFAULT: '#157F3C', light: '#E6F5EA' },
        warning: { DEFAULT: '#B45309', light: '#FBF0DF' },
        danger: { DEFAULT: '#B3261E', light: '#FBE9E8' },
        info: { DEFAULT: '#1D4ED8', light: '#E8EEFC' }
      },
      fontFamily: {
        sans: ['"IBM Plex Sans"', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        mono: ['"IBM Plex Mono"', 'ui-monospace', 'SFMono-Regular', 'monospace']
      },
      boxShadow: {
        card: '0 1px 2px rgba(16,24,40,0.04), 0 1px 3px rgba(16,24,40,0.06)',
        raised: '0 4px 12px rgba(16,24,40,0.08), 0 1px 2px rgba(16,24,40,0.04)',
        focus: '0 0 0 3px rgba(47,93,168,0.35)'
      },
      borderRadius: {
        sm: '6px',
        md: '10px',
        lg: '14px',
        xl: '18px'
      },
      keyframes: {
        pulseDot: {
          '0%, 100%': { opacity: 1 },
          '50%': { opacity: 0.35 }
        },
        riseIn: {
          '0%': { opacity: 0, transform: 'translateY(6px)' },
          '100%': { opacity: 1, transform: 'translateY(0)' }
        }
      },
      animation: {
        pulseDot: 'pulseDot 1.6s ease-in-out infinite',
        riseIn: 'riseIn 0.35s ease-out'
      }
    }
  },
  plugins: []
}
