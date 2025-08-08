'use client';

import React, { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { ProtectedRoute } from '@/components/auth';
import { AppLayout } from '@/components/layout';
import { productService } from '@/services';
import { Product } from '@/types';
import { Button, Card, Badge, Alert, AlertDescription } from '@/components/ui';
import Link from 'next/link';
import { 
  Pencil, 
  Trash, 
  ArrowLeft, 
  Package, 
  DollarSign, 
  Warehouse, 
  Tag, 
  Calendar, 
  User,
  MoreVertical,
  ExternalLink
} from 'lucide-react';

export default function ProductDetailsPage() {
  const params = useParams();
  const router = useRouter();
  const id = params.id as string;
  const [product, setProduct] = useState<Product | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchProduct = async () => {
      try {
        const data = await productService.getProduct(id);
        setProduct(data);
      } catch (err) {
        setError('Failed to load product');
      } finally {
        setLoading(false);
      }
    };
    fetchProduct();
  }, [id]);

  const handleDelete = async () => {
    if (confirm('Are you sure you want to delete this product? This action cannot be undone.')) {
      try {
        await productService.deleteProduct(id);
        router.push('/products');
      } catch (err) {
        setError('Failed to delete product');
      }
    }
  };

  const getStockStatus = (quantity: number) => {
    if (quantity === 0) return { label: 'Out of Stock', variant: 'error' as const, color: 'text-red-600' };
    if (quantity < 10) return { label: 'Low Stock', variant: 'warning' as const, color: 'text-orange-600' };
    return { label: 'In Stock', variant: 'success' as const, color: 'text-green-600' };
  };

  if (loading) {
    return (
      <ProtectedRoute allowedRoles={['Owner', 'Admin', 'Manager', 'Stocker']}>
        <AppLayout title="Product Details">
          <div className="flex items-center justify-center min-h-64">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-4 text-gray-600">Loading product details...</p>
            </div>
          </div>
        </AppLayout>
      </ProtectedRoute>
    );
  }

  if (error || !product) {
    return (
      <ProtectedRoute allowedRoles={['Owner', 'Admin', 'Manager', 'Stocker']}>
        <AppLayout title="Product Details">
          <div className="space-y-6">
            <Alert variant="destructive">
              <AlertDescription>{error || 'Product not found'}</AlertDescription>
            </Alert>
            <div className="flex justify-center">
              <Link href="/products">
                <Button variant="outline">
                  <ArrowLeft className="w-4 h-4 mr-2" />
                  Back to Products
                </Button>
              </Link>
            </div>
          </div>
        </AppLayout>
      </ProtectedRoute>
    );
  }

  const stockStatus = getStockStatus(product.quantity);

  return (
    <ProtectedRoute allowedRoles={['Owner', 'Admin', 'Manager', 'Stocker']}>
      <AppLayout 
        title="Product Details"
        breadcrumbs={[
          { label: 'Dashboard', href: '/dashboard' },
          { label: 'Products', href: '/products' },
          { label: product.name }
        ]}
      >
        <div className="space-y-6">
          {/* Header */}
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <div className="flex items-center gap-3">
              <Link href="/products">
                <Button variant="ghost" size="sm">
                  <ArrowLeft className="w-4 h-4" />
                </Button>
              </Link>
              <div>
                <h2 className="text-xl font-semibold text-gray-900">{product.name}</h2>
                <p className="text-sm text-gray-500">Product Details</p>
              </div>
            </div>
            
            <div className="flex items-center gap-2">
              <Button variant="outline" size="sm">
                <MoreVertical className="w-4 h-4" />
              </Button>
              <Link href={`/products/${id}/edit`}>
                <Button variant="outline" size="sm">
                  <Pencil className="w-4 h-4 mr-2" />
                  Edit
                </Button>
              </Link>
              <Button 
                variant="outline" 
                size="sm" 
                className="text-red-600 hover:text-red-700 hover:bg-red-50 border-red-200"
                onClick={handleDelete}
              >
                <Trash className="w-4 h-4 mr-2" />
                Delete
              </Button>
            </div>
          </div>

          {/* Main Content */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left Column - Main Info */}
            <div className="lg:col-span-2 space-y-6">
              {/* Product Overview */}
              <Card>
                <Card.Header>
                  <h3 className="text-lg font-medium">Product Overview</h3>
                </Card.Header>
                <Card.Content>
                  <div className="space-y-4">
                    <div>
                      <h4 className="text-sm font-medium text-gray-500 mb-1">Name</h4>
                      <p className="text-lg font-semibold text-gray-900">{product.name}</p>
                    </div>
                    
                    {product.description && (
                      <div>
                        <h4 className="text-sm font-medium text-gray-500 mb-1">Description</h4>
                        <p className="text-gray-700">{product.description}</p>
                      </div>
                    )}
                    
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <h4 className="text-sm font-medium text-gray-500 mb-1">Category</h4>
                        <div className="flex items-center">
                          <Tag className="w-4 h-4 text-gray-400 mr-2" />
                          <span className="text-gray-900">{product._category || 'Not specified'}</span>
                        </div>
                      </div>
                      
                      <div>
                        <h4 className="text-sm font-medium text-gray-500 mb-1">Brand</h4>
                        <div className="flex items-center">
                          <Package className="w-4 h-4 text-gray-400 mr-2" />
                          <span className="text-gray-900">{product._brand || 'Not specified'}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </Card.Content>
              </Card>

              {/* Pricing & Inventory */}
              <Card>
                <Card.Header>
                  <h3 className="text-lg font-medium">Pricing & Inventory</h3>
                </Card.Header>
                <Card.Content>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="text-center p-4 bg-blue-50 rounded-lg">
                      <DollarSign className="w-8 h-8 text-blue-600 mx-auto mb-2" />
                      <p className="text-sm text-blue-600 font-medium">Price</p>
                      <p className="text-2xl font-bold text-blue-800">${product.price.toFixed(2)}</p>
                    </div>
                    
                    <div className="text-center p-4 bg-gray-50 rounded-lg">
                      <Warehouse className="w-8 h-8 text-gray-600 mx-auto mb-2" />
                      <p className="text-sm text-gray-600 font-medium">Stock Quantity</p>
                      <p className="text-2xl font-bold text-gray-800">{product.quantity}</p>
                    </div>
                    
                    <div className="text-center p-4 bg-green-50 rounded-lg">
                      <Package className="w-8 h-8 text-green-600 mx-auto mb-2" />
                      <p className="text-sm text-green-600 font-medium">Status</p>
                      <Badge variant={stockStatus.variant} className="mt-1">
                        {stockStatus.label}
                      </Badge>
                    </div>
                  </div>
                </Card.Content>
              </Card>

              {/* SKUs */}
              {product.skus && product.skus.length > 0 && (
                <Card>
                  <Card.Header>
                    <h3 className="text-lg font-medium">Product SKUs</h3>
                  </Card.Header>
                  <Card.Content>
                    <div className="space-y-2">
                      {product.skus.map((sku, index) => (
                        <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                          <span className="font-mono text-sm">{sku.sku}</span>
                          <Button variant="ghost" size="sm">
                            <ExternalLink className="w-4 h-4" />
                          </Button>
                        </div>
                      ))}
                    </div>
                  </Card.Content>
                </Card>
              )}

              {/* Store IDs */}
              {product.store_ids && product.store_ids.length > 0 && (
                <Card>
                  <Card.Header>
                    <h3 className="text-lg font-medium">Store Locations</h3>
                  </Card.Header>
                  <Card.Content>
                    <div className="space-y-2">
                      {product.store_ids.map((store, index) => (
                        <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                          <span className="text-sm">{store.in_store_id}</span>
                          <Button variant="ghost" size="sm">
                            <ExternalLink className="w-4 h-4" />
                          </Button>
                        </div>
                      ))}
                    </div>
                  </Card.Content>
                </Card>
              )}
            </div>

            {/* Right Column - Metadata */}
            <div className="space-y-6">
              {/* Quick Stats */}
              <Card>
                <Card.Header>
                  <h3 className="text-lg font-medium">Quick Stats</h3>
                </Card.Header>
                <Card.Content>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-500">Total Value</span>
                      <span className="font-semibold">${(product.price * product.quantity).toFixed(2)}</span>
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-500">Stock Status</span>
                      <span className={`font-medium ${stockStatus.color}`}>
                        {stockStatus.label}
                      </span>
                    </div>
                  </div>
                </Card.Content>
              </Card>

              {/* Metadata */}
              <Card>
                <Card.Header>
                  <h3 className="text-lg font-medium">Metadata</h3>
                </Card.Header>
                <Card.Content>
                  <div className="space-y-4">
                    <div>
                      <h4 className="text-sm font-medium text-gray-500 mb-1">Created</h4>
                      <div className="flex items-center text-sm text-gray-600">
                        <Calendar className="w-4 h-4 mr-2" />
                        {new Date(product.created_at).toLocaleDateString()}
                      </div>
                    </div>
                    
                    <div>
                      <h4 className="text-sm font-medium text-gray-500 mb-1">Last Updated</h4>
                      <div className="flex items-center text-sm text-gray-600">
                        <Calendar className="w-4 h-4 mr-2" />
                        {new Date(product.updated_at).toLocaleDateString()}
                      </div>
                    </div>
                    
                    {product.created_by && (
                      <div>
                        <h4 className="text-sm font-medium text-gray-500 mb-1">Created By</h4>
                        <div className="flex items-center text-sm text-gray-600">
                          <User className="w-4 h-4 mr-2" />
                          {product.created_by}
                        </div>
                      </div>
                    )}
                    
                    {product.updated_by && (
                      <div>
                        <h4 className="text-sm font-medium text-gray-500 mb-1">Updated By</h4>
                        <div className="flex items-center text-sm text-gray-600">
                          <User className="w-4 h-4 mr-2" />
                          {product.updated_by}
                        </div>
                      </div>
                    )}
                  </div>
                </Card.Content>
              </Card>

              {/* Actions */}
              <Card>
                <Card.Header>
                  <h3 className="text-lg font-medium">Actions</h3>
                </Card.Header>
                <Card.Content>
                  <div className="space-y-3">
                    <Link href={`/products/${id}/edit`} className="block">
                      <Button variant="outline" className="w-full justify-start">
                        <Pencil className="w-4 h-4 mr-2" />
                        Edit Product
                      </Button>
                    </Link>
                    
                    <Button variant="outline" className="w-full justify-start">
                      <Package className="w-4 h-4 mr-2" />
                      Duplicate Product
                    </Button>
                    
                    <Button 
                      variant="outline" 
                      className="w-full justify-start text-red-600 hover:text-red-700 hover:bg-red-50 border-red-200"
                      onClick={handleDelete}
                    >
                      <Trash className="w-4 h-4 mr-2" />
                      Delete Product
                    </Button>
                  </div>
                </Card.Content>
              </Card>
            </div>
          </div>
        </div>
      </AppLayout>
    </ProtectedRoute>
  );
}