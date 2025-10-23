import { Button } from "@/components/ui/button"
import { Home, MessageSquare, BookOpen, BarChart3, Bell, Plus, LogOut, Menu, X, UserCog, Users, User, Settings } from "lucide-react"
import { useAuth } from '@/contexts/AuthContext'
import { useNavigate, useLocation } from 'react-router-dom'
import { useState } from 'react'
import { EditProfilePanel } from '@/components/EditProfilePanel'
import { Avatar } from '@/components/ui/Avatar'

export default function Navigation() {
  const { user, organization, isAuthenticated, logout } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [showEditProfile, setShowEditProfile] = useState(false)
  const [editProfileTab, setEditProfileTab] = useState<'profile' | 'account'>('profile')

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
    setMobileMenuOpen(false)
  }

  const handleNavigation = (path: string) => {
    navigate(path)
    setMobileMenuOpen(false)
  }

  return (
    <>
      <header className="fixed top-0 left-0 right-0 bg-white/95 backdrop-blur-md border-b border-slate-200 shadow-sm z-50">
        <div className="w-full px-4 sm:px-6 lg:max-w-7xl lg:mx-auto py-3 sm:py-4">
          <div className="flex items-center justify-between">
            {/* Logo and Brand - Responsive */}
            <div className="flex items-center space-x-2 sm:space-x-4 lg:space-x-8">
              <img src="/logo.png" alt="P2P Sandbox Logo" className="h-8 sm:h-10 lg:h-12 w-auto" />
              <div className="flex items-end space-x-1 sm:space-x-2">
                <span className="text-lg sm:text-xl lg:text-2xl font-bold text-slate-800">
                  <span className="text-blue-600">Peer</span>Link
                </span>
                <span className="hidden sm:block text-sm lg:text-base font-bold text-slate-400 mb-0.5">For SMEs</span>
              </div>
            </div>

            {/* Desktop Navigation - Hidden on mobile/tablet */}
            <nav className="hidden xl:flex items-center space-x-1">
              {navigationItems.map((item) => {
                const IconComponent = item.icon
                const isActive = location.pathname === item.id
                return (
                  <Button
                    key={item.id}
                    variant={isActive ? "default" : "ghost"}
                    size="sm"
                    className={`flex items-center space-x-2 ${
                      isActive
                        ? "bg-blue-600 text-white hover:bg-blue-700"
                        : "text-slate-600 hover:text-blue-600 hover:bg-blue-50"
                    }`}
                    onClick={() => navigate(item.id)}
                  >
                    <IconComponent className="h-4 w-4" />
                    <span className="text-sm">{item.label}</span>
                  </Button>
                )
              })}
            </nav>

            {/* Right side actions - Responsive */}
            <div className="flex items-center space-x-2 sm:space-x-4">
              {/* Notification Bell - Hidden on mobile */}
              {isAuthenticated && (
                <Button variant="ghost" size="sm" className="relative hidden sm:block">
                  <Bell className="h-5 w-5 text-slate-600" />
                  <div className="absolute -top-1 -right-1 w-3 h-3 bg-blue-600 rounded-full"></div>
                </Button>
              )}

              {/* Desktop Auth Buttons */}
              {!isAuthenticated ? (
                <div className="hidden sm:flex items-center space-x-2 lg:space-x-3">
                  <Button
                    variant="ghost"
                    size="sm"
                    className="text-slate-600 hover:text-blue-600"
                    onClick={() => navigate('/login')}
                  >
                    Sign In
                  </Button>
                  <Button
                    size="sm"
                    className="bg-blue-600 hover:bg-blue-700 text-white"
                    onClick={() => navigate('/signup')}
                  >
                    Sign Up
                  </Button>
                </div>
              ) : (
                <div className="hidden lg:flex items-center space-x-3">
                  <button
                    onClick={() => navigate('/dashboard')}
                    className="flex items-center space-x-3 hover:opacity-80 cursor-pointer"
                  >
                    <Avatar
                      src={user?.profilePictureUrl}
                      name={`${user?.firstName} ${user?.lastName}`}
                      size="md"
                    />
                    <div className="hidden xl:block text-left">
                      <div className="text-sm font-semibold text-slate-900">
                        {user?.firstName} {user?.lastName}
                      </div>
                      <div className="text-xs text-slate-500">
                        {user?.title} • {user?.role === 'admin' ? 'Admin' : 'Member'}
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

              {/* Mobile User Name Display + Menu Button */}
              <div className="flex xl:hidden items-center space-x-2">
                {isAuthenticated && (
                  <div className="flex items-center">
                    <Avatar
                      src={user?.profilePictureUrl}
                      name={`${user?.firstName} ${user?.lastName}`}
                      size="sm"
                    />
                    <span className="ml-2 mr-1 text-sm font-medium text-slate-700 max-w-[80px] truncate">
                      {user?.firstName}
                    </span>
                  </div>
                )}
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                >
                  {mobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
                </Button>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Mobile Menu Overlay */}
      {mobileMenuOpen && (
        <div className="xl:hidden fixed inset-0 z-40 bg-black/50" onClick={() => setMobileMenuOpen(false)}>
          <div
            className="absolute right-0 top-0 h-full w-80 bg-white shadow-xl"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="p-6 space-y-6">
              {/* Close button at top */}
              <div className="flex justify-between items-center pb-2">
                <h2 className="text-lg font-semibold text-slate-900">Menu</h2>
                <button
                  onClick={() => setMobileMenuOpen(false)}
                  className="p-2 hover:bg-slate-100 rounded-lg transition-colors"
                >
                  <X className="h-5 w-5 text-slate-600" />
                </button>
              </div>

              {/* User Info for Mobile */}
              {isAuthenticated && (
                <div className="pb-4 border-b border-slate-200">
                  <div className="flex items-center space-x-3">
                    <Avatar
                      src={user?.profilePictureUrl}
                      name={`${user?.firstName} ${user?.lastName}`}
                      size="lg"
                      className="flex-shrink-0"
                    />
                    <div className="overflow-hidden">
                      <div className="font-semibold text-slate-900 truncate">
                        {user?.firstName} {user?.lastName}
                      </div>
                      <div className="text-sm text-slate-600">
                        {user?.title || 'Member'}
                      </div>
                      <div className="text-xs text-slate-500">
                        {organization?.name || 'Organization'} • {user?.role === 'admin' ? 'Admin' : 'Member'}
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Profile Management Section */}
              {isAuthenticated && (
                <div className="space-y-4">
                  {/* Profile Actions */}
                  <div className="pt-4 border-t border-slate-200">
                    <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-wider mb-3 px-4">
                      Profile
                    </h3>
                    <div className="space-y-2">
                      <button
                        onClick={() => {
                          setEditProfileTab('profile')
                          setShowEditProfile(true)
                          setMobileMenuOpen(false)
                        }}
                        className="w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors text-slate-600 hover:bg-slate-50"
                      >
                        <User className="h-5 w-5" />
                        <span className="font-medium">Edit Profile</span>
                      </button>

                      <button
                        onClick={() => {
                          setEditProfileTab('account')
                          setShowEditProfile(true)
                          setMobileMenuOpen(false)
                        }}
                        className="w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors text-slate-600 hover:bg-slate-50"
                      >
                        <Settings className="h-5 w-5" />
                        <span className="font-medium">Password & Security</span>
                      </button>
                    </div>
                  </div>

                  {/* Quick Actions */}
                  <div className="pt-4 border-t border-slate-200">
                    <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-wider mb-3 px-4">
                      Quick Actions
                    </h3>
                    <div className="space-y-2">
                      <button
                        onClick={() => handleNavigation('/forum')}
                        className="w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors bg-blue-50 text-blue-700 hover:bg-blue-100"
                      >
                        <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                          <MessageSquare className="h-4 w-4 text-white" />
                        </div>
                        <div className="text-left">
                          <div className="font-medium">Ask Question</div>
                          <div className="text-xs text-slate-500">Get help from experts</div>
                        </div>
                      </button>

                      <button
                        onClick={() => handleNavigation('/submit')}
                        className="w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors bg-slate-50 text-slate-700 hover:bg-slate-100"
                      >
                        <div className="w-8 h-8 bg-slate-600 rounded-lg flex items-center justify-center">
                          <Plus className="h-4 w-4 text-white" />
                        </div>
                        <div className="text-left">
                          <div className="font-medium">Share Knowledge</div>
                          <div className="text-xs text-slate-500">Add your insights</div>
                        </div>
                      </button>

                      {user?.role === 'admin' ? (
                        <button
                          onClick={() => handleNavigation('/user-management')}
                          className="w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors bg-green-50 text-green-700 hover:bg-green-100"
                        >
                          <div className="w-8 h-8 bg-green-600 rounded-lg flex items-center justify-center">
                            <UserCog className="h-4 w-4 text-white" />
                          </div>
                          <div className="text-left">
                            <div className="font-medium">Manage Users</div>
                            <div className="text-xs text-slate-500">Organization settings</div>
                          </div>
                        </button>
                      ) : (
                        <button
                          onClick={() => handleNavigation('/connect')}
                          className="w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors bg-purple-50 text-purple-700 hover:bg-purple-100"
                        >
                          <div className="w-8 h-8 bg-purple-600 rounded-lg flex items-center justify-center">
                            <Users className="h-4 w-4 text-white" />
                          </div>
                          <div className="text-left">
                            <div className="font-medium">Connect</div>
                            <div className="text-xs text-slate-500">Network with members</div>
                          </div>
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              )}

              {/* Auth Actions */}
              <div className="pt-4 border-t border-slate-200">
                {!isAuthenticated ? (
                  <div className="space-y-2">
                    <Button
                      variant="outline"
                      className="w-full"
                      onClick={() => handleNavigation('/login')}
                    >
                      Sign In
                    </Button>
                    <Button
                      className="w-full bg-blue-600 hover:bg-blue-700 text-white"
                      onClick={() => handleNavigation('/signup')}
                    >
                      Sign Up
                    </Button>
                  </div>
                ) : (
                  <Button
                    variant="outline"
                    className="w-full text-red-600 border-red-200 hover:bg-red-50"
                    onClick={handleLogout}
                  >
                    <LogOut className="h-4 w-4 mr-2" />
                    Log Out
                  </Button>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Edit Profile Panel */}
      <EditProfilePanel
        isOpen={showEditProfile}
        onClose={() => setShowEditProfile(false)}
        onSave={() => {
          setShowEditProfile(false)
          // Profile will refresh automatically via AuthContext
        }}
        initialTab={editProfileTab}
      />

      {/* Spacer for fixed navbar */}
      <div className="h-14 sm:h-16 lg:h-[72px]"></div>
    </>
  )
}

// Mobile Bottom Navigation
export function MobileBottomNav() {
  const navigate = useNavigate()
  const location = useLocation()
  const { isAuthenticated } = useAuth()

  // Only show for authenticated users
  if (!isAuthenticated) return null

  const navigationItems = [
    { id: '/home', label: 'Home', icon: Home },
    { id: '/dashboard', label: 'Dashboard', icon: BarChart3 },
    { id: '/forum', label: 'Forum', icon: MessageSquare },
    { id: '/usecases', label: 'Cases', icon: BookOpen },
    { id: '/submit', label: 'Submit', icon: Plus },
  ]

  return (
    <div className="md:hidden fixed bottom-0 left-0 right-0 bg-white border-t border-slate-200 shadow-lg z-40 safe-area-pb">
      <div className="grid grid-cols-5 gap-1 px-2 py-2">
        {navigationItems.map((item) => {
          const IconComponent = item.icon
          const isActive = location.pathname === item.id
          return (
            <button
              key={item.id}
              onClick={() => navigate(item.id)}
              className={`flex flex-col items-center justify-center space-y-1 py-2 px-1 rounded-lg transition-all ${
                isActive
                  ? "bg-blue-50 text-blue-600"
                  : "text-slate-600 hover:bg-slate-50"
              }`}
            >
              <IconComponent className={`${isActive ? 'h-5 w-5' : 'h-5 w-5'}`} />
              <span className={`text-[10px] font-medium ${isActive ? 'text-blue-600' : ''}`}>
                {item.label}
              </span>
            </button>
          )
        })}
      </div>
    </div>
  )
}