'use client'
import DashboardLayout from '@/components/DashboardLayout'
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, BarChart, Bar, RadarChart, Radar, PolarGrid, PolarAngleAxis, PieChart, Pie, Cell } from 'recharts'

const MONTHLY_DATA = [
  { month: 'Sep', gst: 45000, it: 20000, tds: 15000, savings: 30000 },
  { month: 'Oct', gst: 95000, it: 35000, tds: 22000, savings: 45000 },
  { month: 'Nov', gst: 145000, it: 48000, tds: 31000, savings: 72000 },
  { month: 'Dec', gst: 210000, it: 76000, tds: 45000, savings: 98000 },
  { month: 'Jan', gst: 380000, it: 102000, tds: 62000, savings: 135000 },
  { month: 'Feb', gst: 520000, it: 134000, tds: 78000, savings: 168000 },
  { month: 'Mar', gst: 684000, it: 176000, tds: 92000, savings: 185000 },
]

const RADAR_DATA = [
  { area: 'GST Filing', score: 78 },
  { area: 'IT Compliance', score: 85 },
  { area: 'TDS Recovery', score: 62 },
  { area: 'Deductions', score: 45 },
  { area: 'Notice Mgmt', score: 90 },
  { area: 'Deadlines', score: 72 },
]

const AGENT_PERF = [
  { name: 'GST Agent', tasks: 145, success: 136, color: '#e11d48' },
  { name: 'IT Agent', tasks: 89, success: 84, color: '#7c3aed' },
  { name: 'TDS Agent', tasks: 67, success: 58, color: '#f59e0b' },
  { name: 'Notice AI', tasks: 23, success: 21, color: '#22c55e' },
]

export default function AnalyticsPage() {
  return (
    <DashboardLayout>
      <div className="p-6 space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-white" style={{ fontFamily: 'Rajdhani' }}>Analytics & Insights</h1>
          <p className="text-slate-400 text-sm mt-1">Money recovery trends • Agent performance • Tax health radar</p>
        </div>

        {/* KPIs */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { label: 'Total Recovered', value: '₹3.12L', change: '+₹1.8L this month', up: true },
            { label: 'Agent Success Rate', value: '94.6%', change: '+2.1% vs last month', up: true },
            { label: 'Avg Filing Time', value: '87 sec', change: '-15 sec improvement', up: true },
            { label: 'Penalties Avoided', value: '₹45K', change: '3 notices defended', up: true },
          ].map(k => (
            <div key={k.label} className="glass rounded-2xl p-4">
              <div className="text-2xl font-bold text-gradient" style={{ fontFamily: 'Rajdhani' }}>{k.value}</div>
              <div className="text-xs text-slate-400 mt-1">{k.label}</div>
              <div className="text-xs text-emerald-400 mt-1">{k.change}</div>
            </div>
          ))}
        </div>

        {/* Money Recovery Trend */}
        <div className="glass rounded-2xl p-5">
          <h3 className="font-semibold text-white mb-4" style={{ fontFamily: 'Rajdhani', fontSize: '16px' }}>Money Recovery by Category (7 months)</h3>
          <ResponsiveContainer width="100%" height={250}>
            <AreaChart data={MONTHLY_DATA}>
              <defs>
                {[['gst', '#e11d48'], ['it', '#7c3aed'], ['tds', '#f59e0b'], ['savings', '#22c55e']].map(([key, color]) => (
                  <linearGradient key={key} id={`${key}Grad`} x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor={color} stopOpacity={0.3} />
                    <stop offset="95%" stopColor={color} stopOpacity={0} />
                  </linearGradient>
                ))}
              </defs>
              <XAxis dataKey="month" tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false}
                tickFormatter={v => `₹${(v/1000).toFixed(0)}K`} />
              <Tooltip contentStyle={{ background: '#0d1527', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', color: '#e2e8f0', fontSize: '12px' }}
                formatter={(v: number) => `₹${(v/1000).toFixed(0)}K`} />
              <Area type="monotone" dataKey="gst" stroke="#e11d48" fill="url(#gstGrad)" strokeWidth={2} name="GST" />
              <Area type="monotone" dataKey="it" stroke="#7c3aed" fill="url(#itGrad)" strokeWidth={2} name="IT" />
              <Area type="monotone" dataKey="tds" stroke="#f59e0b" fill="url(#tdsGrad)" strokeWidth={2} name="TDS" />
              <Area type="monotone" dataKey="savings" stroke="#22c55e" fill="url(#savingsGrad)" strokeWidth={2} name="Tax Savings" />
            </AreaChart>
          </ResponsiveContainer>
          <div className="flex flex-wrap gap-4 mt-2">
            {[['GST', '#e11d48'], ['IT', '#7c3aed'], ['TDS', '#f59e0b'], ['Tax Savings', '#22c55e']].map(([name, color]) => (
              <div key={name} className="flex items-center gap-1.5">
                <div className="w-3 h-0.5 rounded-full" style={{ background: color }} />
                <span className="text-xs text-slate-400">{name}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Tax Health Radar */}
          <div className="glass rounded-2xl p-5">
            <h3 className="font-semibold text-white mb-4" style={{ fontFamily: 'Rajdhani', fontSize: '16px' }}>Tax Health Radar</h3>
            <ResponsiveContainer width="100%" height={240}>
              <RadarChart data={RADAR_DATA}>
                <PolarGrid stroke="rgba(255,255,255,0.1)" />
                <PolarAngleAxis dataKey="area" tick={{ fill: '#64748b', fontSize: 11 }} />
                <Radar name="Score" dataKey="score" stroke="#e11d48" fill="#e11d48" fillOpacity={0.2} strokeWidth={2} />
              </RadarChart>
            </ResponsiveContainer>
          </div>

          {/* Agent Performance */}
          <div className="glass rounded-2xl p-5">
            <h3 className="font-semibold text-white mb-4" style={{ fontFamily: 'Rajdhani', fontSize: '16px' }}>Agent Performance</h3>
            <div className="space-y-4">
              {AGENT_PERF.map(a => (
                <div key={a.name}>
                  <div className="flex justify-between mb-1.5">
                    <span className="text-sm text-white">{a.name}</span>
                    <span className="text-sm font-mono font-bold" style={{ color: a.color }}>
                      {Math.round((a.success / a.tasks) * 100)}%
                    </span>
                  </div>
                  <div className="progress-bar">
                    <div className="progress-fill" style={{ width: `${(a.success / a.tasks) * 100}%`, background: a.color }} />
                  </div>
                  <div className="text-xs text-slate-500 mt-1">{a.success}/{a.tasks} tasks successful</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  )
}
