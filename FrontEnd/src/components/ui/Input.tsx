/**
 * Input Component
 * Reusable input component with validation and error states
 */

import React, { forwardRef } from 'react';
import { InputProps } from '@/types';

interface InputComponentProps extends InputProps, Omit<React.InputHTMLAttributes<HTMLInputElement>, 'className'> {
  icon?: React.ReactNode;
}

const Input = forwardRef<HTMLInputElement, InputComponentProps>(
  ({ label, error, helperText, required, disabled, className = '', icon, ...props }, ref) => {
    const inputClasses = [
      'block w-full px-3 py-2 border rounded-md shadow-sm placeholder-gray-400 bg-white',
      'focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500',
      'disabled:bg-gray-50 disabled:text-gray-500 disabled:cursor-not-allowed',
      error 
        ? 'border-red-500 text-red-900 placeholder-red-300 focus:ring-red-500 focus:border-red-500' 
        : 'border-gray-300 text-gray-900',
      icon && 'pl-10',
      className,
    ].filter(Boolean).join(' ');

    const labelClasses = [
      'block text-sm font-medium mb-1',
      error ? 'text-red-700' : 'text-gray-700',
    ].join(' ');

    return (
      <div className="relative">
        {label && (
          <label className={labelClasses}>
            {label}
            {required && <span className="text-red-500 ml-1">*</span>}
          </label>
        )}
        
        <div className="relative">
          {icon && (
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <div className={error ? 'text-red-400' : 'text-gray-400'}>
                {icon}
              </div>
            </div>
          )}
          
          <input
            ref={ref}
            className={inputClasses}
            disabled={disabled}
            aria-invalid={error ? 'true' : 'false'}
            aria-describedby={error ? `${props.name}-error` : helperText ? `${props.name}-description` : undefined}
            {...props}
          />
        </div>

        {error && (
          <p id={`${props.name}-error`} className="mt-1 text-sm text-red-600">
            {error}
          </p>
        )}

        {helperText && !error && (
          <p id={`${props.name}-description`} className="mt-1 text-sm text-gray-500">
            {helperText}
          </p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';

export default Input;