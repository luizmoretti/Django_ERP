/**
 * Dashboard Page
 * Main dashboard for authenticated users
 */

'use client';

import React from 'react';
import { ProtectedRoute } from '@/components/auth';
import { useAuth } from '@/hooks';
import { Button } from '@/components/ui';
import {
  Users,
  Package,
  TrendingUp,
  DollarSign,
  LogOut,
  Settings,
  User,
  Building2
} from 'lucide-react';

export default function DashboardPage() {
  const { authState, logout } = useAuth();
  const { user } = authState;

  const handleLogout = async () => {
    await logout();
  };

  const stats = [
    {
      name: 'Total Users',
      value: '1,234',
      icon: Users,
      change: '+12%',
      changeType: 'positive' as const,
    },
    {
      name: 'Inventory Items',
      value: '5,678',
      icon: Package,
      change: '+8%',
      changeType: 'positive' as const,
    },
    {
      name: 'Monthly Sales',
      value: '$45,678',
      icon: TrendingUp,
      change: '+23%',
      changeType: 'positive' as const,
    },
    {
      name: 'Revenue',
      value: '$123,456',
      icon: DollarSign,
      change: '+15%',
      changeType: 'positive' as const,
    },
  ];

  const quickActions = [
    { name: 'Manage Users', href: '/users', icon: Users },
    { name: 'Inventory', href: '/inventory', icon: Package },
    { name: 'Reports', href: '/reports', icon: TrendingUp },
    { name: 'Settings', href: '/settings', icon: Settings },
    { name: 'Products', href: '/products', icon: Package },
    { name: 'Suppliers', href: '/suppliers', icon: Building2 },
  ];

  return (
    <ProtectedRoute allowedRoles={['CEO', 'Owner', 'Admin', 'Manager', 'Employee']}>
      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <header className="bg-white shadow">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center py-6">
              <div>
                <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
                <p className="mt-1 text-sm text-gray-600">
                  Welcome back, {user?.first_name} {user?.last_name}
                </p>
              </div>

              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-2 text-sm text-gray-600">
                  <User className="h-4 w-4" />
                  <span>{user?.user_type}</span>
                </div>

                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleLogout}
                >
                  <LogOut className="h-4 w-4 mr-2" />
                  Logout
                </Button>
              </div>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          {/* Stats Grid */}
          <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4 mb-8">
            {stats.map((stat) => {
              const Icon = stat.icon;
              return (
                <div
                  key={stat.name}
                  className="bg-white overflow-hidden shadow rounded-lg"
                >
                  <div className="p-5">
                    <div className="flex items-center">
                      <div className="flex-shrink-0">
                        <Icon className="h-6 w-6 text-gray-400" />
                      </div>
                      <div className="ml-5 w-0 flex-1">
                        <dl>
                          <dt className="text-sm font-medium text-gray-500 truncate">
                            {stat.name}
                          </dt>
                          <dd className="flex items-baseline">
                            <div className="text-2xl font-semibold text-gray-900">
                              {stat.value}
                            </div>
                            <div
                              className={`ml-2 flex items-baseline text-sm font-semibold ${stat.changeType === 'positive'
                                  ? 'text-green-600'
                                  : 'text-red-600'
                                }`}
                            >
                              {stat.change}
                            </div>
                          </dd>
                        </dl>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Quick Actions */}
          <div className="bg-white shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
                Quick Actions
              </h3>
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
                {quickActions.map((action) => {
                  const Icon = action.icon;
                  return (
                    <button
                      key={action.name}
                      className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                    >
                      <Icon className="h-6 w-6 text-blue-600 mr-3" />
                      <span className="text-sm font-medium text-gray-900">
                        {action.name}
                      </span>
                    </button>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Recent Activity */}
          <div className="mt-8 bg-white shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
                Recent Activity
              </h3>
              <div className="space-y-4">
                <div className="flex items-center justify-between py-2 border-b border-gray-200">
                  <div>
                    <p className="text-sm font-medium text-gray-900">
                      New user registered
                    </p>
                    <p className="text-sm text-gray-600">John Doe joined as Employee</p>
                  </div>
                  <span className="text-sm text-gray-500">2 hours ago</span>
                </div>

                <div className="flex items-center justify-between py-2 border-b border-gray-200">
                  <div>
                    <p className="text-sm font-medium text-gray-900">
                      Inventory updated
                    </p>
                    <p className="text-sm text-gray-600">250 new items added to warehouse</p>
                  </div>
                  <span className="text-sm text-gray-500">4 hours ago</span>
                </div>

                <div className="flex items-center justify-between py-2">
                  <div>
                    <p className="text-sm font-medium text-gray-900">
                      Order completed
                    </p>
                    <p className="text-sm text-gray-600">Order #12345 was delivered successfully</p>
                  </div>
                  <span className="text-sm text-gray-500">6 hours ago</span>
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
    </ProtectedRoute>
  );
}