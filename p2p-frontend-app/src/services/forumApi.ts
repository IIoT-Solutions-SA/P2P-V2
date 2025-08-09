import { apiClient } from './apiClient'

export interface ForumCategory {
  id: string
  name: string
  description?: string
  topics_count: number
  posts_count: number
  category_type: string
  color_class: string
  is_active: boolean
  sort_order: number
  created_at: string
  updated_at: string
}

export interface ForumTopicAuthor {
  id: string
  first_name: string
  last_name: string
  email: string
  job_title?: string
  is_verified: boolean
}

export interface ForumTopic {
  id: string
  title: string
  content: string
  excerpt: string
  category_id: string
  author_id: string
  organization_id: string
  is_pinned: boolean
  is_locked: boolean
  has_best_answer: boolean
  best_answer_post_id?: string
  views_count: number
  posts_count: number
  likes_count: number
  last_activity_at: string
  last_post_id?: string
  last_post_author_id?: string
  created_at: string
  updated_at: string
  author?: ForumTopicAuthor
  category?: ForumCategory
}

export interface ForumPost {
  id: string
  content: string
  topic_id: string
  parent_post_id?: string
  author_id: string
  organization_id: string
  is_best_answer: boolean
  is_deleted: boolean
  edited_at?: string
  likes_count: number
  replies_count: number
  created_at: string
  updated_at: string
  author?: ForumTopicAuthor
  replies?: ForumPost[]
}

export interface ForumTopicListResponse {
  topics: ForumTopic[]
  total_count: number
  page: number
  page_size: number
  total_pages: number
  has_next: boolean
  has_prev: boolean
}

export interface ForumStatsResponse {
  total_topics: number
  total_posts: number
  active_members: number
  helpful_answers: number
  categories: ForumCategory[]
}

export interface ForumLikeResponse {
  success: boolean
  liked: boolean
  likes_count: number
  message: string
}

export interface CreateTopicData {
  title: string
  content: string
  excerpt: string
  category_id: string
  is_pinned?: boolean
}

export interface CreatePostData {
  content: string
  topic_id: string
  parent_post_id?: string
}

export interface UpdateTopicData {
  title?: string
  content?: string
  excerpt?: string
  category_id?: string
  is_pinned?: boolean
  is_locked?: boolean
}

export interface UpdatePostData {
  content?: string
}

export interface ForumSearchParams {
  search?: string
  category_id?: string
  author_id?: string
  is_pinned?: boolean
  has_best_answer?: boolean
  sort_by?: string
  sort_order?: 'asc' | 'desc'
  page?: number
  page_size?: number
}

class ForumApiService {
  private basePath = '/api/v1/forum'

  // Categories
  async getCategories(): Promise<ForumCategory[]> {
    const response = await apiClient.get(`${this.basePath}/categories`)
    return response.data
  }

  async createCategory(categoryData: Partial<ForumCategory>): Promise<ForumCategory> {
    const response = await apiClient.post(`${this.basePath}/categories`, categoryData)
    return response.data
  }

  // Topics
  async getTopics(params?: ForumSearchParams): Promise<ForumTopicListResponse> {
    const searchParams = new URLSearchParams()
    if (params?.search) searchParams.append('search', params.search)
    if (params?.category_id) searchParams.append('category_id', params.category_id)
    if (params?.author_id) searchParams.append('author_id', params.author_id)
    if (params?.is_pinned !== undefined) searchParams.append('is_pinned', String(params.is_pinned))
    if (params?.has_best_answer !== undefined) searchParams.append('has_best_answer', String(params.has_best_answer))
    if (params?.sort_by) searchParams.append('sort_by', params.sort_by)
    if (params?.sort_order) searchParams.append('sort_order', params.sort_order)
    if (params?.page) searchParams.append('page', String(params.page))
    if (params?.page_size) searchParams.append('page_size', String(params.page_size))

    const url = `${this.basePath}/topics${searchParams.toString() ? `?${searchParams}` : ''}`
    const response = await apiClient.get(url)
    return response.data
  }

  async getTopic(topicId: string): Promise<ForumTopic> {
    const response = await apiClient.get(`${this.basePath}/topics/${topicId}`)
    return response.data
  }

  async createTopic(topicData: CreateTopicData): Promise<ForumTopic> {
    const response = await apiClient.post(`${this.basePath}/topics`, topicData)
    return response.data
  }

  async updateTopic(topicId: string, topicData: UpdateTopicData): Promise<ForumTopic> {
    const response = await apiClient.put(`${this.basePath}/topics/${topicId}`, topicData)
    return response.data
  }

  async deleteTopic(topicId: string): Promise<void> {
    await apiClient.delete(`${this.basePath}/topics/${topicId}`)
  }

  async toggleTopicLike(topicId: string): Promise<ForumLikeResponse> {
    const response = await apiClient.post(`${this.basePath}/topics/${topicId}/like`)
    return response.data
  }

  // Posts
  async getTopicPosts(topicId: string, skip = 0, limit = 50): Promise<ForumPost[]> {
    const params = new URLSearchParams({
      topic_id: topicId,
      skip: String(skip),
      limit: String(limit)
    })
    const response = await apiClient.get(`${this.basePath}/posts?${params}`)
    return response.data
  }

  async getTopicPostsThreaded(topicId: string, skip = 0, limit = 50): Promise<ForumPost[]> {
    const params = new URLSearchParams({
      topic_id: topicId,
      skip: String(skip),
      limit: String(limit)
    })
    const response = await apiClient.get(`${this.basePath}/posts/threaded?${params}`)
    return response.data
  }

  async createPost(postData: CreatePostData): Promise<ForumPost> {
    const response = await apiClient.post(`${this.basePath}/posts`, postData)
    return response.data
  }

  async updatePost(postId: string, postData: UpdatePostData): Promise<ForumPost> {
    const response = await apiClient.put(`${this.basePath}/posts/${postId}`, postData)
    return response.data
  }

  async deletePost(postId: string): Promise<void> {
    await apiClient.delete(`${this.basePath}/posts/${postId}`)
  }

  async togglePostLike(postId: string): Promise<ForumLikeResponse> {
    const response = await apiClient.post(`${this.basePath}/posts/${postId}/like`)
    return response.data
  }

  async markAsBestAnswer(postId: string): Promise<ForumPost> {
    const response = await apiClient.post(`${this.basePath}/posts/${postId}/best-answer`)
    return response.data
  }

  async unmarkAsBestAnswer(postId: string): Promise<void> {
    await apiClient.delete(`${this.basePath}/posts/${postId}/best-answer`)
  }

  async getPostReplies(postId: string, skip = 0, limit = 50): Promise<ForumPost[]> {
    const params = new URLSearchParams({
      skip: String(skip),
      limit: String(limit)
    })
    const response = await apiClient.get(`${this.basePath}/posts/${postId}/replies?${params}`)
    return response.data
  }

  // Stats
  async getForumStats(): Promise<ForumStatsResponse> {
    const response = await apiClient.get(`${this.basePath}/stats`)
    return response.data
  }

  // Search
  async searchForum(query: string, filters?: Partial<ForumSearchParams>): Promise<any> {
    const params = new URLSearchParams({ q: query })
    
    if (filters?.category_id) params.append('category_id', filters.category_id)
    if (filters?.author_id) params.append('author_id', filters.author_id)
    if (filters?.sort_by) params.append('sort_by', filters.sort_by)
    if (filters?.page) params.append('page', String(filters.page))
    if (filters?.page_size) params.append('page_size', String(filters.page_size))

    const response = await apiClient.get(`${this.basePath}/search?${params}`)
    return response.data
  }
}

export const forumApi = new ForumApiService()