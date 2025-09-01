import { useEffect, useRef, useState } from 'react'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

// Fix for default markers in React-Leaflet
delete (L.Icon.Default.prototype as any)._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
})

interface LocationPickerProps {
  onLocationSelect: (lat: number, lng: number) => void
  defaultLat?: number
  defaultLng?: number
  height?: string
}

export default function LocationPicker({ 
  onLocationSelect, 
  defaultLat = 24.7136, 
  defaultLng = 46.6753,
  height = "400px"
}: LocationPickerProps) {
  const mapRef = useRef<HTMLDivElement>(null)
  const mapInstanceRef = useRef<L.Map | null>(null)
  const markerRef = useRef<L.Marker | null>(null)
  const [selectedLocation, setSelectedLocation] = useState<{lat: number, lng: number}>({
    lat: defaultLat,
    lng: defaultLng
  })

  useEffect(() => {
    if (!mapRef.current) return
    
    // Clean up existing map instance
    if (mapInstanceRef.current) {
      mapInstanceRef.current.remove()
      mapInstanceRef.current = null
    }

    // Initialize map centered on Saudi Arabia
    const map = L.map(mapRef.current, {
      center: [selectedLocation.lat, selectedLocation.lng],
      zoom: 7,
      minZoom: 5,
      maxZoom: 18,
      zoomControl: true,
      scrollWheelZoom: true,
      doubleClickZoom: true,
      touchZoom: true,
    })

    mapInstanceRef.current = map

    // Add tile layer
    L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
      attribution: '© OpenStreetMap contributors © CARTO',
      subdomains: 'abcd',
      maxZoom: 18
    }).addTo(map)

    // Create custom marker icon for selected location
    const createLocationIcon = () => {
      return L.divIcon({
        className: 'location-marker',
        html: `
          <div class="location-pin">
            <div class="location-inner"></div>
            <div class="location-pulse"></div>
          </div>
        `,
        iconSize: [30, 42],
        iconAnchor: [15, 42],
        popupAnchor: [0, -42]
      })
    }

    // Add initial marker
    const marker = L.marker([selectedLocation.lat, selectedLocation.lng], {
      icon: createLocationIcon(),
      draggable: true
    }).addTo(map)

    markerRef.current = marker

    // Add popup to marker
    marker.bindPopup(`
      <div style="text-align: center; font-family: system-ui, -apple-system, sans-serif;">
        <strong style="color: #1e293b;">Factory Location</strong><br/>
        <span style="color: #64748b; font-size: 12px;">
          ${selectedLocation.lat.toFixed(6)}, ${selectedLocation.lng.toFixed(6)}
        </span>
      </div>
    `).openPopup()

    // Handle map clicks to place marker
    map.on('click', (e: L.LeafletMouseEvent) => {
      const { lat, lng } = e.latlng
      
      // Update marker position
      marker.setLatLng([lat, lng])
      
      // Update popup content
      marker.getPopup()?.setContent(`
        <div style="text-align: center; font-family: system-ui, -apple-system, sans-serif;">
          <strong style="color: #1e293b;">Factory Location</strong><br/>
          <span style="color: #64748b; font-size: 12px;">
            ${lat.toFixed(6)}, ${lng.toFixed(6)}
          </span>
        </div>
      `)
      
      // Update state and call callback
      setSelectedLocation({ lat, lng })
      onLocationSelect(lat, lng)
    })

    // Handle marker drag
    marker.on('dragend', () => {
      const position = marker.getLatLng()
      const { lat, lng } = position
      
      // Update popup content
      marker.getPopup()?.setContent(`
        <div style="text-align: center; font-family: system-ui, -apple-system, sans-serif;">
          <strong style="color: #1e293b;">Factory Location</strong><br/>
          <span style="color: #64748b; font-size: 12px;">
            ${lat.toFixed(6)}, ${lng.toFixed(6)}
          </span>
        </div>
      `)
      
      // Update state and call callback
      setSelectedLocation({ lat, lng })
      onLocationSelect(lat, lng)
    })

    // Cleanup function
    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove()
        mapInstanceRef.current = null
      }
    }
  }, []) // Empty dependency array to prevent re-initialization

  // Update marker position when defaultLat/defaultLng change
  useEffect(() => {
    if (markerRef.current && mapInstanceRef.current) {
      const newLocation = { lat: defaultLat, lng: defaultLng }
      
      // Only update if the location actually changed
      if (selectedLocation.lat !== defaultLat || selectedLocation.lng !== defaultLng) {
        markerRef.current.setLatLng([defaultLat, defaultLng])
        mapInstanceRef.current.setView([defaultLat, defaultLng])
        
        // Update popup content
        markerRef.current.getPopup()?.setContent(`
          <div style="text-align: center; font-family: system-ui, -apple-system, sans-serif;">
            <strong style="color: #1e293b;">Factory Location</strong><br/>
            <span style="color: #64748b; font-size: 12px;">
              ${defaultLat.toFixed(6)}, ${defaultLng.toFixed(6)}
            </span>
          </div>
        `)
        
        setSelectedLocation(newLocation)
      }
    }
  }, [defaultLat, defaultLng])

  return (
    <div className="location-picker-container">
      <div className="map-wrapper rounded-xl overflow-hidden border border-slate-200 shadow-sm">
        <div ref={mapRef} style={{ height, width: '100%' }} />
      </div>
      
      <div className="mt-4 p-4 bg-blue-50 rounded-lg border border-blue-200">
        <p className="text-sm text-blue-800 font-medium mb-2">📍 How to select location:</p>
        <ul className="text-sm text-blue-700 space-y-1">
          <li>• Click anywhere on the map to place your factory marker</li>
          <li>• Drag the marker to fine-tune the exact location</li>
          <li>• Use zoom controls to get a better view of the area</li>
        </ul>
      </div>
      
      <style>{`
        .location-picker-container {
          position: relative;
        }

        .map-wrapper {
          background: white;
          position: relative;
        }

        :global(.location-marker) {
          background: none;
          border: none;
        }

        :global(.location-pin) {
          width: 30px;
          height: 42px;
          position: relative;
          background: #3B82F6;
          border-radius: 50% 50% 50% 0;
          transform: rotate(-45deg);
          box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
          animation: drop 0.3s ease-out;
        }

        :global(.location-inner) {
          width: 12px;
          height: 12px;
          background: white;
          border-radius: 50%;
          position: absolute;
          top: 50%;
          left: 50%;
          transform: translate(-50%, -50%) rotate(45deg);
        }

        :global(.location-pulse) {
          width: 30px;
          height: 42px;
          background: rgba(59, 130, 246, 0.3);
          border-radius: 50% 50% 50% 0;
          position: absolute;
          top: 0;
          left: 0;
          animation: pulse 2s infinite;
        }

        @keyframes drop {
          0% {
            transform: rotate(-45deg) translateY(-20px);
            opacity: 0;
          }
          100% {
            transform: rotate(-45deg) translateY(0);
            opacity: 1;
          }
        }

        @keyframes pulse {
          0% {
            transform: scale(1);
            opacity: 0.7;
          }
          50% {
            transform: scale(1.2);
            opacity: 0.3;
          }
          100% {
            transform: scale(1);
            opacity: 0.7;
          }
        }

        :global(.leaflet-popup-content-wrapper) {
          background: white;
          border-radius: 12px;
          box-shadow: 0 8px 32px rgba(0,0,0,0.12);
          border: 1px solid rgba(226, 232, 240, 0.8);
        }

        :global(.leaflet-popup-content) {
          margin: 12px 16px;
          line-height: 1.4;
        }

        :global(.leaflet-popup-tip) {
          background: white;
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        :global(.leaflet-control-zoom) {
          border: none;
          border-radius: 8px;
          box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }

        :global(.leaflet-control-zoom a) {
          background: white;
          color: #3B82F6;
          border: none;
          font-size: 16px;
          font-weight: bold;
          line-height: 28px;
          width: 32px;
          height: 32px;
          transition: all 0.2s ease;
        }

        :global(.leaflet-control-zoom a:hover) {
          background: #3B82F6;
          color: white;
        }

        :global(.leaflet-control-zoom-in) {
          border-radius: 8px 8px 0 0 !important;
        }

        :global(.leaflet-control-zoom-out) {
          border-radius: 0 0 8px 8px !important;
          border-top: 1px solid #e2e8f0;
        }
      `}</style>
    </div>
  )
}