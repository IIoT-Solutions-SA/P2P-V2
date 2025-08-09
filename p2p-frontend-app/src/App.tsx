import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
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
import Navigation, { MobileNavigation } from './components/Navigation'
import ProtectedRoute from './components/ProtectedRoute'
import { AuthProvider } from './contexts/AuthContext'
import { initSuperTokens } from './config/supertokens'
import { useLocation } from 'react-router-dom'

// Initialize SuperTokens on app load
initSuperTokens()

// Layout wrapper component to handle navigation display
function Layout() {
  const location = useLocation()
  const isLandingPage = location.pathname === '/'
  const isAuthPage = location.pathname === '/login' || location.pathname === '/signup'
  
  return (
    <div className="min-h-screen">
      <Navigation />
      <main className={!isLandingPage ? 'pt-0' : ''}>
        <Routes>
          {/* Public Routes */}
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          
          {/* Protected Routes */}
          <Route path="/dashboard" element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          } />
          
          <Route path="/forum" element={
            <ProtectedRoute>
              <Forum />
            </ProtectedRoute>
          } />
          
          <Route path="/forum/:topicId" element={
            <ProtectedRoute>
              <Forum />
            </ProtectedRoute>
          } />
          
          <Route path="/use-cases" element={
            <ProtectedRoute>
              <UseCases />
            </ProtectedRoute>
          } />
          
          <Route path="/use-cases/submit" element={
            <ProtectedRoute>
              <SubmitUseCase />
            </ProtectedRoute>
          } />
          
          <Route path="/use-cases/:id" element={
            <ProtectedRoute>
              <UseCaseDetail />
            </ProtectedRoute>
          } />
          
          <Route path="/users" element={
            <ProtectedRoute>
              <UserManagement />
            </ProtectedRoute>
          } />
          
          <Route path="/settings" element={
            <ProtectedRoute>
              <OrganizationSettings />
            </ProtectedRoute>
          } />
          
          <Route path="/profile" element={
            <ProtectedRoute>
              <Profile />
            </ProtectedRoute>
          } />
          
          {/* Catch all - redirect to landing or 404 page */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
      {!isLandingPage && !isAuthPage && <MobileNavigation />}
    </div>
  )
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <Layout />
      </Router>
    </AuthProvider>
  )
}

export default App