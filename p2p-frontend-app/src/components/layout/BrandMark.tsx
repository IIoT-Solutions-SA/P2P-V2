import { Link } from "react-router-dom"
import peerLinkSidebarLogo from "@/assets/peerlink-logo-dark-sidebar.svg"

export function BrandMark({ compact = false }: { compact?: boolean }) {
  return (
    <Link to="/home" className="flex min-w-0 items-center" aria-label="PeerLink home">
      {compact ? (
        <span className="relative grid size-9 place-items-center" aria-hidden="true">
          <span className="absolute size-6 rotate-45 border-2 border-[#76c5bd]" />
          <span className="absolute size-3 rotate-45 bg-[#76c5bd]" />
        </span>
      ) : (
        <img
          src={peerLinkSidebarLogo}
          alt="Saudi Arabia Centre for the Fourth Industrial Revolution and PeerLink for SMEs"
          className="h-auto w-full max-w-[188px] object-contain object-left"
        />
      )}
    </Link>
  )
}
