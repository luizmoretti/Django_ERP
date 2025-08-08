/**
 * Supplier Modal Component
 * Modal for creating and editing suppliers
 */

import React, { useState, useEffect } from 'react';
import { Supplier } from '@/types';
import { supplierService } from '@/services';
import { Modal, Input, Button, Alert, AlertDescription } from '@/components/ui';

interface SupplierModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: (supplier: Supplier) => void;
  supplier?: Supplier | null;
  mode: 'create' | 'edit';
}

const SupplierModal: React.FC<SupplierModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
  supplier,
  mode,
}) => {
  const [formData, setFormData] = useState({
    name: '',
    tax_number: '',
    phone: '',
    email: '',
    address: '',
    city: '',
    state: '',
    zip_code: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Reset form when modal opens/closes
  useEffect(() => {
    if (isOpen) {
      setFormData({
        name: supplier?.name || '',
        tax_number: supplier?.tax_number || '',
        phone: supplier?.phone || '',
        email: supplier?.email || '',
        address: supplier?.address || '',
        city: supplier?.city || '',
        state: supplier?.state || '',
        zip_code: supplier?.zip_code || '',
      });
      setError(null);
    } else {
      setFormData({
        name: '',
        tax_number: '',
        phone: '',
        email: '',
        address: '',
        city: '',
        state: '',
        zip_code: '',
      });
      setError(null);
    }
  }, [isOpen, supplier]);

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.name.trim()) return;

    setLoading(true);
    setError(null);

    try {
      // Clean empty fields
      const cleanData = Object.fromEntries(
        Object.entries(formData).filter(([_, value]) => value.trim() !== '')
      );

      let savedSupplier: Supplier;
      
      if (mode === 'create') {
        savedSupplier = await supplierService.createSupplier(cleanData);
      } else {
        if (!supplier?.id) throw new Error('Supplier ID is required for editing');
        savedSupplier = await supplierService.updateSupplier(supplier.id, cleanData);
      }

      onSuccess(savedSupplier);
      onClose();
    } catch (err: any) {
      setError(err.message || `Failed to ${mode} supplier`);
    } finally {
      setLoading(false);
    }
  };

  const title = mode === 'create' ? 'Create Supplier' : 'Edit Supplier';

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={title}
      size="lg"
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && (
          <Alert variant="destructive">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Basic Information */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="md:col-span-2">
            <Input
              label="Supplier Name"
              value={formData.name}
              onChange={(e) => handleInputChange('name', e.target.value)}
              placeholder="Enter supplier name"
              required
              disabled={loading}
              autoFocus
            />
          </div>

          <div>
            <Input
              label="Tax Number"
              value={formData.tax_number}
              onChange={(e) => handleInputChange('tax_number', e.target.value)}
              placeholder="Enter tax number"
              disabled={loading}
            />
          </div>

          <div>
            <Input
              label="Phone"
              value={formData.phone}
              onChange={(e) => handleInputChange('phone', e.target.value)}
              placeholder="Enter phone number"
              disabled={loading}
            />
          </div>

          <div className="md:col-span-2">
            <Input
              label="Email"
              type="email"
              value={formData.email}
              onChange={(e) => handleInputChange('email', e.target.value)}
              placeholder="Enter email address"
              disabled={loading}
            />
          </div>
        </div>

        {/* Address Information */}
        <div className="border-t pt-4">
          <h4 className="text-sm font-medium text-gray-700 mb-3">Address Information</h4>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="md:col-span-2">
              <Input
                label="Address"
                value={formData.address}
                onChange={(e) => handleInputChange('address', e.target.value)}
                placeholder="Enter street address"
                disabled={loading}
              />
            </div>

            <div>
              <Input
                label="City"
                value={formData.city}
                onChange={(e) => handleInputChange('city', e.target.value)}
                placeholder="Enter city"
                disabled={loading}
              />
            </div>

            <div>
              <Input
                label="State"
                value={formData.state}
                onChange={(e) => handleInputChange('state', e.target.value)}
                placeholder="Enter state"
                disabled={loading}
              />
            </div>

            <div>
              <Input
                label="ZIP Code"
                value={formData.zip_code}
                onChange={(e) => handleInputChange('zip_code', e.target.value)}
                placeholder="Enter ZIP code"
                disabled={loading}
              />
            </div>
          </div>
        </div>

        <div className="flex justify-end gap-3 pt-4">
          <Button
            type="button"
            variant="outline"
            onClick={onClose}
            disabled={loading}
          >
            Cancel
          </Button>
          
          <Button
            type="submit"
            disabled={loading || !formData.name.trim()}
          >
            {loading ? (
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
            ) : null}
            {mode === 'create' ? 'Create Supplier' : 'Save Changes'}
          </Button>
        </div>
      </form>
    </Modal>
  );
};

export default SupplierModal;