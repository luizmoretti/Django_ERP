/**
 * Authentication Types for React Frontend
 * Interfaces that match the Django backend User model and API responses
 */

// User types matching Django backend choices
export type UserType = 
  // Executive Level
  | 'CEO'
  | 'Owner' 
  | 'Admin'
  // Management Level
  | 'Manager'
  // Operational Level
  | 'Employee'
  | 'Installer'
  | 'Stocker'
  | 'Salesman'
  | 'Driver'
  // External Users
  | 'Customer'
  | 'Supplier';

// Profile department choices
export type Department = 
  | 'Executive'
  | 'Management'
  | 'Sales'
  | 'Installation'
  | 'Warehouse'
  | 'Administration'
  | 'Finance'
  | 'HR';

// Profile position choices
export type Position = 
  | 'Owner'
  | 'Director'
  | 'Manager'
  | 'Salesperson'
  | 'Installer'
  | 'Stockist';

// User interface matching Django User model
export interface User {
  id: string; // UUID from Django
  email: string;
  first_name: string;
  last_name: string;
  user_type?: UserType;
  ip?: string;
  is_staff: boolean;
  is_active: boolean;
  is_superuser: boolean;
  last_login?: string;
  date_joined: string;
  groups?: string[];
  permissions?: string[];
}

// Profile interface (if using profiles)
export interface Profile {
  id: string;
  user: string; // User ID
  department?: Department;
  position?: Position;
  is_active: boolean;
  phone?: string;
  avatar?: string;
}

// Authentication state interface
export interface AuthState {
  user: User | null;
  profile: Profile | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

// Login request/response interfaces
export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  token: string;
  name: string;
  redirect_url: string;
}

// Register request interface
export interface RegisterRequest {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  user_type: UserType;
}

// Password reset interfaces
export interface PasswordResetRequest {
  email: string;
}

export interface PasswordResetConfirm {
  password: string;
  password_confirm: string;
}

// API response interfaces
export interface ApiResponse<T = any> {
  data?: T;
  message?: string;
  error?: string;
  errors?: Record<string, string[]>;
}

export interface ApiError {
  message: string;
  status: number;
  errors?: Record<string, string[]>;
}

// Form validation interfaces
export interface LoginFormData {
  email: string;
  password: string;
}

export interface RegisterFormData {
  email: string;
  password: string;
  confirmPassword: string;
  first_name: string;
  last_name: string;
  user_type: UserType;
}

export interface PasswordResetFormData {
  email: string;
}

export interface PasswordResetConfirmFormData {
  password: string;
  confirmPassword: string;
}

// Role-based access control
export interface Permission {
  id: string;
  name: string;
  codename: string;
}

export interface Group {
  id: string;
  name: string;
  permissions: Permission[];
}

// Authentication context methods
export interface AuthContextType {
  // State
  authState: AuthState;
  
  // Actions
  login: (credentials: LoginRequest) => Promise<LoginResponse>;
  register: (userData: RegisterRequest) => Promise<User>;
  logout: () => void;
  refreshToken: () => Promise<string>;
  resetPassword: (email: string) => Promise<void>;
  confirmPasswordReset: (token: string, uidb64: string, passwords: PasswordResetConfirm) => Promise<void>;
  updateProfile: (profileData: Partial<User>) => Promise<User>;
  
  // Utilities
  hasPermission: (permission: string) => boolean;
  hasRole: (role: UserType) => boolean;
  isUserType: (userType: UserType | UserType[]) => boolean;
}

// Route protection types
export interface ProtectedRouteProps {
  children: React.ReactNode;
  allowedRoles?: UserType[];
  permissions?: string[];
  fallback?: React.ReactNode;
}

// Navigation and routing
export interface NavigationItem {
  name: string;
  href: string;
  icon?: React.ComponentType<{ className?: string }>;
  requiredPermissions?: string[];
  allowedRoles?: UserType[];
  children?: NavigationItem[];
}

// Role hierarchy for access control
export const ROLE_HIERARCHY: Record<UserType, number> = {
  // Executive Level (highest access)
  'CEO': 100,
  'Owner': 95,
  'Admin': 90,
  
  // Management Level
  'Manager': 80,
  
  // Operational Level
  'Employee': 60,
  'Installer': 55,
  'Stocker': 50,
  'Salesman': 50,
  'Driver': 45,
  
  // External Users (lowest access)
  'Customer': 20,
  'Supplier': 15,
};

// Permission groups for different user types
export const USER_TYPE_PERMISSIONS: Record<UserType, string[]> = {
  'CEO': ['*'], // Full access
  'Owner': ['*'], // Full access
  'Admin': ['*'], // Full access
  'Manager': ['view_employees', 'manage_inventory', 'view_reports', 'manage_customers'],
  'Employee': ['view_inventory', 'view_customers'],
  'Installer': ['view_assignments', 'update_installations'],
  'Stocker': ['manage_inventory', 'view_stock'],
  'Salesman': ['manage_customers', 'create_orders', 'view_products'],
  'Driver': ['view_deliveries', 'update_delivery_status'],
  'Customer': ['view_orders', 'update_profile'],
  'Supplier': ['view_purchase_orders', 'update_profile'],
};

// Theme and UI preferences
export interface UserPreferences {
  theme: 'light' | 'dark' | 'system';
  language: 'en' | 'es' | 'pt';
  timezone: string;
  notifications: {
    email: boolean;
    push: boolean;
    sms: boolean;
  };
}