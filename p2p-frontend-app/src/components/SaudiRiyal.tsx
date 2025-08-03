import React from 'react'
import '@emran-alhaddad/saudi-riyal-font/index.css'

interface SaudiRiyalProps {
  className?: string
  style?: React.CSSProperties
}

// Saudi Riyal symbol component using the CSS class method (recommended)
export default function SaudiRiyal({ className = "", style = {} }: SaudiRiyalProps) {
  return (
    <span 
      className={`icon-saudi_riyal ${className}`}
      style={style}
    />
  )
}

// Alternative method using Unicode (fallback)
export function SaudiRiyalUnicode({ className = "", style = {} }: SaudiRiyalProps) {
  return (
    <span 
      className={`saudi-riyal-symbol ${className}`}
      style={{ 
        fontFamily: 'saudi_riyal, Arial, sans-serif',
        ...style 
      }}
    >
      &#xE900;
    </span>
  )
}

// Fallback using standard Unicode Riyal symbol
export function SaudiRiyalFallback({ className = "" }: { className?: string }) {
  return <span className={className}>﷼</span>
}

// Currency formatter component for displaying amounts with Saudi Riyal symbol
interface CurrencyProps {
  amount: string | number
  className?: string
  showSymbol?: boolean
  method?: 'css-class' | 'unicode' | 'fallback'
}

export function SaudiRiyalCurrency({ 
  amount, 
  className = "", 
  showSymbol = true, 
  method = 'css-class' // Use custom font by default
}: CurrencyProps) {
  const renderSymbol = () => {
    if (!showSymbol) return null
    
    switch (method) {
      case 'css-class':
        return <SaudiRiyal className="inline-block mr-1" />
      case 'unicode':
        return <SaudiRiyalUnicode className="inline-block mr-1" />
      case 'fallback':
        return <SaudiRiyalFallback className="inline-block mr-1" />
      default:
        return <SaudiRiyal className="inline-block mr-1" />
    }
  }

  return (
    <span className={className}>
      {renderSymbol()}
      {amount}
    </span>
  )
}

// Robust currency component that tries multiple methods with font detection
export function RobustSaudiRiyalCurrency({ amount, className = "" }: Omit<CurrencyProps, 'method'>) {
  const [fontLoaded, setFontLoaded] = React.useState(false)

  React.useEffect(() => {
    // Check if the font is loaded
    if ('fonts' in document) {
      document.fonts.ready.then(() => {
        const fontFace = [...document.fonts.values()].find(
          font => font.family === 'saudi_riyal'
        )
        setFontLoaded(!!fontFace)
      })
    }
  }, [])

  return (
    <span className={className}>
      {fontLoaded ? (
        <span className="icon-saudi_riyal inline-block mr-1" />
      ) : (
        <span className="inline-block mr-1">﷼</span>
      )}
      {amount}
    </span>
  )
}

// Enhanced currency component with font fallback detection
export function EnhancedSaudiRiyalCurrency({ amount, className = "" }: Omit<CurrencyProps, 'method'>) {
  return (
    <span className={className}>
      <span 
        className="inline-block mr-1 relative"
        style={{
          fontFamily: 'saudi_riyal, Arial, sans-serif'
        }}
      >
        {/* Primary: Custom font icon */}
        <span className="icon-saudi_riyal opacity-100" />
        {/* Fallback: Standard Unicode (hidden when custom font loads) */}
        <span 
          className="absolute top-0 left-0 opacity-0"
          style={{
            fontFamily: 'Arial, sans-serif',
            opacity: 'var(--fallback-opacity, 0)'
          }}
        >
          ﷼
        </span>
      </span>
      {amount}
    </span>
  )
}