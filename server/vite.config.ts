/* eslint-disable import/order */
import { resolve } from 'path';
import { fileURLToPath } from 'url';

import { defineConfig } from 'vite';
/* eslint-enable import/order */

const dirname = fileURLToPath(new URL('.', import.meta.url));

export default defineConfig({
  build: {
    lib: {
      entry: resolve(dirname, 'src/index.ts'),
      formats: ['es'],
      fileName: 'index',
    },
    rollupOptions: {
      external: [
        /^node:/,
        'express',
        'ws',
        '@midscene/web',
        'playwright',
        'winston',
        'cors',
        'uuid',
        'dotenv',
        'http',
        'fs',
        'path',
        'url',
      ],
    },
    target: 'node18',
    outDir: 'dist',
    ssr: true,
  },
});
