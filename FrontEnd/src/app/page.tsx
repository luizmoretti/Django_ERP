/**
 * Home Page
 * Landing page with authentication redirection
 */

'use client';

import React, { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/hooks';
import { Button } from '@/components/ui';
import { 
  Building2, 
  Package, 
  Users, 
  TrendingUp,
  Shield,
  Truck,
  ShoppingCart,
  BarChart3,
  UserCheck,
  Wrench
} from 'lucide-react';

export default function HomePage() {
  const { authState } = useAuth();
  const router = useRouter();

  // Redirect authenticated users to dashboard
  useEffect(() => {
    if (authState.isAuthenticated && !authState.isLoading) {
      router.push('/dashboard');
    }
  }, [authState.isAuthenticated, authState.isLoading, router]);

  // Show loading while checking authentication
  if (authState.isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  // Show landing page for unauthenticated users
  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <Building2 className="h-8 w-8 text-blue-600 mr-3" />
              <h1 className="text-2xl font-bold text-gray-900">
                DryWall ERP
              </h1>
            </div>
            
            <div className="flex items-center space-x-4">
              <Link href="/auth/login">
                <Button variant="outline">Sign In</Button>
              </Link>
              <Link href="/auth/register">
                <Button>Get Started</Button>
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <main>
        <div className="relative bg-gray-50 overflow-hidden">
          <div className="max-w-7xl mx-auto">
            <div className="relative z-10 pb-8 bg-gray-50 sm:pb-16 md:pb-20 lg:max-w-2xl lg:w-full lg:pb-28 xl:pb-32">
              <div className="pt-10 mx-auto max-w-7xl px-4 sm:pt-12 sm:px-6 md:pt-16 lg:pt-20 lg:px-8 xl:pt-28">
                <div className="sm:text-center lg:text-left">
                  <h2 className="text-4xl tracking-tight font-extrabold text-gray-900 sm:text-5xl md:text-6xl">
                    <span className="block xl:inline">Complete</span>{' '}
                    <span className="block text-blue-600 xl:inline">
                      DryWall ERP
                    </span>
                  </h2>
                  <p className="mt-3 text-base text-gray-500 sm:mt-5 sm:text-lg sm:max-w-xl sm:mx-auto md:mt-5 md:text-xl lg:mx-0">
                    Manage your entire Drywall business with our integrated platform. 
                    Sales, inventory, employees, deliveries, fleet management, reporting and much more 
                    in one unified and powerful system.
                  </p>
                  <div className="mt-5 sm:mt-8 sm:flex sm:justify-center lg:justify-start">
                    <div className="rounded-md shadow">
                      <Link href="/auth/register">
                        <Button size="lg" className="w-full">
                          Start Free Trial
                        </Button>
                      </Link>
                    </div>
                    <div className="mt-3 sm:mt-0 sm:ml-3">
                      <Link href="/auth/login">
                        <Button variant="outline" size="lg" className="w-full">
                          Sign In
                        </Button>
                      </Link>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Features Section */}
        <div className="py-12 bg-white">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="lg:text-center">
              <h2 className="text-base text-blue-600 font-semibold tracking-wide uppercase">
                System Modules
              </h2>
              <p className="mt-2 text-3xl leading-8 font-extrabold tracking-tight text-gray-900 sm:text-4xl">
                Everything you need to manage your Drywall business
              </p>
              <p className="mt-4 max-w-2xl text-xl text-gray-500 lg:mx-auto">
                Our comprehensive platform provides all the modules needed to 
                efficiently manage every aspect of your Drywall business operations.
              </p>
            </div>

            <div className="mt-10">
              <div className="space-y-10 md:space-y-0 md:grid md:grid-cols-2 lg:grid-cols-3 md:gap-x-8 md:gap-y-10">
                {/* Sales & CRM */}
                <div className="relative">
                  <div className="absolute flex items-center justify-center h-12 w-12 rounded-md bg-blue-500 text-white">
                    <ShoppingCart className="h-6 w-6" />
                  </div>
                  <p className="ml-16 text-lg leading-6 font-medium text-gray-900">
                    Sales & CRM
                  </p>
                  <p className="mt-2 ml-16 text-base text-gray-500">
                    Manage customers, quotes, orders and track your entire sales 
                    pipeline with detailed performance reports.
                  </p>
                </div>

                {/* Inventory Management */}
                <div className="relative">
                  <div className="absolute flex items-center justify-center h-12 w-12 rounded-md bg-blue-500 text-white">
                    <Package className="h-6 w-6" />
                  </div>
                  <p className="ml-16 text-lg leading-6 font-medium text-gray-900">
                    Inventory Management
                  </p>
                  <p className="mt-2 ml-16 text-base text-gray-500">
                    Complete inventory control with low stock alerts, 
                    automatic movements and supplier integration.
                  </p>
                </div>

                {/* Employee Management */}
                <div className="relative">
                  <div className="absolute flex items-center justify-center h-12 w-12 rounded-md bg-blue-500 text-white">
                    <UserCheck className="h-6 w-6" />
                  </div>
                  <p className="ml-16 text-lg leading-6 font-medium text-gray-900">
                    Employee Management
                  </p>
                  <p className="mt-2 ml-16 text-base text-gray-500">
                    Time tracking, payroll, vacation management, training 
                    and team performance evaluations.
                  </p>
                </div>

                {/* Logistics & Delivery */}
                <div className="relative">
                  <div className="absolute flex items-center justify-center h-12 w-12 rounded-md bg-blue-500 text-white">
                    <Truck className="h-6 w-6" />
                  </div>
                  <p className="ml-16 text-lg leading-6 font-medium text-gray-900">
                    Logistics & Delivery
                  </p>
                  <p className="mt-2 ml-16 text-base text-gray-500">
                    Route planning, real-time delivery tracking 
                    and complete distribution logistics management.
                  </p>
                </div>

                {/* Fleet Management */}
                <div className="relative">
                  <div className="absolute flex items-center justify-center h-12 w-12 rounded-md bg-blue-500 text-white">
                    <Wrench className="h-6 w-6" />
                  </div>
                  <p className="ml-16 text-lg leading-6 font-medium text-gray-900">
                    Fleet Management
                  </p>
                  <p className="mt-2 ml-16 text-base text-gray-500">
                    Preventive maintenance, fuel control, vehicle documentation 
                    and comprehensive fleet performance monitoring.
                  </p>
                </div>

                {/* Reports & BI */}
                <div className="relative">
                  <div className="absolute flex items-center justify-center h-12 w-12 rounded-md bg-blue-500 text-white">
                    <BarChart3 className="h-6 w-6" />
                  </div>
                  <p className="ml-16 text-lg leading-6 font-medium text-gray-900">
                    Reports & BI
                  </p>
                  <p className="mt-2 ml-16 text-base text-gray-500">
                    Executive dashboards, financial reports, trend analysis 
                    and KPIs for strategic decision making.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* CTA Section */}
        <div className="bg-blue-600">
          <div className="max-w-2xl mx-auto text-center py-16 px-4 sm:py-20 sm:px-6 lg:px-8">
            <h2 className="text-3xl font-extrabold text-white sm:text-4xl">
              <span className="block">Ready to get started?</span>
              <span className="block">Start your free trial today.</span>
            </h2>
            <p className="mt-4 text-lg leading-6 text-blue-200">
              Join hundreds of Drywall companies already using our platform 
              to fully optimize their business operations.
            </p>
            <div className="mt-8">
              <Link href="/auth/register">
                <Button 
                  variant="outline"
                  size="lg"
                  className="!bg-white !text-blue-600 !border-white hover:!bg-gray-50 hover:!text-blue-700"
                >
                  Get Started Now
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white">
        <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 md:flex md:items-center md:justify-between lg:px-8">
          <div className="flex justify-center space-x-6 md:order-2">
            <p className="text-center text-sm text-gray-500">
              © 2024 DryWall ERP - Complete Business Management System. All rights reserved.
            </p>
          </div>
          <div className="mt-8 md:mt-0 md:order-1">
            <div className="flex items-center">
              <Building2 className="h-6 w-6 text-blue-600 mr-2" />
              <p className="text-center text-base text-gray-400">
                Built with enterprise security and scalability in mind.
              </p>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
