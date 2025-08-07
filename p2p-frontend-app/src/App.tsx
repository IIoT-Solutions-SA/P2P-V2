import { useState, useEffect } from 'react'
import LandingPage from './pages/LandingPage'
import Dashboard from './pages/Dashboard'
import Forum from './pages/Forum'
import UseCases from './pages/UseCases'
import SubmitUseCase from './pages/SubmitUseCase'
import UseCaseDetail from './pages/UseCaseDetail'
import UserManagement from './pages/UserManagement'
import OrganizationSettings from './pages/OrganizationSettings'
import Profile from './pages/Profile'
import Login from './pages/Login'
import Signup from './pages/Signup'
import Navigation, { MobileNavigation, type Page } from './components/Navigation'
import ProtectedRoute from './components/ProtectedRoute'
import { AuthProvider } from './contexts/AuthContext'
import { initSuperTokens } from './config/supertokens'

// Initialize SuperTokens on app load
initSuperTokens()

function App() {
  // Start with landing page, let ProtectedRoute handle auth redirects
  const [currentPage, setCurrentPage] = useState<Page>('landing')
  
  // Debug page changes
  const handlePageChange = (page: Page) => {
    console.log('🔍 Page changing from', currentPage, 'to', page)
    console.trace('Stack trace for page change')
    setCurrentPage(page)
  }

  const renderPage = () => {
    console.log('🎯 renderPage called with currentPage:', currentPage)
    switch (currentPage) {
      case 'landing':
        console.log('📍 Rendering LandingPage')
        return <LandingPage onNavigate={(page) => handlePageChange(page as Page)} />
      case 'dashboard':
        return (
          <ProtectedRoute>
            <Dashboard onPageChange={handlePageChange} />
          </ProtectedRoute>
        )
      case 'forum':
        return (
          <ProtectedRoute>
            <Forum />
          </ProtectedRoute>
        )
      case 'usecases':
        return (
          <ProtectedRoute>
            <UseCases />
          </ProtectedRoute>
        )
      case 'submit':
        return (
          <ProtectedRoute>
            <SubmitUseCase />
          </ProtectedRoute>
        )
      case 'usecase-detail':
        return (
          <ProtectedRoute>
            <UseCaseDetail onBack={() => handlePageChange('usecases')} />
          </ProtectedRoute>
        )
      case 'user-management':
        return (
          <ProtectedRoute>
            <UserManagement onPageChange={handlePageChange} />
          </ProtectedRoute>
        )
      case 'organization-settings':
        return (
          <ProtectedRoute>
            <OrganizationSettings onPageChange={handlePageChange} />
          </ProtectedRoute>
        )
      case 'profile':
        return (
          <ProtectedRoute>
            <Profile onPageChange={handlePageChange} />
          </ProtectedRoute>
        )
      case 'login':
        console.log('📍 Rendering Login page')
        return <Login 
          onLoginSuccess={() => handlePageChange('dashboard')} 
          onNavigateToSignup={() => handlePageChange('signup')} 
        />
      case 'signup':
        return <Signup 
          onNavigateToLogin={() => handlePageChange('login')}
          onSignupSuccess={() => handlePageChange('dashboard')} 
        />
      default:
        return <LandingPage onNavigate={(page) => handlePageChange(page as Page)} />
    }
  }

  return (
    <AuthProvider>
      <div className="min-h-screen">
        <Navigation currentPage={currentPage} onPageChange={handlePageChange} />
        <main className={currentPage !== 'landing' ? 'pt-0' : ''}>
          {renderPage()}
        </main>
        <MobileNavigation currentPage={currentPage} onPageChange={handlePageChange} />
      </div>
    </AuthProvider>
  )
}

export default App
