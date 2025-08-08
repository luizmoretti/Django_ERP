/**
 * Supplier Management Service
 * Handles supplier-related API calls and operations
 */

import { 
  Supplier, 
  PaginatedResponse, 
  ListQueryParams,
  API_ENDPOINTS 
} from '@/types';
import { apiCall, get, post, put, patch, del } from '@/lib/api';

class SupplierService {
  /**
   * Get list of suppliers with pagination and filtering
   */
  async getSuppliers(params?: ListQueryParams): Promise<PaginatedResponse<Supplier>> {
    try {
      const response = await get<PaginatedResponse<Supplier>>(
        API_ENDPOINTS.SUPPLIERS.LIST,
        { params }
      );
      return response;
    } catch (error) {
      console.error('Failed to fetch suppliers:', error);
      throw error;
    }
  }

  /**
   * Get specific supplier by ID
   */
  async getSupplier(supplierId: string): Promise<Supplier> {
    try {
      const url = API_ENDPOINTS.SUPPLIERS.RETRIEVE.replace('{id}', supplierId);
      const response = await get<Supplier>(url);
      return response;
    } catch (error) {
      console.error(`Failed to fetch supplier ${supplierId}:`, error);
      throw error;
    }
  }

  /**
   * Create new supplier
   */
  async createSupplier(supplierData: Partial<Supplier>): Promise<Supplier> {
    try {
      const response = await post<Supplier>(
        API_ENDPOINTS.SUPPLIERS.CREATE,
        supplierData
      );
      return response;
    } catch (error) {
      console.error('Failed to create supplier:', error);
      throw error;
    }
  }

  /**
   * Update supplier (partial update using PATCH)
   */
  async updateSupplier(supplierId: string, supplierData: Partial<Supplier>): Promise<Supplier> {
    try {
      const url = API_ENDPOINTS.SUPPLIERS.UPDATE.replace('{id}', supplierId);
      const response = await patch<Supplier>(url, supplierData);
      return response;
    } catch (error) {
      console.error(`Failed to update supplier ${supplierId}:`, error);
      throw error;
    }
  }

  /**
   * Delete supplier
   */
  async deleteSupplier(supplierId: string): Promise<void> {
    try {
      const url = API_ENDPOINTS.SUPPLIERS.DELETE.replace('{id}', supplierId);
      await del<void>(url);
    } catch (error) {
      console.error(`Failed to delete supplier ${supplierId}:`, error);
      throw error;
    }
  }
}

// Export singleton instance
export const supplierService = new SupplierService();
export default supplierService; 