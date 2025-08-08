/**
 * Alert Component
 * Reusable alert component for displaying messages and notifications
 */

import React from 'react';
import { AlertCircle, CheckCircle, Info, XCircle, X } from 'lucide-react';

interface AlertProps {
  variant?: 'default' | 'destructive' | 'success' | 'warning';
  type?: 'success' | 'error' | 'warning' | 'info';
  title?: string;
  message?: string;
  dismissible?: boolean;
  onDismiss?: () => void;
  className?: string;
  children?: React.ReactNode;
}

interface AlertTitleProps {
  children: React.ReactNode;
  className?: string;
}

interface AlertDescriptionProps {
  children: React.ReactNode;
  className?: string;
}

const Alert: React.FC<AlertProps> & {
  Title: React.FC<AlertTitleProps>;
  Description: React.FC<AlertDescriptionProps>;
} = ({
  variant = 'default',
  type,
  title,
  message,
  dismissible = false,
  onDismiss,
  className = '',
  children,
}) => {
  // Map variant to type for backward compatibility
  const alertType = type || (variant === 'destructive' ? 'error' : variant === 'success' ? 'success' : variant === 'warning' ? 'warning' : 'info');

  const alertConfig = {
    success: {
      icon: CheckCircle,
      bgColor: 'bg-green-50',
      borderColor: 'border-green-200',
      iconColor: 'text-green-400',
      titleColor: 'text-green-800',
      messageColor: 'text-green-700',
      buttonColor: 'text-green-500 hover:bg-green-100',
    },
    error: {
      icon: XCircle,
      bgColor: 'bg-red-50',
      borderColor: 'border-red-200',
      iconColor: 'text-red-400',
      titleColor: 'text-red-800',
      messageColor: 'text-red-700',
      buttonColor: 'text-red-500 hover:bg-red-100',
    },
    warning: {
      icon: AlertCircle,
      bgColor: 'bg-yellow-50',
      borderColor: 'border-yellow-200',
      iconColor: 'text-yellow-400',
      titleColor: 'text-yellow-800',
      messageColor: 'text-yellow-700',
      buttonColor: 'text-yellow-500 hover:bg-yellow-100',
    },
    info: {
      icon: Info,
      bgColor: 'bg-blue-50',
      borderColor: 'border-blue-200',
      iconColor: 'text-blue-400',
      titleColor: 'text-blue-800',
      messageColor: 'text-blue-700',
      buttonColor: 'text-blue-500 hover:bg-blue-100',
    },
  };

  const config = alertConfig[alertType];
  const IconComponent = config.icon;

  const alertClasses = [
    'rounded-md border p-4',
    config.bgColor,
    config.borderColor,
    className,
  ].filter(Boolean).join(' ');

  // If children are provided, use the new API
  if (children) {
    return (
      <div className={alertClasses} role="alert">
        <div className="flex">
          <div className="flex-shrink-0">
            <IconComponent className={`h-5 w-5 ${config.iconColor}`} />
          </div>
          
          <div className="ml-3 flex-1">
            {children}
          </div>

          {dismissible && onDismiss && (
            <div className="ml-auto pl-3">
              <div className="-mx-1.5 -my-1.5">
                <button
                  type="button"
                  className={`inline-flex rounded-md p-1.5 focus:outline-none focus:ring-2 focus:ring-offset-2 ${config.buttonColor}`}
                  onClick={onDismiss}
                  aria-label="Dismiss alert"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    );
  }

  // Fallback to old API for backward compatibility
  return (
    <div className={alertClasses} role="alert">
      <div className="flex">
        <div className="flex-shrink-0">
          <IconComponent className={`h-5 w-5 ${config.iconColor}`} />
        </div>
        
        <div className="ml-3 flex-1">
          {title && (
            <h3 className={`text-sm font-medium ${config.titleColor}`}>
              {title}
            </h3>
          )}
          
          {message && (
            <div className={`${title ? 'mt-2' : ''} text-sm ${config.messageColor}`}>
              {message}
            </div>
          )}
        </div>

        {dismissible && onDismiss && (
          <div className="ml-auto pl-3">
            <div className="-mx-1.5 -my-1.5">
              <button
                type="button"
                className={`inline-flex rounded-md p-1.5 focus:outline-none focus:ring-2 focus:ring-offset-2 ${config.buttonColor}`}
                onClick={onDismiss}
                aria-label="Dismiss alert"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

const AlertTitle: React.FC<AlertTitleProps> = ({ children, className = '' }) => {
  return (
    <h3 className={`text-sm font-medium ${className}`}>
      {children}
    </h3>
  );
};

const AlertDescription: React.FC<AlertDescriptionProps> = ({ children, className = '' }) => {
  return (
    <div className={`text-sm ${className}`}>
      {children}
    </div>
  );
};

Alert.Title = AlertTitle;
Alert.Description = AlertDescription;

export default Alert;
export { AlertTitle, AlertDescription };