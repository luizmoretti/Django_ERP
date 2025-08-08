'use client';

import React, { useState } from 'react';
import { ProtectedRoute } from '@/components/auth';
import { supplierService } from '@/services';
import { useRouter } from 'next/navigation';
import { Button, Input } from '@/components/ui';

export default function SupplierCreatePage() {
    const router = useRouter();
    const [formData, setFormData] = useState({
        name: '',
        tax_number: '',
        phone: '',
        email: '',
        address: '',
        city: '',
        state: '',
        zip_code: '',
        country: 'USA',
    });

    const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        try {
            await supplierService.createSupplier(formData);
            router.push('/suppliers');
        } catch (err) {
            console.error('Failed to create supplier', err);
        }
    };

    return (
        <ProtectedRoute allowedRoles={['Admin', 'Manager']}>
            <div className="container mx-auto py-8">
                <h1 className="text-2xl font-bold mb-6">Create Supplier</h1>
                <form onSubmit={handleSubmit} className="space-y-4">
                    <Input
                        label="Name"
                        value={formData.name}
                        onChange={e => setFormData({ ...formData, name: e.target.value })}
                    />
                    <Input
                        label="Tax Number"
                        value={formData.tax_number}
                        onChange={e => setFormData({ ...formData, tax_number: e.target.value })}
                    />
                    <Input
                        label="Phone"
                        value={formData.phone}
                        onChange={e => setFormData({ ...formData, phone: e.target.value })}
                    />
                    <Input
                        label="Email"
                        type="email"
                        value={formData.email}
                        onChange={e => setFormData({ ...formData, email: e.target.value })}
                    />
                    <Input
                        label="Address"
                        value={formData.address}
                        onChange={e => setFormData({ ...formData, address: e.target.value })}
                    />
                    <Input
                        label="City"
                        value={formData.city}
                        onChange={e => setFormData({ ...formData, city: e.target.value })}
                    />
                    {/* Add selects for state, country */}
                    <Input
                        label="Zip Code"
                        value={formData.zip_code}
                        onChange={e => setFormData({ ...formData, zip_code: e.target.value })}
                    />
                    <Button type="submit">Create</Button>
                </form>
            </div>
        </ProtectedRoute>
    );
} 