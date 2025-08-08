'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { ProtectedRoute } from '@/components/auth';
import { AppLayout } from '@/components/layout';
import { productService } from '@/services';
import { Button, Table, Alert, AlertDescription, SearchInput, Card, Badge } from '@/components/ui';
import { Pencil, Trash, Eye, Plus, Filter, Download, MoreVertical, Package } from 'lucide-react';
import Link from 'next/link';
import { Product } from '@/types';

export default function ProductsListPage() {
  const router = useRouter();
  const [products, setProducts] = useState<Product[]>([]);
  const [filteredProducts, setFilteredProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedProducts, setSelectedProducts] = useState<string[]>([]);

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const response = await productService.getProducts();
        setProducts(response.results);
        setFilteredProducts(response.results);
      } catch (err) {
        setError('Failed to load products');
      } finally {
        setLoading(false);
      }
    };
    fetchProducts();
  }, []);

  useEffect(() => {
    const filtered = products.filter(product =>
      product.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      product.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      product._category?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      product._brand?.toLowerCase().includes(searchTerm.toLowerCase())
    );
    setFilteredProducts(filtered);
  }, [searchTerm, products]);

  const handleDelete = async (id: string) => {
    if (confirm('Are you sure you want to delete this product?')) {
      try {
        await productService.deleteProduct(id);
        setProducts(products.filter(p => p.id !== id));
      } catch (err) {
        setError('Failed to delete product');
      }
    }
  };

  const handleSelectProduct = (id: string) => {
    setSelectedProducts(prev =>
      prev.includes(id)
        ? prev.filter(productId => productId !== id)
        : [...prev, id]
    );
  };

  const handleSelectAll = () => {
    if (selectedProducts.length === filteredProducts.length) {
      setSelectedProducts([]);
    } else {
      setSelectedProducts(filteredProducts.map(p => p.id));
    }
  };

  const getStockStatus = (quantity: number) => {
    if (quantity === 0) return { label: 'Out of Stock', variant: 'error' as const };
    if (quantity < 10) return { label: 'Low Stock', variant: 'warning' as const };
    return { label: 'In Stock', variant: 'success' as const };
  };

  const handleRowClick = (productId: string, event: React.MouseEvent) => {
    // Don't navigate if clicking on checkbox, buttons, or links
    const target = event.target as HTMLElement;
    const isInteractiveElement = target.closest('input, button, a');
    
    if (!isInteractiveElement) {
      router.push(`/products/${productId}`);
    }
  };

  if (loading) {
    return (
      <ProtectedRoute allowedRoles={['Owner', 'Admin', 'Manager', 'Stocker']}>
        <AppLayout title="Products">
          <div className="flex items-center justify-center min-h-64">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-4 text-gray-600">Loading products...</p>
            </div>
          </div>
        </AppLayout>
      </ProtectedRoute>
    );
  }

  if (error) {
    return (
      <ProtectedRoute allowedRoles={['Owner', 'Admin', 'Manager', 'Stocker']}>
        <AppLayout title="Products">
          <Alert variant="destructive">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        </AppLayout>
      </ProtectedRoute>
    );
  }

  return (
    <ProtectedRoute allowedRoles={['Owner', 'Admin', 'Manager', 'Stocker']}>
      <AppLayout 
        title="Products" 
        breadcrumbs={[
          { label: 'Dashboard', href: '/dashboard' },
          { label: 'Products' }
        ]}
      >
        <div className="space-y-6">
          {/* Page Header */}
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <div>
              <h2 className="text-lg font-medium text-gray-900">Product Management</h2>
              <p className="text-sm text-gray-500">
                Manage your inventory with {products.length} products
              </p>
            </div>
            
            <div className="flex items-center gap-3">
              <Button variant="outline" size="sm">
                <Filter className="w-4 h-4 mr-2" />
                Filter
              </Button>
              <Button variant="outline" size="sm">
                <Download className="w-4 h-4 mr-2" />
                Export
              </Button>
              <Link href="/products/create">
                <Button size="sm">
                  <Plus className="w-4 h-4 mr-2" />
                  Add Product
                </Button>
              </Link>
            </div>
          </div>

          {/* Search and Filters */}
          <Card>
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="flex-1">
                <SearchInput
                  placeholder="Search products by name, category, brand..."
                  value={searchTerm}
                  onChange={setSearchTerm}
                />
              </div>
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-500">
                  {filteredProducts.length} of {products.length} products
                </span>
              </div>
            </div>
          </Card>

          {/* Products Table */}
          <Card padding="none">
            <div className="overflow-x-auto">
              <Table>
                <Table.Header>
                  <Table.Row>
                    <Table.Head className="w-12">
                      <input
                        type="checkbox"
                        checked={selectedProducts.length === filteredProducts.length && filteredProducts.length > 0}
                        onChange={handleSelectAll}
                        className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      />
                    </Table.Head>
                    <Table.Head>Product</Table.Head>
                    <Table.Head>Category</Table.Head>
                    <Table.Head>Brand</Table.Head>
                    <Table.Head>Price</Table.Head>
                    <Table.Head>Stock</Table.Head>
                    <Table.Head>Status</Table.Head>
                    <Table.Head className="w-32">Actions</Table.Head>
                  </Table.Row>
                </Table.Header>
                <Table.Body>
                  {filteredProducts.map(product => {
                    const stockStatus = getStockStatus(product.quantity);
                    return (
                      <Table.Row 
                        key={product.id} 
                        className="hover:bg-gray-50 cursor-pointer transition-colors"
                        onClick={(e) => handleRowClick(product.id, e)}
                        title={`Click to view details of ${product.name}`}
                      >
                        <Table.Cell>
                          <input
                            type="checkbox"
                            checked={selectedProducts.includes(product.id)}
                            onChange={() => handleSelectProduct(product.id)}
                            className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                          />
                        </Table.Cell>
                        <Table.Cell>
                          <div>
                            <div className="font-medium text-blue-900 hover:text-blue-700 transition-colors">
                              {product.name}
                            </div>
                            {product.description && (
                              <div className="text-sm text-gray-500 truncate max-w-xs">
                                {product.description}
                              </div>
                            )}
                          </div>
                        </Table.Cell>
                        <Table.Cell>
                          <span className="text-sm text-gray-600">{product._category || '-'}</span>
                        </Table.Cell>
                        <Table.Cell>
                          <span className="text-sm text-gray-600">{product._brand || '-'}</span>
                        </Table.Cell>
                        <Table.Cell>
                          <span className="font-medium text-gray-900">
                            ${product.price.toFixed(2)}
                          </span>
                        </Table.Cell>
                        <Table.Cell>
                          <span className="font-medium text-gray-900">{product.quantity}</span>
                        </Table.Cell>
                        <Table.Cell>
                          <Badge variant={stockStatus.variant} size="sm">
                            {stockStatus.label}
                          </Badge>
                        </Table.Cell>
                        <Table.Cell>
                          <div className="flex items-center gap-1">
                            <Link href={`/products/${product.id}`}>
                              <Button variant="ghost" size="sm" className="p-1">
                                <Eye className="w-4 h-4" />
                              </Button>
                            </Link>
                            <Link href={`/products/${product.id}/edit`}>
                              <Button variant="ghost" size="sm" className="p-1">
                                <Pencil className="w-4 h-4" />
                              </Button>
                            </Link>
                            <Button 
                              variant="ghost" 
                              size="sm" 
                              className="p-1 text-red-600 hover:text-red-700 hover:bg-red-50"
                              onClick={() => handleDelete(product.id)}
                            >
                              <Trash className="w-4 h-4" />
                            </Button>
                            <Button variant="ghost" size="sm" className="p-1">
                              <MoreVertical className="w-4 h-4" />
                            </Button>
                          </div>
                        </Table.Cell>
                      </Table.Row>
                    );
                  })}
                </Table.Body>
              </Table>

              {filteredProducts.length === 0 && (
                <div className="text-center py-12">
                  <div className="text-gray-400 mb-4">
                    <Package className="w-12 h-12 mx-auto" />
                  </div>
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No products found</h3>
                  <p className="text-gray-500 mb-6">
                    {searchTerm ? 'Try adjusting your search terms' : 'Get started by adding your first product'}
                  </p>
                  {!searchTerm && (
                    <Link href="/products/create">
                      <Button>
                        <Plus className="w-4 h-4 mr-2" />
                        Add Product
                      </Button>
                    </Link>
                  )}
                </div>
              )}
            </div>
          </Card>

          {/* Bulk Actions */}
          {selectedProducts.length > 0 && (
            <Card>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">
                  {selectedProducts.length} product(s) selected
                </span>
                <div className="flex items-center gap-2">
                  <Button variant="outline" size="sm">
                    Bulk Edit
                  </Button>
                  <Button variant="outline" size="sm" className="text-red-600 hover:text-red-700">
                    Delete Selected
                  </Button>
                </div>
              </div>
            </Card>
          )}
        </div>
      </AppLayout>
    </ProtectedRoute>
  );
}