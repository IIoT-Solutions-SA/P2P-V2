import { Button } from "@/components/ui/button"
import { Zap, Home, MessageSquare, BookOpen, BarChart3, Bell, Plus, LogOut, User } from "lucide-react"
import { useAuth } from '@/contexts/AuthContext'
import { useNavigate, useLocation } from 'react-router-dom'

export default function Navigation() {
  const { user, organization, isAuthenticated, logout } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  
  const navigationItems = [
    { id: '/home', label: 'Home', icon: Home },
    { id: '/dashboard', label: 'Dashboard', icon: BarChart3 },
    { id: '/forum', label: 'Forum', icon: MessageSquare },
    { id: '/usecases', label: 'Use Cases', icon: BookOpen },
    { id: '/submit', label: 'Submit Story', icon: Plus },
  ]

  const handleLogout = () => {
    logout()
    navigate('/home')
  }

  return (
    <header className="bg-white/95 backdrop-blur-md border-b border-slate-200 sticky top-0 z-50">
      <div className="container mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          {/* Logo and Brand */}
          <div className="flex items-center space-x-8">
            <img src="/logo.png" alt="P2P Sandbox Logo" className="h-12 w-auto" />
            <div className="flex items-end space-x-2">
              <span className="text-2xl font-bold text-slate-800">
                <span className="text-blue-600">Peer</span>Link
              </span>
              <span className="text-base font-bold text-slate-400 mb-0.5">For SMEs</span>
            </div>
          </div>

          {/* Navigation */}
          <nav className="hidden md:flex items-center space-x-1">
            {navigationItems.map((item) => {
              const IconComponent = item.icon
              const isActive = location.pathname === item.id
              return (
                <Button
                  key={item.id}
                  variant={isActive ? "default" : "ghost"}
                  className={`flex items-center space-x-2 ${
                    isActive 
                      ? "bg-blue-600 text-white hover:bg-blue-700" 
                      : "text-slate-600 hover:text-blue-600 hover:bg-blue-50"
                  }`}
                  onClick={() => navigate(item.id)}
                >
                  <IconComponent className="h-4 w-4" />
                  <span>{item.label}</span>
                </Button>
              )
            })}
          </nav>

          {/* Right side actions */}
          <div className="flex items-center space-x-4">
            {isAuthenticated && (
              <Button variant="ghost" size="sm" className="relative">
                <Bell className="h-5 w-5 text-slate-600" />
                <div className="absolute -top-1 -right-1 w-3 h-3 bg-blue-600 rounded-full"></div>
              </Button>
            )}
            
            {!isAuthenticated || location.pathname === '/home' ? (
              <div className="flex items-center space-x-3">
                <Button 
                  variant="ghost" 
                  className="text-slate-600 hover:text-blue-600"
                  onClick={() => navigate('/login')}
                >
                  Sign In
                </Button>
                <Button 
                  className="bg-blue-600 hover:bg-blue-700 text-white"
                  onClick={() => navigate('/signup')}
                >
                  Sign Up
                </Button>
              </div>
            ) : (
              <div className="flex items-center space-x-3">
                <button
                  onClick={() => navigate('/dashboard')}
                  className="flex items-center space-x-3 hover:opacity-80 cursor-pointer"
                >
                  <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center">
                    <span className="text-sm font-bold text-white">
                      {user?.firstName?.charAt(0) || 'U'}
                    </span>
                  </div>
                  <div className="hidden sm:block text-left">
                    <div className="text-sm font-semibold text-slate-900">
                      {user?.firstName} {user?.lastName}
                    </div>
                    <div className="text-xs text-slate-500">
                      {user?.role === 'admin' ? 'Organization Admin' : 'Team Member'} • {organization?.name}
                    </div>
                  </div>
                </button>
                <Button 
                  variant="ghost" 
                  size="sm"
                  onClick={handleLogout}
                  className="text-slate-600 hover:text-red-600 hover:bg-red-50"
                >
                  <LogOut className="h-4 w-4" />
                </Button>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  )
}

// Mobile Navigation Component
export function MobileNavigation() {
  const navigate = useNavigate()
  const location = useLocation()
  
  const navigationItems = [
    { id: '/home', label: 'Home', icon: Home },
    { id: '/dashboard', label: 'Dashboard', icon: BarChart3 },
    { id: '/forum', label: 'Forum', icon: MessageSquare },
    { id: '/usecases', label: 'Cases', icon: BookOpen },
    { id: '/submit', label: 'Submit', icon: Plus },
  ]

  return (
    <div className="md:hidden fixed bottom-0 left-0 right-0 bg-white border-t border-slate-200 z-50">
      <div className="grid grid-cols-5 gap-1 p-2">
        {navigationItems.map((item) => {
          const IconComponent = item.icon
          const isActive = location.pathname === item.id
          return (
            <button
              key={item.id}
              onClick={() => navigate(item.id)}
              className={`flex flex-col items-center space-y-1 p-3 rounded-lg transition-colors ${
                isActive 
                  ? "bg-blue-600 text-white" 
                  : "text-slate-600 hover:bg-slate-50"
              }`}
            >
              <IconComponent className="h-5 w-5" />
              <span className="text-xs font-medium">{item.label}</span>
            </button>
          )
        })}
      </div>
    </div>
  )
}