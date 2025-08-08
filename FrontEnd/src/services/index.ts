/**
 * Services Index
 * Central export point for all service modules
 */

import { authService } from './authService';
import { userService } from './userService';
import { productService } from './productService';
import { supplierService } from './supplierService';
import { brandService } from './brandService';

// Named exports
export { authService, default as AuthService } from './authService';
export { userService, default as UserService } from './userService';
export { productService, default as ProductService } from './productService';
export { supplierService, default as SupplierService } from './supplierService';
export { brandService, default as BrandService } from './brandService';

// Re-export service instances for convenience
export const services = {
  auth: authService,
  user: userService,
  product: productService,
  supplier: supplierService,
  brand: brandService,
} as const;

export default services;