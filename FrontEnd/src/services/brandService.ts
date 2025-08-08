/**
 * Brand Management Service
 * Handles brand-related API calls
 */

import { Brand, PaginatedResponse, ListQueryParams, API_ENDPOINTS } from '@/types';
import { get, post, put, patch, del } from '@/lib/api';

class BrandService {
  /**
   * Get list of brands
   */
  async getBrands(params?: ListQueryParams): Promise<PaginatedResponse<Brand>> {
    try {
      const response = await get<PaginatedResponse<Brand>>(
        API_ENDPOINTS.BRANDS.LIST,
        { params }
      );
      return response;
    } catch (error) {
      console.error('Failed to fetch brands:', error);
      throw error;
    }
  }

  /**
   * Get specific brand by ID
   */
  async getBrand(brandId: string): Promise<Brand> {
    try {
      const url = API_ENDPOINTS.BRANDS.RETRIEVE.replace('{id}', brandId);
      const response = await get<Brand>(url);
      return response;
    } catch (error) {
      console.error(`Failed to fetch brand ${brandId}:`, error);
      throw error;
    }
  }

  /**
   * Create new brand
   */
  async createBrand(brandData: Partial<Brand>): Promise<Brand> {
    try {
      const response = await post<Brand>(
        API_ENDPOINTS.BRANDS.CREATE,
        brandData
      );
      return response;
    } catch (error) {
      console.error('Failed to create brand:', error);
      throw error;
    }
  }

  /**
   * Update brand (partial update using PATCH)
   */
  async updateBrand(brandId: string, brandData: Partial<Brand>): Promise<Brand> {
    try {
      const url = API_ENDPOINTS.BRANDS.UPDATE.replace('{id}', brandId);
      const response = await patch<Brand>(url, brandData);
      return response;
    } catch (error) {
      console.error(`Failed to update brand ${brandId}:`, error);
      throw error;
    }
  }

  /**
   * Delete brand
   */
  async deleteBrand(brandId: string): Promise<void> {
    try {
      const url = API_ENDPOINTS.BRANDS.DELETE.replace('{id}', brandId);
      await del<void>(url);
    } catch (error) {
      console.error(`Failed to delete brand ${brandId}:`, error);
      throw error;
    }
  }
}

// Export singleton instance
export const brandService = new BrandService();
export default brandService;