/**
 * Reset Password Page
 * Page for setting a new password after email verification
 */

'use client';

import React from 'react';
import { useSearchParams } from 'next/navigation';
import { ResetPasswordForm } from '@/components/auth';
import { Alert, Logo } from '@/components/ui';

export default function ResetPasswordPage() {
    const searchParams = useSearchParams();
    const token = searchParams.get('token');
    const uidb64 = searchParams.get('uid');

    // Check if required parameters are present
    if (!token || !uidb64) {
        return (
            <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
                <div className="sm:mx-auto sm:w-full sm:max-w-md">
                    <div className="text-center">
                        <div className="flex justify-center">
                            <Logo size="lg" />
                        </div>
                    </div>
                </div>

                <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
                    <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
                        <Alert
                            type="error"
                            title="Invalid Reset Link"
                            message="The password reset link is invalid or incomplete. Please request a new password reset."
                        />
                        <div className="mt-6">
                            <a
                                href="/auth/forgot-password"
                                className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                            >
                                Request New Reset Link
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
            <div className="sm:mx-auto sm:w-full sm:max-w-md">
                <div className="text-center">
                    <div className="flex justify-center">
                        <Logo size="lg" />
                    </div>
                    <h2 className="mt-6 text-3xl font-extrabold text-gray-900">
                        Reset Your Password
                    </h2>
                    <p className="mt-2 text-sm text-gray-600">
                        Enter your new password below
                    </p>
                </div>
            </div>

            <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
                <ResetPasswordForm token={token} uidb64={uidb64} />
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