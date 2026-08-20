/// <reference types="vite/client" />

/**
 * vite-env.d.ts
 * =============
 * Provides TypeScript types for Vite's special globals:
 * - import.meta.env  (VITE_* environment variables)
 * - import.meta.hot  (HMR API)
 *
 * This file must be in src/ and referenced in tsconfig.json include.
 */

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string
  readonly VITE_APP_NAME: string
  // Add new VITE_* variables here as they are introduced
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
