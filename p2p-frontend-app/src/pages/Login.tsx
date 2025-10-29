import React, { useState } from 'react'
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  Mail,
  Lock,
  Eye,
  EyeOff,
  Loader2,
  AlertCircle,
  ArrowRight
} from "lucide-react"
import { useAuth } from '@/contexts/AuthContext'
import { useNavigate, useLocation } from 'react-router-dom'
import { buildApiUrl } from '@/config/environment'
import loginImage from '/src/assets/LOGIN.png'

export default function Login() {
  const navigate = useNavigate()
  const location = useLocation()
  const from = location.state?.from?.pathname || '/dashboard'
  const { login, refreshProfile } = useAuth()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setIsLoading(true)

    try {
      await login({ email, password })

      // Check for pending profile picture upload
      const pendingPicture = localStorage.getItem('pendingProfilePicture')
      const pendingPictureType = localStorage.getItem('pendingProfilePictureType')

      if (pendingPicture && pendingPictureType) {
        try {
          // Convert base64 back to File
          const response = await fetch(pendingPicture)
          const blob = await response.blob()
          const file = new File([blob], 'profile-picture', { type: pendingPictureType })

          // Upload profile picture
          const formData = new FormData()
          formData.append('file', file)

          await fetch(buildApiUrl('/api/v1/media/profile-picture'), {
            method: 'POST',
            body: formData,
            credentials: 'include'
          })

          // Refresh profile to get the new picture
          await refreshProfile()

          // Clear localStorage
          localStorage.removeItem('pendingProfilePicture')
          localStorage.removeItem('pendingProfilePictureType')
        } catch (uploadError) {
          console.warn('Profile picture upload failed:', uploadError)
        }
      }

      navigate(from, { replace: true })
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Login failed'

      // Check if it's an email verification error
      if (errorMessage.includes('verify your email') || errorMessage.includes('EMAIL_NOT_VERIFIED')) {
        setError(
          <div className="flex flex-col space-y-2">
            <p>Please verify your email before logging in.</p>
            <button
              onClick={() => navigate(`/verify-email?email=${encodeURIComponent(email)}`)}
              className="text-blue-600 hover:text-blue-700 font-medium underline text-sm"
            >
              Resend verification email
            </button>
          </div> as any
        )
      } else {
        setError(errorMessage)
      }
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">


      <div className="flex items-center justify-center min-h-screen p-6">
        <div className="w-full max-w-5xl">
          <div className="bg-white rounded-2xl shadow-2xl overflow-hidden min-h-[600px]">
            <div className="grid grid-cols-1 lg:grid-cols-2 min-h-[600px]">

              {/* Left Side - Login Form */}
              <div className="p-12 flex flex-col justify-center">
                <div className="text-center mb-8">
                  <h1 className="text-3xl font-bold text-slate-900 mb-2">Sign In</h1>
                  <p className="text-slate-600">Access your factory optimization platform</p>
                </div>

                {error && (
                  <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center space-x-3">
                    <AlertCircle className="h-5 w-5 text-red-600" />
                    <span className="text-red-700">{error}</span>
                  </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-6">
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">
                      Email Address
                    </label>
                    <div className="relative">
                      <Mail className="absolute left-3 top-3 h-5 w-5 text-slate-400" />
                      <Input
                        type="email"
                        placeholder="your.email@company.com"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        className="pl-10"
                        required
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">
                      Password
                    </label>
                    <div className="relative">
                      <Lock className="absolute left-3 top-3 h-5 w-5 text-slate-400" />
                      <Input
                        type={showPassword ? "text" : "password"}
                        placeholder="Enter your password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        className="pl-10 pr-10"
                        required
                      />
                      <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        className="absolute right-3 top-3 text-slate-400 hover:text-slate-600"
                      >
                        {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                      </button>
                    </div>
                  </div>

                  <Button
                    type="submit"
                    disabled={isLoading}
                    className="w-full bg-blue-600 hover:bg-blue-700 text-white py-3"
                  >
                    {isLoading ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Signing In...
                      </>
                    ) : (
                      <>
                        Sign In
                        <ArrowRight className="ml-2 h-4 w-4" />
                      </>
                    )}
                  </Button>
                </form>

                <div className="mt-6 text-center">
                  <p className="text-slate-600">
                    Don't have an account?{' '}
                    <button
                      onClick={() => navigate('/signup')}
                      className="text-blue-600 hover:text-blue-700 font-medium"
                    >
                      Create organization
                    </button>
                  </p>
                </div>
              </div>

            {/* Right Side - Wavy Blue Design */}
            <div className="relative bg-white p-12 flex items-center justify-center overflow-hidden">
              {/* Top blue wave - starts from top right corner */}
              <div className="absolute top-0 right-0 w-full h-1/2">
                <svg viewBox="0 0 1200 600" preserveAspectRatio="none" className="w-full h-full">
                  <path d="M1200,0 L0,0 L0,100 C200,80 400,150 600,120 C800,90 1000,180 1200,140 Z" fill="#2563eb" />
                </svg>
              </div>

              {/* Bottom blue wave - starts from bottom left corner */}
              <div className="absolute bottom-0 left-0 w-full h-1/2">
                <svg viewBox="0 0 1200 600" preserveAspectRatio="none" className="w-full h-full">
                  <path d="M0,600 L1200,600 L1200,500 C1000,520 800,450 600,480 C400,510 200,420 0,460 Z" fill="#2563eb" />
                </svg>
              </div>

              {/* Content */}
              <div className="relative z-10 text-center">
                <img src={loginImage} alt="Login" className="w-64 h-32 mx-auto mb-4 object-contain" />
                <h2 className="text-4xl font-bold text-black mb-4">Welcome Back!</h2>
                <p className="text-slate-700 text-lg max-w-md mx-auto">
                  Join the leading peer-to-peer knowledge platform connecting manufacturers across the region
                </p>
              </div>
            </div>

            </div>
          </div>
        </div>
      </div>
    </div>
  )
}