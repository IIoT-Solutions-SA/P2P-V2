import React, { useState, useEffect } from 'react'
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { 
  Mail, 
  Lock, 
  Eye, 
  EyeOff, 
  Loader2,
  AlertCircle,
  CheckCircle,
  User,
  Users,
  XCircle
} from "lucide-react"
import { useAuth } from '@/contexts/AuthContext'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { API_BASE_URL } from '@/config/environment'

interface InvitationData {
  valid: boolean
  email?: string
  invited_by_name?: string
  expires_at?: string
  error?: string
  // Organization data from inviter
  organization_name?: string
  industry?: string
  organization_size?: string
  city?: string
  country?: string
}

export default function MemberSignup() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const { signup } = useAuth()
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [invitationData, setInvitationData] = useState<InvitationData | null>(null)
  const [validatingToken, setValidatingToken] = useState(true)
  
  const inviteToken = searchParams.get('token')
  const inviteEmail = searchParams.get('email')
  
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: inviteEmail || '',
    password: '',
    title: ''
  })

  // Validate invitation token on mount
  useEffect(() => {
    if (inviteToken) {
      validateInvitation()
    } else {
      setError('No invitation token provided')
      setValidatingToken(false)
    }
  }, [inviteToken])
  
  const validateInvitation = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/invites/validate/${inviteToken}`)
      const data = await response.json()
      
      if (data.valid) {
        setInvitationData(data)
        setFormData(prev => ({ ...prev, email: data.email }))
      } else {
        setInvitationData({ valid: false, error: data.error || 'Invalid or expired invitation' })
        setError(data.error || 'Invalid or expired invitation')
      }
    } catch (error) {
      console.error('Error validating invitation:', error)
      setError('Failed to validate invitation')
      setInvitationData({ valid: false, error: 'Failed to validate invitation' })
    } finally {
      setValidatingToken(false)
    }
  }

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    
    // Validation
    if (!formData.firstName.trim() || !formData.lastName.trim() || !formData.email.trim() || !formData.password.trim()) {
      setError('Please fill in all required fields')
      return
    }
    
    if (formData.password.length < 8 || !/[a-z]/.test(formData.password) || !/[0-9]/.test(formData.password)) {
      setError('Password must be at least 8 characters with at least one lowercase letter and one number')
      return
    }
    
    setIsLoading(true)

    try {
      const signupPayload = {
        firstName: formData.firstName,
        lastName: formData.lastName,
        email: formData.email,
        password: formData.password,
        title: formData.title || 'Team Member',
        organizationName: invitationData?.organization_name || 'Organization',
        industry: invitationData?.industry || 'Manufacturing',
        organizationSize: invitationData?.organization_size || 'medium',
        city: invitationData?.city || 'Riyadh',
        country: invitationData?.country || 'Saudi Arabia',
        inviteToken,
        role: 'member',
        isInvited: true
      }

      // AuthContext.signup() handles member path:
      // backend creates session, AuthContext fetches profile, returns { requiresEmailVerification: false }
      await signup(signupPayload as any)

      // Session is live — go straight to dashboard
      navigate('/dashboard')
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Signup failed')
    } finally {
      setIsLoading(false)
    }
  }

  // Show loading state while validating token
  if (validatingToken) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin text-blue-600 mx-auto mb-4" />
          <p className="text-slate-600">Validating your invitation...</p>
        </div>
      </div>
    )
  }

  // Show error if invitation is invalid
  if (invitationData && !invitationData.valid) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 flex items-center justify-center p-6">
        <div className="bg-white rounded-2xl p-8 max-w-md w-full text-center">
          <XCircle className="h-16 w-16 text-red-500 mx-auto mb-4" />
          <h1 className="text-2xl font-bold text-slate-900 mb-2">Invalid Invitation</h1>
          <p className="text-slate-600 mb-6">{invitationData.error}</p>
          <Button 
            onClick={() => navigate('/login')}
            className="bg-blue-600 hover:bg-blue-700 text-white"
          >
            Go to Login
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      <div className="flex items-center justify-center min-h-screen p-6">
        <div className="w-full max-w-md mx-auto">
          
          <div className="bg-white rounded-2xl p-8 border border-slate-200 shadow-lg">
            
            {/* Invitation Success Banner */}
            {invitationData && invitationData.valid && (
              <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg">
                <div className="flex items-start space-x-3">
                  <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />
                  <div className="flex-1">
                    <p className="text-green-800 font-medium">You're Invited!</p>
                    <p className="text-green-700 text-sm mt-1">
                      {invitationData.invited_by_name} has invited you to join their organization as a team member.
                    </p>
                    <p className="text-green-600 text-xs mt-2">
                      This invitation expires on {new Date(invitationData.expires_at!).toLocaleDateString()}
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Header */}
            <div className="text-center mb-8">
              <Users className="h-12 w-12 text-blue-600 mx-auto mb-4" />
              <h1 className="text-3xl font-bold text-slate-900 mb-2">Join Your Team</h1>
              <p className="text-slate-600">Create your account to start collaborating</p>
            </div>

            {error && (
              <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center space-x-3">
                <AlertCircle className="h-5 w-5 text-red-600" />
                <span className="text-red-700">{error}</span>
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-6">
              
              {/* Name Fields */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    First Name
                  </label>
                  <Input
                    type="text"
                    placeholder="Ahmed"
                    value={formData.firstName}
                    onChange={(e) => handleInputChange('firstName', e.target.value)}
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Last Name
                  </label>
                  <Input
                    type="text"
                    placeholder="Al-Faisal"
                    value={formData.lastName}
                    onChange={(e) => handleInputChange('lastName', e.target.value)}
                    required
                  />
                </div>
              </div>

              {/* Email Field (Read-only for invited users) */}
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Email Address
                </label>
                <div className="relative">
                  <Mail className="absolute left-3 top-3 h-5 w-5 text-slate-400" />
                  <Input
                    type="email"
                    value={formData.email}
                    className="pl-10 bg-slate-50"
                    disabled
                  />
                </div>
                <p className="text-xs text-slate-500 mt-1">
                  This email was used for your invitation
                </p>
              </div>

              {/* Password Field */}
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Password
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-3 h-5 w-5 text-slate-400" />
                  <Input
                    type={showPassword ? "text" : "password"}
                    placeholder="Create a strong password"
                    value={formData.password}
                    onChange={(e) => handleInputChange('password', e.target.value)}
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
                <p className="text-xs text-slate-500 mt-1">
                  Must be more than 5 characters
                </p>
              </div>

              {/* Job Title Field */}
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Job Title (Optional)
                </label>
                <div className="relative">
                  <User className="absolute left-3 top-3 h-5 w-5 text-slate-400" />
                  <Input
                    type="text"
                    placeholder="e.g., Operations Manager"
                    value={formData.title}
                    onChange={(e) => handleInputChange('title', e.target.value)}
                    className="pl-10"
                  />
                </div>
              </div>

              {/* Role Info */}
              <div className="p-4 bg-blue-50 rounded-lg">
                <p className="text-sm text-blue-800">
                  <strong>Your Role:</strong> You'll join as a <span className="font-semibold">Member</span> with access to:
                </p>
                <ul className="text-xs text-blue-700 mt-2 space-y-1">
                  <li>• Browse and connect with other members</li>
                  <li>• View and collaborate on use cases</li>
                  <li>• Participate in forum discussions</li>
                  <li>• Submit your own use cases</li>
                </ul>
              </div>

              {/* Submit Button */}
              <Button
                type="submit"
                disabled={isLoading}
                className="w-full bg-green-600 hover:bg-green-700 text-white"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Creating Account...
                  </>
                ) : (
                  'Join Organization'
                )}
              </Button>
            </form>
          </div>

          {/* Login Link */}
          <div className="mt-6 text-center">
            <p className="text-slate-600">
              Already have an account?{' '}
              <button
                onClick={() => navigate('/login')}
                className="text-blue-600 hover:text-blue-700 font-medium"
              >
                Sign in
              </button>
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}