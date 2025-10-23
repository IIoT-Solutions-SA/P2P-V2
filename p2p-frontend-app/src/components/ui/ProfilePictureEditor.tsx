import React, { useState, useRef } from 'react';
import { Camera, Upload, X, Loader } from 'lucide-react';

interface ProfilePictureEditorProps {
  currentImageUrl?: string;
  onImageUpload: (file: File) => Promise<void>;
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  showUploadButton?: boolean;
}

export const ProfilePictureEditor: React.FC<ProfilePictureEditorProps> = React.memo(({
  currentImageUrl,
  onImageUpload,
  size = 'md',
  disabled = false,
  showUploadButton = true
}) => {
  const [isUploading, setIsUploading] = useState(false);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const sizeClasses = {
    sm: 'w-16 h-16',
    md: 'w-24 h-24',
    lg: 'w-32 h-32'
  };

  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    console.log('handleFileSelect triggered', event.target.files);
    const file = event.target.files?.[0];
    if (!file) {
      console.log('No file selected');
      return;
    }

    console.log('File selected:', file.name, file.type, file.size);

    // Validate file
    const allowedTypes = ['image/jpeg', 'image/png', 'image/webp'];
    if (!allowedTypes.includes(file.type)) {
      console.log('Invalid file type:', file.type);
      setError('Please select a valid image file (JPEG, PNG, or WebP)');
      return;
    }

    const maxSize = 5 * 1024 * 1024; // 5MB
    if (file.size > maxSize) {
      setError('Image must be smaller than 5MB');
      return;
    }

    setError(null);
    setIsUploading(true);

    try {
      // Create preview
      const url = URL.createObjectURL(file);
      setPreviewUrl(url);

      // Upload file
      await onImageUpload(file);

    } catch (err) {
      console.error('Upload error:', err);
      setError('Failed to upload image. Please try again.');

      // Clean up preview on error
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
        setPreviewUrl(null);
      }
    } finally {
      setIsUploading(false);
    }
  };

  const openFileDialog = () => {
    console.log('openFileDialog called', { disabled, isUploading, hasRef: !!fileInputRef.current });
    if (!disabled && !isUploading && fileInputRef.current) {
      console.log('Triggering file input click');
      fileInputRef.current.click();
    }
  };

  const removePreview = () => {
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
      setPreviewUrl(null);
    }
    setError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  React.useEffect(() => {
    console.log('ProfilePictureEditor mounted', { currentImageUrl, disabled });
    return () => {
      console.log('ProfilePictureEditor unmounting');
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
      }
    };
  }, [previewUrl]);

  const displayImageUrl = previewUrl || currentImageUrl;

  return (
    <div className="flex flex-col items-center space-y-4">
      {/* Hidden file input */}
      <input
        ref={fileInputRef}
        type="file"
        accept="image/jpeg,image/png,image/webp"
        onChange={handleFileSelect}
        className="hidden"
        disabled={disabled || isUploading}
      />

      {/* Profile picture display */}
      <div className="relative">
        <div
          className={`
            ${sizeClasses[size]} rounded-full overflow-hidden border-4 border-white shadow-lg
            ${!displayImageUrl ? 'bg-gray-200 flex items-center justify-center' : ''}
          `}
        >
          {displayImageUrl ? (
            <img
              src={displayImageUrl}
              alt="Profile"
              className="w-full h-full object-cover"
            />
          ) : (
            <Camera className="w-8 h-8 text-gray-400" />
          )}

          {/* Loading overlay */}
          {isUploading && (
            <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center rounded-full">
              <Loader className="w-6 h-6 text-white animate-spin" />
            </div>
          )}
        </div>

        {/* Upload button overlay */}
        {showUploadButton && !isUploading && (
          <button
            type="button"
            onClick={openFileDialog}
            disabled={disabled}
            className={`
              absolute -bottom-2 -right-2 p-2 bg-blue-500 text-white rounded-full shadow-lg
              hover:bg-blue-600 transition-colors
              ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
            `}
            title="Change profile picture"
          >
            <Upload className="w-4 h-4" />
          </button>
        )}

        {/* Remove preview button */}
        {previewUrl && !isUploading && (
          <button
            type="button"
            onClick={removePreview}
            className="absolute -top-2 -right-2 p-1 bg-red-500 text-white rounded-full shadow-lg hover:bg-red-600 transition-colors"
            title="Remove preview"
          >
            <X className="w-3 h-3" />
          </button>
        )}
      </div>

      {/* Upload button (alternative to overlay) */}
      {showUploadButton && !displayImageUrl && !isUploading && (
        <button
          type="button"
          onClick={openFileDialog}
          disabled={disabled}
          className={`
            px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors
            flex items-center space-x-2
            ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
          `}
        >
          <Upload className="w-4 h-4" />
          <span>Upload Photo</span>
        </button>
      )}

      {/* Error message */}
      {error && (
        <div className="text-sm text-red-600 text-center max-w-xs">
          {error}
        </div>
      )}

      {/* Upload status */}
      {isUploading && (
        <div className="text-sm text-blue-600 text-center">
          Uploading...
        </div>
      )}

      {/* File requirements */}
      {showUploadButton && (
        <div className="text-xs text-gray-500 text-center max-w-xs">
          JPEG, PNG, or WebP • Max 5MB
        </div>
      )}
    </div>
  );
});

ProfilePictureEditor.displayName = 'ProfilePictureEditor';