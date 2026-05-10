import { useState } from 'react'
import { useSearchParams, useNavigate } from 'react-router-dom'
import { Button } from "@/components/ui/button"
import { Mail, CheckCircle, Loader2, AlertCircle } from "lucide-react"
import { API_BASE_URL, IS_DEV_ENV } from '@/config/environment'

export default function EmailVerificationPending() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const email = searchParams.get('email') || 'your email'
  const [resending, setResending] = useState(false)
  const [devVerifying, setDevVerifying] = useState(false)
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null)

  const handleResendEmail = async () => {
    setResending(true)
    setMessage(null)

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/auth/resend-verification-email`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ email })
      })

      const data = await response.json()

      if (response.ok) {
        setMessage({
          type: 'success',
          text: data.message || 'Verification email sent! Please check your inbox.'
        })
      } else {
        setMessage({
          type: 'error',
          text: data.message || 'Failed to resend email. Please try again.'
        })
      }
    } catch (error) {
      console.error('Error resending verification email:', error)
      setMessage({
        type: 'error',
        text: 'An error occurred. Please try again.'
      })
    } finally {
      setResending(false)
    }
  }

  const handleDevVerify = async () => {
    if (!IS_DEV_ENV) {
      return
    }

    setDevVerifying(true)
    setMessage(null)

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/auth/dev/verify-email`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email })
      })

      const data = await response.json()

      if (response.ok) {
        setMessage({
          type: 'success',
          text: data.message || 'Email verified successfully. You can log in now.'
        })
      } else {
        setMessage({
          type: 'error',
          text: data.message || 'Manual verification failed. Please try again.'
        })
      }
    } catch (error) {
      console.error('Error during dev verification:', error)
      setMessage({
        type: 'error',
        text: 'An error occurred. Please try again.'
      })
    } finally {
      setDevVerifying(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 flex items-center justify-center p-6">
      <div className="bg-white rounded-2xl p-8 max-w-md w-full text-center shadow-lg border border-slate-200">

        {/* Icon */}
        <div className="flex justify-center mb-6">
          <div className="w-20 h-20 bg-blue-100 rounded-full flex items-center justify-center">
            <Mail className="h-10 w-10 text-blue-600" />
          </div>
        </div>

        {/* Header */}
        <h1 className="text-3xl font-bold text-slate-900 mb-3">Check Your Email</h1>
        <p className="text-slate-600 mb-6">
          We've sent a verification link to
        </p>
        <p className="text-lg font-semibold text-blue-600 mb-6">
          {email}
        </p>

        {IS_DEV_ENV && (
          <div className="mb-6 rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
            Development mode: verification emails are disabled. Use manual verification below.
          </div>
        )}

        {/* Instructions */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6 text-left">
          <div className="flex items-start space-x-3">
            <CheckCircle className="h-5 w-5 text-blue-600 mt-0.5 flex-shrink-0" />
            <div className="text-sm text-blue-900">
              <p className="font-medium mb-2">Next steps:</p>
              <ol className="list-decimal list-inside space-y-1 text-blue-800">
                <li>Check your inbox for our email</li>
                <li>Click the verification link</li>
                <li>You'll be redirected to login</li>
              </ol>
            </div>
          </div>
        </div>

        {/* Status Message */}
        {message && (
          <div className={`mb-6 p-4 rounded-lg flex items-center space-x-3 ${
            message.type === 'success'
              ? 'bg-green-50 border border-green-200 text-green-800'
              : 'bg-red-50 border border-red-200 text-red-800'
          }`}>
            {message.type === 'success' ? (
              <CheckCircle className="h-5 w-5 flex-shrink-0" />
            ) : (
              <AlertCircle className="h-5 w-5 flex-shrink-0" />
            )}
            <span className="text-sm">{message.text}</span>
          </div>
        )}

        {/* Resend Button */}
        <Button
          onClick={handleResendEmail}
          disabled={resending}
          variant="outline"
          className="w-full mb-4"
        >
          {resending ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Sending...
            </>
          ) : (
            'Resend Verification Email'
          )}
        </Button>

        {IS_DEV_ENV && (
          <Button
            onClick={handleDevVerify}
            disabled={devVerifying}
            className="w-full mb-4"
          >
            {devVerifying ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Verifying...
              </>
            ) : (
              'Manually Verify (Dev Only)'
            )}
          </Button>
        )}

        {/* Back to Login */}
        <Button
          onClick={() => navigate('/login')}
          variant="ghost"
          className="w-full"
        >
          Back to Login
        </Button>

        {/* Help Text */}
        <div className="mt-6 pt-6 border-t border-slate-200">
          <p className="text-xs text-slate-500">
            Didn't receive the email? Check your spam folder or click the resend button above.
          </p>
        </div>
      </div>
    </div>
  )
}
