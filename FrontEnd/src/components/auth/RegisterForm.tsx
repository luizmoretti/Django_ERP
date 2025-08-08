/**
 * Register Form Component
 * Handles new user registration with comprehensive validation
 */

'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Eye, EyeOff, Mail, Lock, User, UserCheck } from 'lucide-react';

import { useAuth } from '@/hooks';
import { Button, Input, Alert } from '@/components/ui';
import { registerSchema, RegisterFormData } from '@/lib/validations';
import { UserType } from '@/types';

interface RegisterFormProps {
  redirectTo?: string;
  showLoginLink?: boolean;
  allowedUserTypes?: UserType[];
}

const RegisterForm: React.FC<RegisterFormProps> = ({
  redirectTo = '/auth/login',
  showLoginLink = true,
  allowedUserTypes,
}) => {
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const { register: registerUser, authState, clearError } = useAuth();
  const router = useRouter();

  // Clear any existing auth errors when component mounts
  React.useEffect(() => {
    if (authState.error) {
      clearError();
    }
  }, []);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    setError,
    watch,
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      email: '',
      password: '',
      confirmPassword: '',
      first_name: '',
      last_name: '',
      user_type: 'Employee',
    },
  });

  const password = watch('password');

  // Available user types (filtered if allowedUserTypes is provided)
  const userTypeOptions: Array<{ value: UserType; label: string }> = [
    { value: 'CEO', label: 'Chief Executive Officer' },
    { value: 'Owner', label: 'Business Owner' },
    { value: 'Admin', label: 'System Administrator' },
    { value: 'Manager', label: 'Manager' },
    { value: 'Employee', label: 'Employee' },
    { value: 'Installer', label: 'Installer' },
    { value: 'Stocker', label: 'Stock Manager' },
    { value: 'Salesman', label: 'Sales Representative' },
    { value: 'Driver', label: 'Driver' },
    { value: 'Customer', label: 'Customer' },
    { value: 'Supplier', label: 'Supplier' },
  ].filter(option => 
    !allowedUserTypes || allowedUserTypes.includes(option.value)
  );

  const onSubmit = async (data: RegisterFormData) => {
    try {
      clearError();
      
      // Remove confirmPassword from data before sending to API
      const { confirmPassword, ...registrationData } = data;
      
      await registerUser(registrationData);
      
      // Redirect to login page with success message
      router.push(`${redirectTo}?registered=true`);
    } catch (error: any) {
      console.error('Registration error:', error);
      
      // Handle specific error types
      if (error.errors) {
        // Handle validation errors from backend
        Object.entries(error.errors).forEach(([field, messages]) => {
          if (Array.isArray(messages) && messages.length > 0) {
            setError(field as keyof RegisterFormData, { message: messages[0] });
          }
        });
      } else {
        setError('email', { 
          message: error.message || 'Registration failed. Please try again.' 
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

  const passwordStrength = getPasswordStrength(password);

  return (
    <div className="w-full max-w-md mx-auto">
      <div className="bg-white shadow-lg rounded-lg px-8 pt-8 pb-6">
        <div className="mb-8 text-center">
          <h2 className="text-2xl font-bold text-gray-900">
            Create Account
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            Join our warehouse management system
          </p>
        </div>

        {authState.error && (
          <div className="mb-6">
            <Alert
              type="error"
              message={authState.error}
              dismissible
              onDismiss={clearError}
            />
          </div>
        )}

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          {/* Name Fields */}
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <Input
              label="First Name"
              type="text"
              placeholder="John"
              required
              icon={<User className="h-5 w-5" />}
              error={errors.first_name?.message}
              {...register('first_name')}
            />

            <Input
              label="Last Name"
              type="text"
              placeholder="Doe"
              required
              icon={<User className="h-5 w-5" />}
              error={errors.last_name?.message}
              {...register('last_name')}
            />
          </div>

          {/* Email */}
          <Input
            label="Email Address"
            type="email"
            placeholder="john.doe@company.com"
            required
            icon={<Mail className="h-5 w-5" />}
            error={errors.email?.message}
            {...register('email')}
          />

          {/* User Type */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Role <span className="text-red-500">*</span>
            </label>
            <div className="relative">
              <UserCheck className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
              <select
                className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md shadow-sm text-gray-900 bg-white focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                {...register('user_type')}
              >
                {userTypeOptions.map((option) => (
                  <option key={option.value} value={option.value} className="text-gray-900">
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
            {errors.user_type && (
              <p className="mt-1 text-sm text-red-600">{errors.user_type.message}</p>
            )}
          </div>

          {/* Password */}
          <div className="relative">
            <Input
              label="Password"
              type={showPassword ? 'text' : 'password'}
              placeholder="Create a strong password"
              required
              icon={<Lock className="h-5 w-5" />}
              error={errors.password?.message}
              {...register('password')}
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
              label="Confirm Password"
              type={showConfirmPassword ? 'text' : 'password'}
              placeholder="Confirm your password"
              required
              icon={<Lock className="h-5 w-5" />}
              error={errors.confirmPassword?.message}
              {...register('confirmPassword')}
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

          {/* Terms and Conditions */}
          <div className="flex items-start">
            <input
              id="terms"
              name="terms"
              type="checkbox"
              required
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded mt-1"
            />
            <label htmlFor="terms" className="ml-2 block text-sm text-gray-700">
              I agree to the{' '}
              <Link href="/terms" className="text-blue-600 hover:text-blue-500 font-medium">
                Terms of Service
              </Link>{' '}
              and{' '}
              <Link href="/privacy" className="text-blue-600 hover:text-blue-500 font-medium">
                Privacy Policy
              </Link>
            </label>
          </div>

          <Button
            type="submit"
            loading={isSubmitting || authState.isLoading}
            disabled={isSubmitting || authState.isLoading}
            className="w-full"
            size="lg"
          >
            {isSubmitting || authState.isLoading ? 'Creating Account...' : 'Create Account'}
          </Button>
        </form>

        {showLoginLink && (
          <div className="mt-6 text-center">
            <p className="text-sm text-gray-600">
              Already have an account?{' '}
              <Link
                href="/auth/login"
                className="font-medium text-blue-600 hover:text-blue-500"
              >
                Sign in here
              </Link>
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default RegisterForm;