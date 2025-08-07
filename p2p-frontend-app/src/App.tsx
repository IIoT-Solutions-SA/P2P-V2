import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import LandingPage from './pages/LandingPage'
import Login from './pages/Login'
import Signup from './pages/Signup'
import Dashboard from './pages/Dashboard'
import Forum from './pages/Forum'
import UseCases from './pages/UseCases'
import SubmitUseCase from './pages/SubmitUseCase'
import UseCaseDetail from './pages/UseCaseDetail'
import UserManagement from './pages/UserManagement'
import Navigation, { MobileNavigation } from './components/Navigation'
import ProtectedRoute from './components/ProtectedRoute'
import { AuthProvider } from './contexts/AuthContext'

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <div className="min-h-screen">
          <Navigation />
          <main>
            <Routes>
              {/* Public Routes */}
              <Route path="/" element={<Navigate to="/home" replace />} />
              <Route path="/home" element={<LandingPage />} />
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
              <Route path="/submit" element={
                <ProtectedRoute>
                  <SubmitUseCase />
                </ProtectedRoute>
              } />
              {/* UPDATED ROUTES FOR USE CASES */}
              <Route path="/usecases" element={
                <ProtectedRoute>
                  <UseCases />
                </ProtectedRoute>
              } />
              {/* This new route handles the detailed view with a slug */}
              <Route path="/usecases/:company_slug/:title_slug" element={
                <ProtectedRoute>
                  <UseCaseDetail />
                </ProtectedRoute>
              } />
              <Route path="/user-management" element={
                <ProtectedRoute>
                  <UserManagement />
                </ProtectedRoute>
              } />
            </Routes>
          </main>
          <MobileNavigation />
        </div>
      </BrowserRouter>
    </AuthProvider>
  )
}

export default App
