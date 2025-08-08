/**
 * Brand Modal Component
 * Modal for creating and editing brands
 */

import React, { useState, useEffect } from 'react';
import { Brand } from '@/types';
import { brandService } from '@/services';
import { Modal, Input, Button, Alert, AlertDescription } from '@/components/ui';

interface BrandModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: (brand: Brand) => void;
  brand?: Brand | null;
  mode: 'create' | 'edit';
}

const BrandModal: React.FC<BrandModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
  brand,
  mode,
}) => {
  const [name, setName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Reset form when modal opens/closes
  useEffect(() => {
    if (isOpen) {
      setName(brand?.name || '');
      setError(null);
    } else {
      setName('');
      setError(null);
    }
  }, [isOpen, brand]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;

    setLoading(true);
    setError(null);

    try {
      let savedBrand: Brand;
      
      if (mode === 'create') {
        savedBrand = await brandService.createBrand({ name: name.trim() });
      } else {
        if (!brand?.id) throw new Error('Brand ID is required for editing');
        savedBrand = await brandService.updateBrand(brand.id, { name: name.trim() });
      }

      onSuccess(savedBrand);
      onClose();
    } catch (err: any) {
      setError(err.message || `Failed to ${mode} brand`);
    } finally {
      setLoading(false);
    }
  };

  const title = mode === 'create' ? 'Create Brand' : 'Edit Brand';

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={title}
      size="md"
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && (
          <Alert variant="destructive">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        <div>
          <Input
            label="Brand Name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Enter brand name"
            required
            disabled={loading}
            autoFocus
          />
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
            disabled={loading || !name.trim()}
          >
            {loading ? (
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
            ) : null}
            {mode === 'create' ? 'Create Brand' : 'Save Changes'}
          </Button>
        </div>
      </form>
    </Modal>
  );
};

export default BrandModal;