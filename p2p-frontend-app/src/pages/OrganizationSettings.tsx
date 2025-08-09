import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { 
  Building, 
  MapPin, 
  Users,
  Globe,
  Phone,
  Mail,
  Calendar,
  Camera,
  Save,
  X,
  ArrowLeft,
  AlertCircle,
  CheckCircle,
  BarChart3,
  HardDrive,
  TrendingUp,
  Shield
} from "lucide-react"
import { useAuth } from '@/contexts/AuthContext'
import { api } from '@/services/api'

interface OrganizationData {
  name: string
  description?: string
  website?: string
  phone?: string
  email?: string
  address?: string
  city: string
  country: string
  industry: string
  size: string
  logoUrl?: string
}

interface OrganizationStats {
  totalUsers: number
  activeUsers: number
  pendingInvitations: number
  storageUsed: number
  storageLimit: number
  subscriptionTier: string
  trialExpiresAt?: string
}

export default function OrganizationSettings() {
  const navigate = useNavigate()
  const { user, organization } = useAuth()
  const [isEditing, setIsEditing] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  const [logo, setLogo] = useState<File | null>(null)
  const [logoPreview, setLogoPreview] = useState<string | null>(null)
  const [stats, setStats] = useState<OrganizationStats | null>(null)
  
  const [orgData, setOrgData] = useState<OrganizationData>({
    name: '',
    description: '',
    website: '',
    phone: '',
    email: '',
    address: '',
    city: '',
    country: '',
    industry: '',
    size: '',
    logoUrl: ''
  })

  // Load organization data on mount
  useEffect(() => {
    fetchOrganizationData()
    if (user?.role === 'admin') {
      fetchOrganizationStats()
    }
  }, [user])

  const fetchOrganizationData = async () => {
    try {
      setIsLoading(true)
      setError(null)
      
      const response = await api.get('/api/v1/organizations/me')
      const org = response.data
      
      setOrgData({
        name: org.name || '',
        description: org.description || '',
        website: org.website || '',
        phone: org.phone || '',
        email: org.email || '',
        address: org.address || '',
        city: org.city || '',
        country: org.country || '',
        industry: org.industry || '',
        size: org.size || org.organization_size || '',
        logoUrl: org.logo_url || org.logoUrl || ''
      })
    } catch (err: any) {
      console.error('Failed to fetch organization:', err)
      // Fall back to auth context data if API fails
      if (organization) {
        setOrgData({
          name: organization.name || '',
          description: '',
          website: '',
          phone: '',
          email: '',
          address: '',
          city: organization.city || '',
          country: organization.country || '',
          industry: organization.industry || '',
          size: organization.size || '',
          logoUrl: ''
        })
      }
      setError('Failed to load organization data')
    } finally {
      setIsLoading(false)
    }
  }

  const fetchOrganizationStats = async () => {
    try {
      const response = await api.get('/api/v1/organizations/stats')
      const statsData = response.data
      
      setStats({
        totalUsers: statsData.user_count?.total || 0,
        activeUsers: statsData.user_count?.active || 0,
        pendingInvitations: statsData.user_count?.pending_invitations || 0,
        storageUsed: statsData.storage?.used_bytes || 0,
        storageLimit: statsData.storage?.limit_bytes || 0,
        subscriptionTier: statsData.subscription?.tier || 'free',
        trialExpiresAt: statsData.subscription?.trial_expires_at
      })
    } catch (err: any) {
      console.error('Failed to fetch organization stats:', err)
    }
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setOrgData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }))
  }

  const handleLogoChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0]
      setLogo(file)
      
      // Create preview
      const reader = new FileReader()
      reader.onloadend = () => {
        setLogoPreview(reader.result as string)
      }
      reader.readAsDataURL(file)
    }
  }

  const handleSave = async () => {
    try {
      setIsLoading(true)
      setError(null)
      setSuccess(null)

      // Update organization data
      const updateData = {
        name: orgData.name,
        description: orgData.description,
        website: orgData.website,
        phone: orgData.phone,
        email: orgData.email,
        address: orgData.address,
        city: orgData.city,
        country: orgData.country,
        industry: orgData.industry,
        size: orgData.size
      }

      await api.patch('/api/v1/organizations/me', updateData)
      
      // Upload logo if changed
      if (logo) {
        const formData = new FormData()
        formData.append('file', logo)
        
        try {
          const logoResponse = await api.upload('/api/v1/organizations/me/logo', formData)
          setOrgData(prev => ({
            ...prev,
            logoUrl: logoResponse.data.url || logoResponse.data.logo_url
          }))
        } catch (logoErr) {
          console.error('Failed to upload logo:', logoErr)
        }
      }

      setSuccess('Organization settings updated successfully!')
      setIsEditing(false)
      setLogo(null)
      setLogoPreview(null)
      
      // Refresh stats
      if (user?.role === 'admin') {
        fetchOrganizationStats()
      }
    } catch (err: any) {
      console.error('Failed to update organization:', err)
      setError(err.response?.data?.detail || 'Failed to update organization settings')
    } finally {
      setIsLoading(false)
    }
  }

  const handleCancel = () => {
    setIsEditing(false)
    setLogo(null)
    setLogoPreview(null)
    setError(null)
    // Reset to original data
    fetchOrganizationData()
  }

  const handleRemoveLogo = async () => {
    try {
      setIsLoading(true)
      await api.delete('/api/v1/organizations/me/logo')
      setOrgData(prev => ({ ...prev, logoUrl: '' }))
      setLogoPreview(null)
      setSuccess('Organization logo removed successfully!')
    } catch (err: any) {
      console.error('Failed to remove logo:', err)
      setError('Failed to remove organization logo')
    } finally {
      setIsLoading(false)
    }
  }

  // Only allow admins to access this page
  if (user?.role !== 'admin') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 flex items-center justify-center">
        <Card className="max-w-md">
          <CardContent className="pt-6">
            <div className="text-center space-y-4">
              <Shield className="h-16 w-16 text-gray-400 mx-auto" />
              <h2 className="text-2xl font-bold text-gray-900">Access Restricted</h2>
              <p className="text-gray-600">Only organization administrators can access these settings.</p>
              <Button onClick={() => navigate('/dashboard')}>
                Return to Dashboard
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      <div className="container mx-auto px-4 py-8 max-w-6xl">
        {/* Header */}
        <div className="mb-8">
          <Button
            variant="ghost"
            onClick={() => navigate('/dashboard')}
            className="mb-4"
          >
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Dashboard
          </Button>
          
          <h1 className="text-3xl font-bold text-gray-900">Organization Settings</h1>
          <p className="text-gray-600 mt-2">Manage your organization's information and preferences</p>
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

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Settings */}
          <div className="lg:col-span-2 space-y-6">
            {/* Organization Info Card */}
            <Card>
              <CardHeader>
                <div className="flex justify-between items-start">
                  <div>
                    <CardTitle>Organization Information</CardTitle>
                    <CardDescription>Update your organization's details</CardDescription>
                  </div>
                  {!isEditing ? (
                    <Button onClick={() => setIsEditing(true)} disabled={isLoading}>
                      Edit Settings
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
                  {/* Logo */}
                  <div className="flex items-center space-x-6">
                    <div className="relative">
                      <div className="w-24 h-24 rounded-lg bg-gray-200 flex items-center justify-center overflow-hidden">
                        {logoPreview || orgData.logoUrl ? (
                          <img 
                            src={logoPreview || orgData.logoUrl} 
                            alt="Organization Logo" 
                            className="w-full h-full object-cover"
                          />
                        ) : (
                          <Building className="h-12 w-12 text-gray-400" />
                        )}
                      </div>
                      {isEditing && (
                        <button
                          onClick={() => document.getElementById('logo-input')?.click()}
                          className="absolute bottom-0 right-0 bg-blue-600 p-2 rounded-full text-white hover:bg-blue-700"
                        >
                          <Camera className="h-4 w-4" />
                        </button>
                      )}
                      <input
                        id="logo-input"
                        type="file"
                        accept="image/*"
                        onChange={handleLogoChange}
                        className="hidden"
                      />
                    </div>
                    
                    <div>
                      <h3 className="font-semibold text-lg">{orgData.name}</h3>
                      <p className="text-gray-600">{orgData.industry}</p>
                      {isEditing && orgData.logoUrl && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={handleRemoveLogo}
                          className="mt-2 text-red-600 hover:text-red-700"
                        >
                          Remove Logo
                        </Button>
                      )}
                    </div>
                  </div>

                  {/* Form Fields */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <Label htmlFor="name">Organization Name</Label>
                      <Input
                        id="name"
                        name="name"
                        value={orgData.name}
                        onChange={handleInputChange}
                        disabled={!isEditing || isLoading}
                        className="mt-1"
                      />
                    </div>
                    
                    <div>
                      <Label htmlFor="industry">Industry</Label>
                      <Input
                        id="industry"
                        name="industry"
                        value={orgData.industry}
                        onChange={handleInputChange}
                        disabled={!isEditing || isLoading}
                        className="mt-1"
                      />
                    </div>
                    
                    <div>
                      <Label htmlFor="size">Organization Size</Label>
                      <select
                        id="size"
                        name="size"
                        value={orgData.size}
                        onChange={(e) => setOrgData(prev => ({ ...prev, size: e.target.value }))}
                        disabled={!isEditing || isLoading}
                        className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      >
                        <option value="startup">Startup (1-10)</option>
                        <option value="small">Small (11-50)</option>
                        <option value="medium">Medium (51-200)</option>
                        <option value="large">Large (201-500)</option>
                        <option value="enterprise">Enterprise (500+)</option>
                      </select>
                    </div>
                    
                    <div>
                      <Label htmlFor="website">Website</Label>
                      <div className="relative">
                        <Globe className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                        <Input
                          id="website"
                          name="website"
                          type="url"
                          value={orgData.website}
                          onChange={handleInputChange}
                          disabled={!isEditing || isLoading}
                          placeholder="https://example.com"
                          className="mt-1 pl-10"
                        />
                      </div>
                    </div>
                    
                    <div>
                      <Label htmlFor="email">Contact Email</Label>
                      <div className="relative">
                        <Mail className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                        <Input
                          id="email"
                          name="email"
                          type="email"
                          value={orgData.email}
                          onChange={handleInputChange}
                          disabled={!isEditing || isLoading}
                          className="mt-1 pl-10"
                        />
                      </div>
                    </div>
                    
                    <div>
                      <Label htmlFor="phone">Phone Number</Label>
                      <div className="relative">
                        <Phone className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                        <Input
                          id="phone"
                          name="phone"
                          type="tel"
                          value={orgData.phone}
                          onChange={handleInputChange}
                          disabled={!isEditing || isLoading}
                          placeholder="+966 XX XXX XXXX"
                          className="mt-1 pl-10"
                        />
                      </div>
                    </div>
                  </div>

                  <div>
                    <Label htmlFor="description">Description</Label>
                    <Textarea
                      id="description"
                      name="description"
                      value={orgData.description}
                      onChange={handleInputChange}
                      disabled={!isEditing || isLoading}
                      rows={3}
                      placeholder="Brief description of your organization"
                      className="mt-1"
                    />
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <Label htmlFor="address">Street Address</Label>
                      <Input
                        id="address"
                        name="address"
                        value={orgData.address}
                        onChange={handleInputChange}
                        disabled={!isEditing || isLoading}
                        className="mt-1"
                      />
                    </div>
                    
                    <div>
                      <Label htmlFor="city">City</Label>
                      <div className="relative">
                        <MapPin className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                        <Input
                          id="city"
                          name="city"
                          value={orgData.city}
                          onChange={handleInputChange}
                          disabled={!isEditing || isLoading}
                          className="mt-1 pl-10"
                        />
                      </div>
                    </div>
                    
                    <div>
                      <Label htmlFor="country">Country</Label>
                      <Input
                        id="country"
                        name="country"
                        value={orgData.country}
                        onChange={handleInputChange}
                        disabled={!isEditing || isLoading}
                        className="mt-1"
                      />
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Sidebar - Stats and Info */}
          <div className="space-y-6">
            {/* Organization Stats */}
            {stats && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <BarChart3 className="mr-2 h-5 w-5" />
                    Organization Statistics
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <div className="flex justify-between items-center mb-1">
                        <span className="text-sm text-gray-600">Team Members</span>
                        <span className="font-semibold">{stats.totalUsers}</span>
                      </div>
                      <div className="flex justify-between items-center text-xs text-gray-500">
                        <span>{stats.activeUsers} active</span>
                        <span>{stats.pendingInvitations} pending</span>
                      </div>
                    </div>
                    
                    <div className="pt-3 border-t">
                      <div className="flex justify-between items-center mb-2">
                        <span className="text-sm text-gray-600 flex items-center">
                          <HardDrive className="mr-1 h-4 w-4" />
                          Storage Usage
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2 mb-1">
                        <div 
                          className="bg-blue-600 h-2 rounded-full"
                          style={{ 
                            width: `${Math.min((stats.storageUsed / stats.storageLimit) * 100, 100)}%` 
                          }}
                        />
                      </div>
                      <div className="text-xs text-gray-500">
                        {(stats.storageUsed / (1024 * 1024)).toFixed(1)} MB / {(stats.storageLimit / (1024 * 1024)).toFixed(0)} MB
                      </div>
                    </div>
                    
                    <div className="pt-3 border-t">
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-gray-600">Subscription</span>
                        <span className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded-full font-medium capitalize">
                          {stats.subscriptionTier}
                        </span>
                      </div>
                      {stats.trialExpiresAt && (
                        <p className="text-xs text-gray-500 mt-1">
                          Trial expires: {new Date(stats.trialExpiresAt).toLocaleDateString()}
                        </p>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Quick Actions */}
            <Card>
              <CardHeader>
                <CardTitle>Quick Actions</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <Button 
                    variant="outline" 
                    className="w-full justify-start"
                    onClick={() => navigate('/users')}
                  >
                    <Users className="mr-2 h-4 w-4" />
                    Manage Users
                  </Button>
                  <Button variant="outline" className="w-full justify-start">
                    <TrendingUp className="mr-2 h-4 w-4" />
                    View Reports
                  </Button>
                  <Button variant="outline" className="w-full justify-start">
                    <Shield className="mr-2 h-4 w-4" />
                    Security Settings
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Organization Created Date */}
            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center space-x-3 text-gray-600">
                  <Calendar className="h-5 w-5" />
                  <div>
                    <p className="text-sm font-medium">Organization Created</p>
                    <p className="text-xs text-gray-500">
                      {organization?.createdAt ? new Date(organization.createdAt).toLocaleDateString() : 'N/A'}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}