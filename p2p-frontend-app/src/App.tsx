import { useState, useEffect } from 'react'
import LandingPage from './pages/LandingPage'
import Dashboard from './pages/Dashboard'
import Forum from './pages/Forum'
import UseCases from './pages/UseCases'
import SubmitUseCase from './pages/SubmitUseCase'
import UseCaseDetail from './pages/UseCaseDetail'
import UserManagement from './pages/UserManagement'
import Login from './pages/Login'
import Signup from './pages/Signup'
import Navigation, { MobileNavigation, type Page } from './components/Navigation'
import ProtectedRoute from './components/ProtectedRoute'
import { AuthProvider } from './contexts/AuthContext'
import { initSuperTokens } from './config/supertokens'

// Initialize SuperTokens on app load
initSuperTokens()

function App() {
  // TEMPORARY: Force login page to debug auth issues
  const [currentPage, setCurrentPage] = useState<Page>('login')
  
  // Debug page changes
  const handlePageChange = (page: Page) => {
    console.log('Page changing from', currentPage, 'to', page)
    setCurrentPage(page)
  }

  const renderPage = () => {
    switch (currentPage) {
      case 'landing':
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
      case 'login':
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
