module.exports = {
  content: [
    '../../neuroa_app/templates/*.html',
    '../../theme/templates/*.html',
    '../../theme/static_src/*.js',
    '../../theme/static_src/**/*.css',
  ],
  theme: {
    screens: {
      'sm': '640px',
      'md': '768px',
      'lg': '1024px',
      'xl': '1280px',
      '2xl': '1536px',
      'custom-breakpoint': '1700px',
      'semi-large': '770px',
      'max-semi-large': {'max': '770px'},
    },
    extend: {
      translate: {
        '-755': '-755px',   // ajoute la valeur personnalisée -755px
      },
    },
  },
  plugins: [],
}