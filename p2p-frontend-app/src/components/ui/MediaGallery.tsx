import React, { useState } from 'react';
import { X, Play, Download, Expand } from 'lucide-react';

interface MediaItem {
  id?: string;
  url: string;
  filename: string;
  type: string;
  size?: number;
  isVideo?: boolean;
  thumbnail?: string;
}

interface MediaGalleryProps {
  items: MediaItem[];
  onRemove?: (index: number) => void;
  editable?: boolean;
  maxItems?: number;
  className?: string;
}

export const MediaGallery: React.FC<MediaGalleryProps> = ({
  items,
  onRemove,
  editable = false,
  maxItems = 10,
  className = ''
}) => {
  const [selectedItem, setSelectedItem] = useState<MediaItem | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const openModal = (item: MediaItem) => {
    setSelectedItem(item);
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setSelectedItem(null);
    setIsModalOpen(false);
  };

  const formatFileSize = (bytes?: number) => {
    if (!bytes) return '';
    const mb = bytes / (1024 * 1024);
    return mb < 1 ? `${(bytes / 1024).toFixed(0)}KB` : `${mb.toFixed(1)}MB`;
  };

  const handleDownload = (item: MediaItem) => {
    const link = document.createElement('a');
    link.href = item.url;
    link.download = item.filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  if (items.length === 0) {
    return (
      <div className={`text-center py-8 text-gray-500 ${className}`}>
        <p>No media files uploaded</p>
      </div>
    );
  }

  return (
    <>
      <div className={`media-gallery ${className}`}>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {items.slice(0, maxItems).map((item, index) => (
            <div key={index} className="relative group">
              <div className="aspect-square bg-gray-100 rounded-lg overflow-hidden border">
                {item.isVideo ? (
                  // Video thumbnail
                  <div className="relative w-full h-full flex items-center justify-center bg-gray-900">
                    {item.thumbnail ? (
                      <img
                        src={item.thumbnail}
                        alt={item.filename}
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <div className="text-white">
                        <Play className="w-12 h-12" />
                      </div>
                    )}
                    <div className="absolute inset-0 bg-black bg-opacity-30 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                      <Play className="w-8 h-8 text-white" />
                    </div>
                  </div>
                ) : (
                  // Image
                  <img
                    src={item.url}
                    alt={item.filename}
                    className="w-full h-full object-cover cursor-pointer hover:scale-105 transition-transform"
                    onClick={() => openModal(item)}
                  />
                )}

                {/* Overlay controls */}
                <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-200 bg-black bg-opacity-0 group-hover:bg-opacity-40">
                  <div className="flex space-x-3 z-10">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        openModal(item);
                      }}
                      className="p-3 bg-white rounded-full hover:bg-gray-100 transition-colors shadow-lg"
                      title="View full size"
                    >
                      <Expand className="w-5 h-5 text-gray-700" />
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDownload(item);
                      }}
                      className="p-3 bg-white rounded-full hover:bg-gray-100 transition-colors shadow-lg"
                      title="Download"
                    >
                      <Download className="w-5 h-5 text-gray-700" />
                    </button>
                  </div>
                </div>

                {/* Remove button */}
                {editable && onRemove && (
                  <button
                    onClick={() => onRemove(index)}
                    className="absolute top-2 right-2 p-1 bg-red-500 text-white rounded-full opacity-0 group-hover:opacity-100 transition-opacity hover:bg-red-600"
                    title="Remove"
                  >
                    <X className="w-3 h-3" />
                  </button>
                )}
              </div>

            </div>
          ))}
        </div>

        {items.length > maxItems && (
          <div className="mt-4 text-center">
            <p className="text-sm text-gray-500">
              Showing {maxItems} of {items.length} files
            </p>
          </div>
        )}
      </div>

      {/* Full-size modal */}
      {isModalOpen && selectedItem && (
        <div className="fixed inset-0 bg-slate-900/80 backdrop-blur-sm flex items-center justify-center z-50 p-4" onClick={closeModal}>
          <div className="relative max-w-4xl max-h-full" onClick={(e) => e.stopPropagation()}>
            {/* Close button */}
            <button
              onClick={closeModal}
              className="absolute -top-12 right-0 p-2 bg-white/90 text-slate-700 rounded-full hover:bg-white transition-colors z-10"
            >
              <X className="w-6 h-6" />
            </button>

            {/* Media content */}
            <div className="bg-white rounded-lg overflow-hidden">
              {selectedItem.isVideo ? (
                <video
                  src={selectedItem.url}
                  controls
                  className="max-w-full max-h-[80vh]"
                  autoPlay
                >
                  Your browser does not support video playback.
                </video>
              ) : (
                <img
                  src={selectedItem.url}
                  alt={selectedItem.filename}
                  className="max-w-full max-h-[80vh] object-contain"
                />
              )}

              {/* File info bar */}
              <div className="p-4 bg-gray-50 border-t">
                <div className="flex justify-between items-center">
                  <div>
                    <h3 className="font-medium text-gray-900">
                      {selectedItem.filename}
                    </h3>
                    <p className="text-sm text-gray-500">
                      {selectedItem.size && formatFileSize(selectedItem.size)} • {selectedItem.type}
                    </p>
                  </div>
                  <button
                    onClick={() => handleDownload(selectedItem)}
                    className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors flex items-center space-x-2"
                  >
                    <Download className="w-4 h-4" />
                    <span>Download</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
};