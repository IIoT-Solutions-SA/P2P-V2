import { api } from "@/lib/api/client"

export interface ForumCategory {
  id: string
  name: string
  count: number
}

export interface ForumAttachment {
  url: string
  filename: string
  type?: string
  mime_type?: string
  size?: number
}

export interface ForumPost {
  id: string
  title: string
  author: string
  author_id?: string
  author_profile_picture?: string
  authorTitle?: string
  category: string
  content?: string
  attachments?: ForumAttachment[]
  replies: number
  views: number
  likes: number
  isLikedByUser?: boolean
  timeAgo: string
  isPinned?: boolean
  hasBestAnswer?: boolean
  isVerified?: boolean
  excerpt?: string
  tags?: string[]
  comments?: ForumReply[]
}

export interface ForumReply {
  id: string
  author: string
  authorProfilePicture?: string
  authorTitle?: string
  content: string
  attachments?: ForumAttachment[]
  timeAgo: string
  likes: number
  isVerified?: boolean
  isBestAnswer?: boolean
  parent_reply_id?: string | null
  replies?: ForumReply[]
}

export interface ForumStats {
  total_topics: number
  active_members: number
  helpful_answers: number
}

export interface ForumContributor {
  name: string
  points: number
  avatar?: string
  rank?: number
}

export interface ForumBookmark {
  id?: string
  target_id: string
  target_title?: string
  target_category?: string
  created_at?: string
}

export const forumApi = {
  categories: () => api.get<{ categories: ForumCategory[] }>("/api/v1/forum/categories"),
  posts: (category = "all", limit = 100) =>
    api.get<{ posts: ForumPost[]; total: number }>(`/api/v1/forum/posts?category=${encodeURIComponent(category)}&limit=${limit}`),
  post: (postId: string) => api.get<ForumPost>(`/api/v1/forum/posts/${postId}`),
  createPost: (payload: { title: string; content: string; category_id: string; tags?: string[] }) =>
    api.post<{ id: string }>("/api/v1/forum/posts", payload),
  updatePost: (postId: string, payload: { title?: string; content?: string; category?: string; tags?: string[] }) =>
    api.put<{ success?: boolean }>(`/api/v1/forum/posts/${postId}`, payload),
  deletePost: (postId: string) => api.delete<void>(`/api/v1/forum/posts/${postId}`),
  likePost: (postId: string) => api.post<{ success: boolean; liked: boolean; likes: number }>(`/api/v1/forum/posts/${postId}/like`),
  bookmarkPost: (postId: string) => api.post<{ bookmarked: boolean; bookmarks?: number }>(`/api/v1/forum/posts/${postId}/bookmark`),
  bookmarks: () => api.get<ForumBookmark[]>("/api/v1/forum/bookmarks"),
  reply: (postId: string, content: string, parent_reply_id?: string | null) =>
    api.post<{ success: boolean; reply_id: string }>(`/api/v1/forum/posts/${postId}/replies`, { content, parent_reply_id }),
  uploadAttachment: (file: File, target: { postId: string } | { replyId: string }) => {
    const body = new FormData()
    body.append("file", file)
    if ("postId" in target) body.append("post_id", target.postId)
    else body.append("reply_id", target.replyId)
    return api.post<{ success: boolean; attachment: ForumAttachment }>("/api/v1/media/forum-attachment", body)
  },
  likeReply: (replyId: string) => api.post<{ success: boolean; liked: boolean; likes: number }>(`/api/v1/forum/replies/${replyId}/like`),
  stats: () => api.get<ForumStats>("/api/v1/forum/stats"),
  contributors: (limit = 5) => api.get<{ contributors: ForumContributor[] }>(`/api/v1/forum/contributors?limit=${limit}`),
}
