/**
 * API Client Configuration
 * Axios-based HTTP client with interceptors for authentication and error handling
 */

import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse, AxiosError } from 'axios';
import { ApiError, NetworkError, AuthError, ApiResponse } from '@/types';
import config from './config';
import { tokenManager } from './auth/tokenManager';

// Create the main API client instance
const createApiClient = (): AxiosInstance => {
  const client = axios.create({
    baseURL: config.api.baseURL,
    timeout: config.api.timeout,
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
  });

  // Request interceptor - Add authentication token
  client.interceptors.request.use(
    async (config) => {
      // Try to ensure we have a valid token before making the request
      const validToken = await tokenManager.ensureValidToken();
      
      if (validToken) {
        config.headers.Authorization = `Bearer ${validToken}`;
      }

      // Add CSRF token if available
      if (typeof window !== 'undefined') {
        const csrfToken = document.querySelector<HTMLMetaElement>('meta[name="csrf-token"]')?.content;
        if (csrfToken) {
          config.headers['X-CSRFToken'] = csrfToken;
        }
      }

      // Log request in development
      if (config.development && config.development.showApiLogs) {
        console.log(`🚀 ${config.method?.toUpperCase()} ${config.url}`, {
          data: config.data,
          params: config.params,
        });
      }

      return config;
    },
    (error) => {
      console.error('Request interceptor error:', error);
      return Promise.reject(error);
    }
  );

  // Response interceptor - Handle responses and errors
  client.interceptors.response.use(
    (response: AxiosResponse) => {
      // Log response in development
      if (config.development && config.development.showApiLogs) {
        console.log(`✅ ${response.config.method?.toUpperCase()} ${response.config.url}`, {
          status: response.status,
          data: response.data,
        });
      }

      return response;
    },
    async (error: AxiosError) => {
      const originalRequest = error.config;

      // Log error in development
      if (config.development && config.development.showApiLogs) {
        console.error(`❌ ${originalRequest?.method?.toUpperCase()} ${originalRequest?.url}`, {
          status: error.response?.status,
          data: error.response?.data,
          message: error.message,
        });
      }

      // Handle token refresh for 401 errors
      if (error.response?.status === 401 && originalRequest && !originalRequest._retry) {
        originalRequest._retry = true;

        try {
          const newToken = await tokenManager.refreshAccessToken();
          if (newToken && originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${newToken}`;
            return client(originalRequest);
          }
        } catch (refreshError) {
          // Refresh failed, redirect to login
          tokenManager.clearTokens();
          if (typeof window !== 'undefined') {
            window.location.href = '/auth/login';
          }
          return Promise.reject(refreshError);
        }
      }

      // Transform error to our standard format
      const transformedError = transformApiError(error);
      return Promise.reject(transformedError);
    }
  );

  return client;
};

// Transform axios errors to our standard error format
const transformApiError = (error: AxiosError): ApiError | NetworkError | AuthError => {
  // Network errors (no response received)
  if (!error.response) {
    const networkError: NetworkError = {
      message: error.message || 'Network error occurred',
      code: error.code === 'ECONNABORTED' ? 'TIMEOUT' : 'NETWORK_ERROR',
      originalError: error,
    };
    return networkError;
  }

  const { status, data } = error.response;

  // Authentication errors
  if (status === 401 || status === 403) {
    const authError: AuthError = {
      message: (data as any)?.error || (data as any)?.detail || 'Authentication failed',
      code: status === 401 ? 'UNAUTHORIZED' : 'FORBIDDEN',
      status: status as 401 | 403,
    };
    return authError;
  }

  // General API errors
  const apiError: ApiError = {
    message: (data as any)?.error || (data as any)?.detail || error.message || 'An error occurred',
    status,
    errors: (data as any)?.errors || (data as any),
    details: data,
  };

  return apiError;
};

// Create the API client instance
export const apiClient = createApiClient();

// Wrapper function for making API calls with standardized error handling
export const apiCall = async <T = any>(
  config: AxiosRequestConfig
): Promise<T> => {
  try {
    const response = await apiClient(config);
    return response.data;
  } catch (error) {
    throw error;
  }
};

// Wrapper function for making API calls with our ApiResponse wrapper
export const apiRequest = async <T = any>(
  config: AxiosRequestConfig
): Promise<ApiResponse<T>> => {
  try {
    const data = await apiCall<T>(config);
    return {
      success: true,
      data,
    };
  } catch (error) {
    return {
      success: false,
      message: (error as ApiError).message,
      errors: (error as ApiError).errors,
    };
  }
};

// Helper functions for common HTTP methods
export const get = <T = any>(url: string, config?: AxiosRequestConfig): Promise<T> =>
  apiCall<T>({ method: 'GET', url, ...config });

export const post = <T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> =>
  apiCall<T>({ method: 'POST', url, data, ...config });

export const put = <T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> =>
  apiCall<T>({ method: 'PUT', url, data, ...config });

export const patch = <T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> =>
  apiCall<T>({ method: 'PATCH', url, data, ...config });

export const del = <T = any>(url: string, config?: AxiosRequestConfig): Promise<T> =>
  apiCall<T>({ method: 'DELETE', url, ...config });

// File upload helper
export const uploadFile = async (
  url: string,
  file: File,
  onProgress?: (progress: number) => void
): Promise<any> => {
  const formData = new FormData();
  formData.append('file', file);

  return apiCall({
    method: 'POST',
    url,
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    onUploadProgress: (progressEvent) => {
      if (onProgress && progressEvent.total) {
        const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        onProgress(progress);
      }
    },
  });
};

// Health check function
export const healthCheck = async (): Promise<boolean> => {
  try {
    await get('/health/');
    return true;
  } catch {
    return false;
  }
};

// Request cancellation support
export const createCancelToken = () => axios.CancelToken.source();

// Export types for use in services
export type {
  AxiosRequestConfig as RequestConfig,
  AxiosResponse as Response,
  AxiosError as RequestError,
};

export default apiClient;