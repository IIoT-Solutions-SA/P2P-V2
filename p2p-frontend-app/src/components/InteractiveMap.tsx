import React, { useEffect, useRef, useState } from 'react'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import 'leaflet.markercluster/dist/MarkerCluster.css'
import 'leaflet.markercluster/dist/MarkerCluster.Default.css'
import 'leaflet.markercluster'
import { generateUseCasePopupHTML, type UseCase as PopupUseCase } from './UseCasePopup'

// Fix for default markers in React-Leaflet
delete (L.Icon.Default.prototype as any)._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
})


interface InteractiveMapProps {
  height?: string
  showTitle?: boolean
  title?: string
  className?: string
}

type BackendUseCase = {
  id: string
  title: string
  title_slug?: string
  company_slug?: string
  company?: string
  category?: string
  description?: string
  region?: string
  latitude?: number
  longitude?: number
  image?: string
  benefits_list?: string[]
}

export default function InteractiveMap({ 
  height = "500px", 
  showTitle = true, 
  title = "Factory Success Stories Across Saudi Arabia",
  className = ""
}: InteractiveMapProps) {
  const mapRef = useRef<HTMLDivElement>(null)
  const mapInstanceRef = useRef<L.Map | null>(null)
  const currentPopupRef = useRef<L.Popup | null>(null)
  const [currentZoom, setCurrentZoom] = useState(6)
  const [backendUseCases, setBackendUseCases] = useState<BackendUseCase[] | null>(null)

  useEffect(() => {
    // Fetch use-cases from backend for map markers
    const fetchUseCases = async () => {
      try {
        const res = await fetch('http://localhost:8000/api/v1/use-cases?limit=200', { credentials: 'include' })
        if (!res.ok) throw new Error('Failed to load use cases')
        const data = await res.json()
        setBackendUseCases(data)
      } catch (err) {
        console.error('Failed to fetch use cases for map', err)
        setBackendUseCases([])
      }
    }
    fetchUseCases()
  }, [])

  useEffect(() => {
    if (!mapRef.current) return
    if (backendUseCases === null) return // wait for data
    
    // Clean up existing map instance
    if (mapInstanceRef.current) {
      mapInstanceRef.current.remove()
      mapInstanceRef.current = null
    }

    // Initialize map centered on Saudi Arabia
    const map = L.map(mapRef.current, {
      center: [24.7136, 46.6753], // Riyadh coordinates
      zoom: 6,
      minZoom: 5,
      maxZoom: 20, // Enable street-level zoom
      zoomControl: true,
      scrollWheelZoom: 'center', // Enable with Ctrl/Cmd key
      doubleClickZoom: true,
      touchZoom: true,
    })

    mapInstanceRef.current = map

    // Add tile layer with clean, minimalist style - configured for street-level zoom
    L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
      attribution: '© OpenStreetMap contributors © CARTO',
      subdomains: 'abcd',
      maxNativeZoom: 19, // Maximum zoom level with actual tiles
      maxZoom: 20 // Allow zoom beyond tile availability with upscaling
    }).addTo(map)

    // Create custom marker icon
    const createCustomIcon = () => {
      return L.divIcon({
        className: 'custom-marker',
        html: `
          <div class="marker-pin">
            <div class="marker-inner"></div>
          </div>
        `,
        iconSize: [24, 36],
        iconAnchor: [12, 36],
        popupAnchor: [0, -36]
      })
    }

    // Create marker cluster group with Airbnb-style clustering behavior
    const markerClusterGroup = (L as any).markerClusterGroup({
      maxClusterRadius: 60, // Tighter clustering for better separation
      spiderfyOnMaxZoom: false, // Disable spiderfy - we handle clicks differently
      showCoverageOnHover: false,
      zoomToBoundsOnClick: false, // We'll handle cluster clicks manually
      disableClusteringAtZoom: 16, // Show individual markers at zoom 16+ (changed from 18)
      singleMarkerMode: true, // Show individual markers when not clustered
      iconCreateFunction: function(cluster: any) {
        const count = cluster.getChildCount()
        let size = 'small'
        if (count > 10) size = 'large'
        else if (count > 5) size = 'medium'
        
        return L.divIcon({
          html: `<div class="cluster-inner">${count}</div>`,
          className: `marker-cluster marker-cluster-${size}`,
          iconSize: count > 10 ? [50, 50] : count > 5 ? [45, 45] : [40, 40]
        })
      }
    })

    // Create popup content using the dynamic generator
    const createPopupContent = (useCase: PopupUseCase) => {
      return generateUseCasePopupHTML(useCase)
    }

    // Create cluster popup content with zoom controls
    const createClusterPopupContent = (markers: L.Marker[], cluster: any) => {
      const useCases = markers.map((marker: any) => marker.options.useCase)
      const bounds = cluster.getBounds()
      
      console.log('Creating cluster popup for', useCases.length, 'use cases')
      
      // If 4 or fewer use cases, show enhanced card view
      if (useCases.length <= 4) {
        return `
          <div class="cluster-cards-popup">
            <div class="cluster-simple-header">
              <h3 class="simple-title">${useCases.length} Success ${useCases.length === 1 ? 'Story' : 'Stories'} in This Area</h3>
              <div class="simple-actions" style="display: flex; align-items: center; gap: 12px;">
                <button class="zoom-to-area-btn" title="Zoom to see individual factories" style="
                  background: #3b82f6; 
                  color: white; 
                  border: none; 
                  border-radius: 8px; 
                  padding: 10px 12px; 
                  cursor: pointer; 
                  display: flex; 
                  align-items: center; 
                  justify-content: center; 
                  gap: 6px; 
                  font-size: 12px; 
                  font-weight: 600; 
                  transition: all 0.2s ease;
                " onmouseover="this.style.background='#2563eb'; this.style.transform='scale(1.05)'" onmouseout="this.style.background='#3b82f6'; this.style.transform='scale(1)'">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="11" cy="11" r="8"></circle>
                    <path d="m21 21-4.35-4.35"></path>
                    <path d="M11 8v6M8 11h6"></path>
                  </svg>
                  Zoom In
                </button>
                <button class="close-cards-btn" style="
                  background: #f1f5f9; 
                  color: #64748b; 
                  border: none; 
                  border-radius: 8px; 
                  width: 40px; 
                  height: 40px; 
                  cursor: pointer; 
                  display: flex; 
                  align-items: center; 
                  justify-content: center; 
                  font-size: 20px; 
                  font-weight: 600; 
                  transition: all 0.2s ease;
                " onmouseover="this.style.background='#e2e8f0'; this.style.color='#1e293b'" onmouseout="this.style.background='#f1f5f9'; this.style.color='#64748b'">×</button>
              </div>
            </div>
            <div class="cluster-cards-grid" style="
              padding: 24px; 
              overflow-y: auto; 
              max-height: 400px; 
              display: flex !important; 
              flex-direction: column !important; 
              gap: 20px; 
              width: 100% !important; 
              box-sizing: border-box !important; 
              background: white; 
              align-items: center !important;
            ">
              ${useCases.map((useCase: UseCase, index: number) => `
                <div class="cluster-horizontal-card" data-usecase-index="${index}" style="
                  background: white; 
                  border: 1px solid rgba(226, 232, 240, 0.6); 
                  border-radius: 20px; 
                  overflow: hidden; 
                  cursor: pointer; 
                  display: flex !important; 
                  flex-direction: row !important; 
                  height: 130px; 
                  width: 480px !important; 
                  margin: 0 auto !important; 
                  box-sizing: border-box !important; 
                  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
                  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                " onmouseover="this.style.transform='translateY(-4px)'; this.style.boxShadow='0 12px 32px rgba(59, 130, 246, 0.2)'; this.style.borderColor='#3b82f6'" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 16px rgba(0, 0, 0, 0.08)'; this.style.borderColor='rgba(226, 232, 240, 0.6)'">
                  
                  <!-- Image Section (Left) - 130px width -->
                  <div class="cluster-image-section" style="
                    width: 130px !important; 
                    min-width: 130px !important; 
                    max-width: 130px !important; 
                    overflow: hidden; 
                    position: relative; 
                    flex-shrink: 0 !important; 
                    box-sizing: border-box !important;
                  ">
                    <img src="${useCase.image}" alt="${useCase.title}" style="
                      width: 100%; 
                      height: 100%; 
                      object-fit: cover;
                    " />
                    ${useCase.category ? `<span class="cluster-category-badge" style="
                      position: absolute; 
                      top: 6px; 
                      left: 6px; 
                      background: rgba(59, 130, 246, 0.95); 
                      backdrop-filter: blur(8px);
                      color: white; 
                      padding: 4px 10px; 
                      border-radius: 16px; 
                      font-size: 9px; 
                      font-weight: 700;
                      text-transform: uppercase;
                      letter-spacing: 0.5px;
                      border: 1px solid rgba(255, 255, 255, 0.3);
                      box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
                    ">${useCase.category}</span>` : ''}
                  </div>
                  
                  <!-- Content Section (Right) - 330px width -->
                  <div class="cluster-content-section" style="
                    flex: 1; 
                    padding: 18px 20px; 
                    display: flex; 
                    flex-direction: column; 
                    justify-content: space-between; 
                    box-sizing: border-box; 
                    position: relative;
                  ">
                    
                    <!-- Header -->
                    <div class="cluster-header" style="margin-bottom: 10px;">
                      <h4 class="cluster-title" style="
                        font-size: 17px; 
                        font-weight: 700; 
                        color: #1e293b; 
                        margin-bottom: 6px; 
                        margin-top: 0; 
                        line-height: 1.3; 
                        display: -webkit-box; 
                        -webkit-line-clamp: 1; 
                        -webkit-box-orient: vertical; 
                        overflow: hidden;
                      ">${useCase.title}</h4>
                      <p class="cluster-description" style="
                        font-size: 13px; 
                        color: #64748b; 
                        line-height: 1.5; 
                        display: -webkit-box; 
                        -webkit-line-clamp: 2; 
                        -webkit-box-orient: vertical; 
                        overflow: hidden; 
                        margin-bottom: 10px; 
                        margin-top: 0;
                      ">${useCase.description}</p>
                      
                      <!-- Factory Info -->
                      <div class="cluster-factory-info" style="
                        display: flex; 
                        align-items: center; 
                        gap: 8px; 
                        font-size: 13px; 
                        margin-bottom: 10px;
                      ">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="2">
                          <path d="M3 21h18M5 21V7l8-4v18M19 21V11l-6-4"></path>
                        </svg>
                        <strong class="factory-name" style="color: #1e293b; font-weight: 600;">${useCase.factoryName}</strong>
                        <span class="separator" style="color: #64748b; font-weight: 500;">•</span>
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="2">
                          <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
                          <circle cx="12" cy="10" r="3"></circle>
                        </svg>
                        <span class="city-name" style="color: #64748b; font-weight: 500;">${useCase.city}</span>
                      </div>
                    </div>
                    
                    <!-- Footer -->
                    <div class="cluster-footer" style="
                      display: flex; 
                      justify-content: space-between; 
                      align-items: center; 
                      margin-top: auto;
                    ">
                      <div class="cluster-benefits" style="display: flex; flex-wrap: wrap; gap: 6px;">
                        ${useCase.benefits.slice(0, 2).map(benefit => `
                          <span class="cluster-benefit-tag" style="
                            background: linear-gradient(135deg, #eff6ff, #dbeafe); 
                            color: #1e40af; 
                            padding: 4px 10px; 
                            border-radius: 14px; 
                            font-size: 10px; 
                            font-weight: 600; 
                            border: 1px solid #bfdbfe;
                            white-space: nowrap;
                          ">${benefit}</span>
                        `).join('')}
                      </div>
                      <button class="cluster-view-btn" style="
                        padding: 8px 16px; 
                        background: #3b82f6; 
                        color: white; 
                        border: none; 
                        border-radius: 8px; 
                        font-size: 12px; 
                        font-weight: 600; 
                        cursor: pointer; 
                        flex-shrink: 0;
                        transition: all 0.2s ease;
                      " onmouseover="this.style.background='#2563eb'; this.style.transform='translateY(-1px)'" onmouseout="this.style.background='#3b82f6'; this.style.transform='translateY(0)'">View Details</button>
                    </div>
                    
                  </div>
                </div>
              `).join('')}
            </div>
          </div>
        `
      }
      
      // For more than 4 use cases, show list view with zoom option
      return `
        <div class="cluster-popup">
          <div class="cluster-header">
            <h3 class="cluster-title">Use Cases in This Area (${useCases.length})</h3>
            <button class="zoom-to-area-btn" title="Zoom to see individual factories">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="11" cy="11" r="8"></circle>
                <path d="m21 21-4.35-4.35"></path>
                <path d="M11 8v6M8 11h6"></path>
              </svg>
            </button>
          </div>
          <div class="cluster-list">
            ${useCases.map((useCase: UseCase, index: number) => `
              <div class="cluster-item" data-usecase-index="${index}">
                <strong>${useCase.title}</strong>
                <span class="cluster-factory">${useCase.factoryName}</span>
              </div>
            `).join('')}
          </div>
        </div>
      `
    }

    // Add markers for each use case
    const rawMapped = (backendUseCases || []).filter(uc => typeof uc.latitude === 'number' && typeof uc.longitude === 'number')
      .map<PopupUseCase>(uc => ({
        id: uc.id as unknown as any, // popup accepts number|string for navigation usage
        title: uc.title || 'Untitled',
        description: (uc.description || '').trim(),
        factoryName: uc.company || 'Unknown',
        city: uc.region || '',
        latitude: uc.latitude as number,
        longitude: uc.longitude as number,
        image: uc.image || 'https://images.unsplash.com/photo-1581090700227-1e37b190418e?w=1200&auto=format&fit=crop&q=60',
        benefits: (uc.benefits_list && uc.benefits_list.length > 0) ? uc.benefits_list : [
          // Fallback badges so the CTA row always has content
          'Verified implementation',
          'Proven ROI'
        ],
        implementationTime: undefined,
        category: uc.category,
        roiPercentage: undefined,
        contactPerson: undefined,
        contactTitle: undefined,
        companySlug: uc.company_slug || (uc.company && uc.company.length ? uc.company.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '') : undefined),
        titleSlug: uc.title_slug || (uc.title && uc.title.length ? uc.title.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '').replace(/(^-|-$)/g, '') : undefined),
      }))

    // Spread overlapping markers slightly so they are easier to click
    const keyFor = (lat: number, lng: number) => `${lat.toFixed(5)},${lng.toFixed(5)}`
    const groups = new Map<string, PopupUseCase[]>()
    rawMapped.forEach(uc => {
      const k = keyFor(uc.latitude, uc.longitude)
      const arr = groups.get(k) || []
      arr.push(uc)
      groups.set(k, arr)
    })

    const adjusted: PopupUseCase[] = []
    groups.forEach((arr, k) => {
      if (arr.length === 1) {
        adjusted.push(arr[0])
      } else {
        const [baseLat, baseLng] = k.split(',').map(parseFloat)
        const metersPerDegLat = 111320
        const metersPerDegLng = 111320 * Math.cos((baseLat * Math.PI) / 180)
        const n = arr.length
        arr.forEach((uc, i) => {
          const angle = (2 * Math.PI * i) / n
          const radiusMeters = 35 + i * 5 // radial spread
          const dLat = (radiusMeters * Math.cos(angle)) / metersPerDegLat
          const dLng = (radiusMeters * Math.sin(angle)) / metersPerDegLng
          adjusted.push({ ...uc, latitude: baseLat + dLat, longitude: baseLng + dLng })
        })
      }
    })

    adjusted.forEach((useCase: PopupUseCase) => {
      const marker = L.marker([useCase.latitude, useCase.longitude], {
        icon: createCustomIcon(),
        useCase: useCase // Store use case data in marker options
      } as any)

      // Add click event for individual markers - show popup instead of zooming
      marker.on('click', function(e) {
        // Close any existing popup
        if (currentPopupRef.current) {
          map.closePopup(currentPopupRef.current)
        }

        // Zoom straight to the marker before opening popup
        map.setView(e.latlng, 17, { animate: true, duration: 0.5 })
        setTimeout(() => {
          const popup = L.popup({
            closeButton: true,
            autoClose: false,
            closeOnClick: false,
            className: 'use-case-click-popup',
            maxWidth: 560
          })
          .setContent(createPopupContent(useCase))
          .setLatLng(e.latlng)
          .openOn(map)
          currentPopupRef.current = popup
        }, 350)

        // Prevent event from bubbling to map and other clusters
        L.DomEvent.stopPropagation(e.originalEvent)
        e.originalEvent?.preventDefault()
      })

      markerClusterGroup.addLayer(marker)
    })

    // Add cluster click events
    markerClusterGroup.on('clusterclick', function(e: any) {
      const cluster = e.layer
      const markers = cluster.getAllChildMarkers()
      
      // Close any existing popup
      if (currentPopupRef.current) {
        map.closePopup(currentPopupRef.current)
      }
      
      const isCardView = markers.length <= 4
      
      const popup = L.popup({
        closeButton: !isCardView, // No close button for card view (custom close button)
        autoClose: false,
        closeOnClick: true,
        className: isCardView ? 'cluster-cards-popup-wrapper' : 'cluster-click-popup',
        maxWidth: isCardView ? 800 : 350, // Increased width for new larger cards
        maxHeight: isCardView ? 550 : 400  // Increased height for better spacing
      })
      .setContent(createClusterPopupContent(markers, cluster))
      .setLatLng(cluster.getLatLng())
      .openOn(map)
      
      currentPopupRef.current = popup
      
      // Add event listeners after popup is rendered
      setTimeout(() => {
        // Handle close button for card view
        const closeBtn = document.querySelector('.close-cards-btn')
        if (closeBtn) {
          closeBtn.addEventListener('click', () => {
            map.closePopup(popup)
          })
        }
        
        // Handle zoom to area button
        const zoomBtn = document.querySelector('.zoom-to-area-btn')
        if (zoomBtn) {
          zoomBtn.addEventListener('click', () => {
            // Close cluster popup
            map.closePopup(popup)
            
            // Zoom to cluster bounds to show individual markers
            const bounds = cluster.getBounds()
            map.fitBounds(bounds, {
              padding: [20, 20],
              animate: true,
              duration: 1,
              maxZoom: 17 // Ensure we reach a zoom level where clustering is disabled (16+)
            })
          })
        }
        
        // Handle clicks on items (both card and list view)
        const items = document.querySelectorAll(isCardView ? '.cluster-horizontal-card' : '.cluster-item')
        items.forEach((item, index) => {
          item.addEventListener('click', () => {
            const marker = markers[index]
            const useCase = (marker as any).options.useCase
            
            // Close cluster popup
            map.closePopup(popup)
            
            // Zoom to marker location for better focus
            map.setView([useCase.latitude, useCase.longitude], 15, {
              animate: true,
              duration: 1
            })
            
            // Open use case popup after zoom
            setTimeout(() => {
              marker.fire('click')
            }, 600)
          })
        })

        // Handle explicit "View Details" button clicks inside card view
        if (isCardView) {
          const buttons = document.querySelectorAll('.cluster-view-btn')
          buttons.forEach((btn, index) => {
            btn.addEventListener('click', (ev: any) => {
              ev.stopPropagation()
              const marker = markers[index]
              const uc = (marker as any).options.useCase
              const url = (uc.companySlug && uc.titleSlug)
                ? `/usecases/${uc.companySlug}/${uc.titleSlug}`
                : `/usecases/${uc.id}`
              window.location.href = url
            })
          })
        }
      }, 100)
      
      // Prevent default zoom behavior
      e.originalEvent.stopPropagation()
    })

    map.addLayer(markerClusterGroup)

    // Add zoom event listener to track current zoom level
    map.on('zoomend', () => {
      setCurrentZoom(map.getZoom())
    })

    // Cleanup function
    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove()
        mapInstanceRef.current = null
      }
    }
  }, [backendUseCases])

  return (
    <div className={`interactive-map-container ${className}`}>
      {showTitle && (
        <div className="text-center mb-8">
          <h2 className="text-3xl font-bold text-slate-900 mb-4">{title}</h2>
          <p className="text-lg text-slate-600">Explore real implementations across the Kingdom</p>
        </div>
      )}
      <div className="map-wrapper rounded-2xl overflow-hidden border border-slate-200 shadow-lg relative">
        <div ref={mapRef} style={{ height, width: '100%', zIndex: 1 }} />
      </div>
      
      <style jsx>{`
        .interactive-map-container {
          position: relative;
        }

        .map-wrapper {
          background: white;
          z-index: 1;
          position: relative;
        }

        /* Ensure map elements don't cover navbar */
        :global(.leaflet-container) {
          z-index: 1 !important;
        }
        
        :global(.leaflet-popup-pane) {
          z-index: 10 !important;
        }
        
        :global(.leaflet-marker-pane) {
          z-index: 5 !important;
        }

        :global(.custom-marker) {
          background: none;
          border: none;
        }

        :global(.marker-pin) {
          width: 24px;
          height: 36px;
          position: relative;
          background: #3B82F6;
          border-radius: 50% 50% 50% 0;
          transform: rotate(-45deg);
          box-shadow: 0 2px 8px rgba(0,0,0,0.3);
          transition: all 0.2s ease;
        }

        :global(.marker-pin:hover) {
          transform: rotate(-45deg) scale(1.1);
          box-shadow: 0 4px 12px rgba(0,0,0,0.4);
        }

        :global(.marker-inner) {
          width: 8px;
          height: 8px;
          background: white;
          border-radius: 50%;
          position: absolute;
          top: 50%;
          left: 50%;
          transform: translate(-50%, -50%) rotate(45deg);
        }

        :global(.marker-cluster) {
          background: rgba(59, 130, 246, 0.9);
          border-radius: 50%;
          box-shadow: 0 2px 8px rgba(0,0,0,0.3);
          transition: all 0.2s ease;
        }

        :global(.marker-cluster:hover) {
          transform: scale(1.1);
          box-shadow: 0 4px 12px rgba(0,0,0,0.4);
        }

        :global(.cluster-inner) {
          color: white;
          font-weight: bold;
          text-align: center;
          line-height: 40px;
          font-size: 14px;
        }

        :global(.marker-cluster-small) {
          background: rgba(59, 130, 246, 0.8);
        }

        :global(.marker-cluster-medium) {
          background: rgba(59, 130, 246, 0.9);
        }

        :global(.marker-cluster-large) {
          background: rgba(59, 130, 246, 1);
        }


        :global(.cluster-popup) {
          width: 280px;
          font-family: system-ui, -apple-system, sans-serif;
        }

        :global(.cluster-header) {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 12px;
          padding-bottom: 8px;
          border-bottom: 1px solid #e2e8f0;
        }
        
        :global(.cluster-title) {
          font-size: 16px;
          font-weight: bold;
          color: #1e293b;
          margin: 0;
        }

        :global(.cluster-list) {
          max-height: 200px;
          overflow-y: auto;
        }

        :global(.cluster-item) {
          padding: 12px;
          border-bottom: 1px solid #f1f5f9;
          cursor: pointer;
          transition: background-color 0.2s ease;
        }
        
        :global(.cluster-item:hover) {
          background-color: #f8fafc;
        }

        :global(.cluster-item:last-child) {
          border-bottom: none;
        }

        :global(.cluster-item strong) {
          display: block;
          color: #1e293b;
          font-size: 14px;
          margin-bottom: 2px;
        }

        :global(.cluster-factory) {
          color: #64748b;
          font-size: 12px;
        }
        
        /* Card view styles for clusters with 4 or fewer items */
        :global(.cluster-cards-popup-wrapper .leaflet-popup-content-wrapper) {
          background: white;
          border-radius: 20px;
          box-shadow: 0 25px 50px rgba(0,0,0,0.25);
          border: 1px solid rgba(226, 232, 240, 0.8);
          padding: 0;
          max-width: none !important;
        }
        
        :global(.cluster-cards-popup-wrapper .leaflet-popup-content) {
          margin: 0;
          width: 760px !important;
          max-height: 520px;
          overflow: hidden;
          border-radius: 20px;
        }
        
        :global(.cluster-cards-popup-wrapper .cluster-cards-popup) {
          height: 100%;
          display: flex !important;
          flex-direction: column !important;
        }
        
        /* Simplified Header */
        :global(.cluster-simple-header) {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 20px 24px;
          border-bottom: 1px solid #e2e8f0;
          background: white;
          border-radius: 20px 20px 0 0;
        }
        
        :global(.simple-title) {
          font-size: 18px;
          font-weight: 700;
          color: #1e293b;
          margin: 0;
          line-height: 1.3;
        }
        
        :global(.simple-actions) {
          display: flex;
          align-items: center;
          gap: 12px;
        }
        
        :global(.cluster-actions) {
          display: flex;
          align-items: center;
          gap: 12px;
        }
        
        :global(.zoom-to-area-btn) {
          background: #3b82f6;
          color: white;
          border: none;
          border-radius: 8px;
          padding: 8px;
          cursor: pointer;
          transition: all 0.2s ease;
          display: flex;
          align-items: center;
          justify-content: center;
        }
        
        :global(.zoom-to-area-btn:hover) {
          background: #2563eb;
          transform: scale(1.05);
        }
        
        :global(.title-text) {
          font-size: 20px;
          font-weight: bold;
          color: #1e293b;
        }
        
        :global(.close-cards-btn) {
          font-size: 28px;
          color: #64748b;
          cursor: pointer;
          width: 36px;
          height: 36px;
          display: flex;
          align-items: center;
          justify-content: center;
          border-radius: 8px;
          transition: all 0.2s ease;
        }
        
        :global(.close-cards-btn:hover) {
          background: #e2e8f0;
          color: #1e293b;
        }
        
        :global(.cluster-cards-grid),
        :global(.cluster-cards-popup-wrapper .cluster-cards-grid) {
          padding: 24px;
          overflow-y: auto;
          max-height: 400px;
          display: flex !important;
          flex-direction: column !important;
          gap: 16px;
          width: 100% !important;
          box-sizing: border-box !important;
          background: white;
          align-items: center !important;
        }
        
        /* Clean Horizontal Cards - Matching Individual Popup Design */
        :global(.cluster-horizontal-card) {
          background: white;
          border: 1px solid rgba(226, 232, 240, 0.8);
          border-radius: 16px;
          overflow: hidden;
          cursor: pointer;
          transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
          display: flex !important;
          flex-direction: row !important;
          height: 120px;
          width: 450px !important;
          margin: 0 auto !important;
          box-sizing: border-box !important;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
        }
        
        :global(.cluster-horizontal-card:hover) {
          transform: translateY(-2px);
          box-shadow: 0 20px 40px rgba(59, 130, 246, 0.2);
          border-color: #3b82f6;
        }
        
        :global(.cluster-horizontal-card:hover::before) {
          content: '';
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: linear-gradient(135deg, rgba(59, 130, 246, 0.05), rgba(59, 130, 246, 0.02));
          pointer-events: none;
          z-index: 0;
        }
        
        /* Image Section - 120px width (matches individual popup proportions) */
        :global(.cluster-image-section) {
          width: 120px !important;
          min-width: 120px !important;
          max-width: 120px !important;
          overflow: hidden;
          position: relative;
          flex-shrink: 0 !important;
          box-sizing: border-box !important;
        }
        
        :global(.cluster-image-section img) {
          width: 100%;
          height: 100%;
          object-fit: cover;
          transition: transform 0.5s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        :global(.cluster-horizontal-card:hover .cluster-image-section img) {
          transform: scale(1.1);
        }
        
        :global(.cluster-category-badge) {
          position: absolute;
          top: 8px;
          right: 8px;
          background: rgba(59, 130, 246, 0.9);
          backdrop-filter: blur(8px);
          color: white;
          padding: 3px 8px;
          border-radius: 12px;
          font-size: 10px;
          font-weight: 600;
          border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        /* Content Section - 330px width (matches individual popup proportions) */
        :global(.cluster-content-section) {
          flex: 1;
          padding: 16px 18px;
          display: flex;
          flex-direction: column;
          justify-content: space-between;
          box-sizing: border-box;
          position: relative;
          z-index: 1;
        }
        
        /* Header */
        :global(.cluster-header) {
          margin-bottom: 8px;
        }
        
        :global(.cluster-title) {
          font-size: 16px;
          font-weight: 700;
          color: #1e293b;
          margin-bottom: 4px;
          margin-top: 0;
          line-height: 1.3;
          display: -webkit-box;
          -webkit-line-clamp: 1;
          -webkit-box-orient: vertical;
          overflow: hidden;
        }
        
        :global(.cluster-description) {
          font-size: 13px;
          color: #64748b;
          line-height: 1.4;
          display: -webkit-box;
          -webkit-line-clamp: 2;
          -webkit-box-orient: vertical;
          overflow: hidden;
          margin-bottom: 8px;
        }
        
        /* Factory Info */
        :global(.cluster-factory-info) {
          display: flex;
          align-items: center;
          gap: 6px;
          font-size: 12px;
          margin-bottom: 8px;
        }
        
        :global(.factory-name) {
          color: #1e293b;
          font-weight: 600;
        }
        
        :global(.separator) {
          color: #64748b;
          font-weight: 500;
        }
        
        :global(.city-name) {
          color: #64748b;
          font-weight: 500;
        }
        
        /* Footer */
        :global(.cluster-footer) {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-top: auto;
        }
        
        :global(.cluster-benefits) {
          display: flex;
          flex-wrap: wrap;
          gap: 4px;
        }
        
        :global(.cluster-benefit-tag) {
          background: linear-gradient(135deg, #dbeafe, #bfdbfe);
          color: #1e40af;
          padding: 2px 8px;
          border-radius: 12px;
          font-size: 10px;
          font-weight: 600;
          border: 1px solid #93c5fd;
          transition: all 0.2s ease;
        }
        
        :global(.cluster-horizontal-card:hover .cluster-benefit-tag) {
          background: linear-gradient(135deg, #3b82f6, #2563eb);
          color: white;
          border-color: #1d4ed8;
          transform: translateY(-1px);
        }
        
        :global(.cluster-view-btn) {
          padding: 6px 12px;
          background: #3b82f6;
          color: white;
          border: none;
          border-radius: 6px;
          font-size: 11px;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s ease;
          flex-shrink: 0;
        }
        
        :global(.cluster-view-btn:hover) {
          background: #2563eb;
          transform: translateY(-1px);
        }
        

        :global(.use-case-click-popup .leaflet-popup-content-wrapper),
        :global(.cluster-click-popup .leaflet-popup-content-wrapper) {
          background: white;
          border-radius: 16px;
          box-shadow: 0 20px 40px rgba(0,0,0,0.2);
          border: 1px solid rgba(226, 232, 240, 0.8);
          padding: 0;
        }
        
        :global(.use-case-click-popup .leaflet-popup-content) {
          margin: 0;
          width: 520px !important;
          min-height: 240px !important;
        }
        
        :global(.leaflet-popup-close-button) {
          color: #64748b !important;
          font-size: 20px !important;
          font-weight: normal !important;
          width: 28px !important;
          height: 28px !important;
          line-height: 28px !important;
          padding: 0 !important;
          text-align: center !important;
          border-radius: 4px;
          transition: all 0.2s ease;
        }
        
        :global(.leaflet-popup-close-button:hover) {
          color: #1e293b !important;
          background-color: #f1f5f9;
        }

        :global(.leaflet-popup-content) {
          margin: 0;
          line-height: 1.4;
        }

        :global(.leaflet-popup-tip) {
          background: white;
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        :global(.cluster-cards-popup-wrapper .leaflet-popup-tip) {
          display: none;
        }
        
        /* Responsive design for cluster cards */
        @media (max-width: 768px) {
          :global(.cluster-cards-popup-wrapper .leaflet-popup-content) {
            width: 500px !important;
          }
          
          :global(.cluster-horizontal-card) {
            width: 420px !important;
          }
          
          :global(.cluster-image-section) {
            width: 100px !important;
            min-width: 100px !important;
            max-width: 100px !important;
          }
        }
        
        @media (max-width: 540px) {
          :global(.cluster-cards-popup-wrapper .leaflet-popup-content) {
            width: 400px !important;
          }
          
          :global(.cluster-horizontal-card) {
            width: 350px !important;
            height: 100px;
          }
          
          :global(.cluster-benefits) {
            flex-direction: column;
            gap: 2px;
          }
        }
      `}</style>
    </div>
  )
}