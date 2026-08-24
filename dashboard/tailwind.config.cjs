/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx}',
    './components/**/*.{js,ts,jsx,tsx}',
    './pages/**/*.{js,ts,jsx,tsx}'
  ],
  theme: {
    extend: {
      colors: {
        zacma: {
          red: '#C8102E',
          'red-dark': '#A00C24',
          blue: '#0B3D91',
          'blue-dark': '#072B68',
          navy: '#051838',
        },
      },
    },
  },
  plugins: [],
};
