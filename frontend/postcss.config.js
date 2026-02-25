import type { Config } from 'tailwindcss'
import postcss from 'postcss'

export default {
  plugins: [
    require('tailwindcss'),
    require('autoprefixer'),
  ],
} as Config
