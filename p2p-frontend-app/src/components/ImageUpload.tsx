import React, { useState, useRef, useCallback } from 'react'
import { Upload, X, FileImage, AlertCircle } from 'lucide-react'
import { Button } from '@/components/ui/button'

interface ImageUploadProps {
  onImagesUpdate: (files: File[]) => void
  maxImages?: number
  maxSizePerImage?: number // in MB
  acceptedTypes?: string[]
}

interface ImagePreview {
  file: File
  url: string
  id: string
}

export default function ImageUpload({ 
  onImagesUpdate, 
  maxImages = 5,
  maxSizePerImage = 5,
  acceptedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
}: ImageUploadProps) {
  const [images, setImages] = useState<ImagePreview[]>([])
  const [dragActive, setDragActive] = useState(false)
  const [uploadProgress, setUploadProgress] = useState<Record<string, number>>({})
  const [errors, setErrors] = useState<string[]>([])
  const fileInputRef = useRef<HTMLInputElement>(null)

  const validateFile = (file: File): string | null => {
    // Check file type
    if (!acceptedTypes.includes(file.type)) {
      return `Invalid file type. Only ${acceptedTypes.join(', ')} are allowed.`
    }

    // Check file size
    const fileSizeMB = file.size / (1024 * 1024)
    if (fileSizeMB > maxSizePerImage) {
      return `File size must be less than ${maxSizePerImage}MB.`
    }

    return null
  }

  const processFiles = useCallback((files: FileList | File[]) => {
    const fileArray = Array.from(files)
    const newErrors: string[] = []
    const validFiles: File[] = []

    // Check total number of images
    if (images.length + fileArray.length > maxImages) {
      newErrors.push(`Maximum ${maxImages} images allowed.`)
      return
    }

    fileArray.forEach((file) => {
      const error = validateFile(file)
      if (error) {
        newErrors.push(`${file.name}: ${error}`)
      } else {
        validFiles.push(file)
      }
    })

    if (newErrors.length > 0) {
      setErrors(newErrors)
      setTimeout(() => setErrors([]), 5000)
      return
    }

    // Create previews for valid files
    const newPreviews: ImagePreview[] = validFiles.map((file) => ({
      file,
      url: URL.createObjectURL(file),
      id: Math.random().toString(36).substr(2, 9)
    }))

    // Simulate upload progress
    newPreviews.forEach((preview) => {
      setUploadProgress(prev => ({ ...prev, [preview.id]: 0 }))
      
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          const currentProgress = prev[preview.id] || 0
          if (currentProgress >= 100) {
            clearInterval(progressInterval)
            return prev
          }
          return { ...prev, [preview.id]: currentProgress + 10 }
        })
      }, 100)
    })

    const updatedImages = [...images, ...newPreviews]
    setImages(updatedImages)
    onImagesUpdate(updatedImages.map(img => img.file))
    setErrors([])
  }, [images, maxImages, maxSizePerImage, acceptedTypes, onImagesUpdate])

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      processFiles(e.dataTransfer.files)
    }
  }, [processFiles])

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      processFiles(e.target.files)
    }
    // Reset input value to allow selecting the same file again
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const removeImage = (id: string) => {
    const updatedImages = images.filter(img => img.id !== id)
    setImages(updatedImages)
    onImagesUpdate(updatedImages.map(img => img.file))
    
    // Clean up object URL
    const imageToRemove = images.find(img => img.id === id)
    if (imageToRemove) {
      URL.revokeObjectURL(imageToRemove.url)
    }

    // Remove from upload progress
    setUploadProgress(prev => {
      const { [id]: removed, ...rest } = prev
      return rest
    })
  }

  const openFileDialog = () => {
    fileInputRef.current?.click()
  }

  // Cleanup object URLs on unmount
  React.useEffect(() => {
    return () => {
      images.forEach(img => URL.revokeObjectURL(img.url))
    }
  }, [])

  return (
    <div className="image-upload-container">
      {/* Error Messages */}
      {errors.length > 0 && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-center space-x-2 mb-2">
            <AlertCircle className="h-4 w-4 text-red-600" />
            <span className="font-medium text-red-800">Upload Errors:</span>
          </div>
          <ul className="list-disc list-inside text-sm text-red-700 space-y-1">
            {errors.map((error, index) => (
              <li key={index}>{error}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Upload Area */}
      <div
        className={`upload-area ${dragActive ? 'drag-active' : ''} ${images.length >= maxImages ? 'disabled' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={images.length < maxImages ? openFileDialog : undefined}
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept={acceptedTypes.join(',')}
          onChange={handleFileInput}
          className="hidden"
          disabled={images.length >= maxImages}
        />

        <div className="upload-content">
          {images.length >= maxImages ? (
            <>
              <FileImage className="h-12 w-12 text-slate-400 mb-4" />
              <p className="text-slate-500 font-medium">Maximum images reached</p>
              <p className="text-sm text-slate-400">{maxImages} images uploaded</p>
            </>
          ) : (
            <>
              <Upload className="h-12 w-12 text-blue-500 mb-4" />
              <p className="text-slate-700 font-medium mb-2">
                Drop images here or click to browse
              </p>
              <p className="text-sm text-slate-500 mb-4">
                Upload up to {maxImages} images • Max {maxSizePerImage}MB each
              </p>
              <div className="flex flex-wrap gap-2 justify-center">
                {acceptedTypes.map((type) => (
                  <span key={type} className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded-full">
                    {type.split('/')[1].toUpperCase()}
                  </span>
                ))}
              </div>
            </>
          )}
        </div>
      </div>

      {/* Image Previews */}
      {images.length > 0 && (
        <div className="mt-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-slate-900">
              Uploaded Images ({images.length}/{maxImages})
            </h3>
            {images.length < maxImages && (
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={openFileDialog}
                className="flex items-center space-x-2"
              >
                <Upload className="h-4 w-4" />
                <span>Add More</span>
              </Button>
            )}
          </div>

          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {images.map((image) => (
              <div key={image.id} className="image-preview-card">
                <div className="relative">
                  <img
                    src={image.url}
                    alt={image.file.name}
                    className="w-full h-32 object-cover rounded-lg"
                  />
                  
                  {/* Upload Progress */}
                  {uploadProgress[image.id] !== undefined && uploadProgress[image.id] < 100 && (
                    <div className="absolute inset-0 bg-black bg-opacity-50 rounded-lg flex items-center justify-center">
                      <div className="text-center text-white">
                        <div className="w-12 h-12 border-4 border-white border-t-transparent rounded-full animate-spin mb-2"></div>
                        <p className="text-sm">{uploadProgress[image.id]}%</p>
                      </div>
                    </div>
                  )}

                  {/* Remove Button */}
                  <button
                    type="button"
                    onClick={() => removeImage(image.id)}
                    className="absolute top-2 right-2 w-6 h-6 bg-red-500 hover:bg-red-600 text-white rounded-full flex items-center justify-center transition-colors"
                  >
                    <X className="h-3 w-3" />
                  </button>

                  {/* Upload Complete Indicator */}
                  {uploadProgress[image.id] === 100 && (
                    <div className="absolute top-2 left-2 w-6 h-6 bg-green-500 text-white rounded-full flex items-center justify-center">
                      <svg className="h-3 w-3" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                    </div>
                  )}
                </div>

                <div className="mt-2">
                  <p className="text-sm font-medium text-slate-700 truncate">
                    {image.file.name}
                  </p>
                  <p className="text-xs text-slate-500">
                    {(image.file.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <style>{`
        .upload-area {
          border: 2px dashed #d1d5db;
          border-radius: 12px;
          padding: 48px 24px;
          text-align: center;
          background: #fafafa;
          cursor: pointer;
          transition: all 0.3s ease;
        }

        .upload-area:hover:not(.disabled) {
          border-color: #3b82f6;
          background: #f8fafc;
        }

        .upload-area.drag-active {
          border-color: #3b82f6;
          background: #eff6ff;
          transform: scale(1.02);
        }

        .upload-area.disabled {
          background: #f1f5f9;
          border-color: #e2e8f0;
          cursor: not-allowed;
        }

        .upload-content {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
        }

        .image-preview-card {
          background: white;
          border: 1px solid #e2e8f0;
          border-radius: 12px;
          padding: 8px;
          transition: all 0.2s ease;
        }

        .image-preview-card:hover {
          border-color: #3b82f6;
          box-shadow: 0 4px 12px rgba(59, 130, 246, 0.1);
        }
      `}</style>
    </div>
  )
}