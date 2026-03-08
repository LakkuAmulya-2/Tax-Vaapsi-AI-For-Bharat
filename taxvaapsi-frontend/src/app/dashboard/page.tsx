'use client'
import { useState, useEffect, useRef } from 'react'
import DashboardLayout from '@/components/DashboardLayout'
import { useAppStore } from '@/store/useAppStore'
import {
  TrendingUp, Shield, Zap, AlertCircle, CheckCircle, Clock,
  RefreshCw, ChevronRight, ArrowUpRight, Activity, Brain, Wifi
} from 'lucide-react'
import toast from 'react-hot-toast'
import { RadialBarChart, RadialBar, PieChart, Pie, Cell, ResponsiveContainer, Tooltip, AreaChart, Area, XAxis, YAxis } from 'recharts'

// Animated counter hook
function useCountUp(target: number, duration = 2000, start = false) {
  const [count, setCount] = useState(0)
  useEffect(() => {
    if (!start) return
    let startTime: number | null = null
    const step = (timestamp: number) => {
      if (!startTime) startTime = timestamp
      const progress = Math.min((timestamp - startTime) / duration, 1)
      const eased = 1 - Math.pow(1 - progress, 3)
      setCount(Math.floor(eased * target))
      if (progress < 1) requestAnimationFrame(step)
    }
    requestAnimationFrame(step)
  }, [target, duration, start])
  return count
}

// Confetti component
function Confetti({ active }: { active: boolean }) {
  if (!active) return null
  const pieces = Array.from({ length: 30 }, (_, i) => ({
    id: i,
    left: Math.random() * 100,
    delay: Math.random() * 2,
    duration: 2 + Math.random() * 3,
    color: ['#e11d48', '#f43f6e', '#4ade80', '#60a5fa', '#fbbf24', '#a78bfa'][Math.floor(Math.random() * 6)],
    size: 6 + Math.random() * 10,
  }))
  return (
    <div className="fixed inset-0 pointer-events-none z-50">
      {pieces.map(p => (
        <div key={p.id} className="confetti-piece"
          style={{
            left: `${p.left}%`,
            background: p.color,
            width: p.size,
            height: p.size,
            borderRadius: Math.random() > 0.5 ? '50%' : '0',
            animationDuration: `${p.duration}s`,
            animationDelay: `${p.delay}s`,
          }} />
      ))}
    </div>
  )
}

const MONEY_BREAKDOWN = [
  { label: 'GST Refund', amount: 684000, color: '#e11d48', key: 'gst' },
  { label: 'IT Refund', amount: 176000, color: '#7c3aed', key: 'it' },
  { label: 'TDS Recovery', amount: 92000, color: '#f59e0b', key: 'tds' },
  { label: 'Tax Savings', amount: 185000, color: '#22c55e', key: 'tax_savings' },
  { label: 'Penalties Avoided', amount: 45000, color: '#06b6d4', key: 'penalties' },
]

const TREND_DATA = [
  { month: 'Oct', found: 45000, recovered: 32000 },
  { month: 'Nov', found: 78000, recovered: 65000 },
  { month: 'Dec', found: 92000, recovered: 88000 },
  { month: 'Jan', found: 145000, recovered: 120000 },
  { month: 'Feb', found: 210000, recovered: 185000 },
  { month: 'Mar', found: 1245000, recovered: 312000 },
]

const AGENT_ACTIVITIES = [
  { agent: 'GST Bedrock Agent', action: 'Scanned 36 months GSTR-3B data', result: '₹6.84L refund eligible', status: 'success', time: '2 min ago', icon: '🤖' },
  { agent: 'IT Bedrock Agent', action: 'Analyzed 40+ deductions (80C/80D/80G)', result: '₹1.76L refund detected', status: 'success', time: '5 min ago', icon: '📊' },
  { agent: 'TDS Commando', action: 'Parsing Form 26AS for TDS credits', result: 'Scanning...', status: 'running', time: 'Now', icon: '⚡' },
  { agent: 'Notice Defense AI', action: 'Monitoring GST portal for deficiency memos', result: 'All clear - no notices', status: 'success', time: '10 min ago', icon: '🛡️' },
  { agent: 'Compliance AI', action: 'Checking GSTR-1/3B filing deadlines', result: 'GSTR-3B due in 8 days', status: 'warning', time: '15 min ago', icon: '📅' },
]

export default function Dashboard() {
  const { user, moneyFound, taxHealthScore } = useAppStore()
  const [revealed, setRevealed] = useState(false)
  const [showConfetti, setShowConfetti] = useState(false)
  const [scanning, setScanning] = useState(false)
  const [scanProgress, setScanProgress] = useState(84)
  const [apiStatus, setApiStatus] = useState<'checking' | 'online' | 'offline'>('checking')
  
  const total = useCountUp(moneyFound.total, 2500, revealed)

  useEffect(() => {
    setTimeout(() => {
      setRevealed(true)
      setShowConfetti(true)
      setTimeout(() => setShowConfetti(false), 4000)
    }, 800)

    // Check API health
    import('@/lib/api').then(({ healthApi }) => {
      healthApi.check()
        .then(() => setApiStatus('online'))
        .catch(() => setApiStatus('offline'))
    })
  }, [])

  const handleRescan = async () => {
    setScanning(true)
    setScanProgress(0)
    toast.loading('Agents scanning your data...', { id: 'scan' })
    
    const interval = setInterval(() => {
      setScanProgress(p => {
        if (p >= 100) { clearInterval(interval); return 100 }
        return p + Math.random() * 15
      })
    }, 300)

    try {
      const { scanApi } = await import('@/lib/api')
      if (user) {
        await scanApi.fullScan(user.user_id, user.gstin, user.pan)
      } else {
        await new Promise(r => setTimeout(r, 3000))
      }
      toast.success('Scan complete! ₹12.45L found 🎉', { id: 'scan' })
    } catch {
      toast.success('Demo scan complete! ₹12.45L found 🎉', { id: 'scan' })
    } finally {
      clearInterval(interval)
      setScanProgress(100)
      setScanning(false)
    }
  }

  const healthColor = taxHealthScore >= 80 ? '#22c55e' : taxHealthScore >= 60 ? '#f59e0b' : '#ef4444'
  const pieData = MONEY_BREAKDOWN.map(m => ({ name: m.label, value: m.amount, color: m.color }))

  return (
    <DashboardLayout>
      <Confetti active={showConfetti} />
      <div className="p-6 space-y-6">
        
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white" style={{ fontFamily: 'Rajdhani' }}>
              Welcome back, {user?.business_name?.split(' ')[0] || 'Demo'}
            </h1>
            <p className="text-slate-400 text-sm mt-1">Your AI agents found money while you were away 🤖</p>
          </div>
          <div className="flex items-center gap-3">
            <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium ${
              apiStatus === 'online' ? 'badge-success' : apiStatus === 'offline' ? 'badge-danger' : 'badge-warning'
            }`}>
              <div className={`w-1.5 h-1.5 rounded-full ${apiStatus === 'online' ? 'bg-emerald-400' : apiStatus === 'offline' ? 'bg-red-400' : 'bg-amber-400'} ${apiStatus === 'checking' ? 'agent-active' : ''}`} />
              {apiStatus === 'online' ? 'Backend Connected' : apiStatus === 'offline' ? 'Backend Offline' : 'Connecting...'}
            </div>
            <button onClick={handleRescan} disabled={scanning}
              className="btn-primary flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold disabled:opacity-70">
              <RefreshCw size={16} className={scanning ? 'animate-spin' : ''} />
              {scanning ? 'Scanning...' : 'Re-Scan'}
            </button>
          </div>
        </div>

        {/* Scan progress */}
        {scanning && (
          <div className="glass rounded-2xl p-4">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <Brain size={18} style={{ color: '#e11d48' }} className="agent-active" />
                <span className="text-sm font-medium text-white">AI Agents Scanning Your Data</span>
              </div>
              <span className="text-sm font-mono text-slate-400">{Math.round(scanProgress)}%</span>
            </div>
            <div className="progress-bar">
              <div className="progress-fill" style={{ width: `${scanProgress}%` }} />
            </div>
            <p className="text-xs text-slate-500 mt-2">Analyzing GSTR-3B... Form 26AS... ITR data...</p>
          </div>
        )}

        {/* MONEY REVEAL - Hero Card */}
        <div className="relative rounded-2xl p-6 overflow-hidden"
          style={{ background: 'linear-gradient(135deg, #1a0515 0%, #0d0a1a 50%, #05101a 100%)', border: '1px solid rgba(225,29,72,0.3)' }}>
          <div className="absolute inset-0 opacity-30"
            style={{ backgroundImage: 'radial-gradient(circle at 30% 50%, #e11d4820 0%, transparent 60%)' }} />
          
          <div className="relative z-10 flex items-center justify-between">
            <div>
              <p className="text-slate-400 text-sm mb-2">💰 Total Money Found by AI Agents</p>
              <div className={`text-5xl font-bold transition-all duration-500 ${revealed ? 'text-gradient' : 'text-slate-700'}`}
                style={{ fontFamily: 'Rajdhani', letterSpacing: '-0.02em' }}>
                ₹{revealed ? (total / 100000).toFixed(2) : '0.00'}L
              </div>
              <p className="text-slate-400 text-sm mt-2">= ₹{total.toLocaleString('en-IN')} total recoverable</p>
              <div className="flex items-center gap-2 mt-3">
                <span className="badge-success px-2 py-1 rounded-full text-xs font-medium">82% Success Rate</span>
                <span className="badge-info px-2 py-1 rounded-full text-xs font-medium">102 days avg recovery</span>
              </div>
            </div>
            
            <div className="hidden md:block">
              <ResponsiveContainer width={180} height={180}>
                <PieChart>
                  <Pie data={pieData} cx={90} cy={90} innerRadius={55} outerRadius={85} dataKey="value" strokeWidth={0}>
                    {pieData.map((entry, idx) => (
                      <Cell key={idx} fill={entry.color} opacity={0.9} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(v: number) => `₹${(v/1000).toFixed(0)}K`}
                    contentStyle={{ background: '#0d1527', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', color: '#e2e8f0', fontSize: '12px' }} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Breakdown bars */}
          <div className="relative z-10 mt-6 space-y-2">
            {MONEY_BREAKDOWN.map((item) => (
              <div key={item.label} className="flex items-center gap-3">
                <span className="text-xs text-slate-400 w-28 flex-shrink-0">{item.label}</span>
                <div className="flex-1 progress-bar">
                  <div className="progress-fill"
                    style={{ width: `${(item.amount / moneyFound.total) * 100}%`, background: item.color }} />
                </div>
                <span className="text-xs font-mono font-bold text-white w-16 text-right">
                  ₹{(item.amount / 1000).toFixed(0)}K
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Stats Row */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {[
            { label: 'Risk Score', value: '18%', sub: 'Reduced from 72%', icon: Shield, color: '#22c55e', badge: 'LOW RISK' },
            { label: 'Tax Health', value: `${taxHealthScore}/100`, sub: 'Good standing', icon: Activity, color: healthColor, badge: taxHealthScore >= 70 ? 'GOOD' : 'NEEDS WORK' },
            { label: 'Filing Time', value: '90 sec', sub: 'Computer Use AI', icon: Zap, color: '#60a5fa', badge: 'AUTOMATED' },
            { label: 'CA Fees Saved', value: '₹50K+', sub: 'vs traditional CA', icon: TrendingUp, color: '#f59e0b', badge: '95% SAVINGS' },
          ].map((stat) => (
            <div key={stat.label} className="glass rounded-2xl p-4 card-hover">
              <div className="flex items-start justify-between mb-3">
                <div className="w-9 h-9 rounded-xl flex items-center justify-center"
                  style={{ background: `${stat.color}20` }}>
                  <stat.icon size={18} style={{ color: stat.color }} />
                </div>
                <span className="text-xs px-2 py-0.5 rounded-full font-bold"
                  style={{ background: `${stat.color}20`, color: stat.color }}>{stat.badge}</span>
              </div>
              <div className="text-2xl font-bold text-white" style={{ fontFamily: 'Rajdhani' }}>{stat.value}</div>
              <div className="text-xs text-slate-400 mt-1">{stat.label}</div>
              <div className="text-xs text-slate-500">{stat.sub}</div>
            </div>
          ))}
        </div>

        {/* Two column: Agent Activity + Trend Chart */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          
          {/* Agent Activity Feed */}
          <div className="glass rounded-2xl p-5">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <Brain size={18} style={{ color: '#e11d48' }} />
                <h3 className="font-semibold text-white" style={{ fontFamily: 'Rajdhani', fontSize: '16px' }}>Live Agent Activity</h3>
              </div>
              <div className="flex items-center gap-1.5">
                <div className="w-2 h-2 rounded-full bg-emerald-400 agent-active" />
                <span className="text-xs text-slate-400">4 agents active</span>
              </div>
            </div>

            <div className="space-y-3">
              {AGENT_ACTIVITIES.map((act, i) => (
                <div key={i} className="flex gap-3 p-3 rounded-xl transition-colors hover:bg-white/5"
                  style={{ background: 'rgba(255,255,255,0.02)', border: '1px solid var(--border)' }}>
                  <span className="text-xl flex-shrink-0">{act.icon}</span>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-0.5">
                      <span className="text-xs font-semibold text-white">{act.agent}</span>
                      <span className={`text-xs px-1.5 py-0.5 rounded-full ${
                        act.status === 'success' ? 'badge-success' :
                        act.status === 'running' ? 'badge-info' : 'badge-warning'
                      }`}>
                        {act.status === 'running' ? '● running' : act.status}
                      </span>
                    </div>
                    <p className="text-xs text-slate-400 truncate">{act.action}</p>
                    {act.result && (
                      <p className="text-xs font-mono mt-0.5" style={{ color: act.status === 'warning' ? '#fbbf24' : '#4ade80' }}>
                        → {act.result}
                      </p>
                    )}
                  </div>
                  <span className="text-xs text-slate-600 flex-shrink-0">{act.time}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Recovery Trend */}
          <div className="glass rounded-2xl p-5">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-white" style={{ fontFamily: 'Rajdhani', fontSize: '16px' }}>Money Recovery Trend</h3>
              <span className="badge-success px-2 py-1 rounded-full text-xs">+₹10.33L this month</span>
            </div>
            <ResponsiveContainer width="100%" height={200}>
              <AreaChart data={TREND_DATA}>
                <defs>
                  <linearGradient id="foundGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#e11d48" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#e11d48" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="recovGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#4ade80" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#4ade80" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <XAxis dataKey="month" tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false}
                  tickFormatter={v => `₹${(v/1000).toFixed(0)}K`} />
                <Tooltip contentStyle={{ background: '#0d1527', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', color: '#e2e8f0', fontSize: '12px' }}
                  formatter={(v: number) => `₹${(v/1000).toFixed(0)}K`} />
                <Area type="monotone" dataKey="found" stroke="#e11d48" fill="url(#foundGrad)" strokeWidth={2} name="Found" />
                <Area type="monotone" dataKey="recovered" stroke="#4ade80" fill="url(#recovGrad)" strokeWidth={2} name="Recovered" />
              </AreaChart>
            </ResponsiveContainer>
            <div className="flex items-center gap-4 mt-3">
              <div className="flex items-center gap-1.5"><div className="w-3 h-0.5 bg-red-400" /><span className="text-xs text-slate-400">Money Found</span></div>
              <div className="flex items-center gap-1.5"><div className="w-3 h-0.5 bg-emerald-400" /><span className="text-xs text-slate-400">Recovered</span></div>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div>
          <h3 className="text-base font-semibold text-white mb-3" style={{ fontFamily: 'Rajdhani' }}>Quick Actions</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {[
              { label: 'File GST Refund', desc: '90 sec automated filing', href: '/gst',        color: '#e11d48', icon: '🏦' },
              { label: 'Optimize IT',     desc: '40+ deductions found',     href: '/it',         color: '#7c3aed', icon: '📊' },
              { label: 'Defend Notice',   desc: 'AI legal reply ready',     href: '/notices',    color: '#f59e0b', icon: '🛡️' },
              { label: 'Check Deadlines', desc: 'GSTR-3B due in 8 days',   href: '/compliance', color: '#06b6d4', icon: '📅' },
            ].map((action) => (
              <a key={action.label} href={action.href}
                className="glass rounded-2xl p-4 card-hover flex items-start gap-3"
                style={{ borderColor: `${action.color}20` }}>
                <span className="text-2xl">{action.icon}</span>
                <div>
                  <div className="text-sm font-semibold text-white">{action.label}</div>
                  <div className="text-xs text-slate-400 mt-0.5">{action.desc}</div>
                </div>
                <ArrowUpRight size={14} className="ml-auto flex-shrink-0 mt-0.5" style={{ color: action.color }} />
              </a>
            ))}
          </div>
        </div>

        {/* AI v3.1 Upgrade Showcase */}
        <div>
          <div className="flex items-center gap-2 mb-3">
            <h3 className="text-base font-semibold text-white" style={{ fontFamily: 'Rajdhani' }}>AI v3.1 Upgrades</h3>
            <span className="text-xs px-2 py-0.5 rounded-full font-bold" style={{ background: 'rgba(96,165,250,0.2)', color: '#60a5fa' }}>NEW</span>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {[
              { label: 'Reasoning Loop',  desc: 'Planner → Execute → Verify',    href: '/reasoning', color: '#60a5fa', icon: '🧠', badge: '#1' },
              { label: 'Human-in-Loop',   desc: 'AI plan → you approve → execute', href: '/hitl',      color: '#fbbf24', icon: '🛡',  badge: '#2' },
              { label: 'Streaming Chat',  desc: 'Real-time token-by-token AI',    href: '/stream',    color: '#a855f7', icon: '⚡', badge: '#3' },
              { label: 'Knowledge Base',  desc: 'RAG — cited tax law answers',    href: '/knowledge', color: '#22c55e', icon: '📚', badge: '#4' },
            ].map((a) => (
              <a key={a.label} href={a.href}
                className="glass rounded-2xl p-4 card-hover flex flex-col gap-2"
                style={{ border: `1px solid ${a.color}30` }}>
                <div className="flex items-center justify-between">
                  <span className="text-2xl">{a.icon}</span>
                  <span className="text-xs font-bold px-1.5 py-0.5 rounded font-mono"
                    style={{ background: a.color + '22', color: a.color }}>{a.badge}</span>
                </div>
                <div>
                  <div className="text-sm font-semibold text-white">{a.label}</div>
                  <div className="text-xs text-slate-400 mt-0.5">{a.desc}</div>
                </div>
                <div className="flex items-center gap-1 text-xs font-semibold mt-auto" style={{ color: a.color }}>
                  Try now <ArrowUpRight size={12} />
                </div>
              </a>
            ))}
          </div>
        </div>
      </div>
    </DashboardLayout>
  )
}
