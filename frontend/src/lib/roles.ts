export type UserRole = "ADMIN" | "PHOTOGRAPHER" | "CLUB_MEMBER" | "VIEWER"

export const ROLE_LABELS: Record<UserRole, string> = {
  ADMIN: "Admin",
  PHOTOGRAPHER: "Photographer",
  CLUB_MEMBER: "Club Member",
  VIEWER: "Viewer",
}

export const ALL_ROLES: UserRole[] = [
  "ADMIN",
  "PHOTOGRAPHER",
  "CLUB_MEMBER",
  "VIEWER",
]

export function isAdmin(role?: UserRole) {
  return role === "ADMIN"
}

export function canUploadMedia(role?: UserRole) {
  return role === "ADMIN" || role === "PHOTOGRAPHER" || role === "CLUB_MEMBER"
}
