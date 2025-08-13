import React from 'react'
import { MapPin, CheckCircle, Factory, TrendingUp, Calendar, User } from 'lucide-react'

export interface UseCase {
  id: number | string
  title: string
  description: string
  factoryName: string
  city: string
  latitude: number
  longitude: number
  image: string
  benefits: string[]
  implementationTime?: string
  category?: string
  roiPercentage?: string
  contactPerson?: string
  contactTitle?: string
  companySlug?: string
  titleSlug?: string
}

interface UseCasePopupProps {
  useCase: UseCase
  onTitleClick?: () => void
}

export default function UseCasePopup({ useCase, onTitleClick }: UseCasePopupProps) {
  const handleTitleClick = (e: React.MouseEvent) => {
    e.preventDefault()
    if (onTitleClick) {
      onTitleClick()
    } else {
      // Default navigation to use case detail page
      if (useCase.companySlug && useCase.titleSlug) {
        window.location.href = `/usecases/${useCase.companySlug}/${useCase.titleSlug}`
      } else {
        window.location.href = `/usecases/${useCase.id}`
      }
    }
  }

  return (
    <div className="use-case-popup-component">
      <div className="popup-header">
        <img 
          src={useCase.image} 
          alt={useCase.title}
          className="popup-image"
        />
        {useCase.category && (
          <span className="category-badge">{useCase.category}</span>
        )}
      </div>
      
      <div className="popup-body">
        <h3 className="popup-title">
          <a 
            href={useCase.companySlug && useCase.titleSlug ? `/usecases/${useCase.companySlug}/${useCase.titleSlug}` : `/usecases/${useCase.id}`}
            onClick={handleTitleClick}
            className="title-link"
          >
            {useCase.title}
          </a>
        </h3>
        
        <p className="popup-description">{useCase.description}</p>
        
        <div className="factory-info">
          <Factory className="icon" />
          <div>
            <strong>{useCase.factoryName}</strong>
            <span className="location">
              <MapPin className="location-icon" />
              {useCase.city}
            </span>
          </div>
        </div>
        
        <div className="benefits-section">
          <h4>Key Benefits</h4>
          <ul className="benefits-list">
            {useCase.benefits.map((benefit, index) => (
              <li key={index}>
                <CheckCircle className="benefit-icon" />
                <span>{benefit}</span>
              </li>
            ))}
          </ul>
        </div>
        
        {useCase.implementationTime && (
          <div className="implementation-info">
            <Calendar className="icon" />
            <span>{useCase.implementationTime}</span>
          </div>
        )}
        
        {useCase.roiPercentage && (
          <div className="roi-info">
            <TrendingUp className="icon" />
            <span>ROI: {useCase.roiPercentage}</span>
          </div>
        )}
        
        {useCase.contactPerson && (
          <div className="contact-info">
            <User className="icon" />
            <div>
              <strong>{useCase.contactPerson}</strong>
              {useCase.contactTitle && <span>{useCase.contactTitle}</span>}
            </div>
          </div>
        )}
        
        <div className="popup-footer">
          <button 
            className="view-details-btn"
            data-testid="popup-view-details"
            onClick={() => {
              const url = (useCase.companySlug && useCase.titleSlug)
                ? `/usecases/${useCase.companySlug}/${useCase.titleSlug}`
                : `/usecases/${useCase.id}`
              window.location.href = url
            }}
          >
            View Full Case Study
          </button>
        </div>
      </div>
      
      <style jsx>{`
        .use-case-popup-component {
          width: 360px;
          font-family: system-ui, -apple-system, sans-serif;
        }
        
        .popup-header {
          position: relative;
          margin: -20px -20px 0;
        }
        
        .popup-image {
          width: 100%;
          height: 180px;
          object-fit: cover;
          border-radius: 12px 12px 0 0;
        }
        
        .category-badge {
          position: absolute;
          top: 12px;
          right: 12px;
          background: rgba(59, 130, 246, 0.9);
          color: white;
          padding: 4px 12px;
          border-radius: 16px;
          font-size: 12px;
          font-weight: 600;
          backdrop-filter: blur(4px);
        }
        
        .popup-body {
          padding: 20px;
        }
        
        .popup-title {
          font-size: 20px;
          font-weight: bold;
          margin-bottom: 8px;
          line-height: 1.3;
          word-break: break-word;
          overflow-wrap: anywhere;
        }
        
        .title-link {
          color: #1e293b;
          text-decoration: none;
          transition: color 0.2s ease;
        }
        
        .title-link:hover {
          color: #3b82f6;
        }
        
        .popup-description {
          color: #64748b;
          margin-bottom: 16px;
          line-height: 1.5;
          font-size: 14px;
          word-break: break-word;
          overflow-wrap: anywhere;
        }
        
        .factory-info {
          display: flex;
          align-items: flex-start;
          gap: 12px;
          padding: 12px;
          background: #f8fafc;
          border-radius: 8px;
          margin-bottom: 16px;
        }
        
        .factory-info .icon {
          width: 20px;
          height: 20px;
          color: #3b82f6;
          flex-shrink: 0;
          margin-top: 2px;
        }
        
        .factory-info strong {
          display: block;
          color: #1e293b;
          font-size: 14px;
          margin-bottom: 2px;
        }
        
        .location {
          display: flex;
          align-items: center;
          gap: 4px;
          color: #64748b;
          font-size: 12px;
        }
        
        .location-icon {
          width: 12px;
          height: 12px;
        }
        
        .benefits-section {
          margin-bottom: 16px;
        }
        
        .benefits-section h4 {
          font-size: 14px;
          font-weight: 600;
          color: #1e293b;
          margin-bottom: 8px;
        }
        
        .benefits-list {
          list-style: none;
          padding: 0;
          margin: 0;
          space-y: 6px;
        }
        
        .benefits-list li {
          display: flex;
          align-items: flex-start;
          gap: 8px;
          font-size: 13px;
          color: #059669;
          font-weight: 500;
        }
        
        .benefit-icon {
          width: 16px;
          height: 16px;
          color: #059669;
          flex-shrink: 0;
          margin-top: 1px;
        }
        
        .implementation-info,
        .roi-info,
        .contact-info {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 8px 12px;
          background: #eff6ff;
          border-radius: 6px;
          margin-bottom: 8px;
          font-size: 13px;
        }
        
        .roi-info {
          background: #f0fdf4;
          color: #059669;
          font-weight: 600;
        }
        
        .implementation-info .icon,
        .roi-info .icon,
        .contact-info .icon {
          width: 16px;
          height: 16px;
          color: #3b82f6;
        }
        
        .roi-info .icon {
          color: #059669;
        }
        
        .contact-info {
          flex-direction: row;
          align-items: flex-start;
        }
        
        .contact-info div {
          display: flex;
          flex-direction: column;
        }
        
        .contact-info strong {
          font-size: 13px;
          color: #1e293b;
        }
        
        .contact-info span {
          font-size: 12px;
          color: #64748b;
        }
        
        .popup-footer {
          margin-top: 20px;
          padding-top: 16px;
          border-top: 1px solid #e2e8f0;
        }
        
        .view-details-btn {
          width: 100%;
          padding: 10px 16px;
          background: #3b82f6;
          color: white;
          border: none;
          border-radius: 8px;
          font-size: 14px;
          font-weight: 600;
          cursor: pointer;
          transition: background 0.2s ease;
        }
        
        .view-details-btn:hover {
          background: #2563eb;
        }
      `}</style>
    </div>
  )
}

// Function to generate HTML string for Leaflet popup
export function generateUseCasePopupHTML(useCase: UseCase): string {
  return `
    <div class="use-case-popup-horizontal" style="width: 520px; font-family: system-ui, -apple-system, sans-serif; display: flex; height: 240px; border-radius: 16px; overflow: hidden; background: white;">
      
      <!-- Image Section (Left) -->
      <div style="width: 200px; position: relative; flex-shrink: 0;">
        <img src="${useCase.image}" alt="${useCase.title}" style="width: 100%; height: 100%; object-fit: cover;" />
        ${useCase.category ? `<span style="position: absolute; top: 12px; right: 12px; background: rgba(59, 130, 246, 0.9); color: white; padding: 4px 8px; border-radius: 12px; font-size: 11px; font-weight: 600;">${useCase.category}</span>` : ''}
      </div>
      
      <!-- Content Section (Right) -->
      <div style="flex: 1; padding: 20px; display: flex; flex-direction: column; justify-content: space-between;">
        
        <!-- Header -->
        <div>
          <h3 style="font-size: 18px; font-weight: bold; margin-bottom: 8px; line-height: 1.3; margin-top: 0;">
            <a href="${useCase.companySlug && useCase.titleSlug ? `/usecases/${useCase.companySlug}/${useCase.titleSlug}` : `/usecases/${useCase.id}` }" style="color: #1e293b; text-decoration: none;" onmouseover="this.style.color='#3b82f6'" onmouseout="this.style.color='#1e293b'">${useCase.title}</a>
          </h3>
          
          <p style="color: #64748b; margin-bottom: 12px; line-height: 1.45; font-size: 13px; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden;">${useCase.description}</p>
          
          <!-- Factory Info -->
          <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px; font-size: 12px;">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="2">
              <path d="M3 21h18M5 21V7l8-4v18M19 21V11l-6-4"></path>
            </svg>
            <strong style="color: #1e293b;">${useCase.factoryName}</strong>
            <span style="color: #64748b;">•</span>
            <span style="color: #64748b; display: flex; align-items: center; gap: 3px;">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
                <circle cx="12" cy="10" r="3"></circle>
              </svg>
              ${useCase.city}
            </span>
          </div>
        </div>
        
        <!-- Benefits -->
        <div style="margin-bottom: 12px;">
          <div style="display: flex; flex-wrap: wrap; gap: 6px;">
            ${useCase.benefits.slice(0, 2).map(benefit => `
              <span style="background: linear-gradient(135deg, #dbeafe, #bfdbfe); color: #1e40af; padding: 3px 8px; border-radius: 12px; font-size: 11px; font-weight: 600; border: 1px solid #93c5fd;">${benefit}</span>
            `).join('')}
          </div>
        </div>
        
        <!-- Footer -->
        <div style="display: flex; justify-content: space-between; align-items: center;">
          ${useCase.implementationTime ? `
            <div style="display: flex; align-items: center; gap: 6px; font-size: 11px; color: #64748b;">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="2">
                <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                <line x1="16" y1="2" x2="16" y2="6"></line>
                <line x1="8" y1="2" x2="8" y2="6"></line>
                <line x1="3" y1="10" x2="21" y2="10"></line>
              </svg>
              <span>${useCase.implementationTime}</span>
            </div>
          ` : '<div></div>'}
          
          <button class="view-details-link" onclick="window.location.href='${useCase.companySlug && useCase.titleSlug ? `/usecases/${useCase.companySlug}/${useCase.titleSlug}` : `/usecases/${useCase.id}` }'" style="padding: 10px 16px; background: #3b82f6; color: white; border: none; border-radius: 8px; font-size: 13px; font-weight: 700; cursor: pointer;" onmouseover="this.style.background='#2563eb'" onmouseout="this.style.background='#3b82f6'">
            View Details
          </button>
        </div>
        
      </div>
    </div>
  `
}