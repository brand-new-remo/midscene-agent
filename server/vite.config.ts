import { defineConfig } from 'vite'
import { resolve } from 'path'
import { fileURLToPath } from 'url'

const __dirname = fileURLToPath(new URL('.', import.meta.url))

export default defineConfig({
  build: {
    lib: {
      entry: resolve(__dirname, 'src/index.ts'),
      formats: ['es'],
      fileName: 'index'
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
        'url'
      ]
    },
    target: 'node18',
    outDir: 'dist',
    ssr: true
  }
})
