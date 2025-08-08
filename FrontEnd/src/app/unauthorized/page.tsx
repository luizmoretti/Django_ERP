'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { Alert, AlertDescription, Button } from '@/components/ui';
import { ShieldX } from 'lucide-react';

export default function UnauthorizedPage() {
  const router = useRouter();

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="max-w-md w-full text-center">
        <div className="mb-6">
          <ShieldX className="mx-auto h-12 w-12 text-red-500" />
        </div>
        
        <Alert variant="destructive" className="mb-6">
          <AlertDescription>
            You don't have permission to access this page.
          </AlertDescription>
        </Alert>

        <div className="space-y-4">
          <p className="text-gray-600">
            Please contact your administrator if you believe this is an error.
          </p>
          
          <div className="flex gap-4 justify-center">
            <Button 
              variant="ghost" 
              onClick={() => router.back()}
            >
              Go Back
            </Button>
            <Button 
              onClick={() => router.push('/dashboard')}
            >
              Go to Dashboard
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}