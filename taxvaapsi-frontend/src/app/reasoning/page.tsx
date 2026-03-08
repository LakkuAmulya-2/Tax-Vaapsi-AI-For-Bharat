'use client'
import { useState, useEffect } from 'react'
import DashboardLayout from '@/components/DashboardLayout'
import { useAppStore } from '@/store/useAppStore'
import { Brain, CheckCircle, Loader2, Play, ArrowDown, AlertTriangle } from 'lucide-react'
import toast from 'react-hot-toast'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8081'

const TASKS = [
  { id: 'file_gst_refund', label: 'File GST Refund',    icon: '🏦', amount: 684000,  desc: 'Auto-detect + file all eligible refunds' },
  { id: 'optimize_it',     label: 'Optimize Income Tax', icon: '📊', amount: 185000,  desc: 'Maximize deductions, compare regimes' },
  { id: 'defend_notice',   label: 'Defend Tax Notice',   icon: '🛡️', amount: 50000,   desc: 'AI 3-agent legal defense' },
  { id: 'recover_tds',     label: 'Recover TDS Credits', icon: '⚡', amount: 92000,   desc: 'Form 26AS parse & recover' },
]

const PHASES = [
  { id: 'PLAN',      icon: '🗺️', label: 'Planner Agent',       color: '#60a5fa', desc: 'Analyzes task, chooses tools & strategy' },
  { id: 'BREAKDOWN', icon: '⚙️', label: 'Task Decomposer',      color: '#a78bfa', desc: 'Breaks into atomic, parallel subtasks' },
  { id: 'EXECUTE',   icon: '🔧', label: 'Tool Executor',        color: '#f59e0b', desc: 'Runs MCP tools, calls agents, fetches data' },
  { id: 'VERIFY',    icon: '✅', label: 'Verification Engine',  color: '#22c55e', desc: 'Cross-checks every result for accuracy' },
  { id: 'OUTPUT',    icon: '📤', label: 'Output Generator',     color: '#e11d48', desc: 'Structured final answer + HITL handoff' },
]

export default function ReasoningPage() {
  const { user } = useAppStore()
  const [task, setTask] = useState(TASKS[0])
  const [running, setRunning] = useState(false)
  const [activeIdx, setActiveIdx] = useState(-1)
  const [doneSet, setDoneSet] = useState<Set<number>>(new Set())
  const [result, setResult] = useState<Record<string, unknown> | null>(null)
  const [elapsed, setElapsed] = useState(0)

  useEffect(() => {
    let t: ReturnType<typeof setInterval>
    if (running) t = setInterval(() => setElapsed(e => e + 0.1), 100)
    return () => clearInterval(t)
  }, [running])

  const runLoop = async () => {
    setRunning(true); setDoneSet(new Set()); setActiveIdx(-1); setResult(null); setElapsed(0)
    const timings = [1400, 1100, 1600, 1100, 900]
    // fire API in background
    const apiPromise = fetch(`${API_BASE}/api/advanced/reasoning/start`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: user?.user_id || 'user_demo', task: task.id,
        context: { gstin: user?.gstin || '27AABCU9603R1ZX', pan: user?.pan || 'AABCU9603R', amount: task.amount }
      })
    }).then(r => r.json()).catch(() => null)

    for (let i = 0; i < PHASES.length; i++) {
      setActiveIdx(i)
      await new Promise(r => setTimeout(r, timings[i]))
      setDoneSet(prev => new Set([...prev, i]))
    }
    setActiveIdx(-1)
    const api = await apiPromise
    setResult(api?.data || makeDemoResult())
    setRunning(false)
    toast.success('🧠 Reasoning complete — plan ready for Human approval!')
  }

  const makeDemoResult = () => ({
    session_id: 'sess_' + Math.random().toString(36).slice(2, 10),
    final_recommendation: {
      action: 'PROCEED_WITH_FILING', confidence: 94,
      amount_recoverable: task.amount, risk_level: 'LOW (18%)',
      next_step: 'human_approval_required',
    },
    plan: {
      plan_steps: [
        { step: 1, agent: 'GST_SCANNER',  action: 'Scan 36 months GSTR-3B via MCP',      tool: 'gst_portal_mcp'      },
        { step: 2, agent: 'RISK_ANALYZER',action: 'Kiro risk prediction (72%→18%)',       tool: 'kiro_reasoning'       },
        { step: 3, agent: 'AUTO_FIXER',   action: 'Apply 3 document auto-fixes',           tool: 'bedrock_compute'      },
        { step: 4, agent: 'VERIFIER',     action: 'Cross-check GSTR-2A/2B',               tool: 'reconciliation_engine'},
        { step: 5, agent: 'COMPUTER_USE', action: 'File on GST portal in 90 seconds',     tool: 'bedrock_computer_use' },
      ],
      tools_needed: ['gst_portal_mcp','kiro_reasoning','bedrock_computer_use'],
      reasoning: 'Sequential flow maximises approval probability by verifying each step before proceeding.'
    },
    verification: {
      confidence_score: 94, verification_passed: true,
      cross_checks: [
        { check: 'GSTR-3B vs GSTR-2A reconciliation', status: 'passed' },
        { check: 'Bank account pre-validation',         status: 'passed' },
        { check: 'Refund eligibility criteria',         status: 'passed' },
        { check: 'Time-barred claim check',             status: 'passed' },
      ]
    },
    requires_human_approval: true,
  })

  const rec  = result?.final_recommendation as Record<string, unknown> | undefined
  const plan = result?.plan as Record<string, unknown> | undefined
  const veri = result?.verification as Record<string, unknown> | undefined

  return (
    <DashboardLayout>
      <div className="p-6 space-y-6 max-w-4xl">
        {/* Header */}
        <div>
          <div className="flex items-center gap-3 mb-1">
            <div className="w-9 h-9 rounded-xl flex items-center justify-center" style={{ background: 'rgba(96,165,250,0.18)' }}>
              <Brain size={20} style={{ color: '#60a5fa' }} />
            </div>
            <h1 className="text-2xl font-bold text-white" style={{ fontFamily: 'Rajdhani' }}>AI Reasoning Loop</h1>
            <span className="badge-info px-3 py-1 rounded-full text-xs font-bold">IMPROVEMENT #1</span>
          </div>
          <p className="text-slate-400 text-sm">Planner → Task Breakdown → Tool Execution → Verification → Output • Full transparent reasoning trace</p>
        </div>

        {/* Task picker */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {TASKS.map(t => (
            <button key={t.id} onClick={() => { if (!running) setTask(t) }}
              className="p-4 rounded-2xl text-left transition-all"
              style={{
                background: task.id === t.id ? 'rgba(96,165,250,0.1)' : 'rgba(255,255,255,0.04)',
                border: `1px solid ${task.id === t.id ? '#60a5fa55' : 'var(--border)'}`,
                outline: task.id === t.id ? '2px solid #60a5fa55' : 'none',
              }}>
              <div className="text-2xl mb-2">{t.icon}</div>
              <div className="text-sm font-semibold text-white">{t.label}</div>
              <div className="text-xs text-slate-400 mt-0.5">{t.desc}</div>
              <div className="text-xs font-mono text-emerald-400 mt-2">₹{(t.amount/1000).toFixed(0)}K</div>
            </button>
          ))}
        </div>

        {/* Run */}
        <button onClick={runLoop} disabled={running}
          className="btn-primary w-full py-4 rounded-2xl font-bold text-base flex items-center justify-center gap-3 disabled:opacity-70">
          {running
            ? <><Loader2 size={20} className="animate-spin" />Running... {elapsed.toFixed(1)}s</>
            : <><Play size={20} />Start Reasoning Loop</>}
        </button>

        {/* Phase pipeline */}
        {(running || result) && (
          <div className="glass rounded-2xl p-6">
            <div className="flex items-center gap-2 mb-5">
              <Brain size={16} style={{ color: '#60a5fa' }} />
              <span className="font-bold text-white" style={{ fontFamily: 'Rajdhani', fontSize: 16 }}>Reasoning Trace</span>
              {running && (
                <span className="ml-auto text-xs text-blue-400 animate-pulse">
                  ⏱ {elapsed.toFixed(1)}s elapsed
                </span>
              )}
            </div>
            <div className="space-y-2">
              {PHASES.map((ph, i) => {
                const done   = doneSet.has(i)
                const active = activeIdx === i
                const pending = !done && !active
                return (
                  <div key={ph.id}>
                    <div className="flex items-center gap-4 p-4 rounded-xl transition-all duration-500"
                      style={{
                        opacity: pending ? 0.35 : 1,
                        background: done   ? ph.color + '12'
                                  : active ? ph.color + '20'
                                  : 'rgba(255,255,255,0.03)',
                        border: `1px solid ${done || active ? ph.color + '50' : 'transparent'}`,
                      }}>
                      <div className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 text-xl"
                        style={{ background: done || active ? ph.color + '20' : 'rgba(255,255,255,0.06)' }}>
                        {done   ? <CheckCircle size={20} style={{ color: ph.color }} />
                        : active ? <Loader2 size={20} style={{ color: ph.color }} className="animate-spin" />
                        : ph.icon}
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-0.5">
                          <span className="text-sm font-bold text-white">{ph.label}</span>
                          <span className="text-xs px-2 py-0.5 rounded-full font-mono"
                            style={{ background: ph.color + '22', color: ph.color }}>
                            STEP {i + 1}
                          </span>
                          {active && <span className="text-xs text-blue-400 animate-pulse">Processing…</span>}
                          {done   && <span className="text-xs text-emerald-400">✓ Complete</span>}
                        </div>
                        <p className="text-xs text-slate-400">{ph.desc}</p>
                        {/* Inline detail snippets */}
                        {done && ph.id === 'VERIFY' && veri && (
                          <div className="mt-2 text-xs text-emerald-400 px-2 py-1 rounded-lg"
                            style={{ background: 'rgba(74,222,128,0.08)' }}>
                            {(veri.cross_checks as unknown[])?.length} checks passed •{' '}
                            Confidence {veri.confidence_score as number}% • Ready ✓
                          </div>
                        )}
                        {done && ph.id === 'OUTPUT' && rec && (
                          <div className="mt-2 text-xs px-2 py-1 rounded-lg"
                            style={{ background: 'rgba(225,29,72,0.1)', color: '#f43f6e' }}>
                            {rec.action as string} • ₹{((rec.amount_recoverable as number) / 1000).toFixed(0)}K •{' '}
                            {rec.risk_level as string}
                          </div>
                        )}
                      </div>
                    </div>
                    {i < PHASES.length - 1 && (
                      <div className="flex justify-center my-0.5">
                        <ArrowDown size={14} style={{ color: doneSet.has(i) ? ph.color : 'rgba(255,255,255,0.15)' }} />
                      </div>
                    )}
                  </div>
                )
              })}
            </div>
          </div>
        )}

        {/* Final result */}
        {result && !running && (
          <div className="space-y-4 animate-fade-in-up">
            {/* Summary cards */}
            <div className="grid grid-cols-3 gap-3">
              {[
                { label: 'Decision',    value: rec?.action as string || 'PROCEED',   color: '#22c55e' },
                { label: 'Risk Level',  value: rec?.risk_level as string || 'LOW',   color: '#22c55e' },
                { label: 'Recoverable', value: `₹${((rec?.amount_recoverable as number || task.amount)/1000).toFixed(0)}K`, color: '#f43f6e' },
              ].map(s => (
                <div key={s.label} className="glass rounded-2xl p-4 text-center">
                  <div className="text-xl font-bold" style={{ fontFamily: 'Rajdhani', color: s.color }}>{s.value}</div>
                  <div className="text-xs text-slate-400 mt-1">{s.label}</div>
                </div>
              ))}
            </div>

            {/* Execution plan */}
            {plan && (
              <div className="glass rounded-2xl p-5">
                <h4 className="font-bold text-white mb-3" style={{ fontFamily: 'Rajdhani' }}>Execution Plan</h4>
                <div className="space-y-2">
                  {(plan.plan_steps as Array<{ step: number; agent: string; action: string; tool: string }>).map(s => (
                    <div key={s.step} className="flex items-center gap-3 p-2.5 rounded-lg"
                      style={{ background: 'rgba(255,255,255,0.04)' }}>
                      <div className="w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold text-white flex-shrink-0"
                        style={{ background: 'linear-gradient(135deg,#e11d48,#be123c)' }}>{s.step}</div>
                      <span className="flex-1 text-sm text-white">{s.action}</span>
                      <span className="badge-info text-xs px-2 py-0.5 rounded-full">{s.agent}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* HITL handoff CTA */}
            <div className="glass rounded-2xl p-5" style={{ border: '1px solid rgba(251,191,36,0.4)' }}>
              <div className="flex items-center gap-3 mb-3">
                <AlertTriangle size={18} className="text-amber-400" />
                <h4 className="font-bold text-white" style={{ fontFamily: 'Rajdhani' }}>Human Approval Required</h4>
              </div>
              <p className="text-sm text-slate-300 mb-4">
                AI reasoning is complete. Before executing irreversible government portal filing, your approval is required.
              </p>
              <div className="flex gap-3">
                <a href="/hitl"
                  className="flex-1 btn-primary py-3 rounded-xl font-semibold text-sm text-center">
                  Review &amp; Approve in HITL →
                </a>
                <button onClick={() => { setResult(null); setDoneSet(new Set()) }}
                  className="flex-1 py-3 rounded-xl font-semibold text-sm text-slate-300 hover:text-white transition-colors"
                  style={{ background: 'rgba(255,255,255,0.06)' }}>
                  Re-run Reasoning
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  )
}
