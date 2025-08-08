/**
 * Forgot Password Page
 * Page for requesting password reset via email
 */

'use client';

import React from 'react';
import { ForgotPasswordForm } from '@/components/auth';
import { Logo } from '@/components/ui';

export default function ForgotPasswordPage() {
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="text-center">
          <div className="flex justify-center">
            <Logo size="lg" />
          </div>
          <h2 className="mt-6 text-3xl font-extrabold text-gray-900">
            Password Recovery
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            We'll help you get back into your account
          </p>
        </div>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <ForgotPasswordForm showLoginLink={true} />
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