/** @type {import('tailwindcss').Config} */
export default {
  content: ["./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}"],
  theme: {
    extend: {
      typography: {
        DEFAULT: {
          css: {
            "code::before": {
              content: '""',
            },
            "code::after": {
              content: '""',
            },
            code: {
              fontWeight: 400,
            },
            img: {
              margin: "0 auto",
              maxWidth: "90%",
            },
          },
        },
      },
      spacing: {
        144: "36rem",
      },
    },
  },
  plugins: [require("@tailwindcss/typography")],
};
