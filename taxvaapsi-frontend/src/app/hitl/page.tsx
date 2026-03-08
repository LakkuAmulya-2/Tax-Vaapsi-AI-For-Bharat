'use client'
import { useState, useEffect } from 'react'
import DashboardLayout from '@/components/DashboardLayout'
import { useAppStore } from '@/store/useAppStore'
import { Shield, CheckCircle, XCircle, AlertTriangle, Eye, Edit3 } from 'lucide-react'
import toast from 'react-hot-toast'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8081'

type PlanStep = { step: number; action: string; agent: string; tool: string; auto_or_human?: string }
type Pending = {
  session_id: string
  task: string
  status: string
  plan: {
    task_description?: string
    money_at_stake?: number
    risk_level?: string
    human_approval_reason?: string
    compliance_laws_applicable?: string[]
    steps?: PlanStep[]
  }
  rag_sources?: { title: string }[]
  created_at: string
}

const DEMO: Pending[] = [
  {
    session_id: 'sess_gst_001',
    task: 'file_gst_refund',
    status: 'PENDING_APPROVAL',
    plan: {
      task_description: 'File GST Refund (IGST exports) ₹6,84,000 via Computer Use on govt.gst.gov.in',
      money_at_stake: 684000,
      risk_level: 'low',
      human_approval_reason:
        'This action submits an irreversible refund application on the live GST portal. Amount ₹6,84,000. AI will use Computer Use to fill forms autonomously. Your approval is mandatory for safety.',
      compliance_laws_applicable: ['Section 54 CGST Act 2017','Rule 89 CGST Rules','Circular 125/44/2019-GST'],
      steps: [
        { step: 1, action: 'Scan 36 months GSTR-3B via MCP',     agent: 'GST_SCANNER',   tool: 'gst_portal_mcp',       auto_or_human: 'auto' },
        { step: 2, action: 'Kiro risk prediction (72% → 18%)',    agent: 'RISK_ANALYZER', tool: 'kiro_reasoning',        auto_or_human: 'auto' },
        { step: 3, action: 'Apply 3 document auto-fixes',          agent: 'AUTO_FIXER',    tool: 'bedrock_compute',       auto_or_human: 'auto' },
        { step: 4, action: '⚠️ FILE on GST portal — 90 seconds', agent: 'COMPUTER_USE',  tool: 'bedrock_computer_use',  auto_or_human: 'human_approval_required' },
      ],
    },
    rag_sources: [{ title: 'GST Refund under Section 54' }, { title: 'ITC Accumulation Refund' }],
    created_at: new Date(Date.now() - 120_000).toISOString(),
  },
  {
    session_id: 'sess_it_001',
    task: 'optimize_it',
    status: 'PENDING_APPROVAL',
    plan: {
      task_description: 'Switch to Old Tax Regime + File ITR with ₹1.85L additional deductions',
      money_at_stake: 185000,
      risk_level: 'low',
      human_approval_reason:
        'Tax regime switch is irrevocable for FY 2023-24 once ITR is filed. Additional deductions require original receipts. You must confirm accuracy before submission.',
      compliance_laws_applicable: ['Section 115BAC IT Act','Section 80C/80D/80G IT Act'],
      steps: [
        { step: 1, action: 'Scan IT portal for all deductions',        agent: 'IT_SCANNER',         tool: 'it_portal_mcp',        auto_or_human: 'auto' },
        { step: 2, action: 'Compare Old vs New regime',                agent: 'REGIME_COMPARATOR',  tool: 'bedrock_nova',          auto_or_human: 'auto' },
        { step: 3, action: '⚠️ FILE ITR with Old Regime + Deductions', agent: 'COMPUTER_USE',       tool: 'bedrock_computer_use',  auto_or_human: 'human_approval_required' },
      ],
    },
    rag_sources: [{ title: 'Old vs New Tax Regime 2024-25' }],
    created_at: new Date(Date.now() - 300_000).toISOString(),
  },
]

export default function HITLPage() {
  const { user } = useAppStore()
  const [items, setItems]       = useState<Pending[]>(DEMO)
  const [selected, setSelected] = useState<Pending | null>(null)
  const [decisions, setDecisions] = useState<Record<string, 'approved' | 'rejected'>>({})
  const [modAmt, setModAmt]     = useState('')
  const [notes, setNotes]       = useState('')
  const [busy, setBusy]         = useState(false)

  useEffect(() => {
    fetch(`${API_BASE}/api/advanced/hitl/pending/${user?.user_id || 'user_demo'}`)
      .then(r => r.json())
      .then(d => { if (d?.data?.length) setItems([...d.data, ...DEMO]) })
      .catch(() => {})
  }, [user])

  const decide = async (plan: Pending, approved: boolean) => {
    setBusy(true)
    const mods = modAmt ? { amount: parseInt(modAmt), notes } : {}
    try {
      await fetch(`${API_BASE}/api/advanced/hitl/approve`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: plan.session_id, user_id: user?.user_id || 'demo', approved, modifications: mods })
      })
    } catch { /* demo fallback */ }
    toast.success(approved ? '✅ Approved! AI will execute in 90 seconds.' : '❌ Rejected. No action taken.')
    setDecisions(p => ({ ...p, [plan.session_id]: approved ? 'approved' : 'rejected' }))
    setSelected(null); setBusy(false); setModAmt(''); setNotes('')
  }

  const riskColor = (r = 'low') => r === 'low' ? '#22c55e' : r === 'medium' ? '#f59e0b' : '#ef4444'

  return (
    <DashboardLayout>
      <div className="p-6 space-y-6 max-w-3xl">
        {/* Header */}
        <div>
          <div className="flex items-center gap-3 mb-1">
            <div className="w-9 h-9 rounded-xl flex items-center justify-center" style={{ background: 'rgba(251,191,36,0.18)' }}>
              <Shield size={20} style={{ color: '#fbbf24' }} />
            </div>
            <h1 className="text-2xl font-bold text-white" style={{ fontFamily: 'Rajdhani' }}>Human-in-the-Loop</h1>
            <span className="badge-warning px-3 py-1 rounded-full text-xs font-bold">IMPROVEMENT #2</span>
          </div>
          <p className="text-slate-400 text-sm">AI suggests → You review &amp; approve → System executes • Zero filing without consent</p>
        </div>

        {/* Safety banner */}
        <div className="glass rounded-2xl p-4 flex items-center gap-4"
          style={{ border: '1px solid rgba(251,191,36,0.35)' }}>
          <Shield size={22} style={{ color: '#fbbf24' }} className="flex-shrink-0" />
          <div className="flex-1">
            <p className="text-sm font-bold text-white">Safety Guarantee</p>
            <p className="text-xs text-slate-400">Tax Vaapsi will <strong>NEVER</strong> file anything on government portals without your explicit approval. You can also modify amounts before approving.</p>
          </div>
          <div className="text-center flex-shrink-0">
            <div className="text-2xl font-bold text-amber-400" style={{ fontFamily: 'Rajdhani' }}>{items.length}</div>
            <div className="text-xs text-slate-400">pending</div>
          </div>
        </div>

        {/* List */}
        <div className="space-y-3">
          {items.map(p => {
            const dec = decisions[p.session_id]
            return (
              <div key={p.session_id} className="glass rounded-2xl p-5 transition-all"
                style={{ border: `1px solid ${dec === 'approved' ? 'rgba(74,222,128,0.4)' : dec === 'rejected' ? 'rgba(239,68,68,0.3)' : 'var(--border)'}` }}>
                <div className="flex items-start gap-4">
                  <div className="w-10 h-10 rounded-xl flex items-center justify-center text-xl flex-shrink-0"
                    style={{ background: dec ? (dec === 'approved' ? 'rgba(74,222,128,0.15)' : 'rgba(239,68,68,0.15)') : 'rgba(251,191,36,0.15)' }}>
                    {dec === 'approved' ? '✅' : dec === 'rejected' ? '❌' : '⏳'}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex flex-wrap items-center gap-2 mb-1">
                      <span className="text-sm font-bold text-white truncate">{p.plan?.task_description || p.task}</span>
                      <span className="text-xs px-2 py-0.5 rounded-full font-medium flex-shrink-0"
                        style={{ background: riskColor(p.plan?.risk_level) + '22', color: riskColor(p.plan?.risk_level) }}>
                        {(p.plan?.risk_level || 'LOW').toUpperCase()} RISK
                      </span>
                    </div>
                    <div className="flex flex-wrap gap-4 text-xs text-slate-400">
                      <span>💰 ₹{((p.plan?.money_at_stake || 0)/1000).toFixed(0)}K at stake</span>
                      <span>🕐 {new Date(p.created_at).toLocaleTimeString()}</span>
                      {p.rag_sources && <span>📚 {p.rag_sources.length} KB sources</span>}
                    </div>
                  </div>
                  {!dec && (
                    <button onClick={() => setSelected(p)}
                      className="flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-semibold text-slate-300 hover:text-white transition-colors flex-shrink-0"
                      style={{ background: 'rgba(255,255,255,0.07)' }}>
                      <Eye size={13} />Review
                    </button>
                  )}
                  {dec && <span className="text-xs font-semibold flex-shrink-0" style={{ color: dec === 'approved' ? '#4ade80' : '#f87171' }}>{dec === 'approved' ? '✓ Approved' : '✗ Rejected'}</span>}
                </div>
              </div>
            )
          })}
        </div>

        {/* Review modal */}
        {selected && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4"
            style={{ background: 'rgba(0,0,0,0.85)', backdropFilter: 'blur(8px)' }}>
            <div className="w-full max-w-xl max-h-[90vh] overflow-y-auto rounded-2xl p-6 space-y-5"
              style={{ background: 'var(--bg-card)', border: '1px solid rgba(251,191,36,0.45)' }}>
              <div className="flex items-center justify-between">
                <h3 className="font-bold text-white text-lg" style={{ fontFamily: 'Rajdhani' }}>Review AI Plan</h3>
                <button onClick={() => setSelected(null)} className="text-slate-400 hover:text-white text-xl leading-none">✕</button>
              </div>

              {/* Why approval */}
              <div className="p-4 rounded-xl flex gap-3"
                style={{ background: 'rgba(251,191,36,0.08)', border: '1px solid rgba(251,191,36,0.3)' }}>
                <AlertTriangle size={17} className="text-amber-400 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="text-sm font-semibold text-amber-300 mb-1">Why your approval is needed:</p>
                  <p className="text-xs text-slate-300">{selected.plan?.human_approval_reason}</p>
                </div>
              </div>

              {/* Steps */}
              <div>
                <p className="text-sm font-semibold text-white mb-3">Execution Steps</p>
                <div className="space-y-2">
                  {(selected.plan?.steps || []).map(s => (
                    <div key={s.step} className="flex items-center gap-3 p-3 rounded-xl"
                      style={{
                        background: s.auto_or_human === 'human_approval_required' ? 'rgba(251,191,36,0.08)' : 'rgba(255,255,255,0.04)',
                        border: s.auto_or_human === 'human_approval_required' ? '1px solid rgba(251,191,36,0.3)' : '1px solid transparent',
                      }}>
                      <div className="w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold text-white flex-shrink-0"
                        style={{ background: s.auto_or_human === 'human_approval_required' ? '#f59e0b' : 'rgba(255,255,255,0.15)' }}>
                        {s.step}
                      </div>
                      <span className="flex-1 text-sm text-white">{s.action}</span>
                      {s.auto_or_human === 'human_approval_required' && (
                        <span className="badge-warning text-xs px-2 py-0.5 rounded-full flex-shrink-0">⚠ Needs approval</span>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              {/* Laws */}
              {selected.plan?.compliance_laws_applicable && (
                <div>
                  <p className="text-xs font-semibold text-slate-300 mb-2">📚 Laws &amp; Regulations</p>
                  <div className="flex flex-wrap gap-2">
                    {selected.plan.compliance_laws_applicable.map(l => (
                      <span key={l} className="badge-info text-xs px-2 py-1 rounded-full">{l}</span>
                    ))}
                  </div>
                </div>
              )}

              {/* Optional modify */}
              <div className="p-4 rounded-xl" style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid var(--border)' }}>
                <div className="flex items-center gap-2 mb-3">
                  <Edit3 size={13} style={{ color: '#60a5fa' }} />
                  <span className="text-sm font-semibold text-white">Modify Before Approving (optional)</span>
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="text-xs text-slate-400 block mb-1">Override amount (₹)</label>
                    <input type="number" value={modAmt} onChange={e => setModAmt(e.target.value)}
                      className="input-dark w-full px-3 py-2 rounded-lg text-sm font-mono"
                      placeholder={`Default ${selected.plan?.money_at_stake}`} />
                  </div>
                  <div>
                    <label className="text-xs text-slate-400 block mb-1">Notes</label>
                    <input type="text" value={notes} onChange={e => setNotes(e.target.value)}
                      className="input-dark w-full px-3 py-2 rounded-lg text-sm"
                      placeholder="Any special instruction…" />
                  </div>
                </div>
              </div>

              {/* Buttons */}
              <div className="flex gap-3">
                <button onClick={() => decide(selected, true)} disabled={busy}
                  className="flex-1 py-4 rounded-xl font-bold text-sm flex items-center justify-center gap-2 text-white disabled:opacity-60"
                  style={{ background: 'linear-gradient(135deg,#22c55e,#16a34a)' }}>
                  {busy ? <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> : <CheckCircle size={18} />}
                  APPROVE &amp; EXECUTE
                </button>
                <button onClick={() => decide(selected, false)} disabled={busy}
                  className="flex-1 py-4 rounded-xl font-bold text-sm flex items-center justify-center gap-2 disabled:opacity-60"
                  style={{ background: 'rgba(239,68,68,0.15)', border: '1px solid rgba(239,68,68,0.4)', color: '#f87171' }}>
                  <XCircle size={18} />REJECT
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  )
}
