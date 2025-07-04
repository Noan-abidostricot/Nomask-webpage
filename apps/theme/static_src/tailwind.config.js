module.exports = {
  content: [
    './templates/**/*.html',
    './apps/*/templates/**/*.html',
    './theme/**/*.js', // Si tu as des fichiers JS dans l'application theme
  ],
  theme: {
    screens: {
      // Media queries par defaut de tailwind car bug si on met des media queries personalisés
            'sm': '640px',
            'md': '768px',
            'lg': '1024px',
            'xl': '1280px',
            '2xl': '1536px'
    },
    extend: {
      fontFamily: {
        roboto: ['Roboto', 'Arial', 'sans-serif'],
        manrope: ['Manrope', 'sans-serif'],
      },
    },
  },
  plugins: [],
}