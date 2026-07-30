import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { SuperTokensWrapper } from "supertokens-auth-react"
import './index.css'
import './config/supertokens'
import App from './App.tsx'

if ('serviceWorker' in navigator) {
  let reloadingForServiceWorker = false
  navigator.serviceWorker.addEventListener('controllerchange', () => {
    if (reloadingForServiceWorker) return
    reloadingForServiceWorker = true
    window.location.reload()
  })
  window.addEventListener('load', () => {
    void navigator.serviceWorker.register('/sw.js').then((registration) => registration.update())
  })
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <SuperTokensWrapper>
      <App />
    </SuperTokensWrapper>
  </StrictMode>,
)
