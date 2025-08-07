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
  User, 
  Shield, 
  Clock, 
  CheckCircle, 
  XCircle,
  Search,
  Filter,
  MoreHorizontal,
  Edit,
  Trash2,
  ArrowLeft,
  Home
} from "lucide-react"
import { useAuth } from '@/contexts/AuthContext'
import { api } from '@/services/api'
import type { InviteUserData, PendingInvitation } from '@/types/auth'
import { type Page } from '@/components/Navigation'

interface UserManagementProps {
  onPageChange?: (page: Page) => void
}

interface UserData {
  id: string
  email: string
  firstName: string
  lastName: string
  role: 'admin' | 'member'
  status: string
  createdAt: string
  department?: string
  jobTitle?: string
}

export default function UserManagement({ onPageChange }: UserManagementProps) {
  const { user, organization } = useAuth()
  const [showInviteForm, setShowInviteForm] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [roleFilter, setRoleFilter] = useState<'all' | 'admin' | 'member'>('all')
  const [users, setUsers] = useState<UserData[]>([])
  const [pendingInvitations, setPendingInvitations] = useState<PendingInvitation[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  
  const [inviteData, setInviteData] = useState<InviteUserData>({
    email: '',
    firstName: '',
    lastName: '',
    role: 'member'
  })

  // Fetch users and invitations on mount
  useEffect(() => {
    fetchOrganizationData()
  }, [])

  const fetchOrganizationData = async () => {
    try {
      setIsLoading(true)
      setError(null)
      
      // Fetch organization users
      const usersResponse = await api.get('/api/v1/users/organization')
      if (usersResponse.data.users) {
        const formattedUsers = usersResponse.data.users.map((u: any) => ({
          id: u.id,
          email: u.email,
          firstName: u.first_name || u.firstName,
          lastName: u.last_name || u.lastName,
          role: u.role,
          status: u.status || 'active',
          createdAt: u.created_at || u.createdAt,
          department: u.department,
          jobTitle: u.job_title || u.jobTitle
        }))
        setUsers(formattedUsers)
      }
      
      // Fetch pending invitations
      const invitationsResponse = await api.get('/api/v1/invitations')
      if (invitationsResponse.data.invitations) {
        setPendingInvitations(invitationsResponse.data.invitations.map((inv: any) => ({
          id: inv.id,
          email: inv.email,
          firstName: inv.first_name || inv.firstName || '',
          lastName: inv.last_name || inv.lastName || '',
          role: inv.role,
          organizationId: inv.organization_id,
          invitedBy: inv.invited_by,
          status: inv.status,
          expiresAt: new Date(inv.expires_at),
          createdAt: new Date(inv.created_at)
        })))
      }
    } catch (err: any) {
      console.error('Failed to fetch organization data:', err)
      setError('Failed to load users and invitations')
      // Use temporary mock data as fallback
      setPendingInvitations([
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
    } finally {
      setIsLoading(false)
    }
  }

  // Filter users
  const filteredUsers = users.filter(u => {
    const matchesSearch = `${u.firstName} ${u.lastName} ${u.email}`.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesRole = roleFilter === 'all' || u.role === roleFilter
    return matchesSearch && matchesRole
  })

  const handleInviteUser = async (e: React.FormEvent) => {
    e.preventDefault()
    
    try {
      // Send invitation via API
      const response = await api.post('/api/v1/invitations/send', {
        email: inviteData.email,
        first_name: inviteData.firstName,
        last_name: inviteData.lastName,
        role: inviteData.role
      })
      
      if (response.data.invitation) {
        // Add to pending invitations list
        setPendingInvitations(prev => [...prev, {
          id: response.data.invitation.id,
          email: response.data.invitation.email,
          firstName: response.data.invitation.first_name || '',
          lastName: response.data.invitation.last_name || '',
          role: response.data.invitation.role,
          organizationId: response.data.invitation.organization_id,
          invitedBy: user?.id || '',
          status: 'pending',
          expiresAt: new Date(response.data.invitation.expires_at),
          createdAt: new Date(response.data.invitation.created_at)
        }])
      }
      
      // Reset form
      setInviteData({
        email: '',
        firstName: '',
        lastName: '',
        role: 'member'
      })
      setShowInviteForm(false)
    } catch (err: any) {
      console.error('Failed to send invitation:', err)
      setError(err.response?.data?.detail || 'Failed to send invitation')
    }
  }

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
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      <div className="container mx-auto px-6 py-8">
        
        {/* Back to Dashboard Button */}
        <Button 
          variant="ghost" 
          className="mb-6"
          onClick={() => onPageChange?.('dashboard')}
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
                  <p className="text-2xl font-bold text-slate-900">{organizationUsers.length}</p>
                </div>
                <Users className="h-8 w-8 text-blue-600" />
              </div>
            </div>
            <div className="bg-white rounded-xl p-6 border border-slate-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-slate-600 text-sm">Pending Invites</p>
                  <p className="text-2xl font-bold text-slate-900">{pendingInvitations.length}</p>
                </div>
                <Clock className="h-8 w-8 text-amber-600" />
              </div>
            </div>
            <div className="bg-white rounded-xl p-6 border border-slate-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-slate-600 text-sm">Admins</p>
                  <p className="text-2xl font-bold text-slate-900">
                    {organizationUsers.filter(u => u.role === 'admin').length}
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
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">
                      First Name
                    </label>
                    <Input
                      type="text"
                      placeholder="Omar"
                      value={inviteData.firstName}
                      onChange={(e) => setInviteData(prev => ({ ...prev, firstName: e.target.value }))}
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">
                      Last Name
                    </label>
                    <Input
                      type="text"
                      placeholder="Salem"
                      value={inviteData.lastName}
                      onChange={(e) => setInviteData(prev => ({ ...prev, lastName: e.target.value }))}
                      required
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Email Address
                  </label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-3 h-5 w-5 text-slate-400" />
                    <Input
                      type="email"
                      placeholder="omar.salem@advanced-electronics.com"
                      value={inviteData.email}
                      onChange={(e) => setInviteData(prev => ({ ...prev, email: e.target.value }))}
                      className="pl-10"
                      required
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Role
                  </label>
                  <Select 
                    value={inviteData.role} 
                    onValueChange={(value: 'admin' | 'member') => setInviteData(prev => ({ ...prev, role: value }))}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="member">Team Member</SelectItem>
                      <SelectItem value="admin">Organization Admin</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="flex space-x-4 pt-4">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => setShowInviteForm(false)}
                    className="flex-1"
                  >
                    Cancel
                  </Button>
                  <Button
                    type="submit"
                    className="flex-1 bg-blue-600 hover:bg-blue-700 text-white"
                  >
                    Send Invitation
                  </Button>
                </div>
              </form>
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
            {filteredUsers.map((user) => (
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
            {pendingInvitations.map((invitation) => (
              <div key={invitation.id} className="p-6 flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div className="w-10 h-10 bg-amber-100 rounded-full flex items-center justify-center">
                    <Clock className="h-5 w-5 text-amber-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-slate-900">
                      {invitation.firstName} {invitation.lastName}
                    </h3>
                    <p className="text-sm text-slate-600">{invitation.email}</p>
                    <div className="flex items-center space-x-2 mt-1">
                      <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                        invitation.role === 'admin' 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-blue-100 text-blue-800'
                      }`}>
                        {invitation.role === 'admin' ? 'Administrator' : 'Member'}
                      </span>
                      <span className="text-xs text-slate-500">
                        Expires in {Math.ceil((invitation.expiresAt.getTime() - Date.now()) / (1000 * 60 * 60 * 24))} days
                      </span>
                    </div>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <Button variant="outline" size="sm">
                    Resend
                  </Button>
                  <Button variant="ghost" size="sm" className="text-red-600 hover:text-red-700">
                    <XCircle className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}