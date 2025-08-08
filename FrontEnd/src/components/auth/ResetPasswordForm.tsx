/**
 * Reset Password Form Component
 * Form for setting a new password after email verification
 */

'use client';

import React, { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Lock, Eye, EyeOff, CheckCircle } from 'lucide-react';
import { Button, Input, Alert } from '@/components/ui';
import { useAuth } from '@/hooks';
import { passwordResetConfirmSchema, PasswordResetConfirmFormData } from '@/lib/validations';

interface ResetPasswordFormProps {
  token: string;
  uidb64: string;
}

const ResetPasswordForm: React.FC<ResetPasswordFormProps> = ({
  token,
  uidb64,
}) => {
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const { confirmPasswordReset } = useAuth();
  const router = useRouter();

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    setError,
    watch,
  } = useForm<PasswordResetConfirmFormData>({
    resolver: zodResolver(passwordResetConfirmSchema),
    defaultValues: {
      password: '',
      confirmPassword: '',
    },
  });

  const password = watch('password');

  const onSubmit = async (data: PasswordResetConfirmFormData) => {
    try {
      await confirmPasswordReset(token, uidb64, {
        password: data.password,
        password_confirm: data.confirmPassword,
      });
      setIsSuccess(true);
      
      // Redirect to login after 3 seconds
      setTimeout(() => {
        router.push('/auth/login?reset=success');
      }, 3000);
    } catch (error: any) {
      console.error('Password reset error:', error);
      
      if (error.status === 400) {
        if (error.errors?.token) {
          setError('password', { 
            message: 'Invalid or expired reset link. Please request a new one.' 
          });
        } else if (error.errors?.password) {
          setError('password', { message: error.errors.password[0] });
        } else {
          setError('password', { 
            message: error.message || 'Failed to reset password. Please try again.' 
          });
        }
      } else {
        setError('password', { 
          message: 'An unexpected error occurred. Please try again.' 
        });
      }
    }
  };

  // Password strength indicators
  const passwordStrength = {
    hasMinLength: password.length >= 8,
    hasUpperCase: /[A-Z]/.test(password),
    hasLowerCase: /[a-z]/.test(password),
    hasNumber: /\d/.test(password),
    hasSpecial: /[!@#$%^&*(),.?":{}|<>]/.test(password),
  };

  const strengthScore = Object.values(passwordStrength).filter(Boolean).length;
  const strengthText = ['Very Weak', 'Weak', 'Fair', 'Good', 'Strong'][strengthScore - 1] || 'Very Weak';
  const strengthColor = ['red', 'orange', 'yellow', 'blue', 'green'][strengthScore - 1] || 'red';

  if (isSuccess) {
    return (
      <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
        <div className="text-center">
          <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-green-100">
            <CheckCircle className="h-6 w-6 text-green-600" />
          </div>
          <h3 className="mt-4 text-lg font-medium text-gray-900">
            Password Reset Successful!
          </h3>
          <p className="mt-2 text-sm text-gray-600">
            Your password has been successfully reset. 
            Redirecting you to login page...
          </p>
          <div className="mt-6">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900">
          Set new password
        </h2>
        <p className="mt-2 text-sm text-gray-600">
          Your new password must be different from previous passwords.
        </p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        <div>
          <Input
            {...register('password')}
            type={showPassword ? 'text' : 'password'}
            label="New Password"
            placeholder="Enter new password"
            error={errors.password?.message}
            icon={<Lock />}
            autoComplete="new-password"
            required
          />
          <button
            type="button"
            className="absolute right-3 top-9 text-gray-400 hover:text-gray-600"
            onClick={() => setShowPassword(!showPassword)}
          >
            {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
          </button>

          {/* Password strength indicator */}
          {password && (
            <div className="mt-2">
              <div className="flex items-center justify-between text-xs">
                <span className="text-gray-600">Password strength:</span>
                <span className={`font-medium text-${strengthColor}-600`}>
                  {strengthText}
                </span>
              </div>
              <div className="mt-1 h-2 bg-gray-200 rounded-full overflow-hidden">
                <div 
                  className={`h-full bg-${strengthColor}-500 transition-all duration-300`}
                  style={{ width: `${(strengthScore / 5) * 100}%` }}
                />
              </div>
              <ul className="mt-2 space-y-1 text-xs text-gray-500">
                <li className={passwordStrength.hasMinLength ? 'text-green-600' : ''}>
                  ✓ At least 8 characters
                </li>
                <li className={passwordStrength.hasUpperCase ? 'text-green-600' : ''}>
                  ✓ One uppercase letter
                </li>
                <li className={passwordStrength.hasLowerCase ? 'text-green-600' : ''}>
                  ✓ One lowercase letter
                </li>
                <li className={passwordStrength.hasNumber ? 'text-green-600' : ''}>
                  ✓ One number
                </li>
                <li className={passwordStrength.hasSpecial ? 'text-green-600' : ''}>
                  ✓ One special character
                </li>
              </ul>
            </div>
          )}
        </div>

        <div>
          <Input
            {...register('confirmPassword')}
            type={showConfirmPassword ? 'text' : 'password'}
            label="Confirm New Password"
            placeholder="Confirm new password"
            error={errors.confirmPassword?.message}
            icon={<Lock />}
            autoComplete="new-password"
            required
          />
          <button
            type="button"
            className="absolute right-3 top-9 text-gray-400 hover:text-gray-600"
            onClick={() => setShowConfirmPassword(!showConfirmPassword)}
          >
            {showConfirmPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
          </button>
        </div>

        <div>
          <Button
            type="submit"
            variant="primary"
            loading={isSubmitting}
            disabled={isSubmitting}
            className="w-full"
          >
            {isSubmitting ? 'Resetting...' : 'Reset Password'}
          </Button>
        </div>
      </form>
    </div>
  );
};

export default ResetPasswordForm;