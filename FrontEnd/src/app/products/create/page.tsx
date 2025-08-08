'use client';

import React, { useState, useEffect } from 'react';
import { ProtectedRoute } from '@/components/auth';
import { AppLayout } from '@/components/layout';
import { productService, brandService, supplierService } from '@/services';
import { useRouter } from 'next/navigation';
import { Button, Input, Card, Alert, AlertDescription, Select, SelectOption, ConfirmDialog } from '@/components/ui';
import { BrandModal, SupplierModal, CategoryModal } from '@/components/modals';
import { Brand, Supplier } from '@/types';
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

export default function ProductCreatePage() {
  const router = useRouter();
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

  // Load brands and suppliers on component mount
  useEffect(() => {
    const loadData = async () => {
      try {
        setLoadingBrands(true);
        const brandsResponse = await brandService.getBrands();
        console.log('Brands API Response:', brandsResponse);
        console.log('Brands Results:', brandsResponse.results || brandsResponse.data);
        setBrands(brandsResponse.results || brandsResponse.data || []);
      } catch (err) {
        console.error('Failed to load brands:', err);
      } finally {
        setLoadingBrands(false);
      }

      try {
        setLoadingSuppliers(true);
        const suppliersResponse = await supplierService.getSuppliers();
        console.log('Suppliers API Response:', suppliersResponse);
        setSuppliers(suppliersResponse.results || suppliersResponse.data || []);
      } catch (err) {
        console.error('Failed to load suppliers:', err);
      } finally {
        setLoadingSuppliers(false);
      }
    };

    loadData();
  }, []);

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

  const getSelectedBrand = () => brands.find(b => b.id === formData.brand);
  const getSelectedSupplier = () => suppliers.find(s => s.id === formData.supplier);

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
      // Filter out empty/null values before creating
      const createData = Object.fromEntries(
        Object.entries(formData).filter(([key, value]) => {
          // Keep non-empty strings, numbers > 0, and non-empty arrays
          if (typeof value === 'string') return value.trim() !== '';
          if (typeof value === 'number') return value >= 0;
          if (Array.isArray(value)) return value.length > 0;
          return value != null;
        })
      );

      console.log('Sending create data:', createData);
      const newProduct = await productService.createProduct(createData);
      router.push(`/products/${newProduct.id}`);
    } catch (err: any) {
      setError(err.message || 'Failed to create product');
    } finally {
      setSaving(false);
    }
  };

  const resetForm = () => {
    setFormData({
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
    setError(null);
  };

  return (
    <ProtectedRoute allowedRoles={['Owner', 'Admin', 'Manager']}>
      <AppLayout 
        title="Create Product"
        breadcrumbs={[
          { label: 'Dashboard', href: '/dashboard' },
          { label: 'Products', href: '/products' },
          { label: 'Create' }
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
                <h2 className="text-xl font-semibold text-gray-900">Create New Product</h2>
                <p className="text-sm text-gray-500">Add a new product to your inventory</p>
              </div>
            </div>
            
            <div className="flex items-center gap-2">
              <Button variant="outline" size="sm" onClick={resetForm}>
                <X className="w-4 h-4 mr-2" />
                Reset
              </Button>
              <Link href="/products">
                <Button variant="outline" size="sm">
                  Cancel
                </Button>
              </Link>
              <Button 
                size="sm" 
                onClick={handleSubmit}
                disabled={saving || !formData.name.trim()}
              >
                {saving ? (
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                ) : (
                  <Save className="w-4 h-4 mr-2" />
                )}
                {saving ? 'Creating...' : 'Create Product'}
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
                    <p className="text-sm text-gray-500">Essential product details and descriptions</p>
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
                          helperText="A clear, descriptive name for your product"
                        />
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Description
                        </label>
                        <textarea
                          value={formData.description}
                          onChange={(e) => handleInputChange('description', e.target.value)}
                          placeholder="Enter product description (optional)"
                          rows={4}
                          className="block w-full px-3 py-2 border border-gray-300 rounded-lg text-sm 
                                   placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 
                                   focus:border-blue-500 transition-colors duration-200"
                        />
                        <p className="text-xs text-gray-500 mt-1">
                          Provide detailed information about the product features and specifications
                        </p>
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
                                  const mappedOptions = brands?.map(brand => ({
                                    value: brand.id,
                                    label: brand.name
                                  })) || [];
                                  console.log('Creating Brand options - brands:', brands, 'mapped:', mappedOptions);
                                  return mappedOptions;
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
                                options={suppliers?.map(supplier => ({
                                  value: supplier.id,
                                  label: supplier.name
                                })) || []}
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
                    <p className="text-sm text-gray-500">Set pricing and initial stock quantities</p>
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
                          helperText="Product selling price"
                        />
                      </div>
                      
                      <div>
                        <Input
                          label="Initial Quantity"
                          type="number"
                          min="0"
                          required
                          value={formData.quantity}
                          onChange={(e) => handleInputChange('quantity', parseInt(e.target.value) || 0)}
                          placeholder="0"
                          helperText="Starting stock quantity"
                        />
                      </div>
                    </div>
                  </Card.Content>
                </Card>

                {/* SKUs */}
                <Card>
                  <Card.Header>
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="text-lg font-medium">Product SKUs</h3>
                        <p className="text-sm text-gray-500">Unique identifiers for inventory tracking</p>
                      </div>
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
                              placeholder="Enter SKU (e.g., PROD-001)"
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
                        <div className="text-center py-6 border-2 border-dashed border-gray-200 rounded-lg">
                          <p className="text-sm text-gray-500 mb-2">No SKUs added yet</p>
                          <Button type="button" variant="outline" size="sm" onClick={addSku}>
                            <Plus className="w-4 h-4 mr-2" />
                            Add Your First SKU
                          </Button>
                        </div>
                      )}
                    </div>
                  </Card.Content>
                </Card>

                {/* Store IDs */}
                <Card>
                  <Card.Header>
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="text-lg font-medium">Store Locations</h3>
                        <p className="text-sm text-gray-500">Specify which store locations carry this product</p>
                      </div>
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
                              placeholder="Enter store location ID (e.g., STORE-A)"
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
                        <div className="text-center py-6 border-2 border-dashed border-gray-200 rounded-lg">
                          <p className="text-sm text-gray-500 mb-2">No store locations added yet</p>
                          <Button type="button" variant="outline" size="sm" onClick={addStoreId}>
                            <Plus className="w-4 h-4 mr-2" />
                            Add Store Location
                          </Button>
                        </div>
                      )}
                    </div>
                  </Card.Content>
                </Card>
              </div>

              {/* Right Column - Quick Actions & Summary */}
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
                        disabled={saving || !formData.name.trim()}
                      >
                        {saving ? (
                          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                        ) : (
                          <Save className="w-4 h-4 mr-2" />
                        )}
                        {saving ? 'Creating...' : 'Create Product'}
                      </Button>
                      
                      <Button 
                        type="button" 
                        variant="outline" 
                        className="w-full"
                        onClick={resetForm}
                      >
                        <X className="w-4 h-4 mr-2" />
                        Reset Form
                      </Button>

                      <Link href="/products" className="block">
                        <Button variant="outline" className="w-full">
                          Cancel
                        </Button>
                      </Link>
                    </div>
                  </Card.Content>
                </Card>

                <Card>
                  <Card.Header>
                    <h3 className="text-lg font-medium">Product Preview</h3>
                  </Card.Header>
                  <Card.Content>
                    <div className="space-y-3 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-500">Name:</span>
                        <span className="font-medium text-right max-w-32 truncate">
                          {formData.name || 'Not set'}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-500">Price:</span>
                        <span className="font-medium">${formData.price.toFixed(2)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-500">Stock:</span>
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

                <Card>
                  <Card.Header>
                    <h3 className="text-lg font-medium">Tips</h3>
                  </Card.Header>
                  <Card.Content>
                    <div className="space-y-2 text-xs text-gray-600">
                      <p>• Use clear, descriptive product names</p>
                      <p>• Add SKUs for better inventory tracking</p>
                      <p>• Set realistic initial quantities</p>
                      <p>• Include detailed descriptions for clarity</p>
                      <p>• Specify store locations for multi-location tracking</p>
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