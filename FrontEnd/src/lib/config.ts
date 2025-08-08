/**
 * Application Configuration
 * Centralized configuration management for the React application
 */

export const config = {
  // API Configuration
  api: {
    baseURL: process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000',
    timeout: 30000, // 30 seconds
    retryAttempts: 3,
    retryDelay: 1000, // 1 second
  },

  // WebSocket Configuration (if needed for real-time features)
  websocket: {
    baseURL: process.env.NEXT_PUBLIC_WS_BASE_URL || 'ws://localhost:8000',
    reconnectAttempts: 5,
    reconnectDelay: 3000, // 3 seconds
  },

  // Authentication Configuration
  auth: {
    tokenStorageKey: 'auth_token',
    refreshTokenKey: 'refresh_token',
    userDataKey: 'user_data',
    tokenRefreshThreshold: 5 * 60 * 1000, // 5 minutes before expiry
    sessionTimeout: 24 * 60 * 60 * 1000, // 24 hours
  },

  // Application Metadata
  app: {
    name: 'DryWall Warehouse Management',
    version: process.env.NEXT_PUBLIC_APP_VERSION || '1.0.0',
    description: 'Comprehensive warehouse and inventory management system',
    author: 'DryWall Team',
  },

  // Feature Flags
  features: {
    enablePWA: process.env.NEXT_PUBLIC_ENABLE_PWA === 'true',
    enableAnalytics: process.env.NEXT_PUBLIC_ENABLE_ANALYTICS === 'true',
    enableNotifications: process.env.NEXT_PUBLIC_ENABLE_NOTIFICATIONS === 'true',
    enableOfflineMode: process.env.NEXT_PUBLIC_ENABLE_OFFLINE === 'true',
    enableDarkMode: true,
    enableMultiLanguage: true,
  },

  // UI Configuration
  ui: {
    defaultTheme: 'light' as 'light' | 'dark' | 'system',
    defaultLanguage: 'en' as 'en' | 'es' | 'pt',
    sidebarCollapsed: false,
    pageSize: 25,
    maxFileSize: 10 * 1024 * 1024, // 10MB
    allowedFileTypes: ['image/*', '.pdf', '.doc', '.docx', '.xls', '.xlsx'],
  },

  // Security Configuration
  security: {
    enableCSRF: true,
    enableCORS: true,
    maxLoginAttempts: 5,
    lockoutDuration: 15 * 60 * 1000, // 15 minutes
    passwordMinLength: 8,
    passwordRequireSpecialChars: true,
    passwordRequireNumbers: true,
    passwordRequireUppercase: true,
    passwordRequireLowercase: true,
  },

  // Cache Configuration
  cache: {
    userProfile: 5 * 60 * 1000, // 5 minutes
    navigation: 10 * 60 * 1000, // 10 minutes
    staticData: 30 * 60 * 1000, // 30 minutes
  },

  // Error Tracking
  errorTracking: {
    enabled: process.env.NODE_ENV === 'production',
    sampleRate: 0.1, // 10% of errors
    maxBreadcrumbs: 50,
  },

  // Performance
  performance: {
    enableLazyLoading: true,
    enableImageOptimization: true,
    enableCodeSplitting: true,
    preloadRoutes: ['/', '/dashboard', '/auth/login'],
  },

  // Development
  development: {
    enableDevTools: process.env.NODE_ENV === 'development',
    enableHotReload: process.env.NODE_ENV === 'development',
    showApiLogs: process.env.NODE_ENV === 'development',
    mockApiDelay: 1000, // 1 second delay for mocked APIs
  },
} as const;

// Environment-specific configurations
export const getEnvironmentConfig = () => {
  const env = process.env.NODE_ENV || 'development';
  
  const environmentConfigs = {
    development: {
      api: {
        ...config.api,
        baseURL: 'http://localhost:8000',
      },
      logging: {
        level: 'debug',
        enableConsole: true,
        enableRemote: false,
      },
    },
    production: {
      api: {
        ...config.api,
        baseURL: process.env.NEXT_PUBLIC_API_BASE_URL || 'https://api.yourcompany.com',
      },
      logging: {
        level: 'error',
        enableConsole: false,
        enableRemote: true,
      },
    },
    test: {
      api: {
        ...config.api,
        baseURL: 'http://localhost:8001',
        timeout: 5000,
      },
      logging: {
        level: 'warn',
        enableConsole: true,
        enableRemote: false,
      },
    },
  };

  const envConfig = environmentConfigs[env as keyof typeof environmentConfigs];
  
  return {
    ...config,
    api: {
      ...config.api,
      ...envConfig.api,
    },
    logging: envConfig.logging,
  };
};

// Type for the complete configuration
export type Config = typeof config;
export type EnvironmentConfig = ReturnType<typeof getEnvironmentConfig>;

// Export the environment-specific config as default
export default getEnvironmentConfig();