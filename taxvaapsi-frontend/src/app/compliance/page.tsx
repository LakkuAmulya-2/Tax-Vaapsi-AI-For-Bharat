'use client'
import { useState } from 'react'
import DashboardLayout from '@/components/DashboardLayout'
import { Calendar, Bell, AlertTriangle, CheckCircle, Clock } from 'lucide-react'
import toast from 'react-hot-toast'

const DEADLINES = [
  { date: '2024-03-15', form: 'Advance Tax', desc: '4th installment - Q4 advance tax payment', daysLeft: 8, status: 'urgent', penalty: '₹5,000+' },
  { date: '2024-03-20', form: 'GSTR-3B', desc: 'Monthly return for February 2024', daysLeft: 13, status: 'upcoming', penalty: '₹10,000' },
  { date: '2024-03-31', form: 'GSTR-1', desc: 'Outward supplies for February 2024', daysLeft: 24, status: 'normal', penalty: '₹5,000' },
  { date: '2024-04-07', form: 'TDS Payment', desc: 'TDS deducted in March 2024', daysLeft: 31, status: 'normal', penalty: '1.5%/month' },
  { date: '2024-04-11', form: 'GSTR-1', desc: 'Outward supplies for March 2024', daysLeft: 35, status: 'normal', penalty: '₹5,000' },
  { date: '2024-04-20', form: 'GSTR-3B', desc: 'Monthly return for March 2024', daysLeft: 44, status: 'normal', penalty: '₹10,000' },
  { date: '2024-05-31', form: 'TDS Return', desc: 'Q4 TDS Return (Form 24Q)', daysLeft: 85, status: 'future', penalty: '₹200/day' },
  { date: '2024-07-31', form: 'ITR Filing', desc: 'Income Tax Return for FY 2023-24', daysLeft: 146, status: 'future', penalty: '₹5,000-10,000' },
]

const statusColor: Record<string, string> = {
  urgent: '#ef4444', upcoming: '#f59e0b', normal: '#60a5fa', future: '#94a3b8'
}
const statusBadge: Record<string, string> = {
  urgent: 'badge-danger', upcoming: 'badge-warning', normal: 'badge-info', future: ''
}

export default function CompliancePage() {
  const [filter, setFilter] = useState<'all' | 'urgent' | 'upcoming'>('all')

  const filtered = DEADLINES.filter(d =>
    filter === 'all' ? true : d.status === filter || (filter === 'upcoming' && d.status === 'normal')
  )

  return (
    <DashboardLayout>
      <div className="p-6 space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-white" style={{ fontFamily: 'Rajdhani' }}>Compliance Calendar</h1>
          <p className="text-slate-400 text-sm mt-1">50+ deadline tracking • Smart reminders • Pre-filled forms • Time-barred warnings</p>
        </div>

        <div className="grid grid-cols-3 gap-4">
          {[
            { label: 'Urgent (≤15 days)', count: DEADLINES.filter(d => d.daysLeft <= 15).length, color: '#ef4444', icon: AlertTriangle },
            { label: 'Upcoming', count: DEADLINES.filter(d => d.daysLeft > 15 && d.daysLeft <= 30).length, color: '#f59e0b', icon: Clock },
            { label: 'Future', count: DEADLINES.filter(d => d.daysLeft > 30).length, color: '#4ade80', icon: CheckCircle },
          ].map(s => (
            <div key={s.label} className="glass rounded-2xl p-4 flex items-center gap-4">
              <div className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0"
                style={{ background: `${s.color}20` }}>
                <s.icon size={20} style={{ color: s.color }} />
              </div>
              <div>
                <div className="text-2xl font-bold" style={{ fontFamily: 'Rajdhani', color: s.color }}>{s.count}</div>
                <div className="text-xs text-slate-400">{s.label}</div>
              </div>
            </div>
          ))}
        </div>

        <div className="flex gap-2">
          {(['all', 'urgent', 'upcoming'] as const).map(f => (
            <button key={f} onClick={() => setFilter(f)}
              className={`px-4 py-2 rounded-xl text-sm font-semibold transition-all ${filter === f ? 'text-white' : 'text-slate-400'}`}
              style={filter === f ? { background: 'linear-gradient(135deg, #e11d48, #be123c)' } : { background: 'rgba(255,255,255,0.05)' }}>
              {f.charAt(0).toUpperCase() + f.slice(1)}
            </button>
          ))}
        </div>

        <div className="glass rounded-2xl overflow-hidden">
          <div className="divide-y" style={{ borderColor: 'var(--border)' }}>
            {filtered.map((d, i) => (
              <div key={i} className="flex items-center gap-4 p-4 hover:bg-white/5 transition-colors">
                <div className="w-14 text-center flex-shrink-0">
                  <div className="text-lg font-bold" style={{ fontFamily: 'Rajdhani', color: statusColor[d.status] }}>{d.daysLeft}</div>
                  <div className="text-xs text-slate-500">days</div>
                </div>
                <div className="w-1 h-12 rounded-full flex-shrink-0" style={{ background: statusColor[d.status] }} />
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-0.5">
                    <span className="text-sm font-bold text-white">{d.form}</span>
                    {d.status !== 'future' && (
                      <span className={`text-xs px-2 py-0.5 rounded-full ${statusBadge[d.status]}`}>
                        {d.status === 'urgent' ? '⚠️ URGENT' : d.status.toUpperCase()}
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-slate-400 truncate">{d.desc}</p>
                  <p className="text-xs mt-0.5" style={{ color: '#f59e0b' }}>Penalty if missed: {d.penalty}</p>
                </div>
                <div className="text-right flex-shrink-0">
                  <div className="text-xs text-slate-500">{new Date(d.date).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' })}</div>
                  <div className="flex gap-2 mt-2">
                    <button onClick={() => toast.success(`Reminder set for ${d.form}!`)}
                      className="text-xs px-2 py-1 rounded-lg flex items-center gap-1 text-slate-300 hover:text-white"
                      style={{ background: 'rgba(255,255,255,0.06)' }}>
                      <Bell size={11} />Set
                    </button>
                    <button onClick={() => toast.success('Pre-filled form opened!')}
                      className="text-xs px-2 py-1 rounded-lg text-white"
                      style={{ background: 'linear-gradient(135deg, #e11d48, #be123c)' }}>
                      File
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </DashboardLayout>
  )
}
