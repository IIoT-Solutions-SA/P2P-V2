import { Button } from "@/components/ui/button"
import { DeleteConfirmModal } from "@/components/ui/DeleteConfirmModal"
import { 
  MessageSquare, 
  FileText, 
  Users, 
  BookmarkCheck, 
  Award,
  Calendar,
  Sparkles,
  Star,
  Activity,
  Target,
  UserCog,
  X
} from "lucide-react"
import { useAuth } from '@/contexts/AuthContext'
import { useNavigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import { buildApiUrl } from '@/config/environment'

interface DashboardStats {
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

interface Activity {
  type: string
  user: string
  action: string
  content: string
  time: string
  category: string
}

export default function Dashboard() {
  const navigate = useNavigate()
  const { user, organization } = useAuth()
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [activities, setActivities] = useState<Activity[]>([])
  const [loading, setLoading] = useState(true)
  const [showBookmarks, setShowBookmarks] = useState(false)
  const [forumBookmarkCount, setForumBookmarkCount] = useState(0)
  const [useCaseBookmarkCount, setUseCaseBookmarkCount] = useState(0)
  const [bookmarkModalTitle, setBookmarkModalTitle] = useState<string>('Saved Items')
  const [showDrafts, setShowDrafts] = useState(false)
  const [bookmarks, setBookmarks] = useState<any[]>([])
  const [drafts, setDrafts] = useState<any[]>([])
  const [loadingBookmarks, setLoadingBookmarks] = useState(false)
  const [loadingDrafts, setLoadingDrafts] = useState(false)
  const setPrefillDraft = useState<{ title?: string; content?: string; category?: string } | null>(null)[1]
  const [deleteConfirm, setDeleteConfirm] = useState<{
    show: boolean
    title?: string
    message?: string
    onConfirm?: () => void
  }>({ show: false })

  // Dedicated loaders to avoid HMR/effect return confusion
  const fetchStats = async () => {
    try {
      const statsResponse = await fetch(buildApiUrl('/api/v1/dashboard/stats'), {
        credentials: 'include'
      })
      if (statsResponse.ok) {
        const statsData = await statsResponse.json()
        setStats(statsData)
      }
    } catch (error) {
      console.error('Error fetching stats:', error)
    }
  }



  const loadDashboard = async () => {
      try {
        setLoading(true)
        
        // Fetch user stats
        await fetchStats()
        
        // Fetch community activities
        const activitiesResponse = await fetch(buildApiUrl('/api/v1/dashboard/activities'), {
          credentials: 'include'
        })
        if (activitiesResponse.ok) {
          const activitiesData = await activitiesResponse.json()
          setActivities(activitiesData.activities || [])
        }
        
      } catch (error) {
        console.error('Error fetching dashboard data:', error)
        // Use fallback data if API fails
        setStats({
          questions_asked: 0,
          answers_given: 0,
          bookmarks_saved: 0,
          reputation_score: 0,
          activity_level: 0,
          use_cases_submitted: 0,
          best_answers: 0,
          draft_posts: 0,
          connections_count: 0
        })
        setActivities([])
      } finally {
        setLoading(false)
      }
  }

  const preloadBookmarkCounts = async () => {
    try {
      const [forumRes, ucRes] = await Promise.all([
        fetch(buildApiUrl('/api/v1/forum/bookmarks'), { credentials: 'include' }),
        fetch(buildApiUrl('/api/v1/use-cases/bookmarks'), { credentials: 'include' })
      ])
      const forumData = forumRes.ok ? await forumRes.json() : []
      const ucData = ucRes.ok ? await ucRes.json() : []
      setForumBookmarkCount(Array.isArray(forumData) ? forumData.length : 0)
      setUseCaseBookmarkCount(Array.isArray(ucData) ? ucData.length : 0)
    } catch {
      setForumBookmarkCount(0)
      setUseCaseBookmarkCount(0)
    }
  }

  useEffect(() => {

    if (user) {
      loadDashboard()
      preloadBookmarkCounts()
    }
  }, [user])

  const fetchBookmarks = async (type: 'posts' | 'use-cases') => {
    try {
      setLoadingBookmarks(true)
      if (type === 'posts') {
        setBookmarkModalTitle('Saved Posts')
        const res = await fetch(buildApiUrl('/api/v1/forum/bookmarks'), { credentials: 'include' })
        const list = res.ok ? await res.json() : []
        setBookmarks(Array.isArray(list) ? list.map((b: any) => ({
          title: b.target_title || b.title,
          target_type: 'forum_post',
          category: b.target_category,
          saved_at: b.created_at || new Date().toISOString(),
          post_id: Number(b.target_id) || b.target_id
        })) : [])
        setForumBookmarkCount(Array.isArray(list) ? list.length : 0)
      } else {
        setBookmarkModalTitle('Saved Use Cases')
        const res = await fetch(buildApiUrl('/api/v1/use-cases/bookmarks'), { credentials: 'include' })
        const list = res.ok ? await res.json() : []
        setBookmarks(Array.isArray(list) ? list.map((b: any) => ({
          title: b.title,
          target_type: 'use_case',
          category: b.category,
          saved_at: b.created_at || new Date().toISOString(),
          title_slug: b.title_slug,
          company_slug: b.company_slug
        })) : [])
        setUseCaseBookmarkCount(Array.isArray(list) ? list.length : 0)
      }
    } catch (error) {
      console.error('Error fetching bookmarks:', error)
      setBookmarks([])
    } finally {
      setLoadingBookmarks(false)
    }
  }

  const fetchDrafts = async () => {
    try {
      setLoadingDrafts(true)
      const response = await fetch(buildApiUrl('/api/v1/dashboard/drafts'), {
        credentials: 'include'
      })
      if (response.ok) {
        const data = await response.json()
        setDrafts(data.drafts || [])
      }
    } catch (error) {
      console.error('Error fetching drafts:', error)
      setDrafts([])
    } finally {
      setLoadingDrafts(false)
    }
  }

  const handleQuickAccessClick = async (type: string) => {
    if (type === 'Draft Posts') {
      await fetchDrafts()
      setShowDrafts(true)
    } else if (type === 'My Connections') {
      // TODO: Implement connections - for now just show a message
      alert('Connections feature coming soon!')
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-slate-600">Loading dashboard...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">

      <div className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-3 space-y-8">
            {/* Welcome Section */}
            <div className="bg-slate-800 rounded-2xl p-8 text-white">
              <div className="flex items-center space-x-3 mb-4">
                <Sparkles className="h-6 w-6 text-blue-400" />
                <span className="text-lg font-medium">Good morning!</span>
              </div>
              <h1 className="text-3xl font-bold mb-3">Welcome back, {user?.firstName || 'User'}! 👋</h1>
              <p className="text-slate-300 text-lg">Ready to connect and share knowledge today? Here's what's happening in your professional network.</p>
            </div>

            {/* Quick Actions */}
            <div>
              <h2 className="text-xl font-bold text-gray-900 mb-6">Quick Actions</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <button 
                  onClick={() => navigate('/forum')}
                  className="group bg-white p-6 rounded-xl border border-slate-200 hover:shadow-md transition-all duration-300"
                >
                  <div className="bg-blue-600 p-4 rounded-lg mb-4 group-hover:bg-blue-700 transition-colors">
                    <MessageSquare className="h-6 w-6 text-white" />
                  </div>
                  <div className="text-left">
                    <h3 className="font-semibold text-slate-900 mb-1">Ask Question</h3>
                    <p className="text-sm text-slate-600">Get help from experts</p>
                  </div>
                </button>
                <button 
                  onClick={() => navigate('/submit')}
                  className="group bg-white p-6 rounded-xl border border-slate-200 hover:shadow-md transition-all duration-300"
                >
                  <div className="bg-slate-600 p-4 rounded-lg mb-4 group-hover:bg-slate-700 transition-colors">
                    <FileText className="h-6 w-6 text-white" />
                  </div>
                  <div className="text-left">
                    <h3 className="font-semibold text-slate-900 mb-1">Share Knowledge</h3>
                    <p className="text-sm text-slate-600">Add your insights</p>
                  </div>
                </button>
                {user?.role === 'admin' ? (
                  <button 
                    onClick={() => navigate('/user-management')}
                    className="group bg-white p-6 rounded-xl border border-slate-200 hover:shadow-md transition-all duration-300"
                  >
                    <div className="bg-green-600 p-4 rounded-lg mb-4 group-hover:bg-green-700 transition-colors">
                      <UserCog className="h-6 w-6 text-white" />
                    </div>
                    <div className="text-left">
                      <h3 className="font-semibold text-slate-900 mb-1">Manage Users</h3>
                      <p className="text-sm text-slate-600">Organization settings</p>
                    </div>
                  </button>
                ) : (
                  <button className="group bg-white p-6 rounded-xl border border-slate-200 hover:shadow-md transition-all duration-300">
                    <div className="bg-blue-500 p-4 rounded-lg mb-4 group-hover:bg-blue-600 transition-colors">
                      <Users className="h-6 w-6 text-white" />
                    </div>
                    <div className="text-left">
                      <h3 className="font-semibold text-slate-900 mb-1">Connect</h3>
                      <p className="text-sm text-slate-600">Find professionals</p>
                    </div>
                  </button>
                )}
              </div>
            </div>

            {/* Stats Cards */}
            <div>
              <h2 className="text-xl font-bold text-gray-900 mb-6">Your Progress</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <div className="bg-blue-600 p-6 rounded-xl text-white">
                  <div className="flex items-center justify-between mb-4">
                    <MessageSquare className="h-8 w-8 text-blue-200" />
                    <div className="text-right">
                      <div className="text-2xl font-bold">{stats?.questions_asked || 0}</div>
                      <div className="text-blue-200 text-sm">Questions</div>
                    </div>
                  </div>
                  <div className="text-sm text-blue-200">Forum posts created</div>
                </div>
                <div className="bg-slate-600 p-6 rounded-xl text-white">
                  <div className="flex items-center justify-between mb-4">
                    <Award className="h-8 w-8 text-slate-200" />
                    <div className="text-right">
                      <div className="text-2xl font-bold">{stats?.answers_given || 0}</div>
                      <div className="text-slate-200 text-sm">Answers</div>
                    </div>
                  </div>
                  <div className="text-sm text-slate-200">{stats?.best_answers || 0} best answers</div>
                </div>
                <div className="bg-blue-500 p-6 rounded-xl text-white">
                  <div className="flex items-center justify-between mb-4">
                    <BookmarkCheck className="h-8 w-8 text-blue-200" />
                    <div className="text-right">
                      <div className="text-2xl font-bold">{stats?.bookmarks_saved || 0}</div>
                      <div className="text-blue-200 text-sm">Saved</div>
                    </div>
                  </div>
                  <div className="text-sm text-blue-200">Bookmarked items</div>
                </div>
                <div className="bg-slate-700 p-6 rounded-xl text-white">
                  <div className="flex items-center justify-between mb-4">
                    <Star className="h-8 w-8 text-slate-300" />
                    <div className="text-right">
                      <div className="text-2xl font-bold">{stats?.reputation_score || 0}</div>
                      <div className="text-slate-300 text-sm">Reputation</div>
                    </div>
                  </div>
                  <div className="text-sm text-slate-300">{stats?.use_cases_submitted || 0} use cases shared</div>
                </div>
              </div>
            </div>

            {/* Activity Feed */}
            <div>
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-xl font-bold text-gray-900">Recent Activities</h2>
                  <p className="text-gray-600">Stay updated with community happenings</p>
                </div>
                <Button variant="ghost" size="sm" className="text-blue-600 hover:text-blue-700">
                  View All
                </Button>
              </div>
              <div className="space-y-4">
                {activities.map((activity, i) => (
                  <div key={i} className="bg-white p-6 rounded-xl border border-slate-200 hover:shadow-md transition-all duration-300">
                    <div className="flex items-start space-x-4">
                      <div className={`p-3 rounded-lg ${
                        activity.type === "question" ? "bg-blue-600" :
                        activity.type === "answer" ? "bg-slate-600" :
                        activity.type === "usecase" ? "bg-blue-500" :
                        activity.type === "bookmark" ? "bg-green-600" :
                        activity.type === "like" ? "bg-red-500" :
                        "bg-gray-500"
                      }`}>
                        {activity.type === "question" && <MessageSquare className="h-5 w-5 text-white" />}
                        {activity.type === "answer" && <Award className="h-5 w-5 text-white" />}
                        {(activity.type === "usecase" || activity.type === "case") && <FileText className="h-5 w-5 text-white" />}
                        {activity.type === "bookmark" && <BookmarkCheck className="h-5 w-5 text-white" />}
                        {activity.type === "like" && <Star className="h-5 w-5 text-white" />}
                        {activity.type === "comment" && <MessageSquare className="h-5 w-5 text-white" />}
                      </div>
                      <div className="flex-1">
                        <p className="text-slate-900 font-medium mb-1">
                          <span className="font-semibold">{activity.user}</span> {activity.action}
                        </p>
                        <p className="text-slate-600 mb-3">{activity.content}</p>
                        <div className="flex items-center justify-between">
                          <span className="text-xs text-slate-500">{activity.time}</span>
                          <span className="text-xs bg-slate-100 text-slate-700 px-3 py-1 rounded-full font-medium">{activity.category}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-8">
            {/* Profile Summary */}
            <div className="bg-white rounded-2xl p-6 border border-slate-200">
              <div className="text-center space-y-4">
                <div className="relative inline-block">
                  <div className="w-20 h-20 bg-blue-600 rounded-full flex items-center justify-center">
                    <span className="text-2xl font-bold text-white">{user?.firstName?.charAt(0) || 'U'}</span>
                  </div>
                  <div className="absolute -bottom-1 -right-1 w-6 h-6 bg-green-500 rounded-full border-2 border-white flex items-center justify-center">
                    <div className="w-2 h-2 bg-white rounded-full"></div>
                  </div>
                </div>
                <div>
                  <h3 className="font-bold text-slate-900 text-lg">{user?.firstName} {user?.lastName}</h3>
                  <p className="text-slate-600">{user?.title} • {user?.role === 'admin' ? 'Admin' : 'Member'}</p>
                  <p className="text-sm text-slate-500">{organization?.name}</p>
                  <div className="inline-flex items-center space-x-1 bg-green-100 text-green-700 text-xs px-3 py-1 rounded-full mt-2">
                    <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                    <span className="font-medium">Verified</span>
                  </div>
                </div>
                <Button className="w-full bg-blue-600 hover:bg-blue-700 text-white">
                  Edit Profile
                </Button>
              </div>
            </div>

            {/* Quick Access */}
            <div>
              <h3 className="font-bold text-gray-900 mb-4">Quick Access</h3>
              <div className="space-y-3">
                <button 
                  onClick={async () => { await fetchBookmarks('posts'); setShowBookmarks(true); }}
                  className="w-full bg-white p-4 rounded-xl border border-slate-200 hover:shadow-md transition-all duration-300"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-slate-900">Saved Posts</span>
                    <div className="px-2 py-1 rounded-lg text-white text-xs font-bold bg-blue-600">
                      {forumBookmarkCount}
                    </div>
                  </div>
                </button>
                <button 
                  onClick={async () => { await fetchBookmarks('use-cases'); setShowBookmarks(true); }}
                  className="w-full bg-white p-4 rounded-xl border border-slate-200 hover:shadow-md transition-all duration-300"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-slate-900">Saved Use Cases</span>
                    <div className="px-2 py-1 rounded-lg text-white text-xs font-bold bg-blue-600">
                      {useCaseBookmarkCount}
                    </div>
                  </div>
                </button>
                <button 
                  onClick={() => handleQuickAccessClick('My Connections')}
                  className="w-full bg-white p-4 rounded-xl border border-slate-200 hover:shadow-md transition-all duration-300"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-slate-900">My Connections</span>
                    <div className="px-2 py-1 rounded-lg text-white text-xs font-bold bg-slate-600">
                      {String(stats?.connections_count || 0)}
                    </div>
                  </div>
                </button>
                <button 
                  onClick={async () => { await fetchDrafts(); setShowDrafts(true); }}
                  className="w-full bg-white p-4 rounded-xl border border-slate-200 hover:shadow-md transition-all duration-300"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-slate-900">Draft Posts</span>
                    <div className="px-2 py-1 rounded-lg text-white text-xs font-bold bg-blue-600">
                      {String(stats?.draft_posts || 0)}
                    </div>
                  </div>
                </button>
              </div>
            </div>

            {/* Upcoming Events */}
            <div>
              <h3 className="font-bold text-gray-900 mb-4">Upcoming Events</h3>
              <div className="bg-slate-800 p-6 rounded-xl text-white">
                <div className="flex items-center space-x-2 mb-3">
                  <Calendar className="h-5 w-5 text-slate-300" />
                  <span className="text-sm font-medium text-slate-300">Next Event</span>
                </div>
                <h4 className="font-bold text-lg mb-2">Industry Knowledge Summit</h4>
                <div className="space-y-1 text-slate-300 text-sm mb-4">
                  <p>December 15, 2024</p>
                  <p>Virtual Event</p>
                </div>
                <Button className="w-full bg-blue-600 hover:bg-blue-700 text-white">
                  Join Event
                </Button>
              </div>
            </div>

            {/* Activity Insights */}
            <div>
              <h3 className="font-bold text-gray-900 mb-4">This Month</h3>
              <div className="bg-white rounded-xl p-6 border border-slate-200">
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-slate-600">Activity Level</p>
                      <p className="text-2xl font-bold text-blue-600">{Math.round(stats?.activity_level || 0)}%</p>
                    </div>
                    <div className="p-2 bg-blue-600 rounded-lg">
                      <Activity className="h-6 w-6 text-white" />
                    </div>
                  </div>
                  <div className="w-full bg-slate-200 rounded-full h-3">
                    <div className="bg-blue-600 h-3 rounded-full" style={{ width: `${Math.round(stats?.activity_level || 0)}%` }}></div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Target className="h-4 w-4 text-green-500" />
                    <p className="text-xs text-slate-600">
                      {(stats?.activity_level || 0) > 70 
                        ? "Excellent progress! Keep it up!" 
                        : (stats?.activity_level || 0) > 40 
                          ? "Good activity level" 
                          : "Get more active in the community"}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Bookmarks Panel */}
      {showBookmarks && (
        <div className="fixed inset-0 z-50">
          <div className="absolute inset-0 bg-blue-900/20 backdrop-blur-sm" onClick={() => setShowBookmarks(false)} />
          <div className="absolute right-0 top-0 h-full w-full max-w-lg bg-white border-l border-blue-100 shadow-2xl flex flex-col">
            <div className="px-6 py-5 bg-gradient-to-r from-blue-600 to-blue-700 text-white flex items-center justify-between">
              <h3 className="text-xl font-bold">{bookmarkModalTitle}</h3>
              <button onClick={() => setShowBookmarks(false)} className="text-white/80 hover:text-white">✕</button>
            </div>
            <div className="p-6 overflow-y-auto">
              {loadingBookmarks ? (
                <div className="text-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                  <p className="text-slate-600 mt-2">Loading bookmarks...</p>
                </div>
              ) : bookmarks.length > 0 ? (
                <div className="space-y-3">
                  {bookmarks.map((bookmark, i) => (
                    <button
                      key={i}
                      onClick={() => {
                        if (bookmark.target_type === 'use_case' && bookmark.company_slug && bookmark.title_slug) {
                          navigate(`/usecases/${bookmark.company_slug}/${bookmark.title_slug}`)
                          setShowBookmarks(false)
                        } else if (bookmark.target_type === 'forum_post' && bookmark.post_id) {
                          navigate('/forum', { state: { openPostId: bookmark.post_id } })
                          setShowBookmarks(false)
                        }
                      }}
                      className="w-full text-left p-4 bg-white hover:bg-blue-50 border border-blue-100 hover:border-blue-300 rounded-lg transition-colors"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1 pr-3">
                          <h4 className="font-medium text-slate-900 mb-1 line-clamp-2">{bookmark.title}</h4>
                          <div className="flex items-center gap-2">
                            <span className="text-xs text-slate-500 capitalize">{bookmark.target_type === 'use_case' ? 'Use Case' : 'Forum Post'}</span>
                            {bookmark.category && (
                              <span className="inline-flex items-center px-2 py-1 rounded-full text-[10px] bg-blue-100 text-blue-800">
                                {bookmark.category}
                              </span>
                            )}
                          </div>
                        </div>
                        <span className="text-xs text-slate-500 ml-4 whitespace-nowrap">
                          {new Date(bookmark.saved_at).toLocaleDateString()}
                        </span>
                      </div>
                    </button>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <BookmarkCheck className="h-12 w-12 text-slate-300 mx-auto mb-3" />
                  <p className="text-slate-600">No saved items yet</p>
                  <p className="text-sm text-slate-500">Start bookmarking posts and use cases!</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Drafts Panel */}
      {showDrafts && (
        <div className="fixed inset-0 z-50">
          <div className="absolute inset-0 bg-blue-900/20 backdrop-blur-sm" onClick={() => setShowDrafts(false)} />
          <div className="absolute right-0 top-0 h-full w-full max-w-lg bg-white border-l border-blue-100 shadow-2xl flex flex-col">
            <div className="px-6 py-5 bg-gradient-to-r from-blue-600 to-blue-700 text-white flex items-center justify-between">
              <h3 className="text-xl font-bold">Draft Posts</h3>
              <button onClick={() => setShowDrafts(false)} className="text-white/80 hover:text-white">✕</button>
            </div>
            <div className="p-6 overflow-y-auto">
              {loadingDrafts ? (
                <div className="text-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                  <p className="text-slate-600 mt-2">Loading drafts...</p>
                </div>
              ) : drafts.length > 0 ? (
                <div className="space-y-3">
                  {drafts.map((draft, i) => (
                    <div
                      key={i}
                      className="relative group bg-white border border-blue-100 rounded-lg transition-colors hover:border-blue-300"
                    >
                      <div
                        onClick={() => {
                          setPrefillDraft({ title: draft.title, content: draft.content, category: draft.category })
                          navigate('/forum', { state: { openCreateWithDraft: { title: draft.title, content: draft.content, category: draft.category, draftId: draft.id } } })
                          setShowDrafts(false)
                        }}
                        className="w-full text-left p-4 hover:bg-blue-50 rounded-lg transition-colors cursor-pointer"
                      >
                        <div className="flex items-start justify-between mb-1">
                          <h4 className="font-medium text-slate-900 line-clamp-2 pr-8">{draft.title}</h4>
                          <span className="text-xs text-slate-500 ml-4 whitespace-nowrap">
                            {new Date(draft.updated_at).toLocaleDateString()}
                          </span>
                        </div>
                        <p className="text-sm text-slate-600 mb-3 line-clamp-2">{draft.content}</p>
                        <div className="flex items-center gap-2">
                          <span className="inline-flex items-center px-2 py-1 rounded-full text-[10px] bg-slate-100 text-slate-700">
                            {draft.post_type}
                          </span>
                          {draft.category && (
                            <span className="inline-flex items-center px-2 py-1 rounded-full text-[10px] bg-blue-100 text-blue-800">{draft.category}</span>
                          )}
                          <span className="ml-auto text-xs text-blue-700 font-medium">Continue writing →</span>
                        </div>
                      </div>
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          e.preventDefault()
                          console.log('Delete button clicked for draft:', draft.id)
                          setDeleteConfirm({
                            show: true,
                            title: 'Delete Draft',
                            message: 'Are you sure you want to delete this draft? This action cannot be undone.',
                            onConfirm: async () => {
                              try {
                                const res = await fetch(buildApiUrl(`/api/v1/dashboard/drafts/${draft.id}`), {
                                  method: 'DELETE',
                                  credentials: 'include'
                                })
                                if (res.ok) {
                                  // Refresh drafts list
                                  fetchDrafts()
                                  // Refresh stats
                                  fetchStats()
                                }
                              } catch (error) {
                                console.error('Error deleting draft:', error)
                              }
                              setDeleteConfirm({ show: false })
                            }
                          })
                        }}
                        className="absolute top-1 right-1 z-20 opacity-70 group-hover:opacity-100 transition-opacity p-2 bg-red-500 hover:bg-red-600 rounded-full text-white shadow-lg"
                        title="Delete draft"
                      >
                        <X size={12} />
                      </button>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <FileText className="h-12 w-12 text-slate-300 mx-auto mb-3" />
                  <p className="text-slate-600">No draft posts yet</p>
                  <p className="text-sm text-slate-500">Start writing and save drafts for later!</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      <DeleteConfirmModal
        isOpen={deleteConfirm.show}
        title={deleteConfirm.title || "Confirm Delete"}
        message={deleteConfirm.message || "Are you sure you want to delete this item?"}
        onConfirm={() => {
          if (deleteConfirm.onConfirm) {
            deleteConfirm.onConfirm()
          }
        }}
        onClose={() => setDeleteConfirm({ show: false })}
      />
    </div>
  )
}