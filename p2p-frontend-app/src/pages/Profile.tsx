import React, { useState, useEffect } from 'react'
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { 
  User, 
  Mail, 
  Building, 
  MapPin, 
  Calendar,
  Camera,
  Save,
  X,
  ArrowLeft,
  AlertCircle,
  CheckCircle
} from "lucide-react"
import { useAuth } from '@/contexts/AuthContext'
import { api } from '@/services/api'
import type { Page } from '@/components/Navigation'

interface ProfileProps {
  onPageChange?: (page: Page) => void
}

interface ProfileData {
  firstName: string
  lastName: string
  email: string
  phone?: string
  department?: string
  jobTitle?: string
  profilePictureUrl?: string
}

export default function Profile({ onPageChange }: ProfileProps) {
  const { user, organization, updateUser } = useAuth()
  const [isEditing, setIsEditing] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  const [profilePicture, setProfilePicture] = useState<File | null>(null)
  const [profilePicturePreview, setProfilePicturePreview] = useState<string | null>(null)
  
  const [profileData, setProfileData] = useState<ProfileData>({
    firstName: '',
    lastName: '',
    email: '',
    phone: '',
    department: '',
    jobTitle: '',
    profilePictureUrl: ''
  })

  // Load user data on mount
  useEffect(() => {
    fetchUserProfile()
  }, [])

  const fetchUserProfile = async () => {
    try {
      setIsLoading(true)
      setError(null)
      
      const response = await api.get('/api/v1/users/me')
      const userData = response.data
      
      setProfileData({
        firstName: userData.first_name || userData.firstName || '',
        lastName: userData.last_name || userData.lastName || '',
        email: userData.email || '',
        phone: userData.phone || '',
        department: userData.department || '',
        jobTitle: userData.job_title || userData.jobTitle || '',
        profilePictureUrl: userData.profile_picture_url || userData.profilePictureUrl || ''
      })
    } catch (err: any) {
      console.error('Failed to fetch profile:', err)
      // Fall back to auth context data if API fails
      if (user) {
        setProfileData({
          firstName: user.firstName || '',
          lastName: user.lastName || '',
          email: user.email || '',
          phone: '',
          department: '',
          jobTitle: '',
          profilePictureUrl: ''
        })
      }
      setError('Failed to load profile data')
    } finally {
      setIsLoading(false)
    }
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setProfileData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }))
  }

  const handleProfilePictureChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0]
      setProfilePicture(file)
      
      // Create preview
      const reader = new FileReader()
      reader.onloadend = () => {
        setProfilePicturePreview(reader.result as string)
      }
      reader.readAsDataURL(file)
    }
  }

  const handleSave = async () => {
    try {
      setIsLoading(true)
      setError(null)
      setSuccess(null)

      // Update profile data
      const updateData = {
        first_name: profileData.firstName,
        last_name: profileData.lastName,
        phone: profileData.phone,
        department: profileData.department,
        job_title: profileData.jobTitle
      }

      const response = await api.patch('/api/v1/users/me', updateData)
      
      // Upload profile picture if changed
      if (profilePicture) {
        const formData = new FormData()
        formData.append('file', profilePicture)
        
        try {
          const pictureResponse = await api.upload('/api/v1/users/me/profile-picture', formData)
          setProfileData(prev => ({
            ...prev,
            profilePictureUrl: pictureResponse.data.url || pictureResponse.data.file_url
          }))
        } catch (pictureErr) {
          console.error('Failed to upload profile picture:', pictureErr)
        }
      }

      // Update auth context
      if (response.data) {
        await updateUser({
          ...user!,
          firstName: profileData.firstName,
          lastName: profileData.lastName
        })
      }

      setSuccess('Profile updated successfully!')
      setIsEditing(false)
      setProfilePicture(null)
      setProfilePicturePreview(null)
    } catch (err: any) {
      console.error('Failed to update profile:', err)
      setError(err.response?.data?.detail || 'Failed to update profile')
    } finally {
      setIsLoading(false)
    }
  }

  const handleCancel = () => {
    setIsEditing(false)
    setProfilePicture(null)
    setProfilePicturePreview(null)
    setError(null)
    // Reset to original data
    fetchUserProfile()
  }

  const handleRemoveProfilePicture = async () => {
    try {
      setIsLoading(true)
      await api.delete('/api/v1/users/me/profile-picture')
      setProfileData(prev => ({ ...prev, profilePictureUrl: '' }))
      setProfilePicturePreview(null)
      setSuccess('Profile picture removed successfully!')
    } catch (err: any) {
      console.error('Failed to remove profile picture:', err)
      setError('Failed to remove profile picture')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        {/* Header */}
        <div className="mb-8">
          <Button
            variant="ghost"
            onClick={() => onPageChange?.('dashboard')}
            className="mb-4"
          >
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Dashboard
          </Button>
          
          <h1 className="text-3xl font-bold text-gray-900">My Profile</h1>
          <p className="text-gray-600 mt-2">Manage your personal information and preferences</p>
        </div>

        {/* Alerts */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center space-x-2">
            <AlertCircle className="h-5 w-5 text-red-600" />
            <span className="text-red-800">{error}</span>
          </div>
        )}
        
        {success && (
          <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg flex items-center space-x-2">
            <CheckCircle className="h-5 w-5 text-green-600" />
            <span className="text-green-800">{success}</span>
          </div>
        )}

        {/* Profile Card */}
        <Card>
          <CardHeader>
            <div className="flex justify-between items-start">
              <div>
                <CardTitle>Personal Information</CardTitle>
                <CardDescription>Update your profile details</CardDescription>
              </div>
              {!isEditing ? (
                <Button onClick={() => setIsEditing(true)} disabled={isLoading}>
                  Edit Profile
                </Button>
              ) : (
                <div className="space-x-2">
                  <Button variant="outline" onClick={handleCancel} disabled={isLoading}>
                    <X className="mr-2 h-4 w-4" />
                    Cancel
                  </Button>
                  <Button onClick={handleSave} disabled={isLoading}>
                    <Save className="mr-2 h-4 w-4" />
                    Save Changes
                  </Button>
                </div>
              )}
            </div>
          </CardHeader>
          
          <CardContent>
            <div className="space-y-6">
              {/* Profile Picture */}
              <div className="flex items-center space-x-6">
                <div className="relative">
                  <div className="w-24 h-24 rounded-full bg-gray-200 flex items-center justify-center overflow-hidden">
                    {profilePicturePreview || profileData.profilePictureUrl ? (
                      <img 
                        src={profilePicturePreview || profileData.profilePictureUrl} 
                        alt="Profile" 
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <User className="h-12 w-12 text-gray-400" />
                    )}
                  </div>
                  {isEditing && (
                    <button
                      onClick={() => document.getElementById('profile-picture-input')?.click()}
                      className="absolute bottom-0 right-0 bg-blue-600 p-2 rounded-full text-white hover:bg-blue-700"
                    >
                      <Camera className="h-4 w-4" />
                    </button>
                  )}
                  <input
                    id="profile-picture-input"
                    type="file"
                    accept="image/*"
                    onChange={handleProfilePictureChange}
                    className="hidden"
                  />
                </div>
                
                <div>
                  <h3 className="font-semibold text-lg">
                    {profileData.firstName} {profileData.lastName}
                  </h3>
                  <p className="text-gray-600">{user?.role === 'admin' ? 'Administrator' : 'Member'}</p>
                  {isEditing && profileData.profilePictureUrl && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={handleRemoveProfilePicture}
                      className="mt-2 text-red-600 hover:text-red-700"
                    >
                      Remove Picture
                    </Button>
                  )}
                </div>
              </div>

              {/* Form Fields */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <Label htmlFor="firstName">First Name</Label>
                  <Input
                    id="firstName"
                    name="firstName"
                    value={profileData.firstName}
                    onChange={handleInputChange}
                    disabled={!isEditing || isLoading}
                    className="mt-1"
                  />
                </div>
                
                <div>
                  <Label htmlFor="lastName">Last Name</Label>
                  <Input
                    id="lastName"
                    name="lastName"
                    value={profileData.lastName}
                    onChange={handleInputChange}
                    disabled={!isEditing || isLoading}
                    className="mt-1"
                  />
                </div>
                
                <div>
                  <Label htmlFor="email">Email</Label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                    <Input
                      id="email"
                      name="email"
                      type="email"
                      value={profileData.email}
                      disabled={true}
                      className="mt-1 pl-10 bg-gray-50"
                    />
                  </div>
                  <p className="text-xs text-gray-500 mt-1">Email cannot be changed</p>
                </div>
                
                <div>
                  <Label htmlFor="phone">Phone Number</Label>
                  <Input
                    id="phone"
                    name="phone"
                    type="tel"
                    value={profileData.phone}
                    onChange={handleInputChange}
                    disabled={!isEditing || isLoading}
                    placeholder="+966 XX XXX XXXX"
                    className="mt-1"
                  />
                </div>
                
                <div>
                  <Label htmlFor="department">Department</Label>
                  <Input
                    id="department"
                    name="department"
                    value={profileData.department}
                    onChange={handleInputChange}
                    disabled={!isEditing || isLoading}
                    placeholder="e.g., Engineering"
                    className="mt-1"
                  />
                </div>
                
                <div>
                  <Label htmlFor="jobTitle">Job Title</Label>
                  <Input
                    id="jobTitle"
                    name="jobTitle"
                    value={profileData.jobTitle}
                    onChange={handleInputChange}
                    disabled={!isEditing || isLoading}
                    placeholder="e.g., Senior Engineer"
                    className="mt-1"
                  />
                </div>
              </div>

              {/* Organization Info */}
              <div className="pt-6 border-t">
                <h3 className="font-semibold mb-4 flex items-center">
                  <Building className="mr-2 h-5 w-5" />
                  Organization Information
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label>Organization Name</Label>
                    <p className="mt-1 text-gray-700">{organization?.name || 'N/A'}</p>
                  </div>
                  <div>
                    <Label>Industry</Label>
                    <p className="mt-1 text-gray-700">{organization?.industry || 'N/A'}</p>
                  </div>
                  <div>
                    <Label>Location</Label>
                    <p className="mt-1 text-gray-700 flex items-center">
                      <MapPin className="mr-1 h-4 w-4" />
                      {organization?.city}, {organization?.country}
                    </p>
                  </div>
                  <div>
                    <Label>Member Since</Label>
                    <p className="mt-1 text-gray-700 flex items-center">
                      <Calendar className="mr-1 h-4 w-4" />
                      {user?.createdAt ? new Date(user.createdAt).toLocaleDateString() : 'N/A'}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}