import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Trading 212 Dark Theme
        't212': {
          // Primary - Verde vibrante
          'primary': '#00C853',
          'primary-dark': '#00AA44',
          'primary-light': '#4DFF8A',

          // Secondary - Laranja/Amarelo
          'secondary': '#FF9800',
          'secondary-dark': '#E68900',
          'secondary-light': '#FFB74D',

          // Background - Muito escuro
          'bg-dark': '#0A0E27',
          'bg-darker': '#050811',
          'bg-card': '#1A1F3A',
          'bg-hover': '#242D4A',

          // Text
          'text-primary': '#E0E0E0',
          'text-secondary': '#A0A0A0',
          'text-muted': '#7A7A7A',

          // Status
          'success': '#4CAF50',
          'warning': '#FF9800',
          'error': '#F44336',
          'info': '#2196F3',

          // Gradient backgrounds
          'gradient-start': '#0A0E27',
          'gradient-end': '#1A1F3A',
        }
      },
      backgroundColor: {
        't212-dark': '#0A0E27',
        't212-card': '#1A1F3A',
        't212-hover': '#242D4A',
        't212-primary': '#00C853',
        't212-secondary': '#FF9800',
        't212-success': '#4CAF50',
        't212-error': '#F44336',
        't212-warning': '#FF9800',
        't212-info': '#2196F3',
      },
      textColor: {
        't212-primary': '#E0E0E0',
        't212-secondary': '#A0A0A0',
        't212-muted': '#7A7A7A',
        't212-success': '#4CAF50',
        't212-error': '#F44336',
        't212-warning': '#FF9800',
        't212-info': '#2196F3',
      },
      borderColor: {
        't212-border': '#2A3050',
        't212-primary': '#00C853',
        't212-secondary': '#FF9800',
        't212-success': '#4CAF50',
        't212-error': '#F44336',
        't212-warning': '#FF9800',
        't212-info': '#2196F3',
      },
      placeholderColor: {
        't212-muted': '#7A7A7A',
      },
      fontFamily: {
        'sans': ['Inter', 'Roboto', 'system-ui', 'sans-serif'],
      },
      fontSize: {
        'xs': ['0.75rem', { lineHeight: '1rem' }],
        'sm': ['0.875rem', { lineHeight: '1.25rem' }],
        'base': ['1rem', { lineHeight: '1.5rem' }],
        'lg': ['1.125rem', { lineHeight: '1.75rem' }],
        'xl': ['1.25rem', { lineHeight: '1.75rem' }],
        '2xl': ['1.5rem', { lineHeight: '2rem' }],
        '3xl': ['1.875rem', { lineHeight: '2.25rem' }],
      },
      spacing: {
        '0': '0px',
        '1': '0.25rem',
        '2': '0.5rem',
        '3': '0.75rem',
        '4': '1rem',
        '6': '1.5rem',
        '8': '2rem',
        '12': '3rem',
        '16': '4rem',
        '20': '5rem',
        '24': '6rem',
        '32': '8rem',
      },
      borderRadius: {
        'none': '0px',
        'sm': '0.375rem',
        'base': '0.5rem',
        'md': '0.75rem',
        'lg': '1rem',
        'xl': '1.5rem',
        'full': '9999px',
      },
      boxShadow: {
        'sm': '0 1px 2px 0 rgba(0, 0, 0, 0.3)',
        'base': '0 1px 3px 0 rgba(0, 0, 0, 0.4), 0 1px 2px 0 rgba(0, 0, 0, 0.2)',
        'md': '0 4px 6px 0 rgba(0, 0, 0, 0.4), 0 2px 4px 0 rgba(0, 0, 0, 0.2)',
        'lg': '0 10px 15px 0 rgba(0, 0, 0, 0.4), 0 4px 6px 0 rgba(0, 0, 0, 0.2)',
        'xl': '0 20px 25px 0 rgba(0, 0, 0, 0.5), 0 10px 10px 0 rgba(0, 0, 0, 0.2)',
        'glow': '0 0 20px rgba(0, 200, 83, 0.3)',
        'glow-hover': '0 0 30px rgba(0, 200, 83, 0.5)',
      },
      opacity: {
        '0': '0',
        '5': '0.05',
        '10': '0.1',
        '20': '0.2',
        '30': '0.3',
        '40': '0.4',
        '50': '0.5',
        '60': '0.6',
        '70': '0.7',
        '80': '0.8',
        '90': '0.9',
        '95': '0.95',
        '100': '1',
      },
      animation: {
        'pulse': 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'fade-in': 'fadeIn 0.3s ease-in-out',
        'slide-in': 'slideIn 0.3s ease-in-out',
        'spin': 'spin 1s linear infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideIn: {
          '0%': { transform: 'translateY(-10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        pulse: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.5' },
        },
      },
      transitionDuration: {
        '150': '150ms',
        '200': '200ms',
        '300': '300ms',
        '500': '500ms',
      },
    },
  },
  plugins: [],
}

export default config
