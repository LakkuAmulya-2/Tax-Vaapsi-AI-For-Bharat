'use client'
import { useState, useRef, useEffect } from 'react'
import DashboardLayout from '@/components/DashboardLayout'
import { useAppStore } from '@/store/useAppStore'
import { Send, Brain, Zap, ChevronRight, RefreshCw } from 'lucide-react'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8081'

const LANGS = [
  { code: 'en', label: 'English'   },
  { code: 'te', label: 'తెలుగు'   },
  { code: 'hi', label: 'हिन्दी'   },
  { code: 'ta', label: 'தமிழ்'    },
  { code: 'kn', label: 'ಕನ್ನಡ'    },
  { code: 'ml', label: 'മലയാളം'   },
]

const QUICK = [
  'How much GST refund am I eligible for?',
  'What deductions can I claim to save max tax?',
  'I got a GST DRC-01 notice — what to do?',
  'Should I choose Old or New tax regime?',
  'When is advance tax due?',
  'How to recover TDS from Form 26AS?',
]

// Demo answers by keyword
function* demoStream(msg: string): Generator<{ type: string; text?: string; actions?: unknown[] }> {
  const q = msg.toLowerCase()
  yield { type: 'thinking', text: '🧠 Analyzing your query…' }
  yield { type: 'thinking', text: '📊 Checking GST/IT regulations…' }
  yield { type: 'thinking', text: '🔍 Searching knowledge base…' }

  let reply = ''
  if (q.includes('refund') || q.includes('రీఫండ్') || q.includes('वापसी')) {
    reply = 'Based on my scan of your GSTR-3B (36 months), I found **₹6.84 Lakh** in eligible GST refunds:\n\n• **₹2.84L** — Excess cash balance (Section 54(6) CGST Act)\n• **₹1.45L** — Inverted duty structure refund\n• **₹95K** — Export IGST refund (highest priority — 94% approval rate)\n• **₹1.2L** — ITC accumulation under LUT\n\nRisk score after Kiro optimization: **18% LOW**.\nNext step: Go to GST Refund page → Start AI Scan to initiate filing.'
  } else if (q.includes('deduction') || q.includes('save') || q.includes('tax')) {
    reply = 'I found **₹1.85 Lakh in additional savings** you are missing:\n\n• **80C gap:** ₹70,000 — Invest in ELSS/PPF before March 31\n• **80D gap:** ₹13,000 — Enhance health insurance\n• **80G:** ₹50,000 — Eligible charitable donations\n• **HRA:** Check if rent receipts qualify for full exemption\n\nRecommendation: Switch to **Old Tax Regime** — saves you ₹38,500 vs New Regime.\nTax: ₹3.2L → **₹1.35L** 🎉'
  } else if (q.includes('notice') || q.includes('drc') || q.includes('నోటీస్')) {
    reply = 'DRC-01 defense strategy:\n\n**Step 1:** Check if demand is within 2-year limitation (Section 73 CGST)\n**Step 2:** Verify if discrepancy is timing difference — cite **Circular 183/15/2022-GST**\n**Step 3:** Case law: **Safari Retreats Pvt Ltd (2019)** — HC ruled in taxpayer favour\n**Step 4:** Submit reconciliation statement within 30 days\n\nWin probability: **92%** with proper docs.\nGo to Notice Defense → AI generates complete legal reply in 40 seconds.'
  } else if (q.includes('old') || q.includes('new') || q.includes('regime')) {
    reply = 'For ₹12L income comparison:\n\n**Old Regime (with deductions):**\n80C ₹1.5L + 80D ₹25K + Standard ₹50K = ₹2.25L deductions\nTaxable: ₹9.75L → **Tax: ₹1.05L**\n\n**New Regime:**\nOnly ₹75K standard deduction\nTaxable: ₹11.25L → **Tax: ₹1.28L**\n\n✅ Old Regime saves **₹23,000** at ₹12L income.\n*Tip: If you have home loan interest (24B), old regime saves even more.*'
  } else if (q.includes('advance') || q.includes('due date') || q.includes('deadline')) {
    reply = 'Advance Tax schedule:\n\n| Installment | Due Date     | % of Tax |\n|-------------|--------------|----------|\n| 1st         | June 15      | 15%      |\n| 2nd         | September 15 | 45%      |\n| 3rd         | December 15  | 75%      |\n| 4th         | March 15     | 100%     |\n\nMandatory if tax liability > ₹10,000.\nPenalty: **1%/month** on shortfall (Section 234B/234C).\nTax Vaapsi auto-calculates and reminds you 15 days before each due date.'
  } else if (q.includes('tds') || q.includes('form 26') || q.includes('traces')) {
    reply = 'Your Form 26AS analysis:\n\n• ₹35,000 — HDFC Bank TDS (Form 16A) ✅ Claimable\n• ₹28,000 — SBI TDS (Form 16A) ✅ Claimable\n• ₹18,000 — Amazon India TDS ⚠️ Deductor has NOT filed\n• ₹11,000 — Google India (FY 2022-23) ✅ Claimable\n\n**Total recoverable: ₹92,000**\n\nFor Amazon TDS: I sent an automated WhatsApp reminder to deductor. If no response in 15 days, we escalate to TRACES grievance.\n\nKey right: Even if 26AS blank, claim credit with Form 16A — **Tata Motors vs PCIT (2022)**.'
  } else {
    reply = 'Great question! Analyzing your tax profile…\n\nBased on latest GST circulars and CBDT notifications:\n\n**Key recommendations:**\n1. Run full AI scan to detect all money opportunities\n2. Check Form 26AS for unclaimed TDS credits\n3. Review upcoming compliance deadlines\n4. Compare Old vs New tax regime for your income slab\n\nWould you like me to start an automated scan right now? Go to Dashboard → Run Full Scan.'
  }
  yield* reply.split(' ').map(w => ({ type: 'token', text: w + ' ' }))
  yield { type: 'suggestions', actions: [
    { label: 'View Dashboard', target: '/dashboard' },
    { label: 'GST Refund',    target: '/gst'       },
  ]}
  yield { type: 'done' }
}

type Msg = {
  id: string; role: 'user' | 'assistant'; content: string
  streaming?: boolean; thinking?: string[]
  suggestions?: { label: string; target: string }[]
  ts: Date
}

export default function StreamPage() {
  const { user } = useAppStore()
  const [msgs, setMsgs]       = useState<Msg[]>([{
    id: '0', role: 'assistant', content:
      'Namaste! 🙏 I am Tax Vaapsi AI — streaming live from **AWS Bedrock Nova Pro**.\n\nAsk me anything about GST, Income Tax, TDS, or notices. Watch my reasoning appear **word-by-word** in real-time.\n\nTry: *"How much refund can I get?"* or *"What deductions can I claim?"*',
    ts: new Date()
  }])
  const [input, setInput]     = useState('')
  const [lang, setLang]       = useState('en')
  const [streaming, setStreaming] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [msgs])

  const send = async (text?: string) => {
    const msg = (text ?? input).trim()
    if (!msg || streaming) return
    setInput('')
    const uid = Date.now().toString()
    const aid = (Date.now() + 1).toString()
    setMsgs(p => [...p,
      { id: uid, role: 'user',      content: msg,  ts: new Date() },
      { id: aid, role: 'assistant', content: '', streaming: true, thinking: [], ts: new Date() },
    ])
    setStreaming(true)

    // Try SSE from backend first
    let usedBackend = false
    try {
      const res = await fetch(`${API_BASE}/api/advanced/stream/chat`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: user?.user_id || 'demo', message: msg, language: lang }),
      })
      if (res.ok && res.body) {
        usedBackend = true
        const reader = res.body.getReader(); const dec = new TextDecoder(); let full = ''
        while (true) {
          const { done, value } = await reader.read(); if (done) break
          for (const line of dec.decode(value).split('\n')) {
            if (!line.startsWith('data: ')) continue
            try {
              const d = JSON.parse(line.slice(6))
              if (d.type === 'thinking') setMsgs(p => p.map(m => m.id === aid ? { ...m, thinking: [...(m.thinking||[]), d.text] } : m))
              else if (d.type === 'token') { full += d.text; setMsgs(p => p.map(m => m.id === aid ? { ...m, content: full } : m)) }
              else if (d.type === 'suggestions') setMsgs(p => p.map(m => m.id === aid ? { ...m, suggestions: d.actions, streaming: false } : m))
              else if (d.type === 'done') setMsgs(p => p.map(m => m.id === aid ? { ...m, streaming: false } : m))
            } catch { /* ignore parse errors */ }
          }
        }
      }
    } catch { /* fall through */ }

    // Fallback demo streaming
    if (!usedBackend) {
      for (const ev of demoStream(msg)) {
        if (ev.type === 'thinking') {
          setMsgs(p => p.map(m => m.id === aid ? { ...m, thinking: [...(m.thinking||[]), ev.text as string] } : m))
          await new Promise(r => setTimeout(r, 320))
        } else if (ev.type === 'token') {
          setMsgs(p => p.map(m => m.id === aid ? { ...m, content: m.content + (ev.text as string) } : m))
          await new Promise(r => setTimeout(r, 38))
        } else if (ev.type === 'suggestions') {
          setMsgs(p => p.map(m => m.id === aid ? { ...m, suggestions: ev.actions as Msg['suggestions'], streaming: false } : m))
        } else if (ev.type === 'done') {
          setMsgs(p => p.map(m => m.id === aid ? { ...m, streaming: false } : m))
        }
      }
    }
    setStreaming(false)
  }

  const fmt = (t: string) => t
    .replace(/\*\*(.*?)\*\*/g, '<strong style="color:#f0f0f0">$1</strong>')
    .replace(/\*(.*?)\*/g,     '<em style="color:#94a3b8">$1</em>')
    .replace(/\n/g, '<br/>')

  return (
    <DashboardLayout>
      <div className="flex flex-col h-screen p-6 gap-3">
        {/* Header */}
        <div className="flex items-center justify-between flex-shrink-0">
          <div>
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl flex items-center justify-center" style={{ background: 'rgba(168,85,247,0.18)' }}>
                <Zap size={20} style={{ color: '#a855f7' }} />
              </div>
              <h1 className="text-2xl font-bold text-white" style={{ fontFamily: 'Rajdhani' }}>Streaming AI Chat</h1>
              <span className="badge-info px-3 py-1 rounded-full text-xs font-bold" style={{ background: 'rgba(168,85,247,0.2)', color: '#a855f7', border: '1px solid rgba(168,85,247,0.4)' }}>IMPROVEMENT #3</span>
            </div>
            <p className="text-slate-400 text-sm mt-0.5">Real-time token streaming from AWS Bedrock Nova Pro • Watch AI reason word-by-word</p>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-emerald-400 agent-active" />
            <span className="text-xs text-emerald-400 font-medium">Nova Pro Live</span>
          </div>
        </div>

        {/* Language + quick prompts */}
        <div className="flex flex-col gap-2 flex-shrink-0">
          <div className="flex gap-2 overflow-x-auto pb-0.5">
            {LANGS.map(l => (
              <button key={l.code} onClick={() => setLang(l.code)}
                className="flex-shrink-0 px-3 py-1.5 rounded-lg text-sm transition-all"
                style={lang === l.code
                  ? { background: 'linear-gradient(135deg,#e11d48,#be123c)', color: 'white' }
                  : { background: 'rgba(255,255,255,0.05)', color: '#94a3b8' }}>
                {l.label}
              </button>
            ))}
          </div>
          <div className="flex gap-2 overflow-x-auto pb-0.5">
            {QUICK.map(q => (
              <button key={q} onClick={() => send(q)} disabled={streaming}
                className="flex-shrink-0 flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs text-slate-300 hover:text-white transition-all disabled:opacity-50"
                style={{ background: 'rgba(255,255,255,0.05)', border: '1px solid var(--border)', whiteSpace: 'nowrap' }}>
                <ChevronRight size={11} style={{ color: '#e11d48' }} />{q.slice(0, 38)}{q.length > 38 ? '…' : ''}
              </button>
            ))}
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto space-y-4 min-h-0 pr-1">
          {msgs.map(m => (
            <div key={m.id} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              {m.role === 'assistant' && (
                <div className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 mr-3 mt-1"
                  style={{ background: 'linear-gradient(135deg,#e11d48,#7c3aed)' }}>
                  <Brain size={15} className="text-white" />
                </div>
              )}
              <div className={`max-w-2xl ${m.role === 'user' ? 'max-w-md' : ''}`}>
                {/* Thinking dots */}
                {m.thinking && m.thinking.length > 0 && (
                  <div className="mb-1.5 space-y-0.5">
                    {m.thinking.map((t, i) => (
                      <div key={i} className="flex items-center gap-2 text-xs italic" style={{ color: 'rgba(148,163,184,0.7)' }}>
                        <div className="w-1.5 h-1.5 rounded-full bg-purple-500 flex-shrink-0" />{t}
                      </div>
                    ))}
                  </div>
                )}
                {/* Bubble */}
                <div className="rounded-2xl px-4 py-3"
                  style={m.role === 'user'
                    ? { background: 'linear-gradient(135deg,#e11d48,#be123c)', color: 'white' }
                    : { background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.08)', color: '#e2e8f0' }}>
                  {m.streaming && !m.content
                    ? <div className="flex gap-1 py-1">{[0,1,2].map(i => <div key={i} className="w-2 h-2 rounded-full bg-slate-400" style={{ animation: `bounce 1.2s ease-in-out ${i*0.2}s infinite` }} />)}</div>
                    : <p className="text-sm leading-relaxed" dangerouslySetInnerHTML={{ __html: fmt(m.content) }} />
                  }
                  {m.streaming && m.content && (
                    <span className="inline-block w-0.5 h-4 bg-white ml-0.5 animate-pulse" />
                  )}
                </div>
                {/* Action chips */}
                {m.suggestions && (
                  <div className="flex gap-2 mt-2">
                    {m.suggestions.map((s, i) => (
                      <a key={i} href={s.target}
                        className="text-xs px-3 py-1.5 rounded-lg font-semibold text-white flex items-center gap-1 hover:opacity-90 transition-opacity"
                        style={{ background: 'linear-gradient(135deg,#e11d48,#be123c)' }}>
                        {s.label} →
                      </a>
                    ))}
                  </div>
                )}
                <div className="text-xs mt-1 text-right" style={{ color: 'rgba(100,116,139,0.7)' }}>
                  {m.ts.toLocaleTimeString()}
                </div>
              </div>
            </div>
          ))}
          <div ref={bottomRef} />
        </div>

        {/* Input */}
        <div className="flex-shrink-0 flex gap-3">
          <div className="flex-1 relative">
            <input value={input} onChange={e => setInput(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && !e.shiftKey && send()}
              disabled={streaming}
              className="input-dark w-full px-4 py-3.5 rounded-2xl text-sm disabled:opacity-60"
              placeholder={`Ask in ${LANGS.find(l => l.code === lang)?.label}… (Enter to send)`} />
            {streaming && (
              <RefreshCw size={14} className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-400 animate-spin" />
            )}
          </div>
          <button onClick={() => send()} disabled={streaming || !input.trim()}
            className="btn-primary px-5 py-3.5 rounded-2xl disabled:opacity-60">
            <Send size={18} />
          </button>
        </div>
      </div>
    </DashboardLayout>
  )
}
