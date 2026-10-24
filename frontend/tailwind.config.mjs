/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
  theme: {
    extend: {
      colors: {
        "paper": "#ffffff",
        "slateink": "#17252e",
        "teal": {
                "DEFAULT": "#0d7d72",
                "dark": "#0b5f57",
                "bg": "#d7f5ef"
        }
},
      fontFamily: {
        "display": [
                "'Sora'",
                "system-ui",
                "sans-serif"
        ],
        "body": [
                "'Inter'",
                "system-ui",
                "sans-serif"
        ],
        "mono": [
                "'JetBrains Mono'",
                "ui-monospace",
                "monospace"
        ]
},
    },
  },
  plugins: [],
};
