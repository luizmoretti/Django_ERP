/**
 * Password Reset Form Component
 * Handles password reset request and confirmation
 */

'use client';

import React, { useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Mail, Lock, Eye, EyeOff, ArrowLeft, CheckCircle } from 'lucide-react';

import { useAuth } from '@/hooks';
import { Button, Input, Alert } from '@/components/ui';
import { 
  passwordResetSchema, 
  passwordResetConfirmSchema,
  PasswordResetFormData,
  PasswordResetConfirmFormData 
} from '@/lib/validations';

interface PasswordResetFormProps {
  mode: 'request' | 'confirm';
  token?: string;
  uidb64?: string;
}

const PasswordResetForm: React.FC<PasswordResetFormProps> = ({
  mode,
  token,
  uidb64,
}) => {
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const { resetPassword, confirmPasswordReset, clearError } = useAuth();
  const router = useRouter();

  // Password Reset Request Form
  const requestForm = useForm<PasswordResetFormData>({
    resolver: zodResolver(passwordResetSchema),
    defaultValues: { email: '' },
  });

  // Password Reset Confirm Form
  const confirmForm = useForm<PasswordResetConfirmFormData>({
    resolver: zodResolver(passwordResetConfirmSchema),
    defaultValues: { password: '', confirmPassword: '' },
  });

  const onSubmitRequest = async (data: PasswordResetFormData) => {
    try {
      clearError();
      await resetPassword(data.email);
      setIsSuccess(true);
    } catch (error: any) {
      console.error('Password reset request error:', error);
      requestForm.setError('email', {
        message: error.message || 'Failed to send reset email. Please try again.',
      });
    }
  };

  const onSubmitConfirm = async (data: PasswordResetConfirmFormData) => {
    if (!token || !uidb64) {
      confirmForm.setError('password', {
        message: 'Invalid reset link. Please request a new password reset.',
      });
      return;
    }

    try {
      clearError();
      const { confirmPassword, ...resetData } = data;
      await confirmPasswordReset(token, uidb64, {
        password: resetData.password,
        password_confirm: confirmPassword,
      });
      setIsSuccess(true);
    } catch (error: any) {
      console.error('Password reset confirm error:', error);
      
      if (error.errors) {
        Object.entries(error.errors).forEach(([field, messages]) => {
          if (Array.isArray(messages) && messages.length > 0) {
            confirmForm.setError(field as keyof PasswordResetConfirmFormData, {
              message: messages[0],
            });
          }
        });
      } else {
        confirmForm.setError('password', {
          message: error.message || 'Failed to reset password. Please try again.',
        });
      }
    }
  };

  const getPasswordStrength = (password: string): { score: number; label: string; color: string } => {
    if (!password) return { score: 0, label: '', color: '' };
    
    let score = 0;
    if (password.length >= 8) score += 25;
    if (/[a-z]/.test(password)) score += 25;
    if (/[A-Z]/.test(password)) score += 25;
    if (/\d/.test(password)) score += 15;
    if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) score += 10;
    
    if (score >= 90) return { score, label: 'Very Strong', color: 'bg-green-500' };
    if (score >= 70) return { score, label: 'Strong', color: 'bg-green-400' };
    if (score >= 50) return { score, label: 'Moderate', color: 'bg-yellow-400' };
    if (score >= 25) return { score, label: 'Weak', color: 'bg-red-400' };
    return { score, label: 'Very Weak', color: 'bg-red-500' };
  };

  const password = confirmForm.watch('password');
  const passwordStrength = getPasswordStrength(password || '');

  // Success states
  if (isSuccess && mode === 'request') {
    return (
      <div className="w-full max-w-md mx-auto">
        <div className="bg-white shadow-lg rounded-lg px-8 pt-8 pb-6 text-center">
          <div className="mb-6">
            <CheckCircle className="h-16 w-16 text-green-500 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              Check Your Email
            </h2>
            <p className="text-gray-600">
              We've sent a password reset link to your email address. 
              Please check your inbox and follow the instructions to reset your password.
            </p>
          </div>
          
          <div className="space-y-4">
            <p className="text-sm text-gray-500">
              Didn't receive the email? Check your spam folder or{' '}
              <button
                onClick={() => setIsSuccess(false)}
                className="text-blue-600 hover:text-blue-500 font-medium"
              >
                try again
              </button>
            </p>
            
            <Link
              href="/auth/login"
              className="inline-flex items-center text-blue-600 hover:text-blue-500 font-medium"
            >
              <ArrowLeft className="h-4 w-4 mr-1" />
              Back to Sign In
            </Link>
          </div>
        </div>
      </div>
    );
  }

  if (isSuccess && mode === 'confirm') {
    return (
      <div className="w-full max-w-md mx-auto">
        <div className="bg-white shadow-lg rounded-lg px-8 pt-8 pb-6 text-center">
          <div className="mb-6">
            <CheckCircle className="h-16 w-16 text-green-500 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              Password Reset Successfully
            </h2>
            <p className="text-gray-600">
              Your password has been reset successfully. You can now sign in with your new password.
            </p>
          </div>
          
          <Button
            onClick={() => router.push('/auth/login')}
            className="w-full"
            size="lg"
          >
            Sign In Now
          </Button>
        </div>
      </div>
    );
  }

  // Request Form
  if (mode === 'request') {
    return (
      <div className="w-full max-w-md mx-auto">
        <div className="bg-white shadow-lg rounded-lg px-8 pt-8 pb-6">
          <div className="mb-8 text-center">
            <h2 className="text-2xl font-bold text-gray-900">
              Reset Password
            </h2>
            <p className="mt-2 text-sm text-gray-600">
              Enter your email address and we'll send you a link to reset your password.
            </p>
          </div>

          <form onSubmit={requestForm.handleSubmit(onSubmitRequest)} className="space-y-6">
            <Input
              label="Email Address"
              type="email"
              placeholder="Enter your email"
              required
              icon={<Mail className="h-5 w-5" />}
              error={requestForm.formState.errors.email?.message}
              {...requestForm.register('email')}
            />

            <Button
              type="submit"
              loading={requestForm.formState.isSubmitting}
              disabled={requestForm.formState.isSubmitting}
              className="w-full"
              size="lg"
            >
              {requestForm.formState.isSubmitting ? 'Sending...' : 'Send Reset Link'}
            </Button>
          </form>

          <div className="mt-6 text-center">
            <Link
              href="/auth/login"
              className="inline-flex items-center text-blue-600 hover:text-blue-500 font-medium"
            >
              <ArrowLeft className="h-4 w-4 mr-1" />
              Back to Sign In
            </Link>
          </div>
        </div>
      </div>
    );
  }

  // Confirm Form
  return (
    <div className="w-full max-w-md mx-auto">
      <div className="bg-white shadow-lg rounded-lg px-8 pt-8 pb-6">
        <div className="mb-8 text-center">
          <h2 className="text-2xl font-bold text-gray-900">
            Set New Password
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            Enter your new password below.
          </p>
        </div>

        <form onSubmit={confirmForm.handleSubmit(onSubmitConfirm)} className="space-y-6">
          {/* New Password */}
          <div className="relative">
            <Input
              label="New Password"
              type={showPassword ? 'text' : 'password'}
              placeholder="Enter your new password"
              required
              icon={<Lock className="h-5 w-5" />}
              error={confirmForm.formState.errors.password?.message}
              {...confirmForm.register('password')}
            />
            <button
              type="button"
              className="absolute inset-y-0 right-0 top-6 pr-3 flex items-center"
              onClick={() => setShowPassword(!showPassword)}
              tabIndex={-1}
            >
              {showPassword ? (
                <EyeOff className="h-5 w-5 text-gray-400 hover:text-gray-600" />
              ) : (
                <Eye className="h-5 w-5 text-gray-400 hover:text-gray-600" />
              )}
            </button>
          </div>

          {/* Password Strength Indicator */}
          {password && (
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Password strength:</span>
                <span className={`text-sm font-medium ${
                  passwordStrength.score >= 70 ? 'text-green-600' : 
                  passwordStrength.score >= 50 ? 'text-yellow-600' : 
                  'text-red-600'
                }`}>
                  {passwordStrength.label}
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className={`h-2 rounded-full transition-all duration-300 ${passwordStrength.color}`}
                  style={{ width: `${passwordStrength.score}%` }}
                />
              </div>
            </div>
          )}

          {/* Confirm Password */}
          <div className="relative">
            <Input
              label="Confirm New Password"
              type={showConfirmPassword ? 'text' : 'password'}
              placeholder="Confirm your new password"
              required
              icon={<Lock className="h-5 w-5" />}
              error={confirmForm.formState.errors.confirmPassword?.message}
              {...confirmForm.register('confirmPassword')}
            />
            <button
              type="button"
              className="absolute inset-y-0 right-0 top-6 pr-3 flex items-center"
              onClick={() => setShowConfirmPassword(!showConfirmPassword)}
              tabIndex={-1}
            >
              {showConfirmPassword ? (
                <EyeOff className="h-5 w-5 text-gray-400 hover:text-gray-600" />
              ) : (
                <Eye className="h-5 w-5 text-gray-400 hover:text-gray-600" />
              )}
            </button>
          </div>

          <Button
            type="submit"
            loading={confirmForm.formState.isSubmitting}
            disabled={confirmForm.formState.isSubmitting}
            className="w-full"
            size="lg"
          >
            {confirmForm.formState.isSubmitting ? 'Resetting...' : 'Reset Password'}
          </Button>
        </form>

        <div className="mt-6 text-center">
          <Link
            href="/auth/login"
            className="inline-flex items-center text-blue-600 hover:text-blue-500 font-medium"
          >
            <ArrowLeft className="h-4 w-4 mr-1" />
            Back to Sign In
          </Link>
        </div>
      </div>
    </div>
  );
};

export default PasswordResetForm;