'use client'
import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Sidebar from '@/components/Sidebar'
import { useAppStore } from '@/store/useAppStore'

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter()
  const isAuthenticated = useAppStore(s => s.isAuthenticated)

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login')
    }
  }, [isAuthenticated, router])

  if (!isAuthenticated) return null

  return (
    <div className="flex min-h-screen bg-grid" style={{ background: 'var(--bg-deep)' }}>
      <Sidebar />
      <main className="flex-1 overflow-auto">
        {children}
      </main>
    </div>
  )
}
