// components/chat/sidebar-toggle.tsx
'use client'

import { Button } from '@/components/ui/button'
import { PanelLeftClose, PanelLeftOpen } from 'lucide-react'

interface SidebarToggleProps {
  isOpen: boolean
  setIsOpen: (isOpen: boolean) => void
}

export function SidebarToggle({ isOpen, setIsOpen }: SidebarToggleProps) {
  return (
    <Button
      variant="ghost"
      size="icon"
      className="size-10 rounded-full hover:bg-muted"
      onClick={() => setIsOpen(!isOpen)}
    >
      {isOpen ? (
        <PanelLeftClose className="size-5" />
      ) : (
        <PanelLeftOpen className="size-5" />
      )}
    </Button>
  )
}