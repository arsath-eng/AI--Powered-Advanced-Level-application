'use client'

import { Separator } from '@/components/ui/separator'

interface ChatHeaderProps {
  title?: string
}

export function ChatHeader({ title = "Chat" }: ChatHeaderProps) {
  return (
    <div>
      <div className="flex items-center justify-between p-4">
        <h1 className="text-xl font-semibold">{title}</h1>
      </div>
      <Separator />
    </div>
  )
}