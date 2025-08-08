'use client';

import React, { useState, useEffect } from 'react';
import { ProtectedRoute } from '@/components/auth';
import { supplierService } from '@/services';
import { Button, Table, Alert, AlertTitle } from '@/components/ui';
import { Pencil, Trash, Eye, Plus } from 'lucide-react';
import Link from 'next/link';
import { Supplier } from '@/types';

export default function SuppliersListPage() {
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchSuppliers = async () => {
      try {
        const response = await supplierService.getSuppliers();
        setSuppliers(response.results);
      } catch (err) {
        setError('Failed to load suppliers');
      } finally {
        setLoading(false);
      }
    };
    fetchSuppliers();
  }, []);

  const handleDelete = async (id: string) => {
    if (confirm('Are you sure you want to delete this supplier?')) {
      try {
        await supplierService.deleteSupplier(id);
        setSuppliers(suppliers.filter(s => s.id !== id));
      } catch (err) {
        setError('Failed to delete supplier');
      }
    }
  };

  if (loading) return <div>Loading...</div>;
  if (error) return <Alert variant="destructive"><AlertTitle>{error}</AlertTitle></Alert>;

  return (
    <ProtectedRoute allowedRoles={['Admin', 'Manager']}>
      <div className="container mx-auto py-8">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold">Suppliers</h1>
          <Link href="/suppliers/create">
            <Button><Plus className="mr-2" /> Add Supplier</Button>
          </Link>
        </div>
        <Table>
          <Table.Header>
            <Table.Row>
              <Table.Head>Name</Table.Head>
              <Table.Head>Tax Number</Table.Head>
              <Table.Head>Email</Table.Head>
              <Table.Head>Phone</Table.Head>
              <Table.Head>City</Table.Head>
              <Table.Head>Actions</Table.Head>
            </Table.Row>
          </Table.Header>
          <Table.Body>
            {suppliers.map(supplier => (
              <Table.Row key={supplier.id}>
                <Table.Cell>{supplier.name}</Table.Cell>
                <Table.Cell>{supplier.tax_number}</Table.Cell>
                <Table.Cell>{supplier.email}</Table.Cell>
                <Table.Cell>{supplier.phone}</Table.Cell>
                <Table.Cell>{supplier.city}</Table.Cell>
                <Table.Cell>
                  <div className="flex space-x-2">
                    <Link href={`/suppliers/${supplier.id}`}>
                      <Button variant="ghost" size="sm"><Eye /></Button>
                    </Link>
                    <Link href={`/suppliers/${supplier.id}/edit`}>
                      <Button variant="ghost" size="sm"><Pencil /></Button>
                    </Link>
                    <Button variant="ghost" size="sm" onClick={() => handleDelete(supplier.id)}><Trash /></Button>
                  </div>
                </Table.Cell>
              </Table.Row>
            ))}
          </Table.Body>
        </Table>
      </div>
    </ProtectedRoute>
  );
} 