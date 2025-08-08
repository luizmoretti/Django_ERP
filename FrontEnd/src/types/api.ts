/**
 * API Types and Response Interfaces
 * Standardized types for API communication with Django backend
 */

// Base API configuration
export interface ApiConfig {
  baseURL: string;
  timeout: number;
  headers: Record<string, string>;
}

// HTTP Methods
export type HttpMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';

// Request configuration
export interface RequestConfig {
  method: HttpMethod;
  url: string;
  data?: any;
  params?: Record<string, any>;
  headers?: Record<string, string>;
}

// Standardized API response wrapper
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  errors?: ValidationErrors;
  meta?: ResponseMeta;
}

// Validation errors from Django REST Framework
export interface ValidationErrors {
  [field: string]: string[] | ValidationErrors;
}

// Response metadata
export interface ResponseMeta {
  timestamp: string;
  request_id?: string;
  pagination?: PaginationMeta;
}

// Pagination metadata
export interface PaginationMeta {
  count: number;
  next: string | null;
  previous: string | null;
  page_size: number;
  total_pages: number;
  current_page: number;
}

// Paginated response
export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

// Error response structure
export interface ApiError {
  message: string;
  status: number;
  code?: string;
  errors?: ValidationErrors;
  details?: any;
}

// Network error
export interface NetworkError {
  message: string;
  code: 'NETWORK_ERROR' | 'TIMEOUT' | 'CONNECTION_REFUSED';
  originalError?: Error;
}

// Authentication error
export interface AuthError {
  message: string;
  code: 'UNAUTHORIZED' | 'FORBIDDEN' | 'TOKEN_EXPIRED' | 'TOKEN_INVALID';
  status: 401 | 403;
}

// Request interceptor types
export interface RequestInterceptor {
  onRequest?: (config: RequestConfig) => RequestConfig | Promise<RequestConfig>;
  onRequestError?: (error: any) => Promise<any>;
}

// Response interceptor types
export interface ResponseInterceptor {
  onResponse?: (response: any) => any | Promise<any>;
  onResponseError?: (error: any) => Promise<any>;
}

// File upload types
export interface FileUploadConfig {
  file: File;
  fieldName?: string;
  onProgress?: (progress: number) => void;
}

export interface FileUploadResponse {
  url: string;
  filename: string;
  size: number;
  content_type: string;
}

// Query parameters for list endpoints
export interface ListQueryParams {
  page?: number;
  page_size?: number;
  search?: string;
  ordering?: string;
  [key: string]: any;
}

// Common endpoint patterns
export type EndpointPattern = 
  | 'list'        // GET /resource/
  | 'create'      // POST /resource/
  | 'retrieve'    // GET /resource/{id}/
  | 'update'      // PUT /resource/{id}/
  | 'partial'     // PATCH /resource/{id}/
  | 'destroy';    // DELETE /resource/{id}/

// API endpoint configuration
export interface ApiEndpoint {
  path: string;
  method: HttpMethod;
  requiresAuth: boolean;
  cacheable?: boolean;
  timeout?: number;
}

// Service response types
export type ServiceResponse<T> = Promise<T>;
export type ServiceError = ApiError | NetworkError | AuthError;

// Retry configuration
export interface RetryConfig {
  attempts: number;
  delay: number;
  backoff: 'linear' | 'exponential';
  retryCondition?: (error: any) => boolean;
}

// Cache configuration
export interface CacheConfig {
  enabled: boolean;
  ttl: number; // Time to live in milliseconds
  key?: string;
}

// Request queue for offline support
export interface QueuedRequest {
  id: string;
  config: RequestConfig;
  timestamp: number;
  retryCount: number;
  priority: 'low' | 'normal' | 'high';
}

// WebSocket message types
export interface WebSocketMessage<T = any> {
  type: string;
  payload: T;
  timestamp: string;
  id?: string;
}

// Real-time event types
export interface RealtimeEvent<T = any> {
  event: string;
  data: T;
  timestamp: string;
  user_id?: string;
}

// Health check response
export interface HealthCheckResponse {
  status: 'healthy' | 'degraded' | 'unhealthy';
  timestamp: string;
  services: {
    database: 'up' | 'down';
    cache: 'up' | 'down';
    storage: 'up' | 'down';
  };
  version: string;
}

// Feature flags
export interface FeatureFlags {
  [feature: string]: boolean;
}

// API versioning
export interface ApiVersion {
  version: string;
  deprecated: boolean;
  sunset_date?: string;
  migration_guide?: string;
}