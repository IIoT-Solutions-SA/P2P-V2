import React, { useState } from 'react';
import { User } from 'lucide-react';

interface AvatarProps {
  src?: string | null;
  alt?: string;
  name?: string;
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
}

export const Avatar: React.FC<AvatarProps> = ({
  src,
  alt,
  name,
  size = 'md',
  className = '',
}) => {
  const [imageError, setImageError] = useState(false);
  const [imageLoading, setImageLoading] = useState(true);

  // Size mappings
  const sizeClasses = {
    xs: 'w-6 h-6 text-xs',
    sm: 'w-8 h-8 text-sm',
    md: 'w-10 h-10 text-base',
    lg: 'w-12 h-12 text-lg',
    xl: 'w-16 h-16 text-xl',
  };

  // Get initials from name
  const getInitials = (name?: string): string => {
    if (!name) return '?';
    const parts = name.trim().split(' ');
    if (parts.length >= 2) {
      return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
    }
    return name.slice(0, 2).toUpperCase();
  };

  const handleImageLoad = () => {
    setImageLoading(false);
  };

  const handleImageError = () => {
    setImageError(true);
    setImageLoading(false);
  };

  // Determine if we should show image or fallback
  const showImage = src && !imageError;
  const initials = getInitials(name);

  return (
    <div
      className={`relative inline-flex items-center justify-center rounded-full bg-gradient-to-br from-blue-500 to-purple-600 text-white font-semibold overflow-hidden ${sizeClasses[size]} ${className}`}
      title={alt || name}
    >
      {showImage ? (
        <>
          <img
            src={src}
            alt={alt || name || 'Avatar'}
            className={`w-full h-full object-cover object-center ${imageLoading ? 'opacity-0' : 'opacity-100'} transition-opacity duration-200`}
            onLoad={handleImageLoad}
            onError={handleImageError}
          />
          {imageLoading && (
            <div className="absolute inset-0 flex items-center justify-center">
              <User className="w-1/2 h-1/2 text-white opacity-50" />
            </div>
          )}
        </>
      ) : (
        <span className="select-none">{initials}</span>
      )}
    </div>
  );
};
