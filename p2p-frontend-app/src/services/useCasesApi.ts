import { api } from './api'

// Types for Use Cases
export interface UseCase {
  id: string
  title: string
  description: string
  company: string
  industry: string
  category: string
  results: {
    [key: string]: string
  }
  timeframe: string
  views: number
  likes: number
  saves: number
  verified: boolean
  featured: boolean
  tags: string[]
  published_by: string
  publisher_title: string
  published_date: string
  created_at: string
  updated_at: string
}

export interface UseCaseCategory {
  id: string
  name: string
  description: string
  icon: string
  color: string
  count: number
}

export interface UseCaseStats {
  total_use_cases: number
  contributing_companies: number
  success_stories: number
  categories: UseCaseCategory[]
}

export interface UseCaseSubmission {
  title: string
  description: string
  category: string
  industry: string
  results: { [key: string]: string }
  timeframe: string
  tags: string[]
  media_files?: File[]
}

// API endpoints
export const useCasesApi = {
  // Get all use cases with optional filtering
  getUseCases: async (params?: {
    category?: string
    search?: string
    page?: number
    limit?: number
  }): Promise<{ use_cases: UseCase[], total: number, page: number, pages: number }> => {
    const response = await api.get('/api/v1/use-cases', { params })
    return response.data
  },

  // Get a specific use case by ID
  getUseCase: async (id: string): Promise<UseCase> => {
    const response = await api.get(`/api/v1/use-cases/${id}`)
    return response.data
  },

  // Get use case categories
  getCategories: async (): Promise<UseCaseCategory[]> => {
    const response = await api.get('/api/v1/use-cases/categories')
    return response.data
  },

  // Get use case statistics
  getStats: async (): Promise<UseCaseStats> => {
    const response = await api.get('/api/v1/use-cases/stats')
    return response.data
  },

  // Submit a new use case
  submitUseCase: async (useCase: UseCaseSubmission): Promise<UseCase> => {
    const formData = new FormData()
    
    // Add text fields
    formData.append('title', useCase.title)
    formData.append('description', useCase.description)
    formData.append('category', useCase.category)
    formData.append('industry', useCase.industry)
    formData.append('timeframe', useCase.timeframe)
    formData.append('results', JSON.stringify(useCase.results))
    formData.append('tags', JSON.stringify(useCase.tags))
    
    // Add media files if provided
    if (useCase.media_files) {
      useCase.media_files.forEach((file, index) => {
        formData.append(`media_file_${index}`, file)
      })
    }

    const response = await api.post('/api/v1/use-cases', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  // Like a use case
  likeUseCase: async (id: string): Promise<{ likes: number }> => {
    const response = await api.post(`/api/v1/use-cases/${id}/like`)
    return response.data
  },

  // Save/bookmark a use case
  saveUseCase: async (id: string): Promise<{ saved: boolean }> => {
    const response = await api.post(`/api/v1/use-cases/${id}/save`)
    return response.data
  },

  // Get saved use cases for current user
  getSavedUseCases: async (): Promise<UseCase[]> => {
    const response = await api.get('/api/v1/use-cases/saved')
    return response.data
  },

  // Update use case (admin/owner only)
  updateUseCase: async (id: string, updates: Partial<UseCaseSubmission>): Promise<UseCase> => {
    const response = await api.put(`/api/v1/use-cases/${id}`, updates)
    return response.data
  },

  // Delete use case (admin/owner only)
  deleteUseCase: async (id: string): Promise<void> => {
    await api.delete(`/api/v1/use-cases/${id}`)
  },

  // Get top contributing companies
  getTopContributors: async (limit: number = 10): Promise<Array<{
    company: string
    use_case_count: number
    rank: number
  }>> => {
    const response = await api.get('/api/v1/use-cases/contributors', { 
      params: { limit } 
    })
    return response.data
  }
}