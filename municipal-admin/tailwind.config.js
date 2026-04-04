/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        primary:        '#B85C2E',
        'primary-dark': '#9C4C24',
        'primary-light':'#FFF3EB',
        'page-bg':      '#F7F6E8',
        'card-bg':      '#FFFFFF',
        'muted-bg':     '#FDFCF0',
        'warm-border':  '#EDE8DC',
      },
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
