/**
 * User Management Service
 * Handles user-related API calls and operations
 */

import { 
  User, 
  PaginatedResponse, 
  ListQueryParams,
  API_ENDPOINTS 
} from '@/types';
import { apiCall, get, post, patch, del } from '@/lib/api';

class UserService {
  /**
   * Get list of users with pagination and filtering
   */
  async getUsers(params?: ListQueryParams): Promise<PaginatedResponse<User>> {
    try {
      const response = await get<PaginatedResponse<User>>(
        API_ENDPOINTS.USERS.LIST,
        { params }
      );
      return response;
    } catch (error) {
      console.error('Failed to fetch users:', error);
      throw error;
    }
  }

  /**
   * Get specific user by ID
   */
  async getUser(userId: string): Promise<User> {
    try {
      const url = API_ENDPOINTS.USERS.RETRIEVE.replace('{id}', userId);
      const response = await get<User>(url);
      return response;
    } catch (error) {
      console.error(`Failed to fetch user ${userId}:`, error);
      throw error;
    }
  }

  /**
   * Create new user
   */
  async createUser(userData: Partial<User>): Promise<User> {
    try {
      const response = await post<User>(
        API_ENDPOINTS.AUTH.REGISTER,
        userData
      );
      return response;
    } catch (error) {
      console.error('Failed to create user:', error);
      throw error;
    }
  }

  /**
   * Update user profile
   */
  async updateUser(userId: string, userData: Partial<User>): Promise<User> {
    try {
      const url = API_ENDPOINTS.USERS.UPDATE.replace('{id}', userId);
      const response = await patch<User>(url, userData);
      return response;
    } catch (error) {
      console.error(`Failed to update user ${userId}:`, error);
      throw error;
    }
  }

  /**
   * Delete/Deactivate user
   */
  async deleteUser(userId: string): Promise<void> {
    try {
      const url = API_ENDPOINTS.USERS.DELETE.replace('{id}', userId);
      await del(url);
    } catch (error) {
      console.error(`Failed to delete user ${userId}:`, error);
      throw error;
    }
  }

  /**
   * Search users by query
   */
  async searchUsers(query: string, limit: number = 10): Promise<User[]> {
    try {
      const response = await this.getUsers({
        search: query,
        page_size: limit,
      });
      return response.results;
    } catch (error) {
      console.error('Failed to search users:', error);
      throw error;
    }
  }

  /**
   * Get users by role/user_type
   */
  async getUsersByRole(userType: string, params?: ListQueryParams): Promise<User[]> {
    try {
      const response = await this.getUsers({
        ...params,
        user_type: userType,
      });
      return response.results;
    } catch (error) {
      console.error(`Failed to fetch users by role ${userType}:`, error);
      throw error;
    }
  }

  /**
   * Get active users only
   */
  async getActiveUsers(params?: ListQueryParams): Promise<User[]> {
    try {
      const response = await this.getUsers({
        ...params,
        is_active: true,
      });
      return response.results;
    } catch (error) {
      console.error('Failed to fetch active users:', error);
      throw error;
    }
  }

  /**
   * Get staff users
   */
  async getStaffUsers(params?: ListQueryParams): Promise<User[]> {
    try {
      const response = await this.getUsers({
        ...params,
        is_staff: true,
      });
      return response.results;
    } catch (error) {
      console.error('Failed to fetch staff users:', error);
      throw error;
    }
  }

  /**
   * Update user status (activate/deactivate)
   */
  async updateUserStatus(userId: string, isActive: boolean): Promise<User> {
    try {
      return await this.updateUser(userId, { is_active: isActive });
    } catch (error) {
      console.error(`Failed to update user status ${userId}:`, error);
      throw error;
    }
  }

  /**
   * Bulk update users
   */
  async bulkUpdateUsers(userIds: string[], updateData: Partial<User>): Promise<User[]> {
    try {
      const promises = userIds.map(id => this.updateUser(id, updateData));
      const results = await Promise.all(promises);
      return results;
    } catch (error) {
      console.error('Failed to bulk update users:', error);
      throw error;
    }
  }

  /**
   * Get user statistics
   */
  async getUserStats(): Promise<{
    total: number;
    active: number;
    inactive: number;
    byRole: Record<string, number>;
  }> {
    try {
      // This would typically be a dedicated endpoint
      // For now, we'll fetch all users and calculate stats
      const allUsers = await this.getUsers({ page_size: 1000 });
      
      const stats = allUsers.results.reduce((acc, user) => {
        acc.total++;
        if (user.is_active) acc.active++;
        else acc.inactive++;
        
        if (user.user_type) {
          acc.byRole[user.user_type] = (acc.byRole[user.user_type] || 0) + 1;
        }
        
        return acc;
      }, {
        total: 0,
        active: 0,
        inactive: 0,
        byRole: {} as Record<string, number>,
      });
      
      return stats;
    } catch (error) {
      console.error('Failed to get user statistics:', error);
      throw error;
    }
  }

  /**
   * Validate user email availability
   */
  async isEmailAvailable(email: string, excludeUserId?: string): Promise<boolean> {
    try {
      const users = await this.searchUsers(email, 1);
      
      if (excludeUserId) {
        return !users.some(user => user.email === email && user.id !== excludeUserId);
      }
      
      return !users.some(user => user.email === email);
    } catch (error) {
      console.error('Failed to check email availability:', error);
      return false;
    }
  }

  /**
   * Get user permissions and groups
   */
  async getUserPermissions(userId: string): Promise<{
    permissions: string[];
    groups: string[];
  }> {
    try {
      const user = await this.getUser(userId);
      return {
        permissions: user.permissions || [],
        groups: user.groups || [],
      };
    } catch (error) {
      console.error(`Failed to get user permissions ${userId}:`, error);
      throw error;
    }
  }

  /**
   * Update user permissions
   */
  async updateUserPermissions(
    userId: string, 
    permissions: string[],
    groups?: string[]
  ): Promise<User> {
    try {
      const updateData: Partial<User> = { permissions };
      if (groups) {
        updateData.groups = groups;
      }
      
      return await this.updateUser(userId, updateData);
    } catch (error) {
      console.error(`Failed to update user permissions ${userId}:`, error);
      throw error;
    }
  }

  /**
   * Get users with specific permission
   */
  async getUsersWithPermission(permission: string): Promise<User[]> {
    try {
      // This would typically be a dedicated endpoint
      // For now, we'll fetch all users and filter
      const allUsers = await this.getUsers({ page_size: 1000 });
      
      return allUsers.results.filter(user => {
        return user.permissions?.includes(permission) || 
               user.is_superuser || 
               user.is_staff;
      });
    } catch (error) {
      console.error(`Failed to get users with permission ${permission}:`, error);
      throw error;
    }
  }

  /**
   * Export users data
   */
  async exportUsers(format: 'csv' | 'json' = 'csv', filters?: ListQueryParams): Promise<Blob> {
    try {
      const response = await apiCall({
        method: 'GET',
        url: `${API_ENDPOINTS.USERS.LIST}export/`,
        params: {
          format,
          ...filters,
        },
        responseType: 'blob',
      });
      
      return response;
    } catch (error) {
      console.error('Failed to export users:', error);
      throw error;
    }
  }

  /**
   * Import users from file
   */
  async importUsers(file: File): Promise<{
    success: number;
    errors: Array<{ row: number; error: string }>;
  }> {
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await apiCall({
        method: 'POST',
        url: `${API_ENDPOINTS.USERS.LIST}import/`,
        data: formData,
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      return response;
    } catch (error) {
      console.error('Failed to import users:', error);
      throw error;
    }
  }
}

// Export singleton instance
export const userService = new UserService();
export default userService;