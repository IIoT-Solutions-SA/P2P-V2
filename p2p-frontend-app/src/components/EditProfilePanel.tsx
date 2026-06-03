import { useState, useEffect, useCallback } from 'react'
import { X, Save, Loader2, Plus, Mail, Lock, Eye, EyeOff } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { useAuth } from '@/contexts/AuthContext'
import { buildApiUrl } from '@/config/environment'
import type { UpdateProfileData } from '@/types/auth'
import { ProfilePictureEditor } from '@/components/ui/ProfilePictureEditor'

interface EditProfilePanelProps {
  isOpen: boolean
  onClose: () => void
  onSave: () => void
  initialTab?: 'profile' | 'account'
}

export function EditProfilePanel({ isOpen, onClose, onSave, initialTab = 'profile' }: EditProfilePanelProps) {
  const { user, refreshProfile } = useAuth()
  const [profileLoading, setProfileLoading] = useState(false)
  const [emailLoading, setEmailLoading] = useState(false)
  const [passwordLoading, setPasswordLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)
  const [tagInput, setTagInput] = useState('')
  const [activeTab, setActiveTab] = useState<'profile' | 'account'>(initialTab)
  
  // Profile form data
  const [formData, setFormData] = useState<UpdateProfileData>({
    firstName: '',
    lastName: '',
    title: '',
    location: '',
    expertiseTags: []
  })
  
  // Email change form
  const [emailForm, setEmailForm] = useState({
    newEmail: '',
    password: ''
  })
  
  // Password change form
  const [passwordForm, setPasswordForm] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  })
  
  const [showPasswords, setShowPasswords] = useState({
    current: false,
    new: false,
    confirm: false
  })

  useEffect(() => {
    console.log('EditProfilePanel useEffect triggered', { hasUser: !!user, isOpen })
    if (user && isOpen) {
      console.log('Resetting form data')
      setFormData({
        firstName: user.firstName || '',
        lastName: user.lastName || '',
        title: user.title || '',
        location: user.location || '',
        expertiseTags: user.expertiseTags || []
      })
      setEmailForm({ newEmail: '', password: '' })
      setPasswordForm({ currentPassword: '', newPassword: '', confirmPassword: '' })
      setError(null)
      setSuccessMessage(null)
      setActiveTab(initialTab)
    }
  }, [user, isOpen, initialTab])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setProfileLoading(true)
    setError(null)

    try {
      const response = await fetch(buildApiUrl('/api/v1/auth/profile'), {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(formData)
      })

      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.detail || 'Failed to update profile')
      }

      await refreshProfile()
      onSave()
      onClose()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update profile')
    } finally {
      setProfileLoading(false)
    }
  }

  const handleAddTag = () => {
    if (tagInput.trim() && !formData.expertiseTags?.includes(tagInput.trim())) {
      setFormData(prev => ({
        ...prev,
        expertiseTags: [...(prev.expertiseTags || []), tagInput.trim()]
      }))
      setTagInput('')
    }
  }

  const handleRemoveTag = (tag: string) => {
    setFormData(prev => ({
      ...prev,
      expertiseTags: prev.expertiseTags?.filter(t => t !== tag) || []
    }))
  }

  // Blocked personal email domains (mirrors backend list)
  const BLOCKED_EMAIL_DOMAINS = [
    'gmail.com',
    'yahoo.com',
    'hotmail.com',
    'outlook.com',
    'protonmail.com',
    'icloud.com',
    'live.com',
    'msn.com'
  ]

  const getEmailDomain = (email: string) => {
    if (!email || !email.includes('@')) return ''
    return email.split('@').pop()?.trim().toLowerCase() || ''
  }

  const isBlockedDomain = (email: string) => {
    const domain = getEmailDomain(email)
    return BLOCKED_EMAIL_DOMAINS.includes(domain)
  }

  const handleEmailUpdate = async (e: React.FormEvent) => {
    e.preventDefault()
    setEmailLoading(true)
    setError(null)
    setSuccessMessage(null)

    // Client-side validation: block personal email domains
    if (isBlockedDomain(emailForm.newEmail)) {
      setError('Personal email addresses are not allowed. Please use your company email.')
      setEmailLoading(false)
      return
    }

    // Client-side validation: check domain matches current org domain
    const currentDomain = getEmailDomain(user?.email || '')
    const newDomain = getEmailDomain(emailForm.newEmail)
    if (currentDomain && newDomain && currentDomain !== newDomain) {
      setError(`New email must match your organization domain (@${currentDomain}).`)
      setEmailLoading(false)
      return
    }

    try {
      const response = await fetch(buildApiUrl('/api/v1/auth/email'), {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(emailForm)
      })

      const data = await response.json()
      
      if (!response.ok) {
        throw new Error(data.detail || 'Failed to update email')
      }

      setSuccessMessage('Email updated successfully!')
      setEmailForm({ newEmail: '', password: '' })
      await refreshProfile()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update email')
    } finally {
      setEmailLoading(false)
    }
  }

  const handlePasswordUpdate = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (passwordForm.newPassword !== passwordForm.confirmPassword) {
      setError('New passwords do not match')
      return
    }
    
    setPasswordLoading(true)
    setError(null)
    setSuccessMessage(null)

    try {
      const response = await fetch(buildApiUrl('/api/v1/auth/password'), {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          currentPassword: passwordForm.currentPassword,
          newPassword: passwordForm.newPassword
        })
      })

      const data = await response.json()
      
      if (!response.ok) {
        throw new Error(data.detail || 'Failed to update password')
      }

      setSuccessMessage('Password updated successfully!')
      setPasswordForm({ currentPassword: '', newPassword: '', confirmPassword: '' })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update password')
    } finally {
      setPasswordLoading(false)
    }
  }

  const handleProfilePictureUpload = useCallback(async (file: File) => {
    console.log('handleProfilePictureUpload called with file:', file.name)
    try {
      const formData = new FormData()
      formData.append('file', file)

      console.log('Sending POST request to /api/v1/media/profile-picture')
      const response = await fetch(buildApiUrl('/api/v1/media/profile-picture'), {
        method: 'POST',
        body: formData,
        credentials: 'include'
      })

      console.log('Upload response:', response.status, response.ok)

      if (!response.ok) {
        const errorText = await response.text()
        console.error('Upload failed:', errorText)
        throw new Error('Failed to upload profile picture')
      }

      const result = await response.json()
      console.log('Upload successful:', result)

      await refreshProfile()
      setSuccessMessage('Profile picture updated successfully!')
    } catch (err) {
      console.error('Upload error:', err)
      setError(err instanceof Error ? err.message : 'Failed to upload profile picture')
    }
  }, [refreshProfile])

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50">
      <div className="absolute inset-0 bg-blue-900/20 backdrop-blur-sm" onClick={onClose} />
      <div className="absolute right-0 top-0 h-full w-full max-w-lg bg-white border-l border-blue-100 shadow-2xl flex flex-col">
        <div className="px-6 py-5 bg-gradient-to-r from-blue-600 to-blue-700 text-white flex items-center justify-between">
          <h3 className="text-xl font-bold">Edit Profile</h3>
          <button 
            onClick={onClose} 
            className="text-white/80 hover:text-white transition-colors"
            disabled={profileLoading || emailLoading || passwordLoading}
          >
            <X size={24} />
          </button>
        </div>

        {/* Tab Navigation */}
        <div className="flex border-b border-gray-200">
          <button
            type="button"
            onClick={() => setActiveTab('profile')}
            className={`px-6 py-3 text-sm font-medium ${
              activeTab === 'profile'
                ? 'text-blue-600 border-b-2 border-blue-600'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            Profile Information
          </button>
          <button
            type="button"
            onClick={() => setActiveTab('account')}
            className={`px-6 py-3 text-sm font-medium ${
              activeTab === 'account'
                ? 'text-blue-600 border-b-2 border-blue-600'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            Account Settings
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-6">
          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm">
              {error}
            </div>
          )}
          
          {successMessage && (
            <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-lg text-green-600 text-sm">
              {successMessage}
            </div>
          )}

          {/* Profile Tab */}
          {activeTab === 'profile' && (
            <>
              {/* Profile Picture Section - OUTSIDE form to prevent conflicts */}
              <div className="text-center py-6 border-b border-gray-200 mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-4">
                  Profile Picture
                </label>
                <ProfilePictureEditor
                  currentImageUrl={user?.profilePictureUrl || undefined}
                  onImageUpload={handleProfilePictureUpload}
                  size="lg"
                  disabled={profileLoading}
                />
              </div>

              <form onSubmit={handleSubmit} className="space-y-4">

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  First Name
                </label>
                <input
                  type="text"
                  value={formData.firstName}
                  onChange={(e) => setFormData(prev => ({ ...prev, firstName: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Last Name
                </label>
                <input
                  type="text"
                  value={formData.lastName}
                  onChange={(e) => setFormData(prev => ({ ...prev, lastName: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Job Title
              </label>
              <input
                type="text"
                value={formData.title}
                onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="e.g., Manufacturing Engineer"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Company
              </label>
              <input
                type="text"
                value={user?.company || ''}
                disabled
                className="w-full px-3 py-2 border border-gray-200 rounded-lg bg-gray-50 text-gray-600 cursor-not-allowed"
                placeholder="Set by organization"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Industry Sector
              </label>
              <input
                type="text"
                value={user?.industrySector || ''}
                disabled
                className="w-full px-3 py-2 border border-gray-200 rounded-lg bg-gray-50 text-gray-600 cursor-not-allowed"
                placeholder="Set by organization"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Location
              </label>
              <input
                type="text"
                value={formData.location}
                onChange={(e) => setFormData(prev => ({ ...prev, location: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="City, Country"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Expertise Tags
              </label>
              <div className="flex gap-2 mb-2">
                <input
                  type="text"
                  value={tagInput}
                  onChange={(e) => setTagInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddTag())}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Add expertise tag"
                />
                <Button
                  type="button"
                  onClick={handleAddTag}
                  variant="outline"
                  size="sm"
                  className="px-3"
                >
                  <Plus size={16} />
                </Button>
              </div>
              <div className="flex flex-wrap gap-2">
                {formData.expertiseTags?.map((tag, index) => (
                  <span
                    key={index}
                    className="inline-flex items-center px-3 py-1 rounded-full text-xs bg-blue-100 text-blue-800"
                  >
                    {tag}
                    <button
                      type="button"
                      onClick={() => handleRemoveTag(tag)}
                      className="ml-2 text-blue-600 hover:text-blue-800"
                    >
                      <X size={14} />
                    </button>
                  </span>
                ))}
              </div>
            </div>

            <div className="mt-8 flex gap-3">
              <Button
                type="submit"
                disabled={profileLoading}
                className="flex-1 bg-blue-600 hover:bg-blue-700 text-white"
              >
                {profileLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Saving...
                  </>
                ) : (
                  <>
                    <Save className="mr-2 h-4 w-4" />
                    Save Profile
                  </>
                )}
              </Button>
              <Button
                type="button"
                onClick={onClose}
                disabled={profileLoading}
                variant="outline"
                className="flex-1"
              >
                Cancel
              </Button>
            </div>
          </form>
            </>
          )}

          {/* Account Tab */}
          {activeTab === 'account' && (
            <div className="space-y-6">
              {/* Email Change Section */}
              <div className="border border-gray-200 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  <Mail className="mr-2 h-5 w-5" />
                  Change Email
                </h3>
                <form onSubmit={handleEmailUpdate} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Current Email
                    </label>
                    <input
                      type="email"
                      value={user?.email || ''}
                      disabled
                      className="w-full px-3 py-2 border border-gray-200 rounded-lg bg-gray-50 text-gray-600 cursor-not-allowed"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      New Email
                    </label>
                    <input
                      type="email"
                      value={emailForm.newEmail}
                      onChange={(e) => setEmailForm(prev => ({ ...prev, newEmail: e.target.value }))}
                      className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:border-transparent ${
                        emailForm.newEmail && (isBlockedDomain(emailForm.newEmail) || (getEmailDomain(emailForm.newEmail) && getEmailDomain(user?.email || '') && getEmailDomain(emailForm.newEmail) !== getEmailDomain(user?.email || '')))
                          ? 'border-red-300 focus:ring-red-500'
                          : 'border-gray-300 focus:ring-blue-500'
                      }`}
                      placeholder={`Enter new email (must be @${getEmailDomain(user?.email || '') || 'your-company.com'})`}
                      required
                    />
                    {emailForm.newEmail && isBlockedDomain(emailForm.newEmail) && (
                      <p className="mt-1 text-xs text-red-600">
                        Personal email addresses (Gmail, Yahoo, etc.) are not allowed.
                      </p>
                    )}
                    {emailForm.newEmail && !isBlockedDomain(emailForm.newEmail) && getEmailDomain(emailForm.newEmail) && getEmailDomain(user?.email || '') && getEmailDomain(emailForm.newEmail) !== getEmailDomain(user?.email || '') && (
                      <p className="mt-1 text-xs text-red-600">
                        Email must match your organization domain (@{getEmailDomain(user?.email || '')}).
                      </p>
                    )}
                    {!emailForm.newEmail && (
                      <p className="mt-1 text-xs text-gray-500">
                        New email must use your organization domain (@{getEmailDomain(user?.email || '')}).
                      </p>
                    )}
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Current Password (for verification)
                    </label>
                    <input
                      type="password"
                      value={emailForm.password}
                      onChange={(e) => setEmailForm(prev => ({ ...prev, password: e.target.value }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="Enter your password"
                      required
                    />
                  </div>
                  <Button
                    type="submit"
                    disabled={emailLoading}
                    className="w-full bg-blue-600 hover:bg-blue-700 text-white"
                  >
                    {emailLoading ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Updating Email...
                      </>
                    ) : (
                      'Update Email'
                    )}
                  </Button>
                </form>
              </div>

              {/* Password Change Section */}
              <div className="border border-gray-200 rounded-lg p-6" data-section="security">
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  <Lock className="mr-2 h-5 w-5" />
                  Change Password
                </h3>
                <form onSubmit={handlePasswordUpdate} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Current Password
                    </label>
                    <div className="relative">
                      <input
                        type={showPasswords.current ? 'text' : 'password'}
                        value={passwordForm.currentPassword}
                        onChange={(e) => setPasswordForm(prev => ({ ...prev, currentPassword: e.target.value }))}
                        className="w-full px-3 py-2 pr-10 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        placeholder="Enter current password"
                        required
                      />
                      <button
                        type="button"
                        onClick={() => setShowPasswords(prev => ({ ...prev, current: !prev.current }))}
                        className="absolute right-2 top-2.5 text-gray-500 hover:text-gray-700"
                      >
                        {showPasswords.current ? <EyeOff size={20} /> : <Eye size={20} />}
                      </button>
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      New Password
                    </label>
                    <div className="relative">
                      <input
                        type={showPasswords.new ? 'text' : 'password'}
                        value={passwordForm.newPassword}
                        onChange={(e) => setPasswordForm(prev => ({ ...prev, newPassword: e.target.value }))}
                        className="w-full px-3 py-2 pr-10 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        placeholder="Enter new password"
                        required
                      />
                      <button
                        type="button"
                        onClick={() => setShowPasswords(prev => ({ ...prev, new: !prev.new }))}
                        className="absolute right-2 top-2.5 text-gray-500 hover:text-gray-700"
                      >
                        {showPasswords.new ? <EyeOff size={20} /> : <Eye size={20} />}
                      </button>
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Confirm New Password
                    </label>
                    <div className="relative">
                      <input
                        type={showPasswords.confirm ? 'text' : 'password'}
                        value={passwordForm.confirmPassword}
                        onChange={(e) => setPasswordForm(prev => ({ ...prev, confirmPassword: e.target.value }))}
                        className="w-full px-3 py-2 pr-10 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        placeholder="Confirm new password"
                        required
                      />
                      <button
                        type="button"
                        onClick={() => setShowPasswords(prev => ({ ...prev, confirm: !prev.confirm }))}
                        className="absolute right-2 top-2.5 text-gray-500 hover:text-gray-700"
                      >
                        {showPasswords.confirm ? <EyeOff size={20} /> : <Eye size={20} />}
                      </button>
                    </div>
                  </div>
                  <Button
                    type="submit"
                    disabled={passwordLoading}
                    className="w-full bg-blue-600 hover:bg-blue-700 text-white"
                  >
                    {passwordLoading ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Updating Password...
                      </>
                    ) : (
                      'Update Password'
                    )}
                  </Button>
                </form>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}