'use client'
import { usePathname, useRouter } from 'next/navigation'
import {
  LayoutDashboard, FileText, Receipt, Shield, 
  Calendar, Mic, BarChart3, Settings, LogOut, Zap,
  ChevronRight, Activity, Brain, BookOpen, MessageSquareMore
} from 'lucide-react'
import { useAppStore } from '@/store/useAppStore'
import toast from 'react-hot-toast'

type NavItem =
  | { type: 'divider'; label: string }
  | { label: string; icon: React.ElementType; href: string; badge?: string; badgeColor?: string }

const navItems: NavItem[] = [
  { label: 'Dashboard',      icon: LayoutDashboard, href: '/dashboard' },
  { label: 'GST Refund',     icon: Receipt,         href: '/gst',        badge: '₹6.84L' },
  { label: 'Income Tax',     icon: FileText,        href: '/it',         badge: '₹1.76L' },
  { label: 'TDS Recovery',   icon: Zap,             href: '/tds',        badge: '₹92K'  },
  { label: 'Notice Defense', icon: Shield,          href: '/notices'                     },
  { label: 'Compliance',     icon: Calendar,        href: '/compliance'                  },
  { label: 'Analytics',      icon: BarChart3,       href: '/analytics'                   },
  { label: 'Voice Assistant',icon: Mic,             href: '/voice'                       },
  { type: 'divider', label: 'AI v3.1 UPGRADES' },
  { label: 'Reasoning Loop', icon: Brain,           href: '/reasoning',  badge: 'NEW',  badgeColor: '#60a5fa' },
  { label: 'Human-in-Loop',  icon: Shield,          href: '/hitl',       badge: 'HITL', badgeColor: '#fbbf24' },
  { label: 'Streaming Chat', icon: MessageSquareMore, href: '/stream',   badge: 'LIVE', badgeColor: '#a855f7' },
  { label: 'Knowledge Base', icon: BookOpen,        href: '/knowledge',  badge: 'RAG',  badgeColor: '#22c55e' },
]

export default function Sidebar() {
  const pathname  = usePathname()
  const router    = useRouter()
  const { user, moneyFound, activeAgents, logout } = useAppStore()

  const handleLogout = () => {
    logout()
    localStorage.removeItem('tv_token')
    toast.success('Logged out. Agents paused.')
    router.push('/login')
  }

  return (
    <aside className="w-64 flex-shrink-0 flex flex-col h-screen sticky top-0"
      style={{ background: 'var(--bg-card)', borderRight: '1px solid var(--border)' }}>

      {/* Logo */}
      <div className="p-5 border-b" style={{ borderColor: 'var(--border)' }}>
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0"
            style={{ background: 'linear-gradient(135deg, #e11d48, #be123c)' }}>
            <span className="text-lg font-bold text-white" style={{ fontFamily: 'Rajdhani' }}>₹</span>
          </div>
          <div>
            <div className="text-base font-bold text-white" style={{ fontFamily: 'Rajdhani', letterSpacing: '0.05em' }}>TAX VAAPSI</div>
            <div className="text-xs text-slate-500">Autonomous Tax AI v3.1</div>
          </div>
        </div>
      </div>

      {/* Money found */}
      <div className="mx-3 mt-4 p-4 rounded-xl" style={{ background: 'rgba(225,29,72,0.08)', border: '1px solid rgba(225,29,72,0.2)' }}>
        <div className="text-xs text-slate-400 mb-1">Total Money Found</div>
        <div className="text-2xl font-bold text-gradient" style={{ fontFamily: 'Rajdhani' }}>
          ₹{(moneyFound.total / 100000).toFixed(2)}L
        </div>
        <div className="flex items-center gap-1.5 mt-2">
          <div className="w-2 h-2 rounded-full bg-emerald-400 agent-active" />
          <span className="text-xs text-slate-400">{activeAgents.length} agents active</span>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 p-3 space-y-0.5 overflow-y-auto mt-2">
        {navItems.map((item, idx) => {
          if ('type' in item) {
            return (
              <div key={idx} className="px-3 pt-3 pb-1">
                <span className="text-xs font-bold tracking-wider" style={{ color: 'rgba(255,255,255,0.2)' }}>
                  {item.label}
                </span>
              </div>
            )
          }
          const active = pathname === item.href ||
            (item.href !== '/dashboard' && pathname.startsWith(item.href))
          return (
            <button key={item.href}
              onClick={() => router.push(item.href)}
              className={`sidebar-link w-full text-left ${active ? 'active' : ''}`}>
              <item.icon size={16} style={active ? { color: '#f43f6e' } : {}} />
              <span className="flex-1 text-sm">{item.label}</span>
              {item.badge && (
                <span className="text-xs px-1.5 py-0.5 rounded font-mono font-bold"
                  style={{
                    background: (item.badgeColor ?? '#4ade80') + '22',
                    color: item.badgeColor ?? '#4ade80',
                  }}>
                  {item.badge}
                </span>
              )}
              {active && <ChevronRight size={13} style={{ color: '#f43f6e' }} />}
            </button>
          )
        })}
      </nav>

      {/* Agent status */}
      <div className="mx-3 mb-3 p-3 rounded-xl" style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid var(--border)' }}>
        <div className="flex items-center gap-2 mb-2">
          <Activity size={13} style={{ color: '#4ade80' }} />
          <span className="text-xs font-medium text-slate-300">Live Agent Status</span>
        </div>
        <div className="space-y-1.5">
          {[
            { name: 'GST Agent',    status: 'active',   color: '#4ade80' },
            { name: 'IT Agent',     status: 'active',   color: '#4ade80' },
            { name: 'TDS Agent',    status: 'scanning', color: '#fbbf24' },
            { name: 'Notice AI',    status: 'active',   color: '#4ade80' },
            { name: 'Planner',      status: 'standby',  color: '#60a5fa' },
            { name: 'HITL Gate',    status: 'watching', color: '#a855f7' },
          ].map(a => (
            <div key={a.name} className="flex items-center gap-2">
              <div className="w-1.5 h-1.5 rounded-full agent-active flex-shrink-0" style={{ background: a.color }} />
              <span className="text-xs text-slate-400">{a.name}</span>
              <span className="ml-auto text-xs" style={{ color: a.color }}>{a.status}</span>
            </div>
          ))}
        </div>
      </div>

      {/* User footer */}
      <div className="p-3 border-t" style={{ borderColor: 'var(--border)' }}>
        <div className="flex items-center gap-3 mb-2 px-2">
          <div className="w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold text-white flex-shrink-0"
            style={{ background: 'linear-gradient(135deg, #e11d48, #7c3aed)' }}>
            {(user?.business_name || 'U')[0].toUpperCase()}
          </div>
          <div className="flex-1 min-w-0">
            <div className="text-sm font-medium text-white truncate">{user?.business_name || 'Demo User'}</div>
            <div className="text-xs text-slate-500 truncate font-mono">{user?.gstin?.slice(0, 15) || '27AABCU9603R1ZX'}</div>
          </div>
        </div>
        <div className="flex gap-2">
          <button onClick={() => router.push('/settings')}
            className="flex-1 flex items-center justify-center gap-1 py-2 rounded-lg text-xs text-slate-400 hover:text-white transition-colors"
            style={{ background: 'rgba(255,255,255,0.04)' }}>
            <Settings size={13} />Settings
          </button>
          <button onClick={handleLogout}
            className="flex-1 flex items-center justify-center gap-1 py-2 rounded-lg text-xs text-slate-400 hover:text-red-400 transition-colors"
            style={{ background: 'rgba(255,255,255,0.04)' }}>
            <LogOut size={13} />Logout
          </button>
        </div>
      </div>
    </aside>
  )
}
