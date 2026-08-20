/**
 * api/client.ts
 * =============
 * Pre-configured Axios instance for all API calls.
 *
 * Features:
 * - Base URL from VITE_API_BASE_URL env var
 * - JSON content-type header
 * - Automatic JWT token injection (prepared for Issue #5)
 * - 401 → redirect to login (prepared for Issue #5)
 * - Consistent error handling
 */
import axios, { type AxiosError, type InternalAxiosRequestConfig } from 'axios'

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'

export const apiClient = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30_000, // 30 second timeout
})

// ------------------------------------------------------------------ //
// Request interceptor — attach JWT token if present
// ------------------------------------------------------------------ //
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('access_token')
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error: AxiosError) => Promise.reject(error),
)

// ------------------------------------------------------------------ //
// Response interceptor — handle auth errors globally
// ------------------------------------------------------------------ //
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Token expired or invalid — clear storage and redirect to login
      // Full refresh-token logic will be added in Issue #5
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  },
)

export default apiClient
