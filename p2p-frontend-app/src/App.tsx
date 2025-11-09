import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import LandingPage from './pages/LandingPage'
import Login from './pages/Login'
import Signup from './pages/Signup'
import MemberSignup from './pages/MemberSignup'
import ForgotPassword from './pages/ForgotPassword'
import ResetPassword from './pages/ResetPassword'
import EmailVerificationPending from './pages/EmailVerificationPending'
import EmailVerificationSuccess from './pages/EmailVerificationSuccess'
import Dashboard from './pages/Dashboard'
import Forum from './pages/Forum'
import UseCases from './pages/UseCases'
import SubmitUseCase from './pages/SubmitUseCase'
import UseCaseDetail from './pages/UseCaseDetail'
import UserManagement from './pages/UserManagement'
import Connect from './pages/Connect'
import Navigation, { MobileBottomNav } from './components/Navigation'
import ProtectedRoute from './components/ProtectedRoute'
import ScrollToTop from './components/ScrollToTop'
import { AuthProvider } from './contexts/AuthContext'

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <ScrollToTop />
        <div className="min-h-screen overflow-x-hidden">
          <Navigation />
          <main className="w-full overflow-x-hidden">
            <Routes>
              {/* Public Routes */}
              <Route path="/" element={<Navigate to="/home" replace />} />
              <Route path="/home" element={<LandingPage />} />
              <Route path="/login" element={<Login />} />
              <Route path="/signup" element={<Signup />} />
              <Route path="/join" element={<MemberSignup />} />
              <Route path="/forgot-password" element={<ForgotPassword />} />
              <Route path="/reset-password" element={<ResetPassword />} />
              <Route path="/verify-email" element={<EmailVerificationPending />} />
              <Route path="/auth/verify-email" element={<EmailVerificationSuccess />} />

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
              <Route path="/connect" element={
                <ProtectedRoute>
                  <Connect />
                </ProtectedRoute>
              } />
            </Routes>
          </main>
          <MobileBottomNav />
        </div>
      </BrowserRouter>
    </AuthProvider>
  )
}

export default App
