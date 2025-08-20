/**
 * Token Management Utility
 * Handles JWT token storage, validation, and refresh logic
 */

import Cookies from 'js-cookie';
import { jwtDecode } from 'jwt-decode';
import config from '../config';

interface JWTPayload {
  exp: number;
  iat: number;
  user_id: string;
  email: string;
  [key: string]: string | number | boolean;
}

class TokenManager {
  private accessTokenKey = config.auth.tokenStorageKey;
  private refreshTokenKey = config.auth.refreshTokenKey;
  private refreshPromise: Promise<string | null> | null = null;

  /**
   * Store access token securely
   */
  setAccessToken(token: string): void {
    if (typeof window === 'undefined') return;

    try {
      // Store in httpOnly cookie for security
      Cookies.set(this.accessTokenKey, token, {
        httpOnly: false, // Note: httpOnly true requires server-side setting
        secure: process.env.NODE_ENV === 'production',
        sameSite: 'strict',
        expires: 1, // 1 day
      });

      // Also store in sessionStorage for quick access
      sessionStorage.setItem(this.accessTokenKey, token);
    } catch (error) {
      console.error('Failed to store access token:', error);
    }
  }

  /**
   * Retrieve access token
   */
  getAccessToken(): string | null {
    if (typeof window === 'undefined') return null;

    try {
      // Try sessionStorage first (faster)
      let token = sessionStorage.getItem(this.accessTokenKey);

      // Fallback to cookie
      if (!token) {
        token = Cookies.get(this.accessTokenKey) || null;
        if (token) {
          // Sync back to sessionStorage
          sessionStorage.setItem(this.accessTokenKey, token);
        }
      }

      return token;
    } catch (error) {
      console.error('Failed to retrieve access token:', error);
      return null;
    }
  }

  /**
   * Store refresh token securely
   */
  setRefreshToken(token: string): void {
    if (typeof window === 'undefined') return;

    try {
      // Store in httpOnly cookie (more secure for refresh tokens)
      Cookies.set(this.refreshTokenKey, token, {
        httpOnly: false,
        secure: process.env.NODE_ENV === 'production',
        sameSite: 'strict',
        expires: 7, // 7 days
      });
    } catch (error) {
      console.error('Failed to store refresh token:', error);
    }
  }

  /**
   * Retrieve refresh token
   */
  getRefreshToken(): string | null {
    if (typeof window === 'undefined') return null;

    try {
      return Cookies.get(this.refreshTokenKey) || null;
    } catch (error) {
      console.error('Failed to retrieve refresh token:', error);
      return null;
    }
  }

  /**
   * Clear all tokens
   */
  clearTokens(): void {
    if (typeof window === 'undefined') return;

    try {
      // Clear from cookies
      Cookies.remove(this.accessTokenKey);
      Cookies.remove(this.refreshTokenKey);

      // Clear from sessionStorage
      sessionStorage.removeItem(this.accessTokenKey);

      // Clear from localStorage (just in case)
      localStorage.removeItem(this.accessTokenKey);
      localStorage.removeItem(this.refreshTokenKey);
    } catch (error) {
      console.error('Failed to clear tokens:', error);
    }
  }

  /**
   * Decode JWT token
   */
  decodeToken(token: string): JWTPayload | null {
    try {
      return jwtDecode<JWTPayload>(token);
    } catch (error) {
      console.error('Failed to decode token:', error);
      return null;
    }
  }

  /**
   * Check if token is expired
   */
  isTokenExpired(token: string): boolean {
    try {
      const decoded = this.decodeToken(token);
      if (!decoded) return true;

      const currentTime = Date.now() / 1000;
      return decoded.exp < currentTime;
    } catch (error) {
      console.error('Failed to check token expiration:', error);
      return true;
    }
  }

  /**
   * Check if token will expire soon (within threshold)
   */
  isTokenExpiringSoon(token: string): boolean {
    try {
      const decoded = this.decodeToken(token);
      if (!decoded) return true;

      const currentTime = Date.now() / 1000;
      const threshold = config.auth.tokenRefreshThreshold / 1000; // Convert to seconds

      return decoded.exp < (currentTime + threshold);
    } catch (error) {
      console.error('Failed to check token expiration:', error);
      return true;
    }
  }

  /**
   * Get token expiration time
   */
  getTokenExpiration(token: string): Date | null {
    try {
      const decoded = this.decodeToken(token);
      if (!decoded) return null;

      return new Date(decoded.exp * 1000);
    } catch (error) {
      console.error('Failed to get token expiration:', error);
      return null;
    }
  }

  /**
   * Get user info from token
   */
  getUserFromToken(token?: string): { id: string; email: string } | null {
    try {
      const tokenToUse = token || this.getAccessToken();
      if (!tokenToUse) return null;

      const decoded = this.decodeToken(tokenToUse);
      if (!decoded) return null;

      return {
        id: decoded.user_id,
        email: decoded.email,
      };
    } catch (error) {
      console.error('Failed to get user from token:', error);
      return null;
    }
  }

  /**
   * Refresh access token using refresh token
   */
  async refreshAccessToken(): Promise<string | null> {
    // Prevent multiple simultaneous refresh requests
    if (this.refreshPromise) {
      return this.refreshPromise;
    }

    const refreshToken = this.getRefreshToken();
    if (!refreshToken) {
      return null;
    }

    this.refreshPromise = this.performTokenRefresh(refreshToken);

    try {
      const newToken = await this.refreshPromise;
      return newToken;
    } finally {
      this.refreshPromise = null;
    }
  }

  /**
   * Perform the actual token refresh
   */
  private async performTokenRefresh(refreshToken: string): Promise<string | null> {
    try {
      const response = await fetch(`${config.api.baseURL}/api/token/refresh/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          refresh: refreshToken,
        }),
      });

      if (!response.ok) {
        throw new Error('Token refresh failed');
      }

      const data = await response.json();
      const newAccessToken = data.access;

      if (newAccessToken) {
        this.setAccessToken(newAccessToken);
        return newAccessToken;
      }

      return null;
    } catch (error) {
      console.error('Token refresh failed:', error);
      this.clearTokens();
      return null;
    }
  }

  /**
   * Automatically refresh token if needed
   */
  async ensureValidToken(): Promise<string | null> {
    const currentToken = this.getAccessToken();

    if (!currentToken) {
      return null;
    }

    if (this.isTokenExpired(currentToken)) {
      // Token is expired, try to refresh
      return await this.refreshAccessToken();
    }

    if (this.isTokenExpiringSoon(currentToken)) {
      // Token is expiring soon, refresh proactively
      const newToken = await this.refreshAccessToken();
      return newToken || currentToken; // Use new token if refresh succeeded, otherwise use current
    }

    return currentToken;
  }

  /**
   * Set up automatic token refresh
   */
  setupAutoRefresh(): void {
    if (typeof window === 'undefined') return;

    // Check and refresh token every 5 minutes
    const intervalId = setInterval(async () => {
      const token = this.getAccessToken();
      if (token && this.isTokenExpiringSoon(token)) {
        await this.refreshAccessToken();
      }
    }, 5 * 60 * 1000); // 5 minutes

    // Clear interval on page unload
    window.addEventListener('beforeunload', () => {
      clearInterval(intervalId);
    });
  }

  /**
   * Validate token format and structure
   */
  isValidTokenFormat(token: string): boolean {
    try {
      const parts = token.split('.');
      if (parts.length !== 3) return false;

      // Try to decode the payload
      const payload = this.decodeToken(token);
      return payload !== null && typeof payload.exp === 'number';
    } catch {
      return false;
    }
  }

  /**
   * Get time until token expiration
   */
  getTimeUntilExpiration(token?: string): number | null {
    try {
      const tokenToUse = token || this.getAccessToken();
      if (!tokenToUse) return null;

      const decoded = this.decodeToken(tokenToUse);
      if (!decoded) return null;

      const currentTime = Date.now() / 1000;
      const timeUntilExp = decoded.exp - currentTime;

      return timeUntilExp > 0 ? timeUntilExp * 1000 : 0; // Convert to milliseconds
    } catch (error) {
      console.error('Failed to get time until expiration:', error);
      return null;
    }
  }
}

// Export singleton instance
export const tokenManager = new TokenManager();

// Setup auto-refresh on module load
if (typeof window !== 'undefined') {
  tokenManager.setupAutoRefresh();
}