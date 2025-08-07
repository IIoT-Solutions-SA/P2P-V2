import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { 
  Bell, 
  MessageSquare, 
  FileText, 
  Users, 
  TrendingUp, 
  BookmarkCheck, 
  Plus,
  BarChart3,
  Award,
  Calendar,
  Zap,
  Sparkles,
  Star,
  Activity,
  Target,
  UserCog,
  Settings
} from "lucide-react"
import { useAuth } from '@/contexts/AuthContext'
// import { ConnectionTest } from '@/components/ConnectionTest'
import { type Page } from '@/components/Navigation'

interface DashboardProps {
  onPageChange?: (page: Page) => void
}

export default function Dashboard({ onPageChange }: DashboardProps) {
  const { user, organization } = useAuth()
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

            {/* Backend Connection Test - TEMPORARY for Phase 0.5 */}
            {/* Commented out temporarily due to rendering issue
            <div>
              <h2 className="text-xl font-bold text-gray-900 mb-6">🔧 Phase 0.5: Backend Integration Test</h2>
              <ConnectionTest />
            </div>
            */}

            {/* Quick Actions */}
            <div>
              <h2 className="text-xl font-bold text-gray-900 mb-6">Quick Actions</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <button 
                  onClick={() => onPageChange?.('forum')}
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
                  onClick={() => onPageChange?.('submit')}
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
                    onClick={() => onPageChange?.('user-management')}
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
                      <div className="text-2xl font-bold">12</div>
                      <div className="text-blue-200 text-sm">Questions</div>
                    </div>
                  </div>
                  <div className="text-sm text-blue-200">+2 this week</div>
                </div>
                <div className="bg-slate-600 p-6 rounded-xl text-white">
                  <div className="flex items-center justify-between mb-4">
                    <Award className="h-8 w-8 text-slate-200" />
                    <div className="text-right">
                      <div className="text-2xl font-bold">24</div>
                      <div className="text-slate-200 text-sm">Answers</div>
                    </div>
                  </div>
                  <div className="text-sm text-slate-200">+5 this week</div>
                </div>
                <div className="bg-blue-500 p-6 rounded-xl text-white">
                  <div className="flex items-center justify-between mb-4">
                    <BookmarkCheck className="h-8 w-8 text-blue-200" />
                    <div className="text-right">
                      <div className="text-2xl font-bold">8</div>
                      <div className="text-blue-200 text-sm">Saved</div>
                    </div>
                  </div>
                  <div className="text-sm text-blue-200">+1 this week</div>
                </div>
                <div className="bg-slate-700 p-6 rounded-xl text-white">
                  <div className="flex items-center justify-between mb-4">
                    <Star className="h-8 w-8 text-slate-300" />
                    <div className="text-right">
                      <div className="text-2xl font-bold">156</div>
                      <div className="text-slate-300 text-sm">Reputation</div>
                    </div>
                  </div>
                  <div className="text-sm text-slate-300">+12 this week</div>
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
                {[
                  {
                    type: "question",
                    user: "Sarah Ahmed",
                    action: "asked a new question",
                    content: "How can we improve production line efficiency?",
                    time: "2 hours ago",
                    category: "Automation"
                  },
                  {
                    type: "answer",
                    user: "Mohammed Al-Shahri", 
                    action: "answered your question",
                    content: "About implementing quality management systems",
                    time: "4 hours ago",
                    category: "Quality Management"
                  },
                  {
                    type: "case",
                    user: "Fatima Al-Otaibi",
                    action: "added a new use case",
                    content: "AI application in predictive maintenance",
                    time: "Yesterday",
                    category: "Artificial Intelligence"
                  }
                ].map((activity, i) => (
                  <div key={i} className="bg-white p-6 rounded-xl border border-slate-200 hover:shadow-md transition-all duration-300">
                    <div className="flex items-start space-x-4">
                      <div className={`p-3 rounded-lg ${
                        activity.type === "question" ? "bg-blue-600" :
                        activity.type === "answer" ? "bg-slate-600" :
                        "bg-blue-500"
                      }`}>
                        {activity.type === "question" && <MessageSquare className="h-5 w-5 text-white" />}
                        {activity.type === "answer" && <Award className="h-5 w-5 text-white" />}
                        {activity.type === "case" && <FileText className="h-5 w-5 text-white" />}
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
                  <p className="text-slate-600">{user?.role === 'admin' ? 'Organization Admin' : 'Team Member'}</p>
                  <p className="text-sm text-slate-500">{organization?.name}</p>
                  <div className="inline-flex items-center space-x-1 bg-green-100 text-green-700 text-xs px-3 py-1 rounded-full mt-2">
                    <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                    <span className="font-medium">Verified</span>
                  </div>
                </div>
                <Button 
                  className="w-full bg-blue-600 hover:bg-blue-700 text-white"
                  onClick={() => onPageChange?.('profile')}
                >
                  Edit Profile
                </Button>
              </div>
            </div>

            {/* Quick Access */}
            <div>
              <h3 className="font-bold text-gray-900 mb-4">Quick Access</h3>
              <div className="space-y-3">
                {[
                  { title: "Saved Articles", count: "8", color: "blue" },
                  { title: "My Connections", count: "24", color: "slate" },
                  { title: "Draft Posts", count: "3", color: "blue" }
                ].map((item, i) => (
                  <button key={i} className="w-full bg-white p-4 rounded-xl border border-slate-200 hover:shadow-md transition-all duration-300">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-slate-900">{item.title}</span>
                      <div className={`px-2 py-1 rounded-lg text-white text-xs font-bold ${
                        item.color === 'blue' ? 'bg-blue-600' : 'bg-slate-600'
                      }`}>
                        {item.count}
                      </div>
                    </div>
                  </button>
                ))}
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
                      <p className="text-2xl font-bold text-blue-600">85%</p>
                    </div>
                    <div className="p-2 bg-blue-600 rounded-lg">
                      <Activity className="h-6 w-6 text-white" />
                    </div>
                  </div>
                  <div className="w-full bg-slate-200 rounded-full h-3">
                    <div className="bg-blue-600 h-3 rounded-full" style={{ width: "85%" }}></div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Target className="h-4 w-4 text-green-500" />
                    <p className="text-xs text-slate-600">
                      Excellent progress! You're in the top 10%
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}