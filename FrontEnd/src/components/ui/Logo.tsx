/**
 * Logo Component
 * Clickable logo that redirects users based on authentication status
 */

'use client';

import React from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Building2 } from 'lucide-react';
import { useAuth } from '@/hooks';

interface LogoProps {
  size?: 'sm' | 'md' | 'lg';
  showText?: boolean;
  className?: string;
  variant?: 'default' | 'white';
}

const Logo: React.FC<LogoProps> = ({
  size = 'md',
  showText = true,
  className = '',
  variant = 'default'
}) => {
  const { authState } = useAuth();
  const router = useRouter();

  // Determine redirect destination based on auth status
  const getRedirectPath = () => {
    if (!authState.isAuthenticated) {
      return '/';
    }

    // For authenticated users, redirect to dashboard or appropriate page
    // You can customize this logic based on user roles/permissions
    const user = authState.user;
    if (user) {
      // Check user role hierarchy to determine best landing page
      if (['CEO', 'Owner', 'Admin'].includes(user.user_type || '')) {
        return '/dashboard';
      } else if (user.user_type === 'Manager') {
        return '/dashboard';
      } else {
        return '/dashboard'; // Default for all authenticated users
      }
    }
    
    return '/dashboard';
  };

  const redirectPath = getRedirectPath();

  // Size configurations
  const sizeConfig = {
    sm: {
      icon: 'h-6 w-6',
      text: 'text-lg',
      container: 'gap-2'
    },
    md: {
      icon: 'h-8 w-8',
      text: 'text-2xl',
      container: 'gap-3'
    },
    lg: {
      icon: 'h-10 w-10',
      text: 'text-3xl',
      container: 'gap-4'
    }
  };

  // Color variants
  const colorConfig = {
    default: {
      icon: 'text-blue-600',
      text: 'text-gray-900',
      hover: 'hover:text-blue-700'
    },
    white: {
      icon: 'text-white',
      text: 'text-white',
      hover: 'hover:text-gray-200'
    }
  };

  const currentSize = sizeConfig[size];
  const currentColor = colorConfig[variant];

  const handleClick = (e: React.MouseEvent) => {
    e.preventDefault();
    router.push(redirectPath);
  };

  return (
    <Link 
      href={redirectPath}
      onClick={handleClick}
      className={`
        inline-flex items-center ${currentSize.container} 
        transition-colors duration-200 ${currentColor.hover}
        ${className}
      `}
      aria-label="DryWall ERP - Go to home"
    >
      <Building2 
        className={`${currentSize.icon} ${currentColor.icon}`}
        aria-hidden="true"
      />
      {showText && (
        <span className={`${currentSize.text} font-bold ${currentColor.text}`}>
          DryWall ERP
        </span>
      )}
    </Link>
  );
};

export default Logo;