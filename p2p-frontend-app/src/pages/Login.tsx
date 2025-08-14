import React, { useState } from 'react'
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
  ArrowRight,
  ChevronDown,
  ChevronUp 
} from "lucide-react"
import { useAuth } from '@/contexts/AuthContext'
import { useNavigate, useLocation } from 'react-router-dom'

export default function Login() {
  const navigate = useNavigate()
  const location = useLocation()
  const from = location.state?.from?.pathname || '/dashboard'
  const { login } = useAuth()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [showMore, setShowMore] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setIsLoading(true)

    try {
      await login({ email, password })
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
      name: 'Sara Hassan (Admin)',
      email: 'sara.hassan@gulf-plastics.com',
      company: 'Gulf Plastics Industries',
      role: 'Organization Admin'
    },
    {
      name: 'Mohammed Rashid (Admin)',
      email: 'mohammed.rashid@saudi-steel.com',
      company: 'Saudi Steel Industries',
      role: 'Organization Admin'
    }
  ]

  const moreDemoAccounts = [
    {
      name: 'Fatima Ali (Admin)',
      email: 'fatima.ali@arabian-food.com',
      company: 'Arabian Food Processing',
      role: 'Organization Admin'
    },
    {
      name: 'Khalid Abdul (Admin)',
      email: 'khalid.abdul@precision-mfg.com',
      company: 'Precision Manufacturing Ltd',
      role: 'Organization Admin'
    },
    {
      name: 'Sarah Ahmed (Admin)',
      email: 'sarah.ahmed@pharma-excellence.com',
      company: 'Pharma Excellence Ltd',
      role: 'Organization Admin'
    },
    {
      name: 'Mohammed Al-Shahri (Admin)',
      email: 'mohammed.alshahri@secure-supply.com',
      company: 'Secure Supply Co.',
      role: 'Organization Admin'
    },
    {
      name: 'Fatima Al-Otaibi (Admin)',
      email: 'fatima.otaibi@safety-first.com',
      company: 'Safety First Industries',
      role: 'Organization Admin'
    },
    {
      name: 'Hessa Al-Sabah (Admin)',
      email: 'hessa.alsabah@yanbu-smart.com',
      company: 'Yanbu Smart Industries',
      role: 'Organization Admin'
    },
    {
      name: 'Faisal Al-Ghamdi (Admin)',
      email: 'faisal.alghamdi@redsea-logistics.com',
      company: 'Red Sea Logistics',
      role: 'Organization Admin'
    },
    {
      name: 'Nouf Al-Mutawa (Admin)',
      email: 'nouf.almutawa@najd-dates.com',
      company: 'Najd Dates Processing',
      role: 'Organization Admin'
    },
    {
      name: 'Tarek Mansour (Admin)',
      email: 'tarek.mansour@alkhobar-mfg.com',
      company: 'Al-Khobar Advanced Manufacturing',
      role: 'Organization Admin'
    },
    {
      name: 'Omar Bakr (Admin)',
      email: 'omar.bakr@ep-construction.com',
      company: 'Eastern Province Construction Materials',
      role: 'Organization Admin'
    },
    {
      name: 'Aisha Al-Jameel (Admin)',
      email: 'aisha.aljameel@saudi-retail.com',
      company: 'Saudi Retail Distribution Co.',
      role: 'Organization Admin'
    },
    {
      name: 'Sameer Khan (Admin)',
      email: 'sameer.khan@mea-integrators.com',
      company: 'MEA Systems Integrators',
      role: 'Organization Admin'
    },
    {
      name: 'Rania Al-Abdullah (Admin)',
      email: 'rania.alabdullah@agritech-sa.com',
      company: 'Agri-Tech Solutions Arabia',
      role: 'Organization Admin'
    },
    {
      name: 'Bandar Al-Harbi (Admin)',
      email: 'bandar.alharbi@gulf-plastics.com',
      company: 'Gulf Plastics Industries',
      role: 'Organization Admin'
    },
    {
      name: 'Layla Iskandar (Admin)',
      email: 'layla.iskandar@neom-solar.com',
      company: 'NEOM Solar Power Systems',
      role: 'Organization Admin'
    }
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* Header */}
      <div className="bg-white border-b border-slate-200">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-blue-600 rounded-lg">
              <Factory className="h-6 w-6 text-white" />
            </div>
            <span className="text-2xl font-bold text-slate-900">P2P Sandbox</span>
          </div>
        </div>
      </div>

      <div className="flex items-center justify-center min-h-[calc(100vh-80px)] p-6">
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

              <div className="mt-4">
                <button
                  type="button"
                  onClick={() => setShowMore(!showMore)}
                  className="w-full flex items-center justify-center gap-2 text-blue-700 hover:text-blue-800 font-medium"
                >
                  {showMore ? (
                    <>
                      Hide additional demo accounts
                      <ChevronUp className="h-4 w-4" />
                    </>
                  ) : (
                    <>
                      Show {moreDemoAccounts.length} more demo accounts
                      <ChevronDown className="h-4 w-4" />
                    </>
                  )}
                </button>
              </div>

              {showMore && (
                <div className="mt-4 max-h-64 overflow-y-auto space-y-3">
                  {moreDemoAccounts.map((account, index) => (
                    <div
                      key={index}
                      className="p-3 border border-slate-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-colors cursor-pointer"
                      onClick={() => {
                        setEmail(account.email)
                        setPassword('password123')
                      }}
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <h4 className="font-medium text-slate-900">{account.name}</h4>
                          <p className="text-xs text-slate-600">{account.company}</p>
                          <p className="text-[10px] text-blue-600 font-medium">{account.role}</p>
                        </div>
                        <ArrowRight className="h-4 w-4 text-slate-400" />
                      </div>
                    </div>
                  ))}
                </div>
              )}

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