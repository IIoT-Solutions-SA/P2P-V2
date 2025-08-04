/**
 * Use Case Types
 * Type definitions for use case submission and management
 */
import { BaseEntity, UUID, ISODateString, Industry, Status } from './common';

// Use case submission
export interface UseCase extends BaseEntity {
  title: string;
  description: string;
  problem: string;
  solution: string;
  implementation: string;
  results: string;
  industry: Industry;
  tags: string[];
  authorId: UUID;
  organizationId: UUID;
  status: 'draft' | 'submitted' | 'under_review' | 'approved' | 'rejected' | 'published';
  reviewNotes?: string;
  reviewedById?: UUID;
  reviewedAt?: ISODateString;
  publishedAt?: ISODateString;
  viewCount: number;
  downloadCount: number;
  rating: number;
  ratingCount: number;
  isFeatured: boolean;
  attachments: UseCaseAttachment[];
  collaborators: UseCaseCollaborator[];
}

// Use case attachment
export interface UseCaseAttachment {
  id: UUID;
  useCaseId: UUID;
  filename: string;
  originalName: string;
  description: string;
  fileType: 'document' | 'image' | 'video' | 'spreadsheet' | 'presentation' | 'other';
  mimeType: string;
  size: number;
  url: string;
  isPublic: boolean;
  uploadedAt: ISODateString;
  uploadedById: UUID;
}

// Use case collaborator
export interface UseCaseCollaborator {
  id: UUID;
  useCaseId: UUID;
  userId: UUID;
  role: 'contributor' | 'reviewer' | 'viewer';
  addedAt: ISODateString;
  addedById: UUID;
}

// Use case rating/review
export interface UseCaseRating {
  id: UUID;
  useCaseId: UUID;
  userId: UUID;
  rating: number; // 1-5 stars
  comment?: string;
  createdAt: ISODateString;
}

// Use case with populated data (for display)
export interface UseCaseWithDetails extends UseCase {
  author: {
    id: UUID;
    firstName: string;
    lastName: string;
    avatar?: string;
    role: string;
  };
  organization: {
    id: UUID;
    name: string;
    logo?: string;
    industry: Industry;
    size: string;
  };
  reviewer?: {
    id: UUID;
    firstName: string;
    lastName: string;
  };
  userRating?: number;
  canEdit: boolean;
  canDelete: boolean;
  canReview: boolean;
  canDownload: boolean;
}

// Use case submission form data
export interface UseCaseFormData {
  title: string;
  description: string;
  problem: string;
  solution: string;
  implementation: string;
  results: string;
  industry: Industry;
  tags: string[];
  attachments: File[];
  collaboratorEmails: string[];
  isPublic: boolean;
}

// Use case filter options
export interface UseCaseFilters {
  industry?: Industry[];
  status?: string[];
  tags?: string[];
  authorId?: UUID;
  organizationId?: UUID;
  dateFrom?: ISODateString;
  dateTo?: ISODateString;
  minRating?: number;
  isFeatured?: boolean;
}

// Use case statistics
export interface UseCaseStats {
  totalUseCases: number;
  publishedUseCases: number;
  pendingReview: number;
  averageRating: number;
  totalDownloads: number;
  topIndustries: {
    industry: Industry;
    count: number;
  }[];
  topTags: {
    tag: string;
    count: number;
  }[];
}