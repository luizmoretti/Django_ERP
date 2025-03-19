import { type NextRequest, type MiddlewareConfig, NextResponse } from "next/server";
import Cookies from "js-cookie";

const publicRoutes = [
    { path: "/sign-in", whenAuthenticated: "redirect" },
    { path: "/dashboard", whenAuthenticated: "next" },
    { path: "/products", whenAuthenticated: "next" },
    { path: "/categories", whenAuthenticated: "next" },
    {path: "/brands", whenAuthenticated: "next"},
    {path: "/stores", whenAuthenticated: "next"},
    {path: "/suppliers", whenAuthenticated: "next"},
] as const;

const REDIRECT_WHEN_NOT_AUTHENTICATED_ROUTE = '/sign-in';

export function middleware(request: NextRequest) {
    const user = Cookies.get("user");
    const path = request.nextUrl.pathname;
    const publicRoute = publicRoutes.find(route => route.path === path);
    const authToken = request.cookies.get('token');

    if (!authToken && !publicRoute) {
        const redirectUrl = request.nextUrl.clone();
        redirectUrl.pathname = REDIRECT_WHEN_NOT_AUTHENTICATED_ROUTE;
        return NextResponse.redirect(redirectUrl);
    }

    if (authToken && publicRoute && publicRoute.whenAuthenticated === 'redirect') {
        const redirectUrl = request.nextUrl.clone();
        redirectUrl.pathname = '/';
        return NextResponse.redirect(redirectUrl);
    }

    return NextResponse.next();
}

export const config: MiddlewareConfig = {
    matcher: [
        /*
         * Match all request paths except for the ones starting with:
         * - api (API routes)
         * - _next/static (static files)
         * - _next/image (image optimization files)
         * - favicon.ico, sitemap.xml, robots.txt (metadata files)
         * - public (public assets)
         */
        '/((?!api|_next/static|_next/image|favicon.ico|sitemap.xml|robots.txt|public|logo.png).*)',
    ],
};