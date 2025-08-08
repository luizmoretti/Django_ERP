'use client';

import React, { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { ProtectedRoute } from '@/components/auth';
import { AppLayout } from '@/components/layout';
import { productService, brandService, supplierService } from '@/services';
import { Product, Brand, Supplier } from '@/types';
import { Button, Input, Card, Alert, AlertDescription, Select, ConfirmDialog } from '@/components/ui';
import { BrandModal, SupplierModal, CategoryModal } from '@/components/modals';
import Link from 'next/link';
import { ArrowLeft, Save, X, Plus, Trash, Edit, PlusCircle } from 'lucide-react';

interface FormData {
  name: string;
  description: string;
  price: number;
  quantity: number;
  brand: string;
  category: string;
  supplier: string;
  skus: { sku: string }[];
  store_ids: { in_store_id: string }[];
}

export default function ProductEditPage() {
  const params = useParams();
  const router = useRouter();
  const id = params.id as string;
  const [product, setProduct] = useState<Product | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [brands, setBrands] = useState<Brand[]>([]);
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [loadingBrands, setLoadingBrands] = useState(false);
  const [loadingSuppliers, setLoadingSuppliers] = useState(false);
  
  // Modal states
  const [brandModal, setBrandModal] = useState<{ isOpen: boolean; mode: 'create' | 'edit'; brand?: Brand }>(
    { isOpen: false, mode: 'create' }
  );
  const [supplierModal, setSupplierModal] = useState<{ isOpen: boolean; mode: 'create' | 'edit'; supplier?: Supplier }>(
    { isOpen: false, mode: 'create' }
  );
  const [categoryModal, setCategoryModal] = useState<{ isOpen: boolean; mode: 'create' | 'edit' }>(
    { isOpen: false, mode: 'create' }
  );
  const [deleteDialog, setDeleteDialog] = useState<{ isOpen: boolean; type: 'brand' | 'supplier'; item?: any }>(
    { isOpen: false, type: 'brand' }
  );
  const [deleting, setDeleting] = useState(false);
  
  const [formData, setFormData] = useState<FormData>({
    name: '',
    description: '',
    price: 0,
    quantity: 0,
    brand: '',
    category: '',
    supplier: '',
    skus: [],
    store_ids: [],
  });

  useEffect(() => {
    const loadData = async () => {
      setLoadingBrands(true);
      setLoadingSuppliers(true);

      try {
        // Load all data in parallel
        const [brandsResponse, suppliersResponse, productData] = await Promise.all([
          brandService.getBrands().catch(err => {
            console.error('Failed to load brands:', err);
            return { results: [], data: [] };
          }),
          supplierService.getSuppliers().catch(err => {
            console.error('Failed to load suppliers:', err);
            return { results: [], data: [] };
          }),
          productService.getProduct(id).catch(err => {
            console.error('Failed to load product:', err);
            throw err;
          })
        ]);

        console.log('Product data received:', productData);
        console.log('Brand field value:', productData.brand);
        console.log('Supplier field value:', productData.supplier);

        // Set the loaded data
        const loadedBrands = brandsResponse.results || brandsResponse.data || [];
        const loadedSuppliers = suppliersResponse.results || suppliersResponse.data || [];
        
        setBrands(loadedBrands);
        setSuppliers(loadedSuppliers);
        setProduct(productData);

        // Extract brand and supplier IDs properly
        let brandId = '';
        let supplierId = '';

        // Handle brand - check if it's an object with ID, string ID, or name in _brand
        if (productData.brand) {
          if (typeof productData.brand === 'object' && productData.brand.id) {
            brandId = productData.brand.id;
          } else if (typeof productData.brand === 'string') {
            brandId = productData.brand;
          }
        } else if (productData._brand) {
          // _brand contains the name, find the ID by matching name
          const brandMatch = loadedBrands.find(b => b.name === productData._brand);
          if (brandMatch) {
            brandId = brandMatch.id;
          }
        }

        // Handle supplier - check if it's an object with ID, string ID, or name in _supplier
        if (productData.supplier) {
          if (typeof productData.supplier === 'object' && productData.supplier.id) {
            supplierId = productData.supplier.id;
          } else if (typeof productData.supplier === 'string') {
            supplierId = productData.supplier;
          }
        } else if (productData._supplier) {
          // _supplier contains the name, find the ID by matching name
          const supplierMatch = loadedSuppliers.find(s => s.name === productData._supplier);
          if (supplierMatch) {
            supplierId = supplierMatch.id;
          }
        }

        console.log('Extracted brandId:', brandId, 'supplierId:', supplierId);
        console.log('Brand match from name:', productData._brand, '→', brandId);
        console.log('Supplier match from name:', productData._supplier, '→', supplierId);

        setFormData({
          name: productData.name,
          description: productData.description || '',
          price: productData.price,
          quantity: productData.quantity,
          brand: brandId,
          category: productData.category || '',
          supplier: supplierId,
          skus: productData.skus || [],
          store_ids: productData.store_ids || [],
        });

      } catch (err) {
        setError('Failed to load product');
      } finally {
        setLoading(false);
        setLoadingBrands(false);
        setLoadingSuppliers(false);
      }
    };
    
    loadData();
  }, [id]);

  // Reload data after modal actions
  const reloadBrands = async () => {
    try {
      setLoadingBrands(true);
      const brandsResponse = await brandService.getBrands();
      setBrands(brandsResponse.results || brandsResponse.data || []);
    } catch (err) {
      console.error('Failed to reload brands:', err);
    } finally {
      setLoadingBrands(false);
    }
  };

  const reloadSuppliers = async () => {
    try {
      setLoadingSuppliers(true);
      const suppliersResponse = await supplierService.getSuppliers();
      setSuppliers(suppliersResponse.results || suppliersResponse.data || []);
    } catch (err) {
      console.error('Failed to reload suppliers:', err);
    } finally {
      setLoadingSuppliers(false);
    }
  };

  // Modal handlers
  const handleBrandSuccess = (brand: Brand) => {
    reloadBrands();
    if (brandModal.mode === 'create') {
      setFormData(prev => ({ ...prev, brand: brand.id }));
    }
  };

  const handleSupplierSuccess = (supplier: Supplier) => {
    reloadSuppliers();
    if (supplierModal.mode === 'create') {
      setFormData(prev => ({ ...prev, supplier: supplier.id }));
    }
  };

  const handleDelete = async () => {
    if (!deleteDialog.item) return;
    
    setDeleting(true);
    try {
      if (deleteDialog.type === 'brand') {
        await brandService.deleteBrand(deleteDialog.item.id);
        if (formData.brand === deleteDialog.item.id) {
          setFormData(prev => ({ ...prev, brand: '' }));
        }
        reloadBrands();
      } else if (deleteDialog.type === 'supplier') {
        await supplierService.deleteSupplier(deleteDialog.item.id);
        if (formData.supplier === deleteDialog.item.id) {
          setFormData(prev => ({ ...prev, supplier: '' }));
        }
        reloadSuppliers();
      }
      setDeleteDialog({ isOpen: false, type: 'brand' });
    } catch (err: any) {
      setError(`Failed to delete ${deleteDialog.type}: ${err.message}`);
    } finally {
      setDeleting(false);
    }
  };

  const getSelectedBrand = () => {
    const selected = brands.find(b => b.id === formData.brand);
    console.log('getSelectedBrand - formData.brand:', formData.brand, 'brands:', brands, 'selected:', selected);
    return selected;
  };
  const getSelectedSupplier = () => {
    const selected = suppliers.find(s => s.id === formData.supplier);
    console.log('getSelectedSupplier - formData.supplier:', formData.supplier, 'suppliers:', suppliers, 'selected:', selected);
    return selected;
  };

  const handleInputChange = (field: keyof FormData, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSkuChange = (index: number, value: string) => {
    const newSkus = [...formData.skus];
    newSkus[index] = { sku: value };
    setFormData(prev => ({ ...prev, skus: newSkus }));
  };

  const addSku = () => {
    setFormData(prev => ({
      ...prev,
      skus: [...prev.skus, { sku: '' }]
    }));
  };

  const removeSku = (index: number) => {
    setFormData(prev => ({
      ...prev,
      skus: prev.skus.filter((_, i) => i !== index)
    }));
  };

  const handleStoreIdChange = (index: number, value: string) => {
    const newStoreIds = [...formData.store_ids];
    newStoreIds[index] = { in_store_id: value };
    setFormData(prev => ({ ...prev, store_ids: newStoreIds }));
  };

  const addStoreId = () => {
    setFormData(prev => ({
      ...prev,
      store_ids: [...prev.store_ids, { in_store_id: '' }]
    }));
  };

  const removeStoreId = (index: number) => {
    setFormData(prev => ({
      ...prev,
      store_ids: prev.store_ids.filter((_, i) => i !== index)
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError(null);

    try {
      // Filter out empty/null values for PATCH request
      const updateData = Object.fromEntries(
        Object.entries(formData).filter(([key, value]) => {
          // Keep non-empty strings, numbers > 0, and non-empty arrays
          if (typeof value === 'string') return value.trim() !== '';
          if (typeof value === 'number') return value >= 0;
          if (Array.isArray(value)) return value.length > 0;
          return value != null;
        })
      );

      console.log('Sending update data:', updateData);
      await productService.updateProduct(id, updateData);
      router.push(`/products/${id}`);
    } catch (err: any) {
      setError(err.message || 'Failed to update product');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <ProtectedRoute allowedRoles={['Owner', 'Admin', 'Manager']}>
        <AppLayout title="Edit Product">
          <div className="flex items-center justify-center min-h-64">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-4 text-gray-600">Loading product...</p>
            </div>
          </div>
        </AppLayout>
      </ProtectedRoute>
    );
  }

  if (error && !product) {
    return (
      <ProtectedRoute allowedRoles={['Owner', 'Admin', 'Manager']}>
        <AppLayout title="Edit Product">
          <div className="space-y-6">
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
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

  return (
    <ProtectedRoute allowedRoles={['Owner', 'Admin', 'Manager']}>
      <AppLayout 
        title="Edit Product"
        breadcrumbs={[
          { label: 'Dashboard', href: '/dashboard' },
          { label: 'Products', href: '/products' },
          { label: product?.name || 'Product', href: `/products/${id}` },
          { label: 'Edit' }
        ]}
      >
        <div className="space-y-6">
          {/* Header */}
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <div className="flex items-center gap-3">
              <Link href={`/products/${id}`}>
                <Button variant="ghost" size="sm">
                  <ArrowLeft className="w-4 h-4" />
                </Button>
              </Link>
              <div>
                <h2 className="text-xl font-semibold text-gray-900">Edit Product</h2>
                <p className="text-sm text-gray-500">{product?.name}</p>
              </div>
            </div>
            
            <div className="flex items-center gap-2">
              <Link href={`/products/${id}`}>
                <Button variant="outline" size="sm">
                  <X className="w-4 h-4 mr-2" />
                  Cancel
                </Button>
              </Link>
              <Button 
                size="sm" 
                onClick={handleSubmit}
                disabled={saving}
              >
                {saving ? (
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                ) : (
                  <Save className="w-4 h-4 mr-2" />
                )}
                {saving ? 'Saving...' : 'Save Changes'}
              </Button>
            </div>
          </div>

          {/* Error Alert */}
          {error && (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Left Column - Basic Info */}
              <div className="lg:col-span-2 space-y-6">
                <Card>
                  <Card.Header>
                    <h3 className="text-lg font-medium">Basic Information</h3>
                  </Card.Header>
                  <Card.Content>
                    <div className="space-y-4">
                      <div>
                        <Input
                          label="Product Name"
                          required
                          value={formData.name}
                          onChange={(e) => handleInputChange('name', e.target.value)}
                          placeholder="Enter product name"
                        />
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Description
                        </label>
                        <textarea
                          value={formData.description}
                          onChange={(e) => handleInputChange('description', e.target.value)}
                          placeholder="Enter product description"
                          rows={4}
                          className="block w-full px-3 py-2 border border-gray-300 rounded-lg text-sm 
                                   placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 
                                   focus:border-blue-500 transition-colors duration-200"
                        />
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div>
                          <div className="flex items-end gap-2">
                            <div className="flex-1">
                              <Input
                                label="Category"
                                value={formData.category}
                                onChange={(e) => handleInputChange('category', e.target.value)}
                                placeholder="Product category"
                                helperText="Category endpoint not yet available"
                                disabled
                              />
                            </div>
                            <div className="flex gap-1 pb-1">
                              <Button
                                type="button"
                                variant="outline"
                                size="sm"
                                onClick={() => setCategoryModal({ isOpen: true, mode: 'create' })}
                                className="px-2"
                                disabled
                                title="Create Category (API not available)"
                              >
                                <PlusCircle className="w-4 h-4" />
                              </Button>
                            </div>
                          </div>
                        </div>
                        
                        <div>
                          <div className="flex items-end gap-2">
                            <div className="flex-1">
                              <Select
                                label="Brand"
                                value={formData.brand}
                                onChange={(value) => handleInputChange('brand', value)}
                                placeholder="Select a brand"
                                loading={loadingBrands}
                                searchable
                                options={(() => {
                                  const options = brands?.map(brand => ({
                                    value: brand.id,
                                    label: brand.name
                                  })) || [];
                                  console.log('Brand Select - formData.brand:', formData.brand, 'options:', options);
                                  return options;
                                })()}
                              />
                            </div>
                            <div className="flex gap-1 pb-1">
                              <Button
                                type="button"
                                variant="outline"
                                size="sm"
                                onClick={() => setBrandModal({ isOpen: true, mode: 'create' })}
                                className="px-2"
                                title="Create Brand"
                              >
                                <PlusCircle className="w-4 h-4" />
                              </Button>
                              {formData.brand && (
                                <>
                                  <Button
                                    type="button"
                                    variant="outline"
                                    size="sm"
                                    onClick={() => setBrandModal({ 
                                      isOpen: true, 
                                      mode: 'edit', 
                                      brand: getSelectedBrand() 
                                    })}
                                    className="px-2"
                                    title="Edit Brand"
                                  >
                                    <Edit className="w-4 h-4" />
                                  </Button>
                                  <Button
                                    type="button"
                                    variant="outline"
                                    size="sm"
                                    onClick={() => setDeleteDialog({ 
                                      isOpen: true, 
                                      type: 'brand', 
                                      item: getSelectedBrand() 
                                    })}
                                    className="px-2 text-red-600 hover:text-red-700 hover:bg-red-50"
                                    title="Delete Brand"
                                  >
                                    <Trash className="w-4 h-4" />
                                  </Button>
                                </>
                              )}
                            </div>
                          </div>
                        </div>
                        
                        <div>
                          <div className="flex items-end gap-2">
                            <div className="flex-1">
                              <Select
                                label="Supplier"
                                value={formData.supplier}
                                onChange={(value) => handleInputChange('supplier', value)}
                                placeholder="Select a supplier"
                                loading={loadingSuppliers}
                                searchable
                                options={(() => {
                                  const options = suppliers?.map(supplier => ({
                                    value: supplier.id,
                                    label: supplier.name
                                  })) || [];
                                  console.log('Supplier Select - formData.supplier:', formData.supplier, 'options:', options);
                                  return options;
                                })()}
                              />
                            </div>
                            <div className="flex gap-1 pb-1">
                              <Button
                                type="button"
                                variant="outline"
                                size="sm"
                                onClick={() => setSupplierModal({ isOpen: true, mode: 'create' })}
                                className="px-2"
                                title="Create Supplier"
                              >
                                <PlusCircle className="w-4 h-4" />
                              </Button>
                              {formData.supplier && (
                                <>
                                  <Button
                                    type="button"
                                    variant="outline"
                                    size="sm"
                                    onClick={() => setSupplierModal({ 
                                      isOpen: true, 
                                      mode: 'edit', 
                                      supplier: getSelectedSupplier() 
                                    })}
                                    className="px-2"
                                    title="Edit Supplier"
                                  >
                                    <Edit className="w-4 h-4" />
                                  </Button>
                                  <Button
                                    type="button"
                                    variant="outline"
                                    size="sm"
                                    onClick={() => setDeleteDialog({ 
                                      isOpen: true, 
                                      type: 'supplier', 
                                      item: getSelectedSupplier() 
                                    })}
                                    className="px-2 text-red-600 hover:text-red-700 hover:bg-red-50"
                                    title="Delete Supplier"
                                  >
                                    <Trash className="w-4 h-4" />
                                  </Button>
                                </>
                              )}
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </Card.Content>
                </Card>

                <Card>
                  <Card.Header>
                    <h3 className="text-lg font-medium">Pricing & Inventory</h3>
                  </Card.Header>
                  <Card.Content>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <Input
                          label="Price"
                          type="number"
                          step="0.01"
                          min="0"
                          required
                          value={formData.price}
                          onChange={(e) => handleInputChange('price', parseFloat(e.target.value) || 0)}
                          placeholder="0.00"
                        />
                      </div>
                      
                      <div>
                        <Input
                          label="Quantity"
                          type="number"
                          min="0"
                          required
                          value={formData.quantity}
                          onChange={(e) => handleInputChange('quantity', parseInt(e.target.value) || 0)}
                          placeholder="0"
                        />
                      </div>
                    </div>
                  </Card.Content>
                </Card>

                {/* SKUs */}
                <Card>
                  <Card.Header>
                    <div className="flex items-center justify-between">
                      <h3 className="text-lg font-medium">Product SKUs</h3>
                      <Button type="button" variant="outline" size="sm" onClick={addSku}>
                        <Plus className="w-4 h-4 mr-2" />
                        Add SKU
                      </Button>
                    </div>
                  </Card.Header>
                  <Card.Content>
                    <div className="space-y-3">
                      {formData.skus.map((sku, index) => (
                        <div key={index} className="flex items-center gap-3">
                          <div className="flex-1">
                            <Input
                              value={sku.sku}
                              onChange={(e) => handleSkuChange(index, e.target.value)}
                              placeholder="Enter SKU"
                            />
                          </div>
                          <Button
                            type="button"
                            variant="ghost"
                            size="sm"
                            onClick={() => removeSku(index)}
                            className="text-red-600 hover:text-red-700 hover:bg-red-50"
                          >
                            <Trash className="w-4 h-4" />
                          </Button>
                        </div>
                      ))}
                      {formData.skus.length === 0 && (
                        <p className="text-sm text-gray-500 text-center py-4">
                          No SKUs added yet. Click "Add SKU" to get started.
                        </p>
                      )}
                    </div>
                  </Card.Content>
                </Card>

                {/* Store IDs */}
                <Card>
                  <Card.Header>
                    <div className="flex items-center justify-between">
                      <h3 className="text-lg font-medium">Store Locations</h3>
                      <Button type="button" variant="outline" size="sm" onClick={addStoreId}>
                        <Plus className="w-4 h-4 mr-2" />
                        Add Location
                      </Button>
                    </div>
                  </Card.Header>
                  <Card.Content>
                    <div className="space-y-3">
                      {formData.store_ids.map((store, index) => (
                        <div key={index} className="flex items-center gap-3">
                          <div className="flex-1">
                            <Input
                              value={store.in_store_id}
                              onChange={(e) => handleStoreIdChange(index, e.target.value)}
                              placeholder="Enter store location ID"
                            />
                          </div>
                          <Button
                            type="button"
                            variant="ghost"
                            size="sm"
                            onClick={() => removeStoreId(index)}
                            className="text-red-600 hover:text-red-700 hover:bg-red-50"
                          >
                            <Trash className="w-4 h-4" />
                          </Button>
                        </div>
                      ))}
                      {formData.store_ids.length === 0 && (
                        <p className="text-sm text-gray-500 text-center py-4">
                          No store locations added yet. Click "Add Location" to get started.
                        </p>
                      )}
                    </div>
                  </Card.Content>
                </Card>
              </div>

              {/* Right Column - Quick Actions */}
              <div className="space-y-6">
                <Card>
                  <Card.Header>
                    <h3 className="text-lg font-medium">Actions</h3>
                  </Card.Header>
                  <Card.Content>
                    <div className="space-y-3">
                      <Button 
                        type="submit" 
                        className="w-full"
                        disabled={saving}
                      >
                        {saving ? (
                          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                        ) : (
                          <Save className="w-4 h-4 mr-2" />
                        )}
                        {saving ? 'Saving...' : 'Save Changes'}
                      </Button>
                      
                      <Link href={`/products/${id}`} className="block">
                        <Button variant="outline" className="w-full">
                          <X className="w-4 h-4 mr-2" />
                          Cancel
                        </Button>
                      </Link>
                    </div>
                  </Card.Content>
                </Card>

                <Card>
                  <Card.Header>
                    <h3 className="text-lg font-medium">Product Summary</h3>
                  </Card.Header>
                  <Card.Content>
                    <div className="space-y-3 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-500">Current Price:</span>
                        <span className="font-medium">${formData.price.toFixed(2)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-500">Current Stock:</span>
                        <span className="font-medium">{formData.quantity}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-500">Total Value:</span>
                        <span className="font-medium">${(formData.price * formData.quantity).toFixed(2)}</span>
                      </div>
                      <div className="pt-2 border-t border-gray-200">
                        <div className="flex justify-between">
                          <span className="text-gray-500">SKUs:</span>
                          <span className="font-medium">{formData.skus.length}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-500">Locations:</span>
                          <span className="font-medium">{formData.store_ids.length}</span>
                        </div>
                      </div>
                    </div>
                  </Card.Content>
                </Card>
              </div>
            </div>
          </form>

          {/* Modals */}
          <BrandModal
            isOpen={brandModal.isOpen}
            onClose={() => setBrandModal({ isOpen: false, mode: 'create' })}
            onSuccess={handleBrandSuccess}
            brand={brandModal.brand}
            mode={brandModal.mode}
          />

          <SupplierModal
            isOpen={supplierModal.isOpen}
            onClose={() => setSupplierModal({ isOpen: false, mode: 'create' })}
            onSuccess={handleSupplierSuccess}
            supplier={supplierModal.supplier}
            mode={supplierModal.mode}
          />

          <CategoryModal
            isOpen={categoryModal.isOpen}
            onClose={() => setCategoryModal({ isOpen: false, mode: 'create' })}
            onSuccess={() => {}}
            mode={categoryModal.mode}
          />

          <ConfirmDialog
            isOpen={deleteDialog.isOpen}
            onClose={() => setDeleteDialog({ isOpen: false, type: 'brand' })}
            onConfirm={handleDelete}
            title={`Delete ${deleteDialog.type === 'brand' ? 'Brand' : 'Supplier'}`}
            message={`Are you sure you want to delete "${deleteDialog.item?.name}"? This action cannot be undone.`}
            confirmText="Delete"
            loading={deleting}
          />
        </div>
      </AppLayout>
    </ProtectedRoute>
  );
}