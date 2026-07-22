import React, { useEffect, useRef, useState } from "react"
import { Camera, ImagePlus, Loader2, X } from "lucide-react"

interface ProfilePictureEditorProps {
  currentImageUrl?: string
  onImageUpload: (file: File) => Promise<void>
  size?: "sm" | "md" | "lg"
  disabled?: boolean
  showUploadButton?: boolean
}

export const ProfilePictureEditor: React.FC<ProfilePictureEditorProps> = React.memo(({
  currentImageUrl,
  onImageUpload,
  size = "md",
  disabled = false,
  showUploadButton = true,
}) => {
  const [isUploading, setIsUploading] = useState(false)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const sizeClasses = { sm: "size-16", md: "size-24", lg: "size-32" }
  const displayImageUrl = previewUrl || currentImageUrl

  const openFileDialog = () => {
    if (!disabled && !isUploading) fileInputRef.current?.click()
  }

  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return
    if (!["image/jpeg", "image/png", "image/webp"].includes(file.type)) {
      setError("Choose a JPEG, PNG, or WebP image.")
      return
    }
    if (file.size > 5 * 1024 * 1024) {
      setError("The image must be smaller than 5 MB.")
      return
    }

    setError(null)
    setIsUploading(true)
    const nextPreview = URL.createObjectURL(file)
    setPreviewUrl((current) => {
      if (current) URL.revokeObjectURL(current)
      return nextPreview
    })
    try {
      await onImageUpload(file)
    } catch {
      URL.revokeObjectURL(nextPreview)
      setPreviewUrl(null)
      setError("The image could not be uploaded. Please try again.")
    } finally {
      setIsUploading(false)
      event.target.value = ""
    }
  }

  const removePreview = () => {
    if (previewUrl) URL.revokeObjectURL(previewUrl)
    setPreviewUrl(null)
    setError(null)
  }

  useEffect(() => () => { if (previewUrl) URL.revokeObjectURL(previewUrl) }, [previewUrl])

  return (
    <div className="flex flex-col items-center gap-3">
      <input ref={fileInputRef} type="file" accept="image/jpeg,image/png,image/webp" onChange={handleFileSelect} className="sr-only" disabled={disabled || isUploading} />

      <div className="relative">
        <div className={`${sizeClasses[size]} grid place-items-center overflow-hidden rounded-full border border-[var(--peer-line)] bg-[#eeeee9] shadow-[0_0_0_5px_white,0_0_0_6px_var(--peer-line)]`}>
          {displayImageUrl ? <img src={displayImageUrl} alt="Profile" className="size-full object-cover" /> : <Camera className="size-8 text-[#89979a]" />}
          {isUploading ? <span className="absolute inset-0 grid place-items-center rounded-full bg-[rgba(6,31,45,.68)]"><Loader2 className="size-6 animate-spin text-white" /></span> : null}
        </div>

        {showUploadButton && displayImageUrl && !isUploading ? (
          <button type="button" onClick={openFileDialog} disabled={disabled} className="absolute bottom-0 right-0 grid size-9 place-items-center border-2 border-white bg-[var(--peer-teal)] text-white shadow-sm transition hover:bg-[#17636a] disabled:cursor-not-allowed disabled:opacity-50" title="Change profile picture" aria-label="Change profile picture">
            <ImagePlus className="size-4" />
          </button>
        ) : null}

        {previewUrl && !isUploading ? (
          <button type="button" onClick={removePreview} className="absolute -right-2 -top-2 grid size-7 place-items-center border-2 border-white bg-[var(--peer-navy)] text-white" title="Remove preview" aria-label="Remove preview"><X className="size-3.5" /></button>
        ) : null}
      </div>

      {showUploadButton && !displayImageUrl && !isUploading ? (
        <button type="button" onClick={openFileDialog} disabled={disabled} className="inline-flex min-h-10 items-center gap-2 border border-[var(--peer-teal)] bg-[var(--peer-teal-soft)] px-4 text-xs font-bold text-[var(--peer-teal)] transition hover:bg-[#d6ece7] disabled:cursor-not-allowed disabled:opacity-50">
          <ImagePlus className="size-4" /><span>Choose photo</span>
        </button>
      ) : null}

      {isUploading ? <p className="text-xs font-semibold text-[var(--peer-teal)]">Uploading photo…</p> : null}
      {error ? <p className="max-w-48 text-center text-xs leading-5 text-[var(--peer-danger)]">{error}</p> : null}
      {showUploadButton ? <p className="max-w-44 text-center text-[11px] leading-4 text-[var(--peer-muted)]">JPEG, PNG, or WebP · Maximum 5 MB</p> : null}
    </div>
  )
})

ProfilePictureEditor.displayName = "ProfilePictureEditor"
