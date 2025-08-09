import { NavLink, useNavigate } from 'react-router-dom'
import { Button } from "@/components/ui/button"
import { Zap, Home, MessageSquare, BookOpen, BarChart3, Bell, Plus, LogOut, User } from "lucide-react"
import { useAuth } from '@/contexts/AuthContext'

export default function Navigation() {
  const navigate = useNavigate()
  const { user, organization, isAuthenticated, logout } = useAuth()
  
  const navigationItems = [
    { path: '/', label: 'Home', icon: Home },
    { path: '/dashboard', label: 'Dashboard', icon: BarChart3 },
    { path: '/forum', label: 'Forum', icon: MessageSquare },
    { path: '/use-cases', label: 'Use Cases', icon: BookOpen },
    { path: '/use-cases/submit', label: 'Submit Story', icon: Plus },
  ]

  const handleLogout = () => {
    logout()
    navigate('/')
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
              return (
                <NavLink
                  key={item.path}
                  to={item.path}
                  className={({ isActive }) =>
                    `flex items-center space-x-2 px-4 py-2 rounded-md transition-colors ${
                      isActive 
                        ? "bg-blue-600 text-white hover:bg-blue-700" 
                        : "text-slate-600 hover:text-blue-600 hover:bg-blue-50"
                    }`
                  }
                >
                  <IconComponent className="h-4 w-4" />
                  <span>{item.label}</span>
                </NavLink>
              )
            })}
          </nav>

          {/* Actions */}
          <div className="hidden md:flex items-center space-x-3">
            <Button variant="ghost" size="icon" className="text-slate-600 hover:text-blue-600">
              <Bell className="h-5 w-5" />
            </Button>
            
            {isAuthenticated && (
              <div className="flex items-center space-x-3">
                <button
                  onClick={() => navigate('/profile')}
                  className="flex items-center space-x-2 text-slate-600 hover:text-blue-600"
                >
                  <div className="text-right">
                    <p className="text-sm font-medium">{user?.first_name} {user?.last_name}</p>
                    <p className="text-xs text-slate-500">{organization?.name}</p>
                  </div>
                  <div className="h-9 w-9 bg-blue-100 rounded-full flex items-center justify-center">
                    <User className="h-5 w-5 text-blue-600" />
                  </div>
                </button>
                
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={handleLogout}
                  className="text-slate-600 hover:text-red-600"
                >
                  <LogOut className="h-5 w-5" />
                </Button>
              </div>
            )}
          </div>

          {/* Mobile Menu Button */}
          <Button variant="ghost" size="icon" className="md:hidden">
            <svg className="h-6 w-6" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
              <path d="M4 6h16M4 12h16M4 18h16"></path>
            </svg>
          </Button>
        </div>
      </div>
    </header>
  )
}

// Mobile Navigation (updated to use React Router)
export function MobileNavigation() {
  const navigate = useNavigate()
  const { isAuthenticated } = useAuth()
  
  if (!isAuthenticated) return null
  
  const mobileNavItems = [
    { path: '/dashboard', label: 'Dashboard', icon: BarChart3 },
    { path: '/forum', label: 'Forum', icon: MessageSquare },
    { path: '/use-cases', label: 'Use Cases', icon: BookOpen },
    { path: '/use-cases/submit', label: 'Submit', icon: Plus },
  ]

  return (
    <div className="md:hidden fixed bottom-0 left-0 right-0 bg-white border-t border-slate-200 z-50">
      <div className="flex justify-around items-center py-2">
        {mobileNavItems.map((item) => {
          const IconComponent = item.icon
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex flex-col items-center p-2 rounded-lg ${
                  isActive 
                    ? "text-blue-600 bg-blue-50" 
                    : "text-slate-600"
                }`
              }
            >
              <IconComponent className="h-5 w-5" />
              <span className="text-xs mt-1">{item.label}</span>
            </NavLink>
          )
        })}
      </div>
    </div>
  )
}

// For backward compatibility - export the type even though it's not used anymore
export type Page = 'landing' | 'dashboard' | 'forum' | 'usecases' | 'submit' | 'usecase-detail' | 'user-management' | 'organization-settings' | 'profile' | 'login' | 'signup'