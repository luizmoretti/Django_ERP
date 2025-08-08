'use client';

import React, { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { ProtectedRoute } from '@/components/auth';
import { supplierService } from '@/services';
import { Button } from '@/components/ui';
import Link from 'next/link';
import { Pencil, Trash } from 'lucide-react';
import { Supplier } from '@/types';

export default function SupplierDetailsPage() {
    const params = useParams();
    const id = params.id as string;
    const [supplier, setSupplier] = useState<Supplier | null>(null);
    const [loading, setLoading] = useState(true);
    const router = useRouter();

    useEffect(() => {
        const fetchSupplier = async () => {
            try {
                const data = await supplierService.getSupplier(id);
                setSupplier(data);
            } catch (err) {
                console.error('Failed to load supplier');
            } finally {
                setLoading(false);
            }
        };
        fetchSupplier();
    }, [id]);

    if (loading) return <div>Loading...</div>;
    if (!supplier) return <div>Supplier not found</div>;

    return (
        <ProtectedRoute allowedRoles={['Admin', 'Manager']}>
            <div className="container mx-auto py-8">
                <div className="flex justify-between items-center mb-6">
                    <h1 className="text-2xl font-bold">{supplier.name}</h1>
                    <div>
                        <Link href={`/suppliers/${id}/edit`}>
                            <Button variant="ghost"><Pencil /></Button>
                        </Link>
                        <Button variant="ghost" onClick={() => supplierService.deleteSupplier(id).then(() => router.push('/suppliers'))}><Trash /></Button>
                    </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                    <div><strong>Tax Number:</strong> {supplier.tax_number}</div>
                    <div><strong>Email:</strong> {supplier.email}</div>
                    <div><strong>Phone:</strong> {supplier.phone}</div>
                    <div><strong>Address:</strong> {supplier.address}</div>
                    <div><strong>City:</strong> {supplier.city}</div>
                    <div><strong>State:</strong> {supplier.state}</div>
                    <div><strong>Zip Code:</strong> {supplier.zip_code}</div>
                    <div><strong>Country:</strong> {supplier.country}</div>
                </div>
            </div>
        </ProtectedRoute>
    );
} 