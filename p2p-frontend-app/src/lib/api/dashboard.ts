import { api } from "@/lib/api/client"

export interface DashboardStats {
  questions_asked: number
  answers_given: number
  bookmarks_saved: number
  reputation_score: number
  activity_level: number
  use_cases_submitted: number
  best_answers: number
  draft_posts: number
  connections_count: number
}

export interface DashboardActivity {
  type?: string
  user?: string
  action?: string
  content?: string
  time?: string
  category?: string
  target_title?: string
  target_category?: string
  activity_type?: string
  created_at?: string
  description?: string
}

export interface ForumDraft {
  id: string
  title?: string
  content?: string
  post_type?: string
  category?: string
  created_at?: string
  updated_at?: string
}

export const dashboardApi = {
  stats: () => api.get<DashboardStats>("/api/v1/dashboard/stats"),
  activities: () => api.get<{ activities: DashboardActivity[] }>("/api/v1/dashboard/activities"),
  forumDrafts: () => api.get<{ drafts: ForumDraft[]; total: number }>("/api/v1/dashboard/drafts"),
}
