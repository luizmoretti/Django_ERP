/**
 * Hooks Index
 * Central export point for all custom hooks
 */

// Re-export useAuth from AuthContext to avoid duplication
export { useAuth } from '@/contexts/AuthContext';
export { 
  useProtectedRoute, 
  useCanAccess, 
  useRoleCheck, 
  usePermissionCheck 
} from './useProtectedRoute';

// Additional hooks can be exported here as they are created
// export { useForm } from './useForm';
// export { useApi } from './useApi';
// export { useLocalStorage } from './useLocalStorage';