/**
 * Central type exports
 * Re-exports all types for easy importing
 */

import { UserType } from './auth';

// Authentication types
export type {
  User,
  Profile,
  AuthState,
  UserType,
  Department,
  Position,
  LoginRequest,
  LoginResponse,
  RegisterRequest,
  PasswordResetRequest,
  PasswordResetConfirm,
  LoginFormData,
  RegisterFormData,
  PasswordResetFormData,
  PasswordResetConfirmFormData,
  Permission,
  Group,
  AuthContextType,
  ProtectedRouteProps,
  NavigationItem,
  UserPreferences,
} from './auth';

export {
  ROLE_HIERARCHY,
  USER_TYPE_PERMISSIONS,
} from './auth';

// API types
export type {
  ApiConfig,
  ApiResponse,
  ApiError,
  NetworkError,
  AuthError,
  HttpMethod,
  RequestConfig,
  ValidationErrors,
  ResponseMeta,
  PaginationMeta,
  PaginatedResponse,
  RequestInterceptor,
  ResponseInterceptor,
  FileUploadConfig,
  FileUploadResponse,
  ListQueryParams,
  EndpointPattern,
  ApiEndpoint,
  ServiceResponse,
  ServiceError,
  RetryConfig,
  CacheConfig,
  QueuedRequest,
  WebSocketMessage,
  RealtimeEvent,
  HealthCheckResponse,
  FeatureFlags,
  ApiVersion,
} from './api';

// Form types
export interface FormField {
  name: string;
  label: string;
  type: 'text' | 'email' | 'password' | 'select' | 'textarea' | 'checkbox' | 'radio';
  required?: boolean;
  placeholder?: string;
  validation?: any;
  options?: Array<{ value: string; label: string }>;
}

export interface FormConfig {
  fields: FormField[];
  onSubmit: (data: any) => Promise<void>;
  loading?: boolean;
  error?: string;
}

// UI component types
export interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'destructive';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
  disabled?: boolean;
  children: React.ReactNode;
  onClick?: () => void;
  type?: 'button' | 'submit' | 'reset';
  className?: string;
}

export interface InputProps {
  label?: string;
  error?: string;
  helperText?: string;
  required?: boolean;
  disabled?: boolean;
  className?: string;
}

export interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  children: React.ReactNode;
  size?: 'sm' | 'md' | 'lg' | 'xl';
}

// Layout types
export interface LayoutProps {
  children: React.ReactNode;
  sidebar?: boolean;
  header?: boolean;
  footer?: boolean;
}

export interface SidebarItem {
  id: string;
  label: string;
  icon?: React.ComponentType<{ className?: string }>;
  href?: string;
  children?: SidebarItem[];
  permissions?: string[];
  roles?: UserType[];
}

// Toast/Notification types
export interface Toast {
  id: string;
  title: string;
  message?: string;
  type: 'success' | 'error' | 'warning' | 'info';
  duration?: number;
  action?: {
    label: string;
    onClick: () => void;
  };
}

// Loading states
export interface LoadingState {
  isLoading: boolean;
  message?: string;
}

export interface AsyncState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

// Route types
export interface Route {
  path: string;
  component: React.ComponentType;
  exact?: boolean;
  protected?: boolean;
  roles?: UserType[];
  permissions?: string[];
  layout?: React.ComponentType<LayoutProps>;
}

// Environment configuration
export interface Environment {
  NODE_ENV: 'development' | 'production' | 'test';
  API_BASE_URL: string;
  WS_BASE_URL?: string;
  APP_NAME: string;
  APP_VERSION: string;
  DEBUG: boolean;
}

// Local storage keys
export const STORAGE_KEYS = {
  ACCESS_TOKEN: 'auth_token',
  REFRESH_TOKEN: 'refresh_token',
  USER_DATA: 'user_data',
  USER_PREFERENCES: 'user_preferences',
  THEME: 'theme',
  LANGUAGE: 'language',
} as const;

// API endpoints
export const API_ENDPOINTS = {
  AUTH: {
    LOGIN: '/api/v1/user/login/',
    LOGOUT: '/api/v1/user/logout/',
    REGISTER: '/api/v1/user/create/',
    ME: '/api/v1/user/me/',
    PASSWORD_RESET: '/api/v1/user/password-reset/',
    PASSWORD_RESET_CONFIRM: '/api/v1/user/reset/{uidb64}/{token}/',
    PASSWORD_RESET_COMPLETE: '/api/v1/user/reset/done/',
  },
  USERS: {
    LIST: '/api/v1/user/',
    RETRIEVE: '/api/v1/user/retrieve/{id}/',
    UPDATE: '/api/v1/user/update/{id}/',
    DELETE: '/api/v1/user/delete/{id}/',
  },
  PRODUCTS: {
    LIST: '/api/v1/products/',
    CREATE: '/api/v1/products/create/',
    RETRIEVE: '/api/v1/products/retrieve/{id}/',
    UPDATE: '/api/v1/products/update/{id}/',
    DELETE: '/api/v1/products/delete/{id}/',
    HD_ACTIONS: '/api/v1/products/home-depot/{action}/',
  },
  SUPPLIERS: {
    LIST: '/api/v1/suppliers/',
    CREATE: '/api/v1/suppliers/create/',
    RETRIEVE: '/api/v1/suppliers/retrieve/{id}/',
    UPDATE: '/api/v1/suppliers/update/{id}/',
    DELETE: '/api/v1/suppliers/delete/{id}/',
  },
  BRANDS: {
    LIST: '/api/v1/brands/',
    CREATE: '/api/v1/brands/create/',
    RETRIEVE: '/api/v1/brands/retrieve/{id}/',
    UPDATE: '/api/v1/brands/update/{id}/',
    DELETE: '/api/v1/brands/delete/{id}/',
  },
} as const;

// Event types for analytics/tracking
export interface AnalyticsEvent {
  name: string;
  properties?: Record<string, any>;
  timestamp?: string;
  user_id?: string;
}

// Error boundary types
export interface ErrorInfo {
  componentStack: string;
  errorBoundary?: string;
}

export interface ErrorBoundaryState {
  hasError: boolean;
  error?: Error;
  errorInfo?: ErrorInfo;
}

export interface Product {
  id: string;
  name: string;
  description?: string;
  quantity: number;
  price: number;
  brand?: string;
  _brand?: string;
  category?: string;
  _category?: string;
  supplier?: string;
  _supplier?: string;
  skus: { sku: string }[];
  store_ids: { in_store_id: string }[];
  created_at: string;
  updated_at: string;
  created_by?: string;
  updated_by?: string;
  companie?: string;
}

export interface Supplier {
  id: string;
  name: string;
  tax_number?: string;
  phone?: string;
  email?: string;
  address?: string;
  city?: string;
  state?: string;
  zip_code?: string;
  country: string;
  product_prices: { _product: string; unit_price: number; last_purchase_date: string; is_current: boolean }[];
  created_at: string;
  updated_at: string;
  created_by?: string;
  updated_by?: string;
  companie?: string;
}

export interface Brand {
  id: string;
  name: string;
  created_at: string;
  updated_at: string;
  created_by?: string;
  updated_by?: string;
  companie?: string;
}

export interface Category {
  id: string;
  name: string;
  created_at: string;
  updated_at: string;
  created_by?: string;
  updated_by?: string;
  companie?: string;
}