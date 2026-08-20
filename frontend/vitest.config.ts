/// <reference types="vitest" />
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

/**
 * vitest.config.ts — Vitest-specific configuration
 * Kept separate from vite.config.ts to avoid TypeScript type conflicts
 * between Vite's UserConfigExport and Vitest's InlineConfig.
 */
export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: ['node_modules/', 'src/test/'],
    },
  },
})
