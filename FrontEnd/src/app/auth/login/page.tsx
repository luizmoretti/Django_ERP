/**
 * Login Page
 * Authentication page for user login
 */

'use client';

import React, { useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import { LoginForm } from '@/components/auth';
import { Alert } from '@/components/ui';

export default function LoginPage() {
  const searchParams = useSearchParams();
  const redirect = searchParams.get('redirect');
  const registered = searchParams.get('registered');
  const expired = searchParams.get('expired');

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900">
            DryWall Warehouse
          </h1>
          <p className="mt-2 text-sm text-gray-600">
            Management System
          </p>
        </div>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        {/* Success message for completed registration */}
        {registered && (
          <div className="mb-6">
            <Alert
              type="success"
              title="Registration Successful!"
              message="Your account has been created. Please sign in with your credentials."
            />
          </div>
        )}

        {/* Success message for password reset */}
        {searchParams.get('reset') === 'success' && (
          <div className="mb-6">
            <Alert
              type="success"
              title="Password Reset Successful!"
              message="Your password has been reset. Please sign in with your new password."
            />
          </div>
        )}

        {/* Session expired message */}
        {expired && (
          <div className="mb-6">
            <Alert
              type="warning"
              title="Session Expired"
              message="Your session has expired. Please sign in again."
            />
          </div>
        )}

        <LoginForm
          redirectTo={redirect || undefined}
          showRegisterLink={true}
          showForgotPassword={true}
        />
      </div>

      {/* Footer */}
      <div className="mt-8 text-center">
        <p className="text-xs text-gray-500">
          © 2024 DryWall Warehouse Management System. All rights reserved.
        </p>
      </div>
    </div>
  );
}