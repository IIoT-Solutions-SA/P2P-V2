/**
 * Forum Types
 * Type definitions for forum-related entities
 */
import { BaseEntity, UUID, ISODateString, Priority } from './common';

// Forum topic/category
export interface ForumTopic extends BaseEntity {
  name: string;
  description: string;
  slug: string;
  color: string;
  icon?: string;
  isActive: boolean;
  postCount: number;
  moderatorIds: UUID[];
}

// Forum post
export interface ForumPost extends BaseEntity {
  title: string;
  content: string;
  slug: string;
  topicId: UUID;
  authorId: UUID;
  isSticky: boolean;
  isLocked: boolean;
  priority: Priority;
  tags: string[];
  viewCount: number;
  replyCount: number;
  lastReplyAt?: ISODateString;
  lastReplyById?: UUID;
  attachments: PostAttachment[];
  status: 'published' | 'draft' | 'archived';
}

// Forum reply
export interface ForumReply extends BaseEntity {
  content: string;
  postId: UUID;
  authorId: UUID;
  parentReplyId?: UUID; // For nested replies
  isAcceptedAnswer: boolean;
  voteScore: number;
  attachments: PostAttachment[];
  status: 'published' | 'draft' | 'hidden' | 'deleted';
}

// Post attachment
export interface PostAttachment {
  id: UUID;
  filename: string;
  originalName: string;
  mimeType: string;
  size: number;
  url: string;
  uploadedAt: ISODateString;
  uploadedById: UUID;
}

// Vote on post or reply
export interface Vote {
  id: UUID;
  userId: UUID;
  targetType: 'post' | 'reply';
  targetId: UUID;
  voteType: 'up' | 'down';
  createdAt: ISODateString;
}

// Forum post with populated data (for display)
export interface ForumPostWithDetails extends ForumPost {
  topic: ForumTopic;
  author: {
    id: UUID;
    firstName: string;
    lastName: string;
    avatar?: string;
    role: string;
    organizationName: string;
  };
  lastReplyBy?: {
    id: UUID;
    firstName: string;
    lastName: string;
    avatar?: string;
  };
  userVote?: 'up' | 'down' | null;
  canEdit: boolean;
  canDelete: boolean;
  canReply: boolean;
}

// Forum reply with populated data
export interface ForumReplyWithDetails extends ForumReply {
  author: {
    id: UUID;
    firstName: string;
    lastName: string;
    avatar?: string;
    role: string;
    organizationName: string;
  };
  userVote?: 'up' | 'down' | null;
  canEdit: boolean;
  canDelete: boolean;
  canMarkAsAnswer: boolean;
  nestedReplies?: ForumReplyWithDetails[];
}

// Forum statistics
export interface ForumStats {
  totalPosts: number;
  totalReplies: number;
  totalUsers: number;
  activeUsers: number;
  topContributors: {
    userId: UUID;
    userName: string;
    postCount: number;
    replyCount: number;
  }[];
}