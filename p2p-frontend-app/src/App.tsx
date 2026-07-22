import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import LandingPage from './pages/LandingPage'
import Login from './pages/Login'
import Signup from './pages/Signup'
import MemberSignup from './pages/MemberSignup'
import ForgotPassword from './pages/ForgotPassword'
import ResetPassword from './pages/ResetPassword'
import OtpVerification from './pages/OtpVerification'
import EmailVerificationPending from './pages/EmailVerificationPending'
import EmailVerificationSuccess from './pages/EmailVerificationSuccess'
import Dashboard from './pages/Dashboard'
import Forum from './pages/Forum'
import UseCases from './pages/UseCases'
import SubmitUseCase from './pages/SubmitUseCase'
import UseCaseDetail from './pages/UseCaseDetail'
import Connect from './pages/Connect'
import Organization from './pages/Organization'
import ProtectedRoute from './components/ProtectedRoute'
import ScrollToTop from './components/ScrollToTop'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import { AuthenticatedLayout } from './components/layout/AuthenticatedLayout'
import { AuthLayout, PublicLayout } from './components/layout/PublicLayout'
import { LoadingState } from './components/shared/AppState'

function HomeRoute() {
  const { isAuthenticated, isLoading } = useAuth()

  if (isLoading) {
    return <div className="min-h-screen bg-[var(--peer-paper)] px-5 py-10"><LoadingState title="Opening PeerLink" description="Checking your workspace session." /></div>
  }

  return isAuthenticated ? <Navigate to="/dashboard" replace /> : <LandingPage />
}

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <ScrollToTop />
        <Routes>
          <Route path="/" element={<Navigate to="/home" replace />} />
          <Route element={<PublicLayout />}>
            <Route path="/home" element={<HomeRoute />} />
          </Route>

          <Route element={<AuthLayout />}>
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<Signup />} />
            <Route path="/join" element={<MemberSignup />} />
            <Route path="/forgot-password" element={<ForgotPassword />} />
            <Route path="/reset-password" element={<ResetPassword />} />
            {/* OTP verification shared for signup_verify and login_mfa */}
            <Route path="/verify-otp" element={<OtpVerification />} />
            <Route path="/verify-email" element={<EmailVerificationPending />} />
            <Route path="/auth/verify-email" element={<EmailVerificationSuccess />} />
          </Route>

          <Route
            element={
              <ProtectedRoute>
                <AuthenticatedLayout />
              </ProtectedRoute>
            }
          >
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/forum" element={<Forum />} />
            <Route path="/submit" element={<SubmitUseCase />} />
            <Route path="/usecases" element={<UseCases />} />
            <Route path="/usecases/:company_slug/:title_slug" element={<UseCaseDetail />} />
            <Route path="/connect" element={<Connect />} />
            <Route path="/organization" element={<Organization />} />
            <Route path="/user-management" element={<Navigate to="/organization" replace />} />
          </Route>

          <Route path="*" element={<Navigate to="/home" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}

export default App
