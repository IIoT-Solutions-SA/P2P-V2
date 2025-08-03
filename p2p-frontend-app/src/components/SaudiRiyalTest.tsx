import React from 'react'
import '@emran-alhaddad/saudi-riyal-font/index.css'
import { SaudiRiyalCurrency, RobustSaudiRiyalCurrency, EnhancedSaudiRiyalCurrency } from './SaudiRiyal'

// Test component to debug Saudi Riyal font rendering
export default function SaudiRiyalTest() {
  const [fontLoaded, setFontLoaded] = React.useState(false)

  React.useEffect(() => {
    // Check if the font is loaded
    const checkFont = () => {
      if ('fonts' in document) {
        document.fonts.ready.then(() => {
          const fontFaces = [...document.fonts.values()]
          const saudiFont = fontFaces.find(font => font.family === 'saudi_riyal')
          setFontLoaded(!!saudiFont)
          console.log('Saudi Riyal font loaded:', !!saudiFont)
          console.log('All fonts:', fontFaces.map(f => f.family))
        })
      }
    }
    
    checkFont()
    // Also check after a delay
    setTimeout(checkFont, 1000)
  }, [])

  return (
    <div className="p-6 bg-white rounded-lg border border-gray-200 shadow-sm m-4">
      <h3 className="text-xl font-bold mb-6 text-gray-900">Saudi Riyal Font Test</h3>
      
      <div className="space-y-4">
        <div className="p-3 bg-gray-50 rounded">
          <strong>Font Status:</strong>
          <span className={`ml-2 px-2 py-1 rounded text-sm ${fontLoaded ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
            {fontLoaded ? '✅ Font Loaded' : '❌ Font Not Loaded'}
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-3">
            <div className="flex items-center">
              <strong className="w-32">CSS Class:</strong>
              <span className="icon-saudi_riyal text-2xl ml-2 bg-blue-50 px-2 py-1 rounded"></span>
            </div>
            
            <div className="flex items-center">
              <strong className="w-32">Unicode:</strong>
              <span style={{ fontFamily: 'saudi_riyal', fontSize: '24px' }} className="ml-2 bg-blue-50 px-2 py-1 rounded">&#xE900;</span>
            </div>
            
            <div className="flex items-center">
              <strong className="w-32">Fallback:</strong>
              <span className="ml-2 text-2xl bg-gray-50 px-2 py-1 rounded">﷼</span>
            </div>
          </div>

          <div className="space-y-3">
            <div className="flex items-center">
              <strong className="w-32">Standard:</strong>
              <SaudiRiyalCurrency amount="1,000" className="ml-2 bg-green-50 px-2 py-1 rounded" />
            </div>
            
            <div className="flex items-center">
              <strong className="w-32">Robust:</strong>
              <RobustSaudiRiyalCurrency amount="2,500" className="ml-2 bg-yellow-50 px-2 py-1 rounded" />
            </div>
            
            <div className="flex items-center">
              <strong className="w-32">Enhanced:</strong>
              <EnhancedSaudiRiyalCurrency amount="5,000" className="ml-2 bg-purple-50 px-2 py-1 rounded" />
            </div>
          </div>
        </div>

        <div className="mt-4 p-3 bg-blue-50 rounded">
          <strong>Currency Examples:</strong>
          <div className="mt-2 flex flex-wrap gap-4">
            <SaudiRiyalCurrency amount="450K" className="font-semibold" />
            <SaudiRiyalCurrency amount="2.3M" className="font-semibold" />
            <SaudiRiyalCurrency amount="285,000" className="font-semibold" />
          </div>
        </div>
      </div>
    </div>
  )
}