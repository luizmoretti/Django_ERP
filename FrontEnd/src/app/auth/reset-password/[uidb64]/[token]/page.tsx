/**
 * Password Reset Confirmation Page
 * Handles password reset with token validation
 */

'use client';

import React from 'react';
import { ResetPasswordForm } from '@/components/auth';

interface ResetPasswordPageProps {
  params: {
    uidb64: string;
    token: string;
  };
}

export default function ResetPasswordPage({ params }: ResetPasswordPageProps) {
  const { uidb64, token } = React.use(params);

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
        <ResetPasswordForm
          mode="confirm"
          uidb64={uidb64}
          token={token}
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