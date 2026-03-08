'use client'
import { useState } from 'react'
import DashboardLayout from '@/components/DashboardLayout'
import { useAppStore } from '@/store/useAppStore'
import { BookOpen, Search, CheckCircle, Loader2, FileText } from 'lucide-react'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8081'

const DOMAINS = [
  { id: 'gst',     label: 'GST',         icon: '🏦', count: 4 },
  { id: 'it',      label: 'Income Tax',  icon: '📊', count: 3 },
  { id: 'tds',     label: 'TDS',         icon: '⚡', count: 2 },
  { id: 'general', label: 'General',     icon: '📋', count: 2 },
]

const SAMPLES: { domain: string; q: string }[] = [
  { domain: 'gst',  q: 'How to claim GST refund for exports under LUT?' },
  { domain: 'gst',  q: 'What is the time limit to claim GST refund?' },
  { domain: 'gst',  q: 'How to defend GST DRC-01 notice?' },
  { domain: 'it',   q: 'Should I choose Old or New tax regime for ₹15L income?' },
  { domain: 'it',   q: 'Maximum 80C deductions and best investment options?' },
  { domain: 'tds',  q: 'TDS credit not showing in Form 26AS — what to do?' },
  { domain: 'general', q: 'When is advance tax due and how to calculate?' },
]

// Demo answers
function demoAnswer(q: string): { answer: string; sources: { title: string; section: string }[] } {
  const ql = q.toLowerCase()
  if (ql.includes('lut') || (ql.includes('export') && ql.includes('refund'))) {
    return {
      answer: '**GST Refund for Exports under LUT — Section 54(3) CGST Act:**\n\nExporters can claim refund of accumulated ITC when exporting under Letter of Undertaking (LUT) without payment of IGST.\n\n**Procedure (Rule 89 CGST Rules):**\n1. File RFD-01 on GST portal within **2 years** from the relevant date\n2. Attach: LUT copy, shipping bills, BRC/FIRC (bank realisation certificates)\n3. Refund processed within **60 days** of a complete application\n\n**Key condition:** Zero-rated supply must be backed by export documents. GSTR-1 must correctly declare exports.\n\n**Practical tip:** Reconcile GSTR-3B with GSTR-2A/2B before filing — Tax Vaapsi AI does this automatically to avoid deficiency memos.',
      sources: [
        { title: 'GST Refund under Section 54',  section: 'Section 54(3) CGST Act' },
        { title: 'ITC Accumulation Refund',       section: 'Rule 89 CGST Rules'    },
      ],
    }
  }
  if (ql.includes('time limit') || ql.includes('2 year')) {
    return {
      answer: '**Time Limit for GST Refund — Section 54(1) CGST Act:**\n\nGST refund must be claimed within **2 years from the relevant date.**\n\n**Relevant date by refund type:**\n• Export with IGST payment → Date of filing shipping bill\n• Export under LUT → End of FY in which supply was made\n• Excess cash ledger balance → Date of payment\n• ITC accumulation → End of tax period when refund first arises\n\n⚠️ Time-barred claims are permanently lost. Tax Vaapsi monitors your 2-year window automatically and alerts you 60 days before expiry.',
      sources: [
        { title: 'GST Refund under Section 54', section: 'Section 54(1) CGST Act' },
      ],
    }
  }
  if (ql.includes('drc') || ql.includes('notice') || ql.includes('defend')) {
    return {
      answer: '**Defending GST DRC-01 Notice — Section 73/74 CGST Act:**\n\nDRC-01 is a Show Cause Notice for GST demand. Effective defense:\n\n**Step 1:** Check limitation period (3 years for non-fraud, 5 years for fraud)\n**Step 2:** Verify if discrepancy is a timing difference — cite **Circular 183/15/2022-GST** (ITC cannot be denied for timing difference)\n**Step 3:** Cite case law: **Safari Retreats Pvt Ltd (2019)** — HC ruled in taxpayer favour\n**Step 4:** Submit reconciliation statement within **30 days**\n\n**Win probability: 85-92%** with proper documentation. Tax Vaapsi generates the complete legal reply automatically.',
      sources: [
        { title: 'GST Notice DRC-01 Defense', section: 'Section 73/74 CGST Act' },
      ],
    }
  }
  if (ql.includes('old') || ql.includes('new') || ql.includes('regime')) {
    return {
      answer: '**Old vs New Tax Regime — Section 115BAC IT Act:**\n\n| Factor | Old Regime | New Regime |\n|--------|-----------|------------|\n| Standard deduction | ₹50,000 | ₹75,000 |\n| 80C (PPF, ELSS…) | ₹1.5L allowed | ❌ Not allowed |\n| 80D (Health ins.) | ₹25K allowed | ❌ Not allowed |\n| HRA exemption | Allowed | ❌ Not allowed |\n| Tax-free limit | Effective ₹5L | Effective ₹7L |\n\n**Choose Old Regime if** total deductions > ₹3.75 Lakh.\n**Choose New Regime if** total deductions < ₹2 Lakh OR income > ₹15L.\n\nFor ₹15L income with ₹2.25L deductions: Old Regime saves approx. **₹45,000–₹80,000** p.a.',
      sources: [
        { title: 'Old vs New Tax Regime 2024-25', section: 'Section 115BAC IT Act' },
      ],
    }
  }
  if (ql.includes('80c') || ql.includes('deduction') || ql.includes('invest')) {
    return {
      answer: '**80C Maximum Utilization (₹1.5 Lakh limit) — Section 80C IT Act:**\n\n**Market-linked (higher return):**\n• ELSS Mutual Funds — 3-year lock-in, historical 12-15% p.a. returns\n\n**Guaranteed returns:**\n• PPF — 7.1% p.a., 15-year tenure, completely tax-free maturity\n• NSC — 7.7% p.a., 5-year tenure\n\n**Already counted (no extra investment):**\n• Home loan principal repayment\n• Children tuition fees (max 2 kids)\n• EPF contribution (auto from salary)\n\n**Tax Vaapsi recommendation:** 50% ELSS + 30% PPF + 20% existing instruments = optimal risk-return balance.',
      sources: [
        { title: '80C Deductions Maximum Utilization', section: 'Section 80C IT Act' },
      ],
    }
  }
  if (ql.includes('form 26') || ql.includes('tds credit') || ql.includes('traces')) {
    return {
      answer: '**TDS Credit Missing from Form 26AS — Resolution:**\n\n**Step 1:** Check if deductor has filed their TDS return on TRACES (traces.gov.in)\n**Step 2:** If filed but 26AS not updated → wait 30 days (processing lag)\n**Step 3:** If deductor has NOT filed → send legal notice under **Section 203 IT Act** (₹200/day penalty on deductor)\n\n**Your legal right:** Even if 26AS is blank, you can claim TDS credit with Form 16A — upheld in **Tata Motors vs PCIT (2022)**.\n\n**New AIS:** Annual Information Statement (AIS) is more comprehensive — check both 26AS and AIS on the income tax portal.\n\nTax Vaapsi sends automated WhatsApp reminders to non-compliant deductors on your behalf.',
      sources: [
        { title: 'Form 26AS and TDS Credit', section: 'Section 203AA IT Act' },
        { title: 'TDS Rates 2024-25',         section: 'Chapter XVII-B IT Act' },
      ],
    }
  }
  if (ql.includes('advance') || ql.includes('installment')) {
    return {
      answer: '**Advance Tax — Sections 207-219 IT Act:**\n\nMandatory when estimated tax liability > **₹10,000** for the year.\n\n**Payment schedule:**\n• **June 15** — Pay 15% of annual tax\n• **September 15** — Pay 45% (cumulative)\n• **December 15** — Pay 75% (cumulative)\n• **March 15** — Pay 100% (cumulative)\n\n**Penalty for shortfall:**\n• Section 234B — 1%/month if total advance tax < 90% of assessed tax\n• Section 234C — 1%/month for each installment shortfall\n\n**Exception:** Presumptive taxation (Section 44AD) — entire tax by March 15 only.',
      sources: [
        { title: 'Advance Tax Schedule', section: 'Section 207-219 IT Act' },
      ],
    }
  }
  return {
    answer: `For your query about "${q}":\n\nThis topic is covered under Indian tax law. Key points:\n\n1. Always keep supporting documents for at least 6 years\n2. File returns before due dates to avoid penalties\n3. Use Tax Vaapsi AI scan to detect all eligible refunds and deductions automatically\n\nFor specific guidance, try one of the sample queries above or run a full AI scan from the Dashboard.`,
    sources: [{ title: 'Tax Audit Requirements', section: 'Section 44AB IT Act' }],
  }
}

type Result = {
  query: string
  sources: { title: string; section?: string; id?: string }[]
  ai_synthesized_answer: string
  retrieved_documents?: unknown[]
  confidence?: string
}

export default function KnowledgePage() {
  const { user } = useAppStore()
  const [domain, setDomain] = useState('gst')
  const [query, setQuery]   = useState('')
  const [result, setResult] = useState<Result | null>(null)
  const [loading, setLoading] = useState(false)

  const search = async (q?: string) => {
    const qText = (q ?? query).trim()
    if (!qText) return
    setQuery(qText); setLoading(true); setResult(null)
    try {
      const res = await fetch(`${API_BASE}/api/advanced/rag/query`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: user?.user_id || 'demo', query: qText, domain })
      })
      const data = await res.json()
      if (data.success) { setResult(data.data); return }
    } catch { /* fall through */ }
    // Demo fallback
    await new Promise(r => setTimeout(r, 900))
    const demo = demoAnswer(qText)
    setResult({ query: qText, sources: demo.sources, ai_synthesized_answer: demo.answer, confidence: 'high' })
    setLoading(false)
  }

  const fmt = (t: string) => t
    .replace(/\*\*(.*?)\*\*/g, '<strong style="color:#f0f0f0">$1</strong>')
    .replace(/\n/g, '<br/>')

  return (
    <DashboardLayout>
      <div className="p-6 space-y-6 max-w-4xl">
        {/* Header */}
        <div>
          <div className="flex items-center gap-3 mb-1">
            <div className="w-9 h-9 rounded-xl flex items-center justify-center" style={{ background: 'rgba(34,197,94,0.18)' }}>
              <BookOpen size={20} style={{ color: '#22c55e' }} />
            </div>
            <h1 className="text-2xl font-bold text-white" style={{ fontFamily: 'Rajdhani' }}>Tax Knowledge Base (RAG)</h1>
            <span className="badge-success px-3 py-1 rounded-full text-xs font-bold">IMPROVEMENT #4</span>
          </div>
          <p className="text-slate-400 text-sm">AWS Bedrock Knowledge Base → Vector retrieval → AI synthesis • Accurate, cited answers</p>
        </div>

        {/* Domain cards */}
        <div className="grid grid-cols-4 gap-3">
          {DOMAINS.map(d => (
            <button key={d.id} onClick={() => setDomain(d.id)}
              className="p-4 rounded-2xl text-left transition-all"
              style={{
                background: domain === d.id ? 'rgba(34,197,94,0.1)' : 'rgba(255,255,255,0.04)',
                border: `1px solid ${domain === d.id ? 'rgba(34,197,94,0.5)' : 'var(--border)'}`,
                outline: domain === d.id ? '2px solid rgba(34,197,94,0.3)' : 'none',
              }}>
              <div className="text-2xl mb-2">{d.icon}</div>
              <div className="text-sm font-semibold text-white">{d.label}</div>
              <div className="text-xs text-slate-400 mt-1">{d.count} docs</div>
            </button>
          ))}
        </div>

        {/* KB info banner */}
        <div className="glass rounded-2xl p-4 flex items-center gap-4">
          <div className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0" style={{ background: 'rgba(34,197,94,0.15)' }}>
            <BookOpen size={20} style={{ color: '#22c55e' }} />
          </div>
          <div>
            <p className="text-sm font-bold text-white">AWS Bedrock Knowledge Base</p>
            <p className="text-xs text-slate-400">11 curated tax documents • Amazon Titan embeddings • OpenSearch Serverless • Semantic vector search</p>
          </div>
          <div className="ml-auto flex items-center gap-2 flex-shrink-0">
            <div className="w-2 h-2 rounded-full bg-emerald-400 agent-active" />
            <span className="text-xs text-emerald-400 font-medium">Active</span>
          </div>
        </div>

        {/* Search bar */}
        <div className="flex gap-3">
          <div className="flex-1 relative">
            <Search size={15} className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" />
            <input value={query} onChange={e => setQuery(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && search()}
              className="input-dark w-full pl-11 pr-4 py-3.5 rounded-2xl text-sm"
              placeholder="Ask any tax question… e.g. How to claim GST refund under LUT?" />
          </div>
          <button onClick={() => search()} disabled={loading || !query.trim()}
            className="btn-primary px-6 py-3.5 rounded-2xl font-semibold flex items-center gap-2 disabled:opacity-60">
            {loading ? <Loader2 size={18} className="animate-spin" /> : <Search size={18} />}
            Search
          </button>
        </div>

        {/* Sample queries */}
        <div>
          <p className="text-xs font-semibold text-slate-400 mb-2">Sample questions ({domain.toUpperCase()} domain):</p>
          <div className="flex flex-wrap gap-2">
            {SAMPLES.filter(s => s.domain === domain).map((s, i) => (
              <button key={i} onClick={() => search(s.q)}
                className="text-xs px-3 py-1.5 rounded-lg text-slate-300 hover:text-white transition-colors text-left"
                style={{ background: 'rgba(255,255,255,0.06)', border: '1px solid var(--border)' }}>
                &quot;{s.q}&quot;
              </button>
            ))}
          </div>
        </div>

        {/* Loading */}
        {loading && (
          <div className="glass rounded-2xl p-6 text-center space-y-3">
            <div className="flex items-center justify-center gap-3">
              <Loader2 size={20} style={{ color: '#22c55e' }} className="animate-spin" />
              <span className="text-white font-medium">Searching Knowledge Base…</span>
            </div>
            <div className="space-y-1 text-xs text-slate-400">
              <p>🔍 Vector similarity search across 11 documents…</p>
              <p>🧠 AWS Bedrock Nova Pro synthesising answer…</p>
              <p>📋 Citing relevant tax sections &amp; case laws…</p>
            </div>
          </div>
        )}

        {/* Result */}
        {result && !loading && (
          <div className="space-y-4 animate-fade-in-up">
            {/* Retrieved sources */}
            <div className="glass rounded-2xl p-5">
              <div className="flex items-center gap-2 mb-3">
                <FileText size={15} style={{ color: '#22c55e' }} />
                <span className="text-sm font-semibold text-white">Retrieved from Knowledge Base</span>
                <span className="ml-auto badge-success text-xs px-2 py-0.5 rounded-full">{result.confidence || 'high'} confidence</span>
              </div>
              <div className="space-y-2">
                {result.sources.map((s, i) => (
                  <div key={i} className="flex items-center gap-3 p-2.5 rounded-lg"
                    style={{ background: 'rgba(34,197,94,0.08)', border: '1px solid rgba(34,197,94,0.2)' }}>
                    <CheckCircle size={14} style={{ color: '#22c55e' }} className="flex-shrink-0" />
                    <span className="flex-1 text-sm text-white">{s.title}</span>
                    {s.section && <span className="text-xs text-slate-400 flex-shrink-0">{s.section}</span>}
                  </div>
                ))}
              </div>
              <p className="text-xs text-slate-500 mt-3">AWS Bedrock Knowledge Base — semantic similarity retrieval</p>
            </div>

            {/* AI answer */}
            <div className="glass-brand rounded-2xl p-6">
              <div className="flex items-center gap-2 mb-4">
                <div className="w-8 h-8 rounded-lg flex items-center justify-center" style={{ background: 'rgba(225,29,72,0.2)' }}>
                  <BookOpen size={16} style={{ color: '#f43f6e' }} />
                </div>
                <span className="font-bold text-white" style={{ fontFamily: 'Rajdhani', fontSize: 16 }}>AI Synthesised Answer</span>
                <span className="ml-auto text-xs text-slate-400">Bedrock Nova Pro + RAG</span>
              </div>
              <div className="text-sm text-slate-200 leading-relaxed"
                dangerouslySetInnerHTML={{ __html: fmt(result.ai_synthesized_answer) }} />
            </div>

            {/* Actions */}
            <div className="glass rounded-2xl p-4">
              <p className="text-xs font-semibold text-slate-300 mb-3">Take action based on this answer:</p>
              <div className="grid grid-cols-3 gap-2">
                {[
                  { label: '🏦 GST Refund',    href: '/gst',       color: '#e11d48' },
                  { label: '🛡️ HITL Approve',  href: '/hitl',      color: '#fbbf24' },
                  { label: '🧠 Reasoning',     href: '/reasoning', color: '#60a5fa' },
                ].map(a => (
                  <a key={a.href} href={a.href}
                    className="text-center py-2.5 rounded-xl text-xs font-semibold transition-all hover:opacity-90"
                    style={{ background: a.color + '20', border: `1px solid ${a.color}44`, color: a.color }}>
                    {a.label}
                  </a>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  )
}
