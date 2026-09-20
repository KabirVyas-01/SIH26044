/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        cream:      '#F6F3ED',
        mutedsage:  '#C2CBD3',
        deepblue:   '#313851',
        deepblue2:  '#232840',
        sage:       '#A3B18A',
        sagedark:   '#748158',
        sagedeep:   '#4B5A3A',
        pcream:     '#F2E8CF',
      },
      fontFamily: {
        display: ['"Fraunces"', 'ui-serif', 'Georgia', 'serif'],
        sans:    ['"Manrope"', 'ui-sans-serif', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
