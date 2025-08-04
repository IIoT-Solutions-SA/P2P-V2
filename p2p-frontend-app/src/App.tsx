import { useState } from 'react'
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

function App() {
  const [currentPage, setCurrentPage] = useState<Page>('landing')

  const renderPage = () => {
    switch (currentPage) {
      case 'landing':
        return <LandingPage onNavigate={(page) => setCurrentPage(page as Page)} />
      case 'dashboard':
        return (
          <ProtectedRoute>
            <Dashboard onPageChange={setCurrentPage} />
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
            <UseCaseDetail onBack={() => setCurrentPage('usecases')} />
          </ProtectedRoute>
        )
      case 'user-management':
        return (
          <ProtectedRoute>
            <UserManagement onPageChange={setCurrentPage} />
          </ProtectedRoute>
        )
      case 'login':
        return <Login 
          onLoginSuccess={() => setCurrentPage('dashboard')} 
          onNavigateToSignup={() => setCurrentPage('signup')} 
        />
      case 'signup':
        return <Signup onSuccess={() => setCurrentPage('dashboard')} />
      default:
        return <LandingPage onNavigate={(page) => setCurrentPage(page as Page)} />
    }
  }

  return (
    <AuthProvider>
      <div className="min-h-screen">
        <Navigation currentPage={currentPage} onPageChange={setCurrentPage} />
        <main className={currentPage !== 'landing' ? 'pt-0' : ''}>
          {renderPage()}
        </main>
        <MobileNavigation currentPage={currentPage} onPageChange={setCurrentPage} />
      </div>
    </AuthProvider>
  )
}

export default App
