/**
 * Form Validation Schemas
 * Zod schemas for form validation throughout the application
 */

import { z } from 'zod';
import { UserType } from '@/types';

// Common validation rules
const emailSchema = z
  .string()
  .min(1, 'Email is required')
  .email('Please enter a valid email address');

const passwordSchema = z
  .string()
  .min(8, 'Password must be at least 8 characters long')
  .regex(/[a-z]/, 'Password must contain at least one lowercase letter')
  .regex(/[A-Z]/, 'Password must contain at least one uppercase letter')
  .regex(/\d/, 'Password must contain at least one number')
  .regex(/[!@#$%^&*(),.?":{}|<>]/, 'Password must contain at least one special character');

const nameSchema = z
  .string()
  .min(1, 'This field is required')
  .min(2, 'Must be at least 2 characters long')
  .max(50, 'Must be no more than 50 characters long')
  .regex(/^[a-zA-Z\s]*$/, 'Only letters and spaces are allowed');

// User type validation
const userTypeSchema = z.enum([
  'CEO',
  'Owner',
  'Admin',
  'Manager',
  'Employee',
  'Installer',
  'Stocker',
  'Salesman',
  'Driver',
  'Customer',
  'Supplier',
] as const);

// Login form validation
export const loginSchema = z.object({
  email: emailSchema,
  password: z.string().min(1, 'Password is required'),
});

export type LoginFormData = z.infer<typeof loginSchema>;

// Register form validation
export const registerSchema = z.object({
  email: emailSchema,
  password: passwordSchema,
  confirmPassword: z.string().min(1, 'Please confirm your password'),
  first_name: nameSchema,
  last_name: nameSchema,
  user_type: userTypeSchema,
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ["confirmPassword"],
});

export type RegisterFormData = z.infer<typeof registerSchema>;

// Password reset request validation
export const passwordResetSchema = z.object({
  email: emailSchema,
});

export type PasswordResetFormData = z.infer<typeof passwordResetSchema>;

// Password reset confirm validation
export const passwordResetConfirmSchema = z.object({
  password: passwordSchema,
  confirmPassword: z.string().min(1, 'Please confirm your password'),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ["confirmPassword"],
});

export type PasswordResetConfirmFormData = z.infer<typeof passwordResetConfirmSchema>;

// Profile update validation
export const profileUpdateSchema = z.object({
  first_name: nameSchema,
  last_name: nameSchema,
  email: emailSchema,
  user_type: userTypeSchema.optional(),
}).partial();

export type ProfileUpdateFormData = z.infer<typeof profileUpdateSchema>;

// Change password validation
export const changePasswordSchema = z.object({
  currentPassword: z.string().min(1, 'Current password is required'),
  newPassword: passwordSchema,
  confirmNewPassword: z.string().min(1, 'Please confirm your new password'),
}).refine((data) => data.newPassword === data.confirmNewPassword, {
  message: "New passwords don't match",
  path: ["confirmNewPassword"],
}).refine((data) => data.currentPassword !== data.newPassword, {
  message: "New password must be different from current password",
  path: ["newPassword"],
});

export type ChangePasswordFormData = z.infer<typeof changePasswordSchema>;

// User creation validation (for admin panel)
export const createUserSchema = z.object({
  email: emailSchema,
  first_name: nameSchema,
  last_name: nameSchema,
  user_type: userTypeSchema,
  is_active: z.boolean().default(true),
  is_staff: z.boolean().default(false),
  password: passwordSchema.optional(),
});

export type CreateUserFormData = z.infer<typeof createUserSchema>;

// Contact form validation
export const contactFormSchema = z.object({
  name: nameSchema,
  email: emailSchema,
  subject: z.string().min(1, 'Subject is required').max(100, 'Subject is too long'),
  message: z.string().min(1, 'Message is required').max(1000, 'Message is too long'),
});

export type ContactFormData = z.infer<typeof contactFormSchema>;

// Search validation
export const searchSchema = z.object({
  query: z.string().min(1, 'Search query is required').max(100, 'Search query is too long'),
  filters: z.record(z.string()).optional(),
});

export type SearchFormData = z.infer<typeof searchSchema>;

// File upload validation
export const fileUploadSchema = z.object({
  file: z.instanceof(File, { message: 'Please select a file' }),
}).refine((data) => {
  const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'application/pdf'];
  return allowedTypes.includes(data.file.type);
}, {
  message: 'Only JPEG, PNG, GIF images and PDF files are allowed',
}).refine((data) => {
  const maxSize = 10 * 1024 * 1024; // 10MB
  return data.file.size <= maxSize;
}, {
  message: 'File size must be less than 10MB',
});

export type FileUploadFormData = z.infer<typeof fileUploadSchema>;

// Utility function to get error message from Zod error
export const getZodErrorMessage = (error: z.ZodError, field: string): string | undefined => {
  const fieldError = error.errors.find(err => err.path.includes(field));
  return fieldError?.message;
};

// Utility function to transform Zod errors to form-friendly format
export const transformZodErrors = (error: z.ZodError): Record<string, string> => {
  const errors: Record<string, string> = {};
  
  error.errors.forEach((err) => {
    const path = err.path.join('.');
    errors[path] = err.message;
  });
  
  return errors;
};

// Custom validation functions
export const validateEmail = (email: string): boolean => {
  return emailSchema.safeParse(email).success;
};

export const validatePassword = (password: string): { isValid: boolean; errors: string[] } => {
  const result = passwordSchema.safeParse(password);
  
  if (result.success) {
    return { isValid: true, errors: [] };
  }
  
  return {
    isValid: false,
    errors: result.error.errors.map(err => err.message),
  };
};

export const validatePasswordMatch = (password: string, confirmPassword: string): boolean => {
  return password === confirmPassword;
};

// Phone number validation (if needed)
export const phoneSchema = z
  .string()
  .regex(/^\+?[\d\s\-\(\)]+$/, 'Please enter a valid phone number')
  .min(10, 'Phone number must be at least 10 digits')
  .max(15, 'Phone number must be no more than 15 digits');

// URL validation
export const urlSchema = z
  .string()
  .url('Please enter a valid URL')
  .optional()
  .or(z.literal(''));

// Date validation
export const dateSchema = z
  .string()
  .regex(/^\d{4}-\d{2}-\d{2}$/, 'Please enter a valid date (YYYY-MM-DD)')
  .refine((date) => {
    const parsed = new Date(date);
    return !isNaN(parsed.getTime());
  }, 'Please enter a valid date');

// Age validation
export const ageSchema = z
  .number()
  .min(13, 'Must be at least 13 years old')
  .max(120, 'Must be less than 120 years old');

export default {
  loginSchema,
  registerSchema,
  passwordResetSchema,
  passwordResetConfirmSchema,
  profileUpdateSchema,
  changePasswordSchema,
  createUserSchema,
  contactFormSchema,
  searchSchema,
  fileUploadSchema,
};