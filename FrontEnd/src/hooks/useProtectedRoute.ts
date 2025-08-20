/**
 * Protected Route Hook
 * Custom hook for route protection and access control
 */

import { useEffect, useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { UserType } from '@/types';

interface UseProtectedRouteOptions {
  requiredRoles?: UserType[];
  requiredPermissions?: string[];
  redirectTo?: string;
  requireAuth?: boolean;
}

interface ProtectedRouteState {
  isLoading: boolean;
  hasAccess: boolean;
  error: string | null;
}

/**
 * Hook for protecting routes with role and permission checks
 */
export const useProtectedRoute = (options: UseProtectedRouteOptions = {}) => {
  const {
    requiredRoles = [],
    requiredPermissions = [],
    redirectTo = '/auth/login',
    requireAuth = true,
  } = options;

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const { authState, hasRole, hasPermission, isUserType } = useAuth();
  const router = useRouter();
  const [state, setState] = useState<ProtectedRouteState>({
    isLoading: true,
    hasAccess: false,
    error: null,
  });

  const checkAccess = useCallback(async () => {
    // Wait for auth to finish loading
    if (authState.isLoading) {
      setState(prev => ({ ...prev, isLoading: true }));
      return;
    }

    // Check authentication requirement
    if (requireAuth && !authState.isAuthenticated) {
      setState({
        isLoading: false,
        hasAccess: false,
        error: 'Authentication required',
      });
      router.push(redirectTo);
      return;
    }

    // If no auth required and user is not authenticated, allow access
    if (!requireAuth && !authState.isAuthenticated) {
      setState({
        isLoading: false,
        hasAccess: true,
        error: null,
      });
      return;
    }

    // Check role requirements
    if (requiredRoles.length > 0 && !isUserType(requiredRoles)) {
      console.error('Access denied - Role check failed:', {
        userType: authState.user?.user_type,
        requiredRoles,
        hasAccess: isUserType(requiredRoles)
      });
      setState({
        isLoading: false,
        hasAccess: false,
        error: 'Insufficient role permissions',
      });
      router.push('/unauthorized');
      return;
    }

    // Check permission requirements
    if (requiredPermissions.length > 0) {
      const hasAllPermissions = requiredPermissions.every(permission => 
        hasPermission(permission)
      );

      if (!hasAllPermissions) {
        setState({
          isLoading: false,
          hasAccess: false,
          error: 'Insufficient permissions',
        });
        router.push('/unauthorized');
        return;
      }
    }

    // All checks passed
    setState({
      isLoading: false,
      hasAccess: true,
      error: null,
    });
  }, [authState.isAuthenticated, authState.user, authState.isLoading, requireAuth, requiredRoles, requiredPermissions, redirectTo, router, hasPermission, isUserType]);

  useEffect(() => {
    checkAccess();
  }, [checkAccess]);

  return state;
};

/**
 * Hook for checking if user can access a specific resource
 */
export const useCanAccess = (
  requiredRoles?: UserType[],
  requiredPermissions?: string[]
): boolean => {
  const { authState, hasPermission, isUserType } = useAuth();

  if (!authState.isAuthenticated || !authState.user) {
    return false;
  }

  // Check role requirements
  if (requiredRoles && requiredRoles.length > 0) {
    if (!isUserType(requiredRoles)) {
      return false;
    }
  }

  // Check permission requirements
  if (requiredPermissions && requiredPermissions.length > 0) {
    return requiredPermissions.every(permission => hasPermission(permission));
  }

  return true;
};

/**
 * Hook for role-based rendering
 */
export const useRoleCheck = (allowedRoles: UserType[]) => {
  const { isUserType } = useAuth();
  return isUserType(allowedRoles);
};

/**
 * Hook for permission-based rendering
 */
export const usePermissionCheck = (requiredPermissions: string[]) => {
  const { hasPermission } = useAuth();
  return requiredPermissions.every(permission => hasPermission(permission));
};

export default useProtectedRoute;