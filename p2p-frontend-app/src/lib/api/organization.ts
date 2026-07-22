import { api } from "@/lib/api/client"

export interface Invitation {
  id: string
  email: string
  token?: string
  invited_by_id?: string
  invited_by_email?: string
  invited_by_name?: string
  expires_at?: string
  used?: boolean
  used_at?: string | null
  created_at?: string
}

export const organizationApi = {
  invitations: () => api.get<{ invitations: Invitation[]; total: number }>("/api/v1/invites/all"),
  pendingInvitations: () => api.get<{ invitations: Invitation[]; total: number }>("/api/v1/invites/pending"),
  invite: (email: string) => api.post<Invitation>("/api/v1/invites/send", { email }),
  cancelInvitation: (invitationId: string) => api.delete<{ message: string }>(`/api/v1/invites/${invitationId}`),
}
