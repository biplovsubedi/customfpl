module.exports = {
  future: {
    removeDeprecatedGapUtilities: true,
    purgeLayersByDefault: true,
  },
  purge: {
    enabled: true, //true for production build
    content: [
      '../**/templates/*.html',
      '../**/templates/**/*.html'
    ]
  },
  darkMode: "class", // or 'media' or 'class'
  theme: {
    extend: {},
  },
  variants: {},
  plugins: [],
}