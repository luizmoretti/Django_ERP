/**
 * Protected Route Component
 * Wrapper component for route protection with role and permission checks
 */

'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { useAuth, useProtectedRoute } from '@/hooks';
import { ProtectedRouteProps } from '@/types';
import { Alert } from '@/components/ui';

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  allowedRoles,
  permissions,
  fallback,
}) => {
  const { authState } = useAuth();
  const router = useRouter();
  
  const { isLoading, hasAccess, error } = useProtectedRoute({
    requiredRoles: allowedRoles,
    requiredPermissions: permissions,
    requireAuth: true,
  });

  // Show loading state
  if (isLoading || authState.isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  // Show unauthorized state
  if (!hasAccess) {
    if (fallback) {
      return <>{fallback}</>;
    }

    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <div className="max-w-md w-full">
          <Alert
            type="error"
            title="Access Denied"
            message={error || "You don't have permission to access this page."}
          />
          <div className="mt-6 text-center">
            <button
              onClick={() => router.back()}
              className="text-blue-600 hover:text-blue-500 font-medium"
            >
              Go Back
            </button>
            <span className="mx-2 text-gray-400">•</span>
            <button
              onClick={() => router.push('/dashboard')}
              className="text-blue-600 hover:text-blue-500 font-medium"
            >
              Go to Dashboard
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Render protected content
  return <>{children}</>;
};

export default ProtectedRoute;