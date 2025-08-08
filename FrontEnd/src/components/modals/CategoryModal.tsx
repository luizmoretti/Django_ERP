/**
 * Category Modal Component
 * Modal for creating and editing categories
 * Note: Category API not yet available in backend
 */

import React, { useState, useEffect } from 'react';
import { Modal, Input, Button, Alert, AlertDescription } from '@/components/ui';

interface Category {
  id: string;
  name: string;
}

interface CategoryModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: (category: Category) => void;
  category?: Category | null;
  mode: 'create' | 'edit';
}

const CategoryModal: React.FC<CategoryModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
  category,
  mode,
}) => {
  const [name, setName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Reset form when modal opens/closes
  useEffect(() => {
    if (isOpen) {
      setName(category?.name || '');
      setError(null);
    } else {
      setName('');
      setError(null);
    }
  }, [isOpen, category]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;

    setLoading(true);
    setError(null);

    try {
      // TODO: Implement when Category API becomes available
      // For now, simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Mock response - replace with actual API call
      const savedCategory: Category = {
        id: category?.id || `cat-${Date.now()}`,
        name: name.trim()
      };

      setError('Category API not yet available in backend');
      // onSuccess(savedCategory);
      // onClose();
    } catch (err: any) {
      setError(err.message || `Failed to ${mode} category`);
    } finally {
      setLoading(false);
    }
  };

  const title = mode === 'create' ? 'Create Category' : 'Edit Category';

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={title}
      size="md"
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        <Alert variant="warning">
          <AlertDescription>
            Category API is not yet available in the backend. This modal is prepared for future use.
          </AlertDescription>
        </Alert>

        {error && (
          <Alert variant="destructive">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        <div>
          <Input
            label="Category Name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Enter category name"
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
            {mode === 'create' ? 'Create Category' : 'Save Changes'}
          </Button>
        </div>
      </form>
    </Modal>
  );
};

export default CategoryModal;