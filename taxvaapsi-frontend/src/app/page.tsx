'use client'
import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAppStore } from '@/store/useAppStore'

export default function Home() {
  const router = useRouter()
  const isAuthenticated = useAppStore(s => s.isAuthenticated)
  
  useEffect(() => {
    if (isAuthenticated) {
      router.replace('/dashboard')
    } else {
      router.replace('/login')
    }
  }, [isAuthenticated, router])

  return (
    <div className="min-h-screen flex items-center justify-center" style={{ background: 'var(--bg-deep)' }}>
      <div className="text-center">
        <div className="w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-4 glow-red"
          style={{ background: 'linear-gradient(135deg, #e11d48, #be123c)' }}>
          <span className="text-3xl font-bold text-white" style={{ fontFamily: 'Rajdhani' }}>₹</span>
        </div>
        <div className="text-white font-bold text-xl" style={{ fontFamily: 'Rajdhani' }}>TAX VAAPSI</div>
        <div className="text-slate-400 text-sm mt-1">Loading...</div>
      </div>
    </div>
  )
}
