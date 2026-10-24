/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
  theme: {
    extend: {
      colors: {
        paper: '#ffffff',
        slateink: '#1e293b',
        teal: {
          DEFAULT: '#0f766e',
          dark: '#115e59',
          bg: '#ccfbf1',
        },
      },
    },
  },
  plugins: [],
};
