/**
 * types/index.ts
 * ==============
 * Shared TypeScript interfaces matching backend API schemas.
 * Expanded as new models are introduced in future issues.
 */

// ---- Generic API response wrapper ----
export interface ApiResponse<T> {
  data: T
  message?: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
}

// ---- Health check ----
export interface HealthStatus {
  status: 'ok' | 'degraded'
  version: string
  environment: string
  dependencies: Record<string, string>
}

// ---- Error ----
export interface ApiError {
  detail: string
  type?: string
}

// ---- Auth (populated in Issue #5) ----
// export interface User { ... }
// export interface LoginRequest { ... }
// export interface TokenResponse { ... }

// ---- Document (populated in Issue #10) ----
// export interface Document { ... }
