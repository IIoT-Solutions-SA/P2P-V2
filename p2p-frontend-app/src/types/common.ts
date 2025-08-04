/**
 * Common Types
 * Shared utility types used across the application
 */

// UUID type for better type safety
export type UUID = string;

// ISO date string type
export type ISODateString = string;

// Common entity base structure
export interface BaseEntity {
  id: UUID;
  createdAt: ISODateString;
  updatedAt: ISODateString;
}

// Status types
export type Status = 'active' | 'inactive' | 'pending' | 'suspended';

// Priority levels
export type Priority = 'low' | 'medium' | 'high' | 'urgent';

// Organization size enum (matches backend)
export type OrganizationSize = 'startup' | 'small' | 'medium' | 'large' | 'enterprise';

// User role enum (matches backend)
export type UserRole = 'admin' | 'member' | 'moderator';

// Industry categories (Saudi Arabia focused)
export type Industry = 
  | 'manufacturing'
  | 'oil_gas'
  | 'petrochemicals'
  | 'mining'
  | 'construction'
  | 'logistics'
  | 'food_beverage'
  | 'textiles'
  | 'automotive'
  | 'technology'
  | 'renewable_energy'
  | 'healthcare'
  | 'other';

// Saudi regions/cities
export type SaudiRegion = 
  | 'riyadh'
  | 'makkah'
  | 'eastern'
  | 'madinah'
  | 'qassim'
  | 'hail'
  | 'tabuk'
  | 'northern_borders'
  | 'jazan'
  | 'najran'
  | 'bahah'
  | 'asir'
  | 'jouf';

// File types for uploads
export type FileType = 'image' | 'document' | 'video' | 'audio' | 'other';

// Notification types
export type NotificationType = 
  | 'forum_reply'
  | 'use_case_approved'
  | 'use_case_rejected'
  | 'new_message'
  | 'user_invited'
  | 'system_update';

// Theme types
export type Theme = 'light' | 'dark' | 'system';