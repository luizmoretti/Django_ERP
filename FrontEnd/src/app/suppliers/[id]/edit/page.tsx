'use client';

import React, { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { ProtectedRoute } from '@/components/auth';
import { supplierService } from '@/services';
import { Button, Input } from '@/components/ui';
import { Supplier } from '@/types';

export default function SupplierEditPage() {
    const params = useParams();
    const id = params.id as string;
    const router = useRouter();
    const [formData, setFormData] = useState<Supplier | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchSupplier = async () => {
            try {
                const data = await supplierService.getSupplier(id);
                setFormData(data);
            } catch (err) {
                console.error('Failed to load supplier');
            } finally {
                setLoading(false);
            }
        };
        fetchSupplier();
    }, [id]);

    const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        try {
            await supplierService.updateSupplier(id, formData as Partial<Supplier>);
            router.push('/suppliers');
        } catch (err) {
            console.error('Failed to update supplier', err);
        }
    };

    if (loading) return <div>Loading...</div>;
    if (!formData) return <div>Supplier not found</div>;

    return (
        <ProtectedRoute allowedRoles={['Admin', 'Manager']}>
            <div className="container mx-auto py-8">
                <h1 className="text-2xl font-bold mb-6">Edit Supplier</h1>
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
                    <Button type="submit">Update</Button>
                </form>
            </div>
        </ProtectedRoute>
    );
} 