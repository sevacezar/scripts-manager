/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#0065AA',
          dark: '#004d80',
          light: '#007acc',
        },
      },
    },
  },
  plugins: [],
}

