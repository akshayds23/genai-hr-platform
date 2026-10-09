module.exports = {
  content: [
    './public/index.html',
    './src/**/*.{vue,js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      boxShadow: {
        card: '0 15px 40px -15px rgba(15, 23, 42, 0.25)',
      },
      colors: {
        muted: {
          DEFAULT: '#e2e8f0',
          foreground: '#64748b',
        },
        foreground: '#0f172a',
      },
    },
  },
  plugins: [
    require('@tailwindcss/line-clamp'),
  ],
};
