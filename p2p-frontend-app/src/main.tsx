import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { SuperTokensWrapper } from "supertokens-auth-react"
import './index.css'
import './config/supertokens'
import App from './App.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <SuperTokensWrapper>
      <App />
    </SuperTokensWrapper>
  </StrictMode>,
)
