import React, { useState, useEffect } from 'react'
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { 
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { 
  Users, 
  UserPlus, 
  Mail, 
 
  Shield, 
  Clock, 
  CheckCircle, 
  XCircle,
  Search,
  Edit,
  Trash2,
  ArrowLeft,
} from "lucide-react"
import { useAuth } from '@/contexts/AuthContext'
// import { mockUsers, mockOrganizations } from '@/contexts/AuthContext' // REMOVED - exports disabled
// import type { PendingInvitation } from '@/types/auth' // Will be used when pending invitations are displayed
import { useNavigate } from 'react-router-dom'
import { API_BASE_URL } from '@/config/environment'

export default function UserManagement() {
  const navigate = useNavigate()
  const { user, organization } = useAuth()
  const [showInviteForm, setShowInviteForm] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [roleFilter, setRoleFilter] = useState<'all' | 'admin' | 'member'>('all')
  
  const [inviteEmail, setInviteEmail] = useState<string>('')
  const [inviting, setInviting] = useState(false)
  const [realInvitations, setRealInvitations] = useState<any[]>([])
  const [organizationMembers, setOrganizationMembers] = useState<any[]>([])

  // Notification state
  const [notification, setNotification] = useState<{
    show: boolean;
    message: string;
    type: 'success' | 'error'
  }>({ show: false, message: '', type: 'success' })

  // Confirmation modal state
  const [confirmCancel, setConfirmCancel] = useState<{
    show: boolean;
    invitationId: string | null;
    email: string;
  }>({ show: false, invitationId: null, email: '' })

  // Mock pending invitations - not currently used, will be replaced with real API data
  /*
  const [pendingInvitations] = useState<PendingInvitation[]>([
    {
      id: 'inv-1',
      email: 'omar.salem@advanced-electronics.com',
      firstName: 'Omar',
      lastName: 'Salem',
      role: 'member',
      organizationId: 'org-1',
      invitedBy: 'user-1',
      status: 'pending',
      expiresAt: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000),
      createdAt: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000)
    },
    {
      id: 'inv-2',
      email: 'fatima.ali@advanced-electronics.com',
      firstName: 'Fatima',
      lastName: 'Ali',
      role: 'admin',
      organizationId: 'org-1',
      invitedBy: 'user-1',
      status: 'pending',
      expiresAt: new Date(Date.now() + 5 * 24 * 60 * 60 * 1000),
      createdAt: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000)
    }
  ])
  */

  // Filter users for current organization
  const filteredUsers = organizationMembers.filter((u: any) => {
    const matchesSearch = `${u.name || ''} ${u.email}`.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesRole = roleFilter === 'all' || u.role === roleFilter
    return matchesSearch && matchesRole
  })

  const handleInviteUser = async (e: React.FormEvent) => {
    e.preventDefault()
    setInviting(true)
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/invites/send`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ email: inviteEmail })
      })
      
      if (response.ok) {
        // const data = await response.json() // Response data not currently used
        setNotification({ show: true, message: 'Invitation sent successfully!', type: 'success' })
        setTimeout(() => setNotification({ show: false, message: '', type: 'success' }), 5000)
        setInviteEmail('')
        setShowInviteForm(false)
        fetchInvitations() // Refresh the invitations list
      } else {
        const error = await response.json()
        setNotification({
          show: true,
          message: `Failed to send invitation: ${error.detail || 'Unknown error'}`,
          type: 'error'
        })
        setTimeout(() => setNotification({ show: false, message: '', type: 'success' }), 5000)
      }
    } catch (error) {
      console.error('Error inviting user:', error)
      setNotification({
        show: true,
        message: 'Failed to send invitation. Please try again.',
        type: 'error'
      })
      setTimeout(() => setNotification({ show: false, message: '', type: 'success' }), 5000)
    } finally {
      setInviting(false)
    }
  }
  
  const fetchInvitations = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/invites/pending`, {
        credentials: 'include'
      })
      if (response.ok) {
        const data = await response.json()
        setRealInvitations(data.invitations || [])
      }
    } catch (error) {
      console.error('Error fetching invitations:', error)
    }
  }
  
  const fetchOrganizationMembers = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/auth/users/organization`, {
        credentials: 'include'
      })
      if (response.ok) {
        const data = await response.json()
        setOrganizationMembers(data.users || [])
      }
    } catch (error) {
      console.error('Error fetching organization members:', error)
    }
  }

  const handleCancelInvitation = async () => {
    if (!confirmCancel.invitationId) return

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/invites/${confirmCancel.invitationId}`, {
        method: 'DELETE',
        credentials: 'include'
      })
      if (response.ok) {
        setNotification({
          show: true,
          message: 'Invitation cancelled successfully',
          type: 'success'
        })
        setTimeout(() => setNotification({ show: false, message: '', type: 'success' }), 5000)
        fetchInvitations()
      } else {
        setNotification({
          show: true,
          message: 'Failed to cancel invitation',
          type: 'error'
        })
        setTimeout(() => setNotification({ show: false, message: '', type: 'success' }), 5000)
      }
    } catch (error) {
      console.error('Error cancelling invitation:', error)
      setNotification({
        show: true,
        message: 'Error cancelling invitation. Please try again.',
        type: 'error'
      })
      setTimeout(() => setNotification({ show: false, message: '', type: 'success' }), 5000)
    } finally {
      setConfirmCancel({ show: false, invitationId: null, email: '' })
    }
  }

  useEffect(() => {
    if (user?.role === 'admin') {
      fetchInvitations()
      fetchOrganizationMembers()
    }
  }, [user])

  // Only allow admins to access this page
  if (user?.role !== 'admin') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 flex items-center justify-center">
        <div className="text-center">
          <Shield className="h-16 w-16 text-slate-400 mx-auto mb-4" />
          <h1 className="text-2xl font-bold text-slate-900 mb-2">Access Denied</h1>
          <p className="text-slate-600">Only organization administrators can access user management.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 pb-20 md:pb-0">
      <div className="w-full px-4 sm:px-6 lg:max-w-7xl lg:mx-auto py-6 sm:py-8">

        {/* Notification Banner */}
        {notification.show && (
          <div
            className={`fixed top-4 right-4 z-50 px-6 py-4 rounded-lg shadow-lg transition-all duration-500 ${
              notification.type === 'success'
                ? 'bg-green-500 text-white'
                : 'bg-red-500 text-white'
            }`}
            style={{
              animation: 'slideInRight 0.3s ease-out',
              maxWidth: '400px'
            }}
          >
            <div className="flex items-center gap-3">
              {notification.type === 'success' ? (
                <CheckCircle className="h-5 w-5 flex-shrink-0" />
              ) : (
                <XCircle className="h-5 w-5 flex-shrink-0" />
              )}
              <p className="font-medium">{notification.message}</p>
              <button
                onClick={() => setNotification({ show: false, message: '', type: 'success' })}
                className="ml-auto hover:opacity-80 transition-opacity"
              >
                <XCircle className="h-5 w-5" />
              </button>
            </div>
          </div>
        )}

        {/* Back to Dashboard Button */}
        <Button 
          variant="ghost" 
          className="mb-6"
                          onClick={() => navigate('/dashboard')}
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Dashboard
        </Button>
        
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-3xl font-bold text-slate-900 mb-2">User Management</h1>
              <p className="text-slate-600">Manage your organization's team members and invitations</p>
            </div>
            <Button
              onClick={() => setShowInviteForm(true)}
              className="bg-blue-600 hover:bg-blue-700 text-white"
            >
              <UserPlus className="h-4 w-4 mr-2" />
              Invite User
            </Button>
          </div>

          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div className="bg-white rounded-xl p-6 border border-slate-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-slate-600 text-sm">Total Users</p>
                  <p className="text-2xl font-bold text-slate-900">{organizationMembers.length}</p>
                </div>
                <Users className="h-8 w-8 text-blue-600" />
              </div>
            </div>
            <div className="bg-white rounded-xl p-6 border border-slate-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-slate-600 text-sm">Pending Invites</p>
                  <p className="text-2xl font-bold text-slate-900">{realInvitations.length}</p>
                </div>
                <Clock className="h-8 w-8 text-amber-600" />
              </div>
            </div>
            <div className="bg-white rounded-xl p-6 border border-slate-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-slate-600 text-sm">Admins</p>
                  <p className="text-2xl font-bold text-slate-900">
                    {organizationMembers.filter(u => u.role === 'admin').length}
                  </p>
                </div>
                <Shield className="h-8 w-8 text-green-600" />
              </div>
            </div>
          </div>
        </div>

        {/* Invite Form Modal */}
        {showInviteForm && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-2xl p-8 max-w-md w-full">
              <h2 className="text-2xl font-bold text-slate-900 mb-6">Invite Team Member</h2>
              
              <form onSubmit={handleInviteUser} className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Email Address
                  </label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-3 h-5 w-5 text-slate-400" />
                    <Input
                      type="email"
                      placeholder="Enter email address to invite"
                      value={inviteEmail}
                      onChange={(e) => setInviteEmail(e.target.value)}
                      className="pl-10"
                      required
                      disabled={inviting}
                    />
                  </div>
                  <p className="text-xs text-slate-500 mt-2">
                    The invited user will receive an email with a link to sign up and automatically join as a member.
                  </p>
                </div>

                <div className="flex space-x-4 pt-4">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => setShowInviteForm(false)}
                    className="flex-1"
                    disabled={inviting}
                  >
                    Cancel
                  </Button>
                  <Button
                    type="submit"
                    className="flex-1 bg-blue-600 hover:bg-blue-700 text-white"
                    disabled={inviting}
                  >
                    {inviting ? 'Sending...' : 'Send Invitation'}
                  </Button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Cancel Confirmation Modal */}
        {confirmCancel.show && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-2xl p-6 max-w-md w-full">
              <div className="mb-6">
                <div className="flex items-center justify-center w-12 h-12 bg-red-100 rounded-full mx-auto mb-4">
                  <XCircle className="h-6 w-6 text-red-600" />
                </div>
                <h3 className="text-xl font-semibold text-slate-900 text-center mb-2">
                  Cancel Invitation?
                </h3>
                <p className="text-slate-600 text-center">
                  Are you sure you want to cancel the invitation sent to{' '}
                  <span className="font-medium">{confirmCancel.email}</span>?
                </p>
              </div>

              <div className="flex space-x-3">
                <Button
                  variant="outline"
                  onClick={() => setConfirmCancel({ show: false, invitationId: null, email: '' })}
                  className="flex-1"
                >
                  No, Keep It
                </Button>
                <Button
                  onClick={handleCancelInvitation}
                  className="flex-1 bg-red-600 hover:bg-red-700 text-white"
                >
                  Yes, Cancel
                </Button>
              </div>
            </div>
          </div>
        )}

        {/* Current Users */}
        <div className="bg-white rounded-xl border border-slate-200 mb-8">
          <div className="p-6 border-b border-slate-200">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-slate-900">Team Members</h2>
            </div>
            
            {/* Search and Filter */}
            <div className="flex items-center space-x-4">
              <div className="relative flex-1 max-w-sm">
                <Search className="absolute left-3 top-3 h-4 w-4 text-slate-400" />
                <Input
                  placeholder="Search users..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
              <Select value={roleFilter} onValueChange={(value: any) => setRoleFilter(value)}>
                <SelectTrigger className="w-40">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Roles</SelectItem>
                  <SelectItem value="admin">Admins</SelectItem>
                  <SelectItem value="member">Members</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="divide-y divide-slate-200">
            {filteredUsers.map((user: any) => (
              <div key={user.id} className="p-6 flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center">
                    <span className="text-sm font-bold text-white">
                      {user.firstName.charAt(0)}
                    </span>
                  </div>
                  <div>
                    <h3 className="font-semibold text-slate-900">
                      {user.firstName} {user.lastName}
                    </h3>
                    <p className="text-sm text-slate-600">{user.email}</p>
                    <div className="flex items-center space-x-2 mt-1">
                      <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                        user.role === 'admin' 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-blue-100 text-blue-800'
                      }`}>
                        {user.role === 'admin' ? 'Administrator' : 'Member'}
                      </span>
                      <CheckCircle className="h-4 w-4 text-green-600" />
                      <span className="text-xs text-slate-500">Active</span>
                    </div>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <Button variant="ghost" size="sm">
                    <Edit className="h-4 w-4" />
                  </Button>
                  {user.id !== organization?.adminUserId && (
                    <Button variant="ghost" size="sm" className="text-red-600 hover:text-red-700">
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Pending Invitations */}
        <div className="bg-white rounded-xl border border-slate-200">
          <div className="p-6 border-b border-slate-200">
            <h2 className="text-xl font-semibold text-slate-900">Pending Invitations</h2>
          </div>
          
          <div className="divide-y divide-slate-200">
            {realInvitations.length > 0 ? (
              realInvitations.map((invitation) => (
                <div key={invitation.id} className="p-6 flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div className="w-10 h-10 bg-amber-100 rounded-full flex items-center justify-center">
                      <Clock className="h-5 w-5 text-amber-600" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-slate-900">
                        {invitation.email}
                      </h3>
                      <p className="text-sm text-slate-600">Invited by {invitation.invited_by_name}</p>
                      <div className="flex items-center space-x-2 mt-1">
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                          Member (Auto-assigned)
                        </span>
                        <span className="text-xs text-slate-500">
                          Expires: {new Date(invitation.expires_at).toLocaleDateString()}
                        </span>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Button 
                      variant="ghost" 
                      size="sm" 
                      className="text-red-600 hover:text-red-700"
                      onClick={() => {
                        setConfirmCancel({
                          show: true,
                          invitationId: invitation.id,
                          email: invitation.email
                        })
                      }}
                    >
                      <XCircle className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              ))
            ) : (
              <div className="p-6 text-center text-slate-500">
                No pending invitations
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}