import React, { useState } from 'react'
import { useNavigate, useLocation, Link } from 'react-router-dom'
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { 
  Factory, 
  Mail, 
  Lock, 
  Eye, 
  EyeOff, 
  Loader2,
  AlertCircle,
  ArrowRight 
} from "lucide-react"
import { useAuth } from '@/contexts/AuthContext'

export default function Login() {
  const navigate = useNavigate()
  const location = useLocation()
  const { login } = useAuth()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  
  // Get the page the user was trying to access before being redirected
  const from = location.state?.from?.pathname || '/dashboard'

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setIsLoading(true)

    try {
      await login({ email, password })
      // Navigate to the page they were trying to access or dashboard
      navigate(from, { replace: true })
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Login failed')
    } finally {
      setIsLoading(false)
    }
  }

  const demoAccounts = [
    {
      name: 'Ahmed Al-Faisal (Admin)',
      email: 'ahmed.faisal@advanced-electronics.com',
      company: 'Advanced Electronics Co.',
      role: 'Organization Admin'
    },
    {
      name: 'Sara Hassan (Member)',
      email: 'sara.hassan@advanced-electronics.com',
      company: 'Advanced Electronics Co.',
      role: 'Team Member'
    },
    {
      name: 'Mohammed Rashid (Admin)',
      email: 'mohammed.rashid@gulf-plastics.com',
      company: 'Gulf Plastics Industries',
      role: 'Organization Admin'
    }
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      <div className="flex items-center justify-center min-h-[calc(100vh-80px)] p-6 pt-24">
        <div className="w-full max-w-6xl grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          
          {/* Left Side - Login Form */}
          <div className="max-w-md mx-auto w-full">
            <div className="bg-white rounded-2xl p-8 border border-slate-200 shadow-lg">
              <div className="text-center mb-8">
                <h1 className="text-3xl font-bold text-slate-900 mb-2">Welcome Back</h1>
                <p className="text-slate-600">Sign in to access your factory optimization platform</p>
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
          </div>

          {/* Right Side - Demo Accounts */}
          <div className="max-w-lg mx-auto w-full">
            <div className="bg-white rounded-2xl p-8 border border-slate-200 shadow-lg">
              <h2 className="text-2xl font-bold text-slate-900 mb-6">Demo Accounts</h2>
              <p className="text-slate-600 mb-6">
                Try the platform with these demo accounts. All passwords are: <code className="bg-slate-100 px-2 py-1 rounded text-sm">password123</code>
              </p>
              
              <div className="space-y-4">
                {demoAccounts.map((account, index) => (
                  <div 
                    key={index}
                    className="p-4 border border-slate-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-colors cursor-pointer"
                    onClick={() => {
                      setEmail(account.email)
                      setPassword('password123')
                    }}
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="font-semibold text-slate-900">{account.name}</h3>
                        <p className="text-sm text-slate-600">{account.company}</p>
                        <p className="text-xs text-blue-600 font-medium">{account.role}</p>
                      </div>
                      <ArrowRight className="h-4 w-4 text-slate-400" />
                    </div>
                  </div>
                ))}
              </div>

              <div className="mt-6 p-4 bg-blue-50 rounded-lg">
                <h3 className="font-semibold text-blue-900 mb-2">Organization Features</h3>
                <ul className="text-sm text-blue-700 space-y-1">
                  <li>• Admin users can invite team members</li>
                  <li>• Organization-wide use case sharing</li>
                  <li>• Role-based access control</li>
                  <li>• Team collaboration tools</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}