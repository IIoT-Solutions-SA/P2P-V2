export interface User {
  id: string
  email: string
  firstName: string
  lastName: string
  role: 'admin' | 'member'
  title: string
  organizationId: string
  avatar?: string
  profilePictureUrl?: string
  isActive: boolean
  lastLogin?: Date
  createdAt: Date
  company?: string
  location?: string
  industrySector?: string
  expertiseTags?: string[]
}

export interface Organization {
  id: string
  name: string
  domain: string
  industry: string
  size: 'startup' | 'small' | 'medium' | 'large' | 'enterprise'
  country: string
  city: string
  logo?: string
  isActive: boolean
  createdAt: Date
  adminUserId: string
}

export interface AuthState {
  user: User | null
  organization: Organization | null
  isAuthenticated: boolean
  isLoading: boolean
}

export interface LoginCredentials {
  email: string
  password: string
}

export interface SignupData {
  firstName: string
  lastName: string
  email: string
  password: string
  title: string
  organizationName: string
  industry: string
  organizationSize: string
  country: string
  city: string
  inviteToken?: string
  isInvited?: boolean
  role?: string
}

export interface InviteUserData {
  email: string
  firstName: string
  lastName: string
  role: 'admin' | 'member'
}

export interface PendingInvitation {
  id: string
  email: string
  firstName: string
  lastName: string
  role: 'admin' | 'member'
  organizationId: string
  invitedBy: string
  status: 'pending' | 'accepted' | 'expired'
  expiresAt: Date
  createdAt: Date
}

export interface UpdateProfileData {
  firstName?: string
  lastName?: string
  title?: string
  location?: string
  expertiseTags?: string[]
}