/**
 * Register Page
 * New user registration page
 */

'use client';

import React from 'react';
import { RegisterForm } from '@/components/auth';

export default function RegisterPage() {
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
        <RegisterForm 
          redirectTo="/auth/login"
          showLoginLink={true}
          allowedUserTypes={[
            'Employee',
            'Installer', 
            'Stocker',
            'Salesman',
            'Driver',
            'Customer',
            'Supplier'
          ]}
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