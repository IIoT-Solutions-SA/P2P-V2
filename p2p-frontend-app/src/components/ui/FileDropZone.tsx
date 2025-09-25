import React, { useState, DragEvent } from 'react';
import { Upload, File, AlertCircle, X } from 'lucide-react';

interface SelectedFile {
  file: File;
  id: string;
  preview?: string;
}

interface FileDropZoneProps {
  onFilesSelect: (files: File[]) => void;
  maxFiles?: number;
  maxSize?: number; // in bytes
  acceptedTypes?: string[];
  allowMultiple?: boolean;
  disabled?: boolean;
  className?: string;
  showPreview?: boolean;
}

export const FileDropZone: React.FC<FileDropZoneProps> = ({
  onFilesSelect,
  maxFiles = 10,
  maxSize = 50 * 1024 * 1024, // 50MB default
  acceptedTypes = ['image/jpeg', 'image/png', 'image/webp', 'video/mp4', 'video/webm'],
  allowMultiple = true,
  disabled = false,
  className = '',
  showPreview = true
}) => {
  const [selectedFiles, setSelectedFiles] = useState<SelectedFile[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const validateFile = (file: File): string | null => {
    // Check if file type is accepted (support wildcards like 'image/*')
    const isAccepted = acceptedTypes.some(acceptedType => {
      if (acceptedType.endsWith('/*')) {
        const baseType = acceptedType.slice(0, -2);
        return file.type.startsWith(baseType + '/');
      }
      return acceptedType === file.type;
    });

    if (!isAccepted) {
      return `Invalid file type: ${file.name}. Accepted types: ${acceptedTypes.join(', ')}`;
    }

    if (file.size > maxSize) {
      const maxSizeMB = maxSize / (1024 * 1024);
      return `File too large: ${file.name}. Maximum size: ${maxSizeMB}MB`;
    }

    return null;
  };

  const generateFileId = () => Math.random().toString(36).substr(2, 9);

  const createPreviewUrl = (file: File): string | undefined => {
    if (file.type.startsWith('image/')) {
      return URL.createObjectURL(file);
    }
    return undefined;
  };

  const addFiles = (files: FileList | File[]) => {
    const fileArray = Array.from(files);
    const newFiles: SelectedFile[] = [];
    let errors: string[] = [];

    // Check total file count
    if (selectedFiles.length + fileArray.length > maxFiles) {
      errors.push(`Too many files. Maximum ${maxFiles} files allowed.`);
      setError(errors[0]);
      return;
    }

    fileArray.forEach(file => {
      const validationError = validateFile(file);
      if (validationError) {
        errors.push(validationError);
        return;
      }

      const selectedFile: SelectedFile = {
        file,
        id: generateFileId(),
        preview: createPreviewUrl(file)
      };

      newFiles.push(selectedFile);
    });

    if (errors.length > 0) {
      setError(errors[0]);
      return;
    }

    setError(null);
    const updatedFiles = [...selectedFiles, ...newFiles];
    setSelectedFiles(updatedFiles);
    onFilesSelect(updatedFiles.map(sf => sf.file));
  };

  const removeFile = (id: string) => {
    setSelectedFiles(prev => {
      const fileToRemove = prev.find(f => f.id === id);
      if (fileToRemove && fileToRemove.preview) {
        URL.revokeObjectURL(fileToRemove.preview);
      }

      const updated = prev.filter(f => f.id !== id);
      onFilesSelect(updated.map(sf => sf.file));
      return updated;
    });

    setError(null);
  };

  const handleFileInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (files && files.length > 0) {
      addFiles(files);
    }
  };

  const handleDragEnter = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const files = e.dataTransfer.files;
    if (files.length > 0) {
      addFiles(files);
    }
  };

  const formatFileSize = (bytes: number) => {
    const mb = bytes / (1024 * 1024);
    return mb < 1 ? `${(bytes / 1024).toFixed(0)}KB` : `${mb.toFixed(1)}MB`;
  };

  const getFileTypeIcon = (file: File) => {
    if (file.type.startsWith('image/')) {
      return '🖼️';
    } else if (file.type.startsWith('video/')) {
      return '🎥';
    }
    return '📄';
  };

  // Clean up preview URLs when component unmounts
  React.useEffect(() => {
    return () => {
      selectedFiles.forEach(file => {
        if (file.preview) {
          URL.revokeObjectURL(file.preview);
        }
      });
    };
  }, []);

  return (
    <div className={`file-drop-zone ${className}`}>
      {/* Drop zone */}
      <div
        onDragEnter={handleDragEnter}
        onDragLeave={handleDragLeave}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
        className={`
          relative border-2 border-dashed rounded-lg p-6 text-center transition-colors
          ${isDragging
            ? 'border-blue-500 bg-blue-50'
            : 'border-gray-300 hover:border-gray-400'
          }
          ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
        `}
        onClick={() => !disabled && document.getElementById('file-input')?.click()}
      >
        <input
          id="file-input"
          type="file"
          multiple={allowMultiple}
          accept={acceptedTypes.join(',')}
          onChange={handleFileInputChange}
          className="hidden"
          disabled={disabled}
        />

        <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
        <p className="text-sm font-medium text-gray-900 mb-2">
          {isDragging ? 'Drop files here' : 'Click to upload or drag and drop'}
        </p>
        <p className="text-xs text-gray-500">
          {acceptedTypes.map(type => type.split('/')[1].toUpperCase()).join(', ')} •
          Max {maxSize / (1024 * 1024)}MB •
          {allowMultiple ? `Up to ${maxFiles} files` : '1 file'}
        </p>
      </div>

      {/* Error display */}
      {error && (
        <div className="mt-4 flex items-center text-sm text-red-600">
          <AlertCircle className="h-4 w-4 mr-2" />
          {error}
        </div>
      )}

      {/* Selected files preview */}
      {selectedFiles.length > 0 && (
        <div className="mt-6">
          <h4 className="text-sm font-medium text-gray-900 mb-3">
            Selected Files ({selectedFiles.length})
          </h4>

          {showPreview ? (
            /* Horizontal preview for modal contexts */
            <div className="flex flex-wrap gap-3">
              {selectedFiles.map((selectedFile) => (
                <div key={selectedFile.id} className="relative group">
                  <div className="w-20 h-20 bg-gray-100 rounded-lg overflow-hidden border flex-shrink-0">
                    {selectedFile.preview ? (
                      <img
                        src={selectedFile.preview}
                        alt={selectedFile.file.name}
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center text-4xl">
                        {getFileTypeIcon(selectedFile.file)}
                      </div>
                    )}

                    {/* Remove button */}
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        removeFile(selectedFile.id);
                      }}
                      className="absolute top-2 right-2 p-1 bg-red-500 text-white rounded-full opacity-0 group-hover:opacity-100 transition-opacity hover:bg-red-600"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </div>

                  <div className="mt-2 text-xs text-gray-600">
                    <p className="truncate" title={selectedFile.file.name}>
                      {selectedFile.file.name}
                    </p>
                    <p className="text-gray-400">
                      {formatFileSize(selectedFile.file.size)}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            /* List view */
            <div className="space-y-2">
              {selectedFiles.map((selectedFile) => (
                <div
                  key={selectedFile.id}
                  className="flex items-center justify-between p-3 bg-gray-50 rounded-lg border"
                >
                  <div className="flex items-center min-w-0">
                    <File className="h-8 w-8 text-gray-400 mr-3 flex-shrink-0" />
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {selectedFile.file.name}
                      </p>
                      <p className="text-xs text-gray-500">
                        {formatFileSize(selectedFile.file.size)} • {selectedFile.file.type}
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={() => removeFile(selectedFile.id)}
                    className="p-1 text-red-500 hover:text-red-700 flex-shrink-0"
                  >
                    <X className="h-4 w-4" />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};