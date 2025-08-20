/**
 * Next.js Middleware
 * Handles authentication and route protection at the edge
 */

import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

// Define protected routes and their requirements
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const protectedRoutes = [
  { path: '/dashboard', roles: ['CEO', 'Owner', 'Admin', 'Manager', 'Employee'] },
  { path: '/admin', roles: ['CEO', 'Owner', 'Admin'] },
  { path: '/management', roles: ['CEO', 'Owner', 'Admin', 'Manager'] },
  { path: '/inventory', roles: ['CEO', 'Owner', 'Admin', 'Manager', 'Employee', 'Stocker'] },
  { path: '/sales', roles: ['CEO', 'Owner', 'Admin', 'Manager', 'Salesman'] },
  { path: '/profile', roles: [] }, // All authenticated users
  { path: '/products', roles: ['CEO', 'Owner', 'Admin', 'Manager', 'Stocker'] },
  { path: '/suppliers', roles: ['CEO', 'Owner', 'Admin', 'Manager'] },
];

// Define public routes that don't require authentication
const publicRoutes = [
  '/auth/login',
  '/auth/register',
  '/auth/forgot-password',
  '/auth/reset-password',
  '/',
  '/about',
  '/contact',
  '/terms',
  '/privacy',
];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Check if the route is public
  const isPublicRoute = publicRoutes.some(route => pathname.startsWith(route));

  if (isPublicRoute) {
    return NextResponse.next();
  }

  // Get token from cookies
  const token = request.cookies.get('auth_token')?.value;

  // If no token and route is protected, redirect to login
  if (!token) {
    const loginUrl = new URL('/auth/login', request.url);
    loginUrl.searchParams.set('redirect', pathname);
    return NextResponse.redirect(loginUrl);
  }

  // For now, let the client-side handle detailed role/permission checks
  // In a production app, you might want to verify the JWT here

  return NextResponse.next();
}

// Configure which routes to run middleware on
export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public assets
     */
    '/((?!api|_next/static|_next/image|favicon.ico|public).*)',
  ],
};