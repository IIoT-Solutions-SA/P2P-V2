import { api } from './api'

// Types for Dashboard
export interface UserStats {
  questions_asked: number
  answers_given: number
  use_cases_submitted: number
  reputation_score: number
  saved_items: number
  connections: number
}

export interface ActivityItem {
  id: string
  type: 'question' | 'answer' | 'use_case' | 'user_action'
  user_name: string
  user_avatar?: string
  action: string
  content: string
  timestamp: string
  category: string
  metadata?: {
    question_id?: string
    use_case_id?: string
    user_id?: string
  }
}

export interface DashboardStats {
  user_stats: UserStats
  recent_activities: ActivityItem[]
  trending_topics: string[]
  upcoming_events: Array<{
    id: string
    title: string
    date: string
    type: string
    description?: string
  }>
}

// API endpoints
export const dashboardApi = {
  // Get user dashboard data
  getUserDashboard: async (): Promise<DashboardStats> => {
    const response = await api.get('/api/v1/dashboard/user')
    return response.data
  },

  // Get recent activities with pagination
  getRecentActivities: async (params?: {
    page?: number
    limit?: number
    type?: string
  }): Promise<{
    activities: ActivityItem[]
    total: number
    page: number
    pages: number
  }> => {
    const response = await api.get('/api/v1/dashboard/activities', { params })
    return response.data
  },

  // Get user statistics
  getUserStats: async (): Promise<UserStats> => {
    const response = await api.get('/api/v1/dashboard/stats')
    return response.data
  },

  // Get trending topics
  getTrendingTopics: async (limit: number = 10): Promise<string[]> => {
    const response = await api.get('/api/v1/dashboard/trending', { 
      params: { limit } 
    })
    return response.data
  },

  // Get upcoming events
  getUpcomingEvents: async (): Promise<Array<{
    id: string
    title: string
    date: string
    type: string
    description?: string
  }>> => {
    const response = await api.get('/api/v1/dashboard/events')
    return response.data
  },

  // Get saved content for user
  getSavedContent: async (type?: 'questions' | 'use_cases' | 'all'): Promise<{
    questions: any[]
    use_cases: any[]
    total: number
  }> => {
    const response = await api.get('/api/v1/dashboard/saved', { 
      params: { type } 
    })
    return response.data
  },

  // Get user connections/network
  getUserConnections: async (): Promise<Array<{
    id: string
    name: string
    title: string
    company: string
    avatar?: string
    connection_date: string
  }>> => {
    const response = await api.get('/api/v1/dashboard/connections')
    return response.data
  },

  // Mark activity as read
  markActivityAsRead: async (activityId: string): Promise<void> => {
    await api.post(`/api/v1/dashboard/activities/${activityId}/read`)
  },

  // Get personalized recommendations
  getRecommendations: async (): Promise<{
    questions: any[]
    use_cases: any[]
    connections: any[]
  }> => {
    const response = await api.get('/api/v1/dashboard/recommendations')
    return response.data
  }
}