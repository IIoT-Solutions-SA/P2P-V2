import { api } from "@/lib/api/client"

export interface UseCaseListItem {
  id: string
  title: string
  title_slug: string
  company_slug: string
  company: string
  industry?: string
  category: string
  description?: string
  results?: { benefits?: string } & Record<string, unknown>
  timeframe?: string
  views: number
  likes: number
  saves: number
  verified?: boolean
  featured?: boolean
  tags?: string[]
  publishedBy?: string
  publisherTitle?: string
  publishedDate?: string
  image?: string
}

export interface UseCaseDraftListItem {
  id: string
  title: string
  subtitle?: string
  description?: string
  category?: string
  current_step?: number
  created_at?: string
  updated_at?: string
}

export interface UseCasesResponse {
  items: UseCaseListItem[]
  total: number
  limit: number
  skip: number
  has_more: boolean
}

export const useCasesApi = {
  list: (params: { category?: string; search?: string; sortBy?: string; limit?: number; skip?: number }) => {
    const query = new URLSearchParams({
      category: params.category || "all",
      search: params.search || "",
      sort_by: params.sortBy || "newest",
      limit: String(params.limit || 20),
      skip: String(params.skip || 0),
    })
    return api.get<UseCasesResponse>(`/api/v1/use-cases/?${query.toString()}`)
  },
  categories: () => api.get<Array<{ id: string; name: string; count: number }>>("/api/v1/use-cases/categories"),
  stats: () => api.get<{ totalUseCases: number; contributingCompanies: number; successStories: number }>("/api/v1/use-cases/stats"),
  contributors: () => api.get<Array<{ name: string; cases: number; avatar: string }>>("/api/v1/use-cases/contributors"),
  detail: (companySlug: string, titleSlug: string) => api.get<Record<string, unknown>>(`/api/v1/use-cases/${companySlug}/${titleSlug}`),
  like: (companySlug: string, titleSlug: string) => api.post<{ liked: boolean; likes: number }>(`/api/v1/use-cases/${companySlug}/${titleSlug}/like`),
  bookmark: (companySlug: string, titleSlug: string) =>
    api.post<{ bookmarked: boolean; bookmarks: number }>(`/api/v1/use-cases/${companySlug}/${titleSlug}/bookmark`),
  bookmarks: () => api.get<UseCaseListItem[]>("/api/v1/use-cases/bookmarks"),
  drafts: () => api.get<UseCaseDraftListItem[]>("/api/v1/use-cases/drafts"),
  draft: (draftId: string) => api.get<Record<string, unknown>>(`/api/v1/use-cases/drafts/${draftId}`),
  publishDraft: (draftId: string) => api.post<{ success: boolean; can_publish: boolean; missing_fields?: string[]; use_case?: { slug?: string } }>(`/api/v1/use-cases/drafts/${draftId}/publish`),
  deleteDraft: (draftId: string) => api.delete<void>(`/api/v1/use-cases/drafts/${draftId}`),
}
