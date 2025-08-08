/**
 * Product Management Service
 * Handles product-related API calls and operations
 */

import {
    Product,
    PaginatedResponse,
    ListQueryParams,
    API_ENDPOINTS
} from '@/types';
import { apiCall, get, post, put, patch, del } from '@/lib/api';

class ProductService {
    /**
     * Get list of products with pagination and filtering
     */
    async getProducts(params?: ListQueryParams): Promise<PaginatedResponse<Product>> {
        try {
            const response = await get<PaginatedResponse<Product>>(
                API_ENDPOINTS.PRODUCTS.LIST,
                { params }
            );
            return response;
        } catch (error) {
            console.error('Failed to fetch products:', error);
            throw error;
        }
    }

    /**
     * Get specific product by ID
     */
    async getProduct(productId: string): Promise<Product> {
        try {
            const url = API_ENDPOINTS.PRODUCTS.RETRIEVE.replace('{id}', productId);
            const response = await get<Product>(url);
            return response;
        } catch (error) {
            console.error(`Failed to fetch product ${productId}:`, error);
            throw error;
        }
    }

    /**
     * Create new product
     */
    async createProduct(productData: Partial<Product>): Promise<Product> {
        try {
            const response = await post<Product>(
                API_ENDPOINTS.PRODUCTS.CREATE,
                productData
            );
            return response;
        } catch (error) {
            console.error('Failed to create product:', error);
            throw error;
        }
    }

    /**
     * Update product (partial update using PATCH)
     */
    async updateProduct(productId: string, productData: Partial<Product>): Promise<Product> {
        try {
            const url = API_ENDPOINTS.PRODUCTS.UPDATE.replace('{id}', productId);
            const response = await patch<Product>(url, productData);
            return response;
        } catch (error) {
            console.error(`Failed to update product ${productId}:`, error);
            throw error;
        }
    }

    /**
     * Delete product
     */
    async deleteProduct(productId: string): Promise<void> {
        try {
            const url = API_ENDPOINTS.PRODUCTS.DELETE.replace('{id}', productId);
            await del<void>(url);
        } catch (error) {
            console.error(`Failed to delete product ${productId}:`, error);
            throw error;
        }
    }

    /**
     * Execute Home Depot action (search or update)
     */
    async homeDepotAction(action: 'search' | 'update', productId?: string): Promise<any> {
        try {
            let url = API_ENDPOINTS.PRODUCTS.HD_ACTIONS.replace('{action}', action);
            if (productId) {
                url += `?pk=${productId}`;
            }
            const response = await post<any>(url);
            return response;
        } catch (error) {
            console.error(`Failed to execute Home Depot ${action}:`, error);
            throw error;
        }
    }
}

// Export singleton instance
export const productService = new ProductService();
export default productService; 