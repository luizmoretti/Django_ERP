/**
 * Authentication Context
 * Provides authentication state and methods throughout the application
 */

'use client';

import React, { createContext, useContext, useReducer, useEffect, ReactNode } from 'react';
import { 
  User, 
  AuthState, 
  AuthContextType, 
  LoginRequest, 
  LoginResponse, 
  RegisterRequest,
  PasswordResetConfirm,
  UserType 
} from '@/types';
import { authService } from '@/services';
import { tokenManager } from '@/lib/auth/tokenManager';

// Initial auth state
const initialAuthState: AuthState = {
  user: null,
  profile: null,
  token: null,
  isAuthenticated: false,
  isLoading: true,
  error: null,
};

// Auth action types
type AuthAction =
  | { type: 'AUTH_START' }
  | { type: 'AUTH_SUCCESS'; payload: { user: User; token: string } }
  | { type: 'AUTH_FAILURE'; payload: string }
  | { type: 'AUTH_LOGOUT' }
  | { type: 'AUTH_LOADING'; payload: boolean }
  | { type: 'AUTH_ERROR'; payload: string | null }
  | { type: 'UPDATE_USER'; payload: User }
  | { type: 'CLEAR_ERROR' };

// Auth reducer
const authReducer = (state: AuthState, action: AuthAction): AuthState => {
  switch (action.type) {
    case 'AUTH_START':
      return {
        ...state,
        isLoading: true,
        error: null,
      };

    case 'AUTH_SUCCESS':
      return {
        ...state,
        user: action.payload.user,
        token: action.payload.token,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      };

    case 'AUTH_FAILURE':
      return {
        ...state,
        user: null,
        token: null,
        isAuthenticated: false,
        isLoading: false,
        error: action.payload,
      };

    case 'AUTH_LOGOUT':
      return {
        ...initialAuthState,
        isLoading: false,
      };

    case 'AUTH_LOADING':
      return {
        ...state,
        isLoading: action.payload,
      };

    case 'AUTH_ERROR':
      return {
        ...state,
        error: action.payload,
        isLoading: false,
      };

    case 'UPDATE_USER':
      return {
        ...state,
        user: action.payload,
      };

    case 'CLEAR_ERROR':
      return {
        ...state,
        error: null,
      };

    default:
      return state;
  }
};

// Create context
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Auth provider props
interface AuthProviderProps {
  children: ReactNode;
}

// Auth provider component
export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [authState, dispatch] = useReducer(authReducer, initialAuthState);

  // Initialize authentication on mount
  useEffect(() => {
    initializeAuth();
  }, []);

  /**
   * Initialize authentication by checking existing tokens
   */
  const initializeAuth = async (): Promise<void> => {
    try {
      dispatch({ type: 'AUTH_START' });

      const token = tokenManager.getAccessToken();
      if (!token) {
        // No token found - this is normal for unauthenticated users on public pages
        // Don't set an error, just mark as not authenticated
        dispatch({ type: 'AUTH_LOGOUT' });
        return;
      }

      // Check if token is expired
      if (tokenManager.isTokenExpired(token)) {
        // Try to refresh the token
        const newToken = await tokenManager.refreshAccessToken();
        if (!newToken) {
          // Token refresh failed - clear tokens and mark as unauthenticated
          tokenManager.clearTokens();
          dispatch({ type: 'AUTH_LOGOUT' });
          return;
        }
      }

      // Get current user profile
      const user = await authService.getCurrentUser();
      dispatch({ 
        type: 'AUTH_SUCCESS', 
        payload: { user, token: tokenManager.getAccessToken() || '' } 
      });

    } catch (error) {
      console.error('Auth initialization failed:', error);
      // Only show error if it's not a token/authentication issue
      if (error && (error as any).status !== 401 && (error as any).status !== 403) {
        dispatch({ type: 'AUTH_ERROR', payload: 'Authentication initialization failed' });
      } else {
        // For auth-related errors, just mark as unauthenticated without error message
        tokenManager.clearTokens();
        dispatch({ type: 'AUTH_LOGOUT' });
      }
    }
  };

  /**
   * Login user with credentials
   */
  const login = async (credentials: LoginRequest): Promise<LoginResponse> => {
    try {
      dispatch({ type: 'AUTH_START' });

      const response = await authService.login(credentials);
      
      // Get user profile after successful login
      const user = await authService.getCurrentUser();
      
      dispatch({ 
        type: 'AUTH_SUCCESS', 
        payload: { user, token: response.token } 
      });

      return response;
    } catch (error: any) {
      const errorMessage = error.message || 'Login failed';
      dispatch({ type: 'AUTH_FAILURE', payload: errorMessage });
      throw error;
    }
  };

  /**
   * Register new user
   */
  const register = async (userData: RegisterRequest): Promise<User> => {
    try {
      dispatch({ type: 'AUTH_START' });

      const user = await authService.register(userData);
      
      // Don't automatically log in after registration
      dispatch({ type: 'AUTH_LOADING', payload: false });
      
      return user;
    } catch (error: any) {
      const errorMessage = error.message || 'Registration failed';
      dispatch({ type: 'AUTH_FAILURE', payload: errorMessage });
      throw error;
    }
  };

  /**
   * Logout user
   */
  const logout = async (): Promise<void> => {
    try {
      await authService.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      dispatch({ type: 'AUTH_LOGOUT' });
    }
  };

  /**
   * Refresh authentication token
   */
  const refreshToken = async (): Promise<string> => {
    try {
      const newToken = await authService.refreshToken();
      if (!newToken) {
        throw new Error('Token refresh failed');
      }

      // Update the user profile with the new token
      const user = await authService.getCurrentUser();
      dispatch({ 
        type: 'AUTH_SUCCESS', 
        payload: { user, token: newToken } 
      });

      return newToken;
    } catch (error: any) {
      const errorMessage = error.message || 'Token refresh failed';
      dispatch({ type: 'AUTH_FAILURE', payload: errorMessage });
      throw error;
    }
  };

  /**
   * Request password reset
   */
  const resetPassword = async (email: string): Promise<void> => {
    try {
      await authService.requestPasswordReset(email);
    } catch (error: any) {
      const errorMessage = error.message || 'Password reset request failed';
      dispatch({ type: 'AUTH_ERROR', payload: errorMessage });
      throw error;
    }
  };

  /**
   * Confirm password reset
   */
  const confirmPasswordReset = async (
    token: string, 
    uidb64: string, 
    passwords: PasswordResetConfirm
  ): Promise<void> => {
    try {
      await authService.confirmPasswordReset(uidb64, token, passwords);
    } catch (error: any) {
      const errorMessage = error.message || 'Password reset confirmation failed';
      dispatch({ type: 'AUTH_ERROR', payload: errorMessage });
      throw error;
    }
  };

  /**
   * Update user profile
   */
  const updateProfile = async (profileData: Partial<User>): Promise<User> => {
    try {
      const updatedUser = await authService.updateProfile(profileData);
      dispatch({ type: 'UPDATE_USER', payload: updatedUser });
      return updatedUser;
    } catch (error: any) {
      const errorMessage = error.message || 'Profile update failed';
      dispatch({ type: 'AUTH_ERROR', payload: errorMessage });
      throw error;
    }
  };

  /**
   * Check if user has specific permission
   */
  const hasPermission = (permission: string): boolean => {
    return authService.hasPermission(authState.user, permission);
  };

  /**
   * Check if user has specific role
   */
  const hasRole = (role: UserType): boolean => {
    return authService.hasRole(authState.user, role);
  };

  /**
   * Check if user is one of the specified user types
   */
  const isUserType = (userType: UserType | UserType[]): boolean => {
    if (!authState.user?.user_type) {
      console.log('isUserType: No user type found', { user: authState.user });
      return false;
    }
    
    console.log('isUserType check:', {
      userCurrentType: authState.user.user_type,
      requiredTypes: userType,
      isArray: Array.isArray(userType)
    });
    
    if (Array.isArray(userType)) {
      const hasMatch = userType.includes(authState.user.user_type);
      console.log('isUserType result (array):', hasMatch);
      return hasMatch;
    }
    
    const hasMatch = authState.user.user_type === userType;
    console.log('isUserType result (single):', hasMatch);
    return hasMatch;
  };

  /**
   * Clear authentication error
   */
  const clearError = (): void => {
    dispatch({ type: 'CLEAR_ERROR' });
  };

  // Context value
  const contextValue: AuthContextType = {
    authState,
    login,
    register,
    logout,
    refreshToken,
    resetPassword,
    confirmPasswordReset,
    updateProfile,
    hasPermission,
    hasRole,
    isUserType,
  };

  // Add clearError to context if needed
  const extendedContextValue = {
    ...contextValue,
    clearError,
  };

  return (
    <AuthContext.Provider value={extendedContextValue}>
      {children}
    </AuthContext.Provider>
  );
};

// Custom hook to use auth context
export const useAuth = (): AuthContextType & { clearError: () => void } => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context as AuthContextType & { clearError: () => void };
};

// Higher-order component for authentication
export const withAuth = <P extends object>(
  Component: React.ComponentType<P>
): React.FC<P> => {
  const AuthenticatedComponent: React.FC<P> = (props) => {
    const { authState } = useAuth();

    if (authState.isLoading) {
      return (
        <div className="flex items-center justify-center min-h-screen">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      );
    }

    if (!authState.isAuthenticated) {
      return (
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <h2 className="text-xl font-semibold text-gray-900 mb-2">
              Authentication Required
            </h2>
            <p className="text-gray-600">
              Please log in to access this page.
            </p>
          </div>
        </div>
      );
    }

    return <Component {...props} />;
  };

  AuthenticatedComponent.displayName = `withAuth(${Component.displayName || Component.name})`;

  return AuthenticatedComponent;
};

// Export both as named export and default export for flexibility
export { AuthContext };
export default AuthContext;