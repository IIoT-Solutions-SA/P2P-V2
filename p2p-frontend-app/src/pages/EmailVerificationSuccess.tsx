import { useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { CheckCircle, Loader2, XCircle, Mail } from "lucide-react"
import { Button } from "@/components/ui/button"
import { API_BASE_URL } from '@/config/environment'

export default function EmailVerificationSuccess() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const [status, setStatus] = useState<'ready' | 'verifying' | 'success' | 'error'>('ready')
  const [message, setMessage] = useState('Click the button below to verify your email address.')

  const handleVerifyClick = async () => {
    setStatus('verifying')
    setMessage('Verifying your email...')

    try {
      const token = searchParams.get('token')

      if (!token) {
        setStatus('error')
        setMessage('No verification token found.')
        return
      }

      // Call backend API to verify the email
      const response = await fetch(`${API_BASE_URL}/api/v1/auth/user/email/verify`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          method: 'token',
          token: token
        })
      })

      const data = await response.json()

      if (response.ok && data.status === 'OK') {
        setStatus('success')
        setMessage('Email verified successfully! You can now log in.')

        // Redirect to login page
        setTimeout(() => {
          navigate('/login')
        }, 2000)
      } else {
        setStatus('error')
        setMessage('Verification failed. The link may be expired or already used.')
      }
    } catch (error) {
      console.error('Verification error:', error)
      setStatus('error')
      setMessage('Verification failed. The link may be expired or invalid.')
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 flex items-center justify-center p-6">
      <div className="bg-white rounded-2xl p-8 max-w-md w-full text-center shadow-lg border border-slate-200">

        {/* Icon */}
        <div className="flex justify-center mb-6">
          {status === 'ready' && (
            <div className="w-20 h-20 bg-blue-100 rounded-full flex items-center justify-center">
              <Mail className="h-10 w-10 text-blue-600" />
            </div>
          )}
          {status === 'verifying' && (
            <div className="w-20 h-20 bg-blue-100 rounded-full flex items-center justify-center">
              <Loader2 className="h-10 w-10 text-blue-600 animate-spin" />
            </div>
          )}
          {status === 'success' && (
            <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center">
              <CheckCircle className="h-10 w-10 text-green-600" />
            </div>
          )}
          {status === 'error' && (
            <div className="w-20 h-20 bg-red-100 rounded-full flex items-center justify-center">
              <XCircle className="h-10 w-10 text-red-600" />
            </div>
          )}
        </div>

        {/* Header */}
        <h1 className={`text-3xl font-bold mb-3 ${
          status === 'ready' ? 'text-slate-900' :
          status === 'verifying' ? 'text-slate-900' :
          status === 'success' ? 'text-green-600' :
          'text-red-600'
        }`}>
          {status === 'ready' && 'Verify Your Email'}
          {status === 'verifying' && 'Verifying Email'}
          {status === 'success' && 'Email Verified!'}
          {status === 'error' && 'Verification Failed'}
        </h1>

        <p className="text-slate-600 mb-6">
          {message}
        </p>

        {/* Ready State - Show Verify Button */}
        {status === 'ready' && (
          <div className="space-y-4">
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <p className="text-sm text-blue-800">
                ✓ We've received your verification request
              </p>
            </div>
            <Button
              onClick={handleVerifyClick}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white"
              size="lg"
            >
              Verify Email Address
            </Button>
          </div>
        )}

        {/* Verifying State */}
        {status === 'verifying' && (
          <div className="flex justify-center">
            <Loader2 className="h-8 w-8 text-blue-600 animate-spin" />
          </div>
        )}

        {/* Success State */}
        {status === 'success' && (
          <div className="space-y-4">
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <p className="text-sm text-green-800">
                ✓ Your account is now active!
              </p>
            </div>
            <div className="flex justify-center">
              <Loader2 className="h-6 w-6 text-blue-600 animate-spin" />
            </div>
          </div>
        )}

        {/* Error State */}
        {status === 'error' && (
          <div className="space-y-4">
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-left">
              <p className="text-sm text-red-800 mb-2">
                This could happen if:
              </p>
              <ul className="text-xs text-red-700 list-disc list-inside space-y-1">
                <li>The verification link has expired</li>
                <li>The link was already used</li>
                <li>The link is invalid</li>
              </ul>
            </div>
            <button
              onClick={() => navigate('/verify-email')}
              className="text-blue-600 hover:text-blue-700 font-medium text-sm"
            >
              Request a new verification link
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
