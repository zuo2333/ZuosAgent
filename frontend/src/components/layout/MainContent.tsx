import { ReactNode } from 'react'

interface MainContentProps {
  children: ReactNode
}

export function MainContent({ children }: MainContentProps) {
  return (
    <main className="flex-1 flex flex-col h-full bg-transparent">
      {children}
    </main>
  )
}
