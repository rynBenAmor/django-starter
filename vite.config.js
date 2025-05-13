import { resolve } from 'path';

export default {
  build: {
    outDir: 'static/',
    emptyOutDir: true,
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'assets/js/main.js'),
        style: resolve(__dirname, 'assets/scss/main.scss'),
      },
      output: {
        entryFileNames: '[name].js',         // disables hashed names
        assetFileNames: '[name].css',
      },
    },
  },
};
