/**
 * App Layout Component
 * Main layout wrapper with sidebar for authenticated pages
 */

'use client';

import React from 'react';
import { useAuth } from '@/hooks';
import Sidebar from './Sidebar';

interface AppLayoutProps {
  children: React.ReactNode;
  title?: string;
  breadcrumbs?: Array<{ label: string; href?: string }>;
}

const AppLayout: React.FC<AppLayoutProps> = ({ 
  children, 
  title = 'Dashboard',
  breadcrumbs = [] 
}) => {
  const { authState } = useAuth();

  if (!authState.isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <Sidebar />
      
      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="bg-white border-b border-gray-200 px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-semibold text-gray-900">{title}</h1>
              {breadcrumbs.length > 0 && (
                <nav className="flex mt-1" aria-label="Breadcrumb">
                  <ol className="flex items-center space-x-2">
                    {breadcrumbs.map((crumb, index) => (
                      <li key={index} className="flex items-center">
                        {index > 0 && (
                          <span className="text-gray-400 mx-2">/</span>
                        )}
                        {crumb.href ? (
                          <a
                            href={crumb.href}
                            className="text-sm text-blue-600 hover:text-blue-700"
                          >
                            {crumb.label}
                          </a>
                        ) : (
                          <span className="text-sm text-gray-500">{crumb.label}</span>
                        )}
                      </li>
                    ))}
                  </ol>
                </nav>
              )}
            </div>
            
            {/* Header Actions */}
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-500">
                Welcome, {authState.user?.first_name}
              </span>
            </div>
          </div>
        </header>

        {/* Main Content Area */}
        <main className="flex-1 overflow-y-auto p-6">
          {children}
        </main>
      </div>
    </div>
  );
};

export default AppLayout;