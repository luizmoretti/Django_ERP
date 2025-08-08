/**
 * Authentication Service
 * Handles all authentication-related API calls and business logic
 */

import { 
  User, 
  LoginRequest, 
  LoginResponse, 
  RegisterRequest, 
  PasswordResetRequest, 
  PasswordResetConfirm,
  API_ENDPOINTS 
} from '@/types';
import { apiCall, post, get } from '@/lib/api';
import { tokenManager } from '@/lib/auth/tokenManager';

class AuthService {
  /**
   * Login user with email and password
   */
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    try {
      const response = await post<LoginResponse>(
        API_ENDPOINTS.AUTH.LOGIN,
        credentials
      );

      // Store the JWT token
      if (response.token) {
        tokenManager.setAccessToken(response.token);
      }

      return response;
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    }
  }

  /**
   * Register new user account
   */
  async register(userData: RegisterRequest): Promise<User> {
    try {
      const response = await post<User>(
        API_ENDPOINTS.AUTH.REGISTER,
        userData
      );

      return response;
    } catch (error) {
      console.error('Registration failed:', error);
      throw error;
    }
  }

  /**
   * Logout user and clear tokens
   */
  async logout(): Promise<void> {
    try {
      // Call logout endpoint if token exists
      const token = tokenManager.getAccessToken();
      if (token) {
        try {
          await post(API_ENDPOINTS.AUTH.LOGOUT);
        } catch (error) {
          // Logout endpoint might fail if token is invalid, but we still want to clear local tokens
          console.warn('Logout endpoint failed:', error);
        }
      }
    } finally {
      // Always clear tokens locally
      tokenManager.clearTokens();
    }
  }

  /**
   * Get current authenticated user profile
   */
  async getCurrentUser(): Promise<User> {
    try {
      const response = await get<User>(API_ENDPOINTS.AUTH.ME);
      return response;
    } catch (error) {
      console.error('Failed to get current user:', error);
      throw error;
    }
  }

  /**
   * Update current user profile
   */
  async updateProfile(profileData: Partial<User>): Promise<User> {
    try {
      // Get the current user first to get the user ID
      const currentUser = await this.getCurrentUser();
      
      const response = await apiCall<User>({
        method: 'PATCH',
        url: API_ENDPOINTS.USERS.UPDATE.replace('{id}', currentUser.id),
        data: profileData,
      });

      return response;
    } catch (error) {
      console.error('Failed to update profile:', error);
      throw error;
    }
  }

  /**
   * Request password reset email
   */
  async requestPasswordReset(email: string): Promise<void> {
    try {
      await post(API_ENDPOINTS.AUTH.PASSWORD_RESET, { email });
    } catch (error) {
      console.error('Password reset request failed:', error);
      throw error;
    }
  }

  /**
   * Confirm password reset with token
   */
  async confirmPasswordReset(
    uidb64: string, 
    token: string, 
    passwords: PasswordResetConfirm
  ): Promise<void> {
    try {
      const url = API_ENDPOINTS.AUTH.PASSWORD_RESET_CONFIRM
        .replace('{uidb64}', uidb64)
        .replace('{token}', token);

      await post(url, passwords);
    } catch (error) {
      console.error('Password reset confirmation failed:', error);
      throw error;
    }
  }

  /**
   * Validate password reset token
   */
  async validatePasswordResetToken(uidb64: string, token: string): Promise<boolean> {
    try {
      const url = API_ENDPOINTS.AUTH.PASSWORD_RESET_CONFIRM
        .replace('{uidb64}', uidb64)
        .replace('{token}', token);

      await get(url);
      return true;
    } catch (error) {
      console.error('Password reset token validation failed:', error);
      return false;
    }
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    const token = tokenManager.getAccessToken();
    if (!token) return false;
    
    return !tokenManager.isTokenExpired(token);
  }

  /**
   * Get user info from current token
   */
  getUserFromToken(): { id: string; email: string } | null {
    return tokenManager.getUserFromToken();
  }

  /**
   * Refresh authentication token
   */
  async refreshToken(): Promise<string | null> {
    try {
      return await tokenManager.refreshAccessToken();
    } catch (error) {
      console.error('Token refresh failed:', error);
      return null;
    }
  }

  /**
   * Ensure user has valid authentication token
   */
  async ensureAuthenticated(): Promise<boolean> {
    try {
      const token = await tokenManager.ensureValidToken();
      return token !== null;
    } catch (error) {
      console.error('Authentication check failed:', error);
      return false;
    }
  }

  /**
   * Check if user has specific permission
   */
  hasPermission(user: User | null, permission: string): boolean {
    if (!user) return false;
    
    // Admins and superusers have all permissions
    if (user.is_superuser || user.is_staff) return true;
    
    // Check user permissions
    if (user.permissions?.includes(permission)) return true;
    
    // Check group permissions (if groups have permissions)
    // This would need to be implemented based on your group structure
    
    return false;
  }

  /**
   * Check if user has specific role/user_type
   */
  hasRole(user: User | null, role: string): boolean {
    if (!user) return false;
    return user.user_type === role;
  }

  /**
   * Check if user has any of the specified roles
   */
  hasAnyRole(user: User | null, roles: string[]): boolean {
    if (!user) return false;
    return roles.includes(user.user_type || '');
  }

  /**
   * Get user's role hierarchy level (for access control)
   */
  getUserRoleLevel(user: User | null): number {
    if (!user || !user.user_type) return 0;
    
    const roleHierarchy: Record<string, number> = {
      'CEO': 100,
      'Owner': 95,
      'Admin': 90,
      'Manager': 80,
      'Employee': 60,
      'Installer': 55,
      'Stocker': 50,
      'Salesman': 50,
      'Driver': 45,
      'Customer': 20,
      'Supplier': 15,
    };
    
    return roleHierarchy[user.user_type] || 0;
  }

  /**
   * Check if user can access resource based on role hierarchy
   */
  canAccessResource(user: User | null, requiredLevel: number): boolean {
    const userLevel = this.getUserRoleLevel(user);
    return userLevel >= requiredLevel;
  }

  /**
   * Validate password strength
   */
  validatePassword(password: string): { isValid: boolean; errors: string[] } {
    const errors: string[] = [];
    
    if (password.length < 8) {
      errors.push('Password must be at least 8 characters long');
    }
    
    if (!/[a-z]/.test(password)) {
      errors.push('Password must contain at least one lowercase letter');
    }
    
    if (!/[A-Z]/.test(password)) {
      errors.push('Password must contain at least one uppercase letter');
    }
    
    if (!/\d/.test(password)) {
      errors.push('Password must contain at least one number');
    }
    
    if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
      errors.push('Password must contain at least one special character');
    }
    
    return {
      isValid: errors.length === 0,
      errors,
    };
  }

  /**
   * Generate password strength score
   */
  getPasswordStrength(password: string): { score: number; feedback: string } {
    let score = 0;
    let feedback = 'Very Weak';
    
    if (password.length >= 8) score += 20;
    if (password.length >= 12) score += 10;
    if (/[a-z]/.test(password)) score += 15;
    if (/[A-Z]/.test(password)) score += 15;
    if (/\d/.test(password)) score += 15;
    if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) score += 15;
    if (password.length >= 16) score += 10;
    
    if (score >= 90) feedback = 'Very Strong';
    else if (score >= 70) feedback = 'Strong';
    else if (score >= 50) feedback = 'Moderate';
    else if (score >= 30) feedback = 'Weak';
    
    return { score, feedback };
  }
}

// Export singleton instance
export const authService = new AuthService();
export default authService;