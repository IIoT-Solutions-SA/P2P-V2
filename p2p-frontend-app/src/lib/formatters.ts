export function formatOrganizationName(value?: string | null, fallback = "Organization") {
  const name = value?.trim()
  if (!name) return fallback

  const compact = name.replace(/[^a-z0-9]/gi, "").toLowerCase()
  if (compact === "iiotsolutions") return "IIoT Solutions"

  return name
}
