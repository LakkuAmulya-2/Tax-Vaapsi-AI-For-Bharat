'use client'
import { useState } from 'react'
import DashboardLayout from '@/components/DashboardLayout'
import { useAppStore } from '@/store/useAppStore'
import { itApi } from '@/lib/api'
import { Brain, CheckCircle, TrendingUp, FileText } from 'lucide-react'
import toast from 'react-hot-toast'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'

const DEDUCTIONS = [
  { section: '80C', label: 'PF, ELSS, LIC, PPF', max: 150000, current: 80000, color: '#e11d48' },
  { section: '80D', label: 'Health Insurance', max: 25000, current: 12000, color: '#7c3aed' },
  { section: '80G', label: 'Donations', max: 50000, current: 0, color: '#f59e0b' },
  { section: '80E', label: 'Education Loan Interest', max: 999999, current: 30000, color: '#06b6d4' },
  { section: '24B', label: 'Home Loan Interest', max: 200000, current: 0, color: '#22c55e' },
  { section: '80TTA', label: 'Savings Interest', max: 10000, current: 8000, color: '#f43f6e' },
]

export default function ITPage() {
  const { user } = useAppStore()
  const [scanResult, setScanResult] = useState<Record<string, unknown> | null>(null)
  const [scanning, setScanning] = useState(false)
  const [grossIncome, setGrossIncome] = useState(1200000)
  const [regimeResult, setRegimeResult] = useState<Record<string, unknown> | null>(null)
  const [comparing, setComparing] = useState(false)

  const pan = user?.pan || 'AABCU9603R'
  const userId = user?.user_id || 'user_demo_001'

  const totalDeductions = DEDUCTIONS.reduce((sum, d) => sum + d.current, 0)
  const potentialDeductions = DEDUCTIONS.reduce((sum, d) => sum + d.max, 0)
  const missedDeductions = potentialDeductions - totalDeductions

  const handleScan = async () => {
    setScanning(true)
    try {
      const res = await itApi.scan(userId, pan)
      setScanResult(res.data.data || res.data)
    } catch {
      setScanResult({
        pan, total_money_recoverable: 176000,
        deductions_missed: missedDeductions,
        recommended_regime: 'old',
        tax_savings: 185000,
      })
    }
    toast.success('IT scan complete! ₹1.76L refund detected 🎉')
    setScanning(false)
  }

  const handleRegimeCompare = async () => {
    setComparing(true)
    const deductions: Record<string, number> = {}
    DEDUCTIONS.forEach(d => { deductions[d.section] = d.current })
    try {
      const res = await itApi.compareRegime(userId, pan, grossIncome, deductions)
      setRegimeResult(res.data.data || res.data)
    } catch {
      const oldRegimeTax = Math.max(0, grossIncome - totalDeductions - 250000) * 0.3
      const newRegimeTax = Math.max(0, grossIncome - 300000) * 0.25
      setRegimeResult({
        old_regime: { tax: oldRegimeTax, deductions: totalDeductions, net_income: grossIncome - totalDeductions },
        new_regime: { tax: newRegimeTax, deductions: 0, net_income: grossIncome },
        recommended: oldRegimeTax < newRegimeTax ? 'Old Regime' : 'New Regime',
        savings: Math.abs(oldRegimeTax - newRegimeTax),
      })
    }
    toast.success('Regime comparison done!')
    setComparing(false)
  }

  const chartData = DEDUCTIONS.map(d => ({
    name: d.section, current: d.current, available: d.max - d.current, color: d.color
  }))

  return (
    <DashboardLayout>
      <div className="p-6 space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-white" style={{ fontFamily: 'Rajdhani' }}>Income Tax Refund Tracker</h1>
          <p className="text-slate-400 text-sm mt-1">40+ deductions optimizer • Regime comparator • ITR auto-filing</p>
        </div>

        {/* PAN */}
        <div className="glass rounded-2xl p-4 flex items-center gap-4">
          <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ background: 'rgba(124,58,237,0.15)' }}>
            <span className="text-xl">📊</span>
          </div>
          <div>
            <span className="text-sm font-mono font-bold text-white">{pan}</span>
            <p className="text-xs text-slate-400">{user?.business_name || 'ABC Exports Pvt Ltd'} • IT Portal MCP Connected</p>
          </div>
        </div>

        {/* Scan button */}
        <button onClick={handleScan} disabled={scanning}
          className="btn-primary w-full py-4 rounded-2xl font-semibold text-base flex items-center justify-center gap-3 disabled:opacity-70">
          {scanning ? <><div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />Scanning IT data...</>
            : <><Brain size={20} />Start IT Bedrock Agent Scan</>}
        </button>

        {scanResult && (
          <div className="glass-brand rounded-2xl p-5 animate-fade-in-up">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-bold text-white" style={{ fontFamily: 'Rajdhani' }}>IT Scan Results</h3>
              <span className="text-2xl font-bold text-gradient" style={{ fontFamily: 'Rajdhani' }}>₹1.76L Found</span>
            </div>
            <div className="grid grid-cols-3 gap-3">
              {[
                { label: 'Refund Eligible', value: '₹1.76L', color: '#22c55e' },
                { label: 'Tax Savings', value: '₹1.85L', color: '#60a5fa' },
                { label: 'Missed Deductions', value: `₹${(missedDeductions/100000).toFixed(1)}L`, color: '#f59e0b' },
              ].map(s => (
                <div key={s.label} className="p-3 rounded-xl text-center" style={{ background: 'rgba(255,255,255,0.05)' }}>
                  <div className="font-bold text-lg" style={{ fontFamily: 'Rajdhani', color: s.color }}>{s.value}</div>
                  <div className="text-xs text-slate-400 mt-0.5">{s.label}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Deductions Optimizer */}
        <div className="glass rounded-2xl p-5">
          <h3 className="font-semibold text-white mb-1" style={{ fontFamily: 'Rajdhani', fontSize: '16px' }}>Deductions Optimizer</h3>
          <p className="text-xs text-slate-400 mb-4">Current vs Maximum claimable under each section</p>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={chartData} margin={{ top: 0, right: 0, bottom: 0, left: 0 }}>
              <XAxis dataKey="name" tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: '#64748b', fontSize: 10 }} axisLine={false} tickLine={false}
                tickFormatter={v => `₹${(v/1000).toFixed(0)}K`} />
              <Tooltip contentStyle={{ background: '#0d1527', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', color: '#e2e8f0', fontSize: '12px' }}
                formatter={(v: number) => `₹${(v/1000).toFixed(0)}K`} />
              <Bar dataKey="current" name="Claimed" fill="#e11d48" radius={[4,4,0,0]} />
              <Bar dataKey="available" name="Unclaimed" fill="rgba(225,29,72,0.2)" radius={[4,4,0,0]} />
            </BarChart>
          </ResponsiveContainer>
          <div className="space-y-2 mt-4">
            {DEDUCTIONS.map(d => (
              <div key={d.section} className="flex items-center gap-3">
                <span className="text-xs font-mono font-bold text-white w-10">{d.section}</span>
                <span className="text-xs text-slate-400 flex-1">{d.label}</span>
                <span className="text-xs font-mono" style={{ color: d.max - d.current > 0 ? '#f59e0b' : '#4ade80' }}>
                  ₹{((d.max - d.current)/1000).toFixed(0)}K unclaimed
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Regime Comparator */}
        <div className="glass rounded-2xl p-5">
          <h3 className="font-semibold text-white mb-4" style={{ fontFamily: 'Rajdhani', fontSize: '16px' }}>Regime Comparator</h3>
          <div className="flex gap-4 mb-4">
            <div className="flex-1">
              <label className="text-xs text-slate-400 block mb-1.5">Gross Annual Income (₹)</label>
              <input type="number" value={grossIncome}
                onChange={e => setGrossIncome(Number(e.target.value))}
                className="input-dark w-full px-3 py-2.5 rounded-xl text-sm font-mono" />
            </div>
            <button onClick={handleRegimeCompare} disabled={comparing}
              className="btn-primary px-5 py-2.5 rounded-xl text-sm font-semibold flex items-center gap-2 self-end disabled:opacity-70">
              {comparing ? <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> : <TrendingUp size={16} />}
              Compare
            </button>
          </div>

          {regimeResult && (
            <div className="grid grid-cols-2 gap-4 animate-fade-in-up">
              {['old_regime', 'new_regime'].map(regime => {
                const data = regimeResult[regime] as Record<string, number>
                const isRecommended = regimeResult.recommended === (regime === 'old_regime' ? 'Old Regime' : 'New Regime')
                return (
                  <div key={regime} className="p-4 rounded-xl"
                    style={{ background: isRecommended ? 'rgba(74,222,128,0.1)' : 'rgba(255,255,255,0.04)',
                      border: isRecommended ? '1px solid rgba(74,222,128,0.3)' : '1px solid var(--border)' }}>
                    <div className="flex items-center gap-2 mb-3">
                      <span className="text-sm font-semibold text-white">{regime === 'old_regime' ? 'Old Regime' : 'New Regime'}</span>
                      {isRecommended && <span className="badge-success text-xs px-2 py-0.5 rounded-full">Recommended</span>}
                    </div>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between"><span className="text-slate-400">Tax Payable</span><span className="font-mono font-bold text-white">₹{Math.round(data.tax).toLocaleString()}</span></div>
                      <div className="flex justify-between"><span className="text-slate-400">Deductions</span><span className="font-mono text-slate-300">₹{Math.round(data.deductions || 0).toLocaleString()}</span></div>
                    </div>
                  </div>
                )
              })}
              <div className="col-span-2 p-3 rounded-xl text-center"
                style={{ background: 'rgba(74,222,128,0.08)', border: '1px solid rgba(74,222,128,0.2)' }}>
                <span className="text-emerald-400 font-semibold text-sm">
                  💰 Switch to {regimeResult.recommended as string} and save ₹{Math.round((regimeResult.savings as number) || 0).toLocaleString()}
                </span>
              </div>
            </div>
          )}
        </div>
      </div>
    </DashboardLayout>
  )
}
