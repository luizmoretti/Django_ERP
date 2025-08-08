/**
 * Login Form Component
 * Handles user authentication with email and password
 */

'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Eye, EyeOff, Mail, Lock } from 'lucide-react';

import { useAuth } from '@/hooks';
import { Button, Input, Alert } from '@/components/ui';
import { loginSchema, LoginFormData } from '@/lib/validations';

interface LoginFormProps {
  redirectTo?: string;
  showRegisterLink?: boolean;
  showForgotPassword?: boolean;
}

const LoginForm: React.FC<LoginFormProps> = ({
  redirectTo,
  showRegisterLink = true,
  showForgotPassword = true,
}) => {
  const [showPassword, setShowPassword] = useState(false);
  const { login, authState, clearError } = useAuth();
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
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: '',
      password: '',
    },
  });

  const onSubmit = async (data: LoginFormData) => {
    try {
      clearError();
      const response = await login(data);
      
      // Redirect after successful login
      const destination = redirectTo || response.redirect_url || '/dashboard';
      router.push(destination);
    } catch (error: any) {
      console.error('Login error:', error);
      
      // Handle specific error types
      if (error.status === 400) {
        setError('email', { message: 'Invalid email or password' });
      } else if (error.errors) {
        // Handle validation errors from backend
        Object.entries(error.errors).forEach(([field, messages]) => {
          if (Array.isArray(messages) && messages.length > 0) {
            setError(field as keyof LoginFormData, { message: messages[0] });
          }
        });
      } else {
        setError('email', { 
          message: error.message || 'Login failed. Please try again.' 
        });
      }
    }
  };

  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

  return (
    <div className="w-full max-w-md mx-auto">
      <div className="bg-white shadow-lg rounded-lg px-8 pt-8 pb-6">
        <div className="mb-8 text-center">
          <h2 className="text-2xl font-bold text-gray-900">
            Sign In
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            Welcome back! Please sign in to your account.
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
          <Input
            label="Email Address"
            type="email"
            placeholder="Enter your email"
            required
            icon={<Mail className="h-5 w-5" />}
            error={errors.email?.message}
            {...register('email')}
          />

          <div className="relative">
            <Input
              label="Password"
              type={showPassword ? 'text' : 'password'}
              placeholder="Enter your password"
              required
              icon={<Lock className="h-5 w-5" />}
              error={errors.password?.message}
              {...register('password')}
            />
            <button
              type="button"
              className="absolute inset-y-0 right-0 top-6 pr-3 flex items-center"
              onClick={togglePasswordVisibility}
              tabIndex={-1}
            >
              {showPassword ? (
                <EyeOff className="h-5 w-5 text-gray-400 hover:text-gray-600" />
              ) : (
                <Eye className="h-5 w-5 text-gray-400 hover:text-gray-600" />
              )}
            </button>
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <input
                id="remember-me"
                name="remember-me"
                type="checkbox"
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label htmlFor="remember-me" className="ml-2 block text-sm text-gray-700">
                Remember me
              </label>
            </div>

            {showForgotPassword && (
              <Link
                href="/auth/forgot-password"
                className="text-sm text-blue-600 hover:text-blue-500 font-medium"
              >
                Forgot password?
              </Link>
            )}
          </div>

          <Button
            type="submit"
            loading={isSubmitting || authState.isLoading}
            disabled={isSubmitting || authState.isLoading}
            className="w-full"
            size="lg"
          >
            {isSubmitting || authState.isLoading ? 'Signing In...' : 'Sign In'}
          </Button>
        </form>

        {showRegisterLink && (
          <div className="mt-6 text-center">
            <p className="text-sm text-gray-600">
              Don't have an account?{' '}
              <Link
                href="/auth/register"
                className="font-medium text-blue-600 hover:text-blue-500"
              >
                Sign up here
              </Link>
            </p>
          </div>
        )}
      </div>

      {/* Additional Help Text */}
      <div className="mt-4 text-center">
        <p className="text-xs text-gray-500">
          By signing in, you agree to our{' '}
          <Link href="/terms" className="text-blue-600 hover:text-blue-500">
            Terms of Service
          </Link>{' '}
          and{' '}
          <Link href="/privacy" className="text-blue-600 hover:text-blue-500">
            Privacy Policy
          </Link>
        </p>
      </div>
    </div>
  );
};

export default LoginForm;