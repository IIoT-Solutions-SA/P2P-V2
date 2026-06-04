import React, { useState, useRef, useEffect, useCallback } from 'react'
import { useNavigate, useSearchParams, useLocation } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Loader2, ShieldCheck, Mail, AlertCircle, CheckCircle, RefreshCw, ArrowLeft } from 'lucide-react'
import { buildApiUrl } from '@/config/environment'
import { useAuth } from '@/contexts/AuthContext'

/**
 * OtpVerification — shared page for both signup email verification and login MFA.
 *
 * Query params:
 *   purpose  = 'signup_verify' | 'login_mfa'
 *   email    = recipient email address
 *
 * Route state (for login_mfa):
 *   challengeId  = opaque ID from the /custom-signin response
 */
export default function OtpVerification() {
  const navigate = useNavigate()
  const location = useLocation()
  const [searchParams] = useSearchParams()
  const { verifyLoginOtp, fetchProfile } = useAuth()

  const purpose = searchParams.get('purpose') || 'login_mfa'
  const emailParam = searchParams.get('email') || ''
  const [challengeId, setChallengeId] = useState<string>((location.state as any)?.challengeId || '')

  // 6 individual digit state
  const [digits, setDigits] = useState<string[]>(['', '', '', '', '', ''])
  const inputRefs = useRef<Array<HTMLInputElement | null>>([null, null, null, null, null, null])

  // UI state
  const [isVerifying, setIsVerifying] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [attemptsRemaining, setAttemptsRemaining] = useState<number | null>(null)
  const [success, setSuccess] = useState(false)

  // Countdown timer (OTP expiry)
  const OTP_EXPIRY_SECS = 7 * 60
  const [timeLeft, setTimeLeft] = useState(OTP_EXPIRY_SECS)
  useEffect(() => {
    if (timeLeft <= 0 || success) return
    const t = setTimeout(() => setTimeLeft(s => s - 1), 1000)
    return () => clearTimeout(t)
  }, [timeLeft, success])

  // Resend cooldown
  const [resendCooldown, setResendCooldown] = useState(0)
  const [isResending, setIsResending] = useState(false)
  useEffect(() => {
    if (resendCooldown <= 0) return
    const t = setTimeout(() => setResendCooldown(s => s - 1), 1000)
    return () => clearTimeout(t)
  }, [resendCooldown])

  // Derived
  const isLoginMfa = purpose === 'login_mfa'
  const maskedEmail = emailParam.replace(/(.{2}).*@/, '$1***@')
  const code = digits.join('')
  const isComplete = code.length === 6

  // ── Digit input handlers ─────────────────────────────────────────────────

  const focusInput = (idx: number) => {
    inputRefs.current[idx]?.focus()
  }

  const handleDigitChange = (idx: number, val: string) => {
    // Allow only digits
    const digit = val.replace(/\D/g, '').slice(-1)
    const next = [...digits]
    next[idx] = digit
    setDigits(next)
    setError(null)
    if (digit && idx < 5) focusInput(idx + 1)
  }

  const handleKeyDown = (idx: number, e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Backspace') {
      if (digits[idx]) {
        const next = [...digits]
        next[idx] = ''
        setDigits(next)
      } else if (idx > 0) {
        focusInput(idx - 1)
      }
    } else if (e.key === 'ArrowLeft' && idx > 0) {
      focusInput(idx - 1)
    } else if (e.key === 'ArrowRight' && idx < 5) {
      focusInput(idx + 1)
    }
  }

  const handlePaste = (e: React.ClipboardEvent) => {
    e.preventDefault()
    const pasted = e.clipboardData.getData('text').replace(/\D/g, '').slice(0, 6)
    if (!pasted) return
    const next = [...digits]
    pasted.split('').forEach((ch, i) => { if (i < 6) next[i] = ch })
    setDigits(next)
    focusInput(Math.min(pasted.length, 5))
  }

  // ── Submit ───────────────────────────────────────────────────────────────

  const handleSubmit = useCallback(async (e?: React.FormEvent) => {
    e?.preventDefault()
    if (!isComplete || isVerifying) return
    setError(null)
    setIsVerifying(true)

    try {
      if (isLoginMfa) {
        // Verify login OTP → creates session
        await verifyLoginOtp(emailParam, challengeId, code)
        setSuccess(true)
        setTimeout(() => navigate('/dashboard', { replace: true }), 800)
      } else {
        // Verify signup OTP → mark email verified
        const res = await fetch(buildApiUrl('/api/v1/auth/verify-signup-otp'), {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify({ email: emailParam, code })
        })
        const data = await res.json()

        if (data.status === 'OK') {
          if (data.requiresManualLogin) {
            navigate('/login', { replace: true, state: { message: 'Email verified! Please sign in to continue.' } })
          } else {
            await fetchProfile()
            setSuccess(true)
            setTimeout(() => navigate('/dashboard', { replace: true }), 800)
          }
        } else if (data.status === 'INVALID_CODE') {
          setError(data.message)
          setAttemptsRemaining(data.attemptsRemaining ?? null)
          setDigits(['', '', '', '', '', ''])
          focusInput(0)
        } else if (data.status === 'MAX_ATTEMPTS_REACHED') {
          setError(data.message)
          setAttemptsRemaining(0)
        } else if (data.status === 'OTP_EXPIRED') {
          setError('Your code has expired. Please request a new one.')
          setTimeLeft(0)
        } else {
          setError(data.message || 'Verification failed. Please try again.')
        }
      }
    } catch (err) {
      setError('An error occurred. Please try again.')
    } finally {
      setIsVerifying(false)
    }
  }, [isComplete, isVerifying, isLoginMfa, emailParam, challengeId, code, navigate, verifyLoginOtp])

  // Removed auto-submit when all 6 digits entered
  // User must explicitly click the Verify button

  // ── Resend ───────────────────────────────────────────────────────────────

  const handleResend = async () => {
    if (resendCooldown > 0 || isResending) return
    setIsResending(true)
    setError(null)

    try {
      const res = await fetch(buildApiUrl('/api/v1/auth/resend-otp'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: emailParam, purpose })
      })
      const data = await res.json()

      if (data.status === 'OK') {
        setTimeLeft(OTP_EXPIRY_SECS)
        setDigits(['', '', '', '', '', ''])
        setAttemptsRemaining(null)
        setResendCooldown(60)
        focusInput(0)
        if (data.challengeId) {
          setChallengeId(data.challengeId)
        }
      } else if (data.status === 'RATE_LIMITED') {
        setResendCooldown(data.retryAfterSeconds || 60)
        setError(`Please wait ${data.retryAfterSeconds}s before requesting a new code.`)
      } else {
        setError(data.message || 'Failed to resend code. Please try again.')
      }
    } catch {
      setError('Failed to resend code. Please try again.')
    } finally {
      setIsResending(false)
    }
  }

  // ── Format time ──────────────────────────────────────────────────────────
  const formatTime = (s: number) => `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`

  // ── Render ───────────────────────────────────────────────────────────────

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-blue-50">
      <div className="w-full max-w-md">

        {/* Card */}
        <div className="bg-white rounded-2xl border border-blue-100 shadow-xl p-10 md:p-12">

          {/* Icon */}
          <div className="flex justify-center mb-6">
            <div className={`w-20 h-20 rounded-full flex items-center justify-center transition-all duration-300 ${success ? 'bg-green-100 shadow-[0_0_30px_rgba(16,185,129,0.2)]' : 'bg-blue-100 shadow-[0_0_30px_rgba(37,99,235,0.2)]'}`}>
              {success
                ? <CheckCircle className="h-10 w-10 text-green-600" />
                : isLoginMfa
                  ? <ShieldCheck className="h-10 w-10 text-blue-600" />
                  : <Mail className="h-10 w-10 text-blue-600" />
              }
            </div>
          </div>

          {/* Heading */}
          <div className="text-center mb-8">
            <h1 className="text-2xl font-bold text-gray-900 mb-2">
              {success
                ? isLoginMfa ? 'You\'re in!' : 'Email Verified!'
                : isLoginMfa ? 'Verify Your Identity' : 'Verify Your Email'}
            </h1>
            <p className="text-sm text-gray-500 leading-relaxed">
              {success
                ? 'Redirecting to your dashboard...'
                : <>We sent a 6-digit code to<br /><span className="font-semibold text-blue-600">{maskedEmail}</span></>
              }
            </p>
          </div>

          {!success && (
            <>
              {/* OTP Input Boxes */}
              <form onSubmit={handleSubmit}>
                <div className="flex justify-center gap-3 mb-6" onPaste={handlePaste}>
                  {digits.map((digit, idx) => (
                    <input
                      key={idx}
                      ref={el => { inputRefs.current[idx] = el }}
                      id={`otp-digit-${idx}`}
                      type="text"
                      inputMode="numeric"
                      maxLength={1}
                      value={digit}
                      onChange={e => handleDigitChange(idx, e.target.value)}
                      onKeyDown={e => handleKeyDown(idx, e)}
                      onFocus={e => e.target.select()}
                      disabled={isVerifying || attemptsRemaining === 0 || timeLeft === 0}
                      style={{
                        width: 52,
                        height: 64,
                        textAlign: 'center',
                        fontSize: 28,
                        fontWeight: 700,
                        borderRadius: 12,
                        border: error
                          ? '2px solid rgba(239,68,68,0.8)'
                          : digit
                            ? '2px solid rgba(37,99,235,0.8)' // blue-600
                            : '2px solid #e5e7eb', // gray-200
                        background: digit
                          ? '#eff6ff' // blue-50
                          : '#f9fafb', // gray-50
                        color: '#1f2937', // gray-900
                        outline: 'none',
                        transition: 'all 0.15s ease',
                        caretColor: '#2563eb', // blue-600
                      }}
                      className="focus:border-blue-500 focus:bg-blue-50/50"
                    />
                  ))}
                </div>

                {/* Timer */}
                {timeLeft > 0 && (
                  <p className={`text-center text-sm mb-4 ${timeLeft < 60 ? 'text-amber-500' : 'text-gray-500'}`}>
                    Code expires in <span className="font-bold">{formatTime(timeLeft)}</span>
                  </p>
                )}
                {timeLeft === 0 && (
                  <div className="text-center mb-4 p-3 rounded-lg bg-red-50 border border-red-200">
                    <p className="text-red-500 text-sm">⏰ Code expired — request a new one below</p>
                  </div>
                )}

                {/* Error */}
                {error && (
                  <div className="mb-4 p-3 rounded-lg flex items-start gap-2 bg-red-50 border border-red-200">
                    <AlertCircle className="h-4 w-4 mt-0.5 flex-shrink-0 text-red-500" />
                    <div>
                      <p className="text-red-500 text-sm">{error}</p>
                      {attemptsRemaining !== null && attemptsRemaining > 0 && (
                        <p className="text-red-400/80 text-xs mt-0.5">
                          {attemptsRemaining} attempt{attemptsRemaining !== 1 ? 's' : ''} remaining
                        </p>
                      )}
                    </div>
                  </div>
                )}

                {/* Submit button */}
                <Button
                  type="submit"
                  disabled={!isComplete || isVerifying || attemptsRemaining === 0 || timeLeft === 0}
                  className="w-full font-semibold py-6 mb-4 text-white rounded-xl text-base transition-all"
                  style={{ 
                    background: (!isComplete || attemptsRemaining === 0 || timeLeft === 0) ? '#94a3b8' : '#2563eb', 
                    opacity: (!isComplete || attemptsRemaining === 0 || timeLeft === 0) ? 0.8 : 1
                  }}
                >
                  {isVerifying
                    ? <><Loader2 className="mr-2 h-5 w-5 animate-spin" />Verifying...</>
                    : isLoginMfa ? 'Confirm & Sign In' : 'Verify Email'}
                </Button>
              </form>

              {/* Resend */}
              <div className="text-center">
                <p className="text-sm text-gray-500 mb-2">Didn't receive a code?</p>
                <button
                  onClick={handleResend}
                  disabled={resendCooldown > 0 || isResending}
                  className={`flex items-center gap-2 mx-auto text-sm font-medium transition-all ${resendCooldown > 0 ? 'text-gray-400 cursor-not-allowed' : 'text-blue-600 hover:text-blue-700'}`}
                >
                  {isResending
                    ? <><Loader2 className="h-3 w-3 animate-spin" />Sending...</>
                    : resendCooldown > 0
                      ? <><RefreshCw className="h-3 w-3" />Resend in {resendCooldown}s</>
                      : <><RefreshCw className="h-3 w-3" />Resend code</>
                  }
                </button>
              </div>

              {/* Back link */}
              <div className="text-center mt-6">
                <button
                  onClick={() => navigate(isLoginMfa ? '/login' : '/signup')}
                  className="flex items-center gap-1 mx-auto text-sm text-gray-400 hover:text-gray-600"
                >
                  <ArrowLeft className="h-3 w-3" />
                  {isLoginMfa ? 'Back to login' : 'Back to signup'}
                </button>
              </div>
            </>
          )}

          {/* Success animation */}
          {success && (
            <div className="text-center">
              <div className="flex justify-center">
                <Loader2 className="h-6 w-6 animate-spin text-blue-600" />
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
