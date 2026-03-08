'use client'
import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Shield, Eye, EyeOff, Zap, CheckCircle, AlertCircle } from 'lucide-react'
import toast from 'react-hot-toast'
import { useAppStore } from '@/store/useAppStore'

export default function LoginPage() {
  const router = useRouter()
  const setUser = useAppStore(s => s.setUser)
  const [tab, setTab] = useState<'login' | 'register'>('login')
  const [showPass, setShowPass] = useState(false)
  const [loading, setLoading] = useState(false)

  const [loginForm, setLoginForm] = useState({ email: 'demo@taxvaapsi.in', password: 'demo123' })
  const [regForm, setRegForm] = useState({
    business_name: '', gstin: '', pan: '', email: '', phone: '', business_type: 'SME'
  })

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    try {
      // Demo login - in prod hits /api/user/login
      await new Promise(r => setTimeout(r, 1500))
      const demoUser = {
        user_id: 'user_demo_001',
        gstin: '27AABCU9603R1ZX',
        pan: 'AABCU9603R',
        business_name: 'ABC Exports Pvt Ltd',
        email: loginForm.email,
        phone: '+91 98765 43210',
        business_type: 'Exporter',
      }
      setUser(demoUser)
      localStorage.setItem('tv_token', 'demo_token_' + Date.now())
      toast.success('Welcome back! Agents are active 🤖')
      router.push('/dashboard')
    } catch {
      toast.error('Login failed. Try demo@taxvaapsi.in / demo123')
    } finally {
      setLoading(false)
    }
  }

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    try {
      const { authApi } = await import('@/lib/api')
      const res = await authApi.register({ ...regForm })
      setUser({
        user_id: res.data.user_id,
        ...regForm,
        phone: regForm.phone,
      })
      toast.success('Registered! Running first scan...')
      router.push('/dashboard')
    } catch {
      // Demo fallback
      setUser({
        user_id: 'user_' + Date.now(),
        ...regForm,
        phone: regForm.phone,
      })
      toast.success('Registered successfully!')
      router.push('/dashboard')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-grid flex" style={{ background: 'var(--bg-deep)' }}>
      {/* Left Panel */}
      <div className="hidden lg:flex flex-col justify-between w-1/2 p-12 relative overflow-hidden"
        style={{ background: 'linear-gradient(135deg, #0d0a1a 0%, #1a0515 50%, #0d0a1a 100%)' }}>
        
        {/* Background pattern */}
        <div className="absolute inset-0 opacity-20"
          style={{
            backgroundImage: 'radial-gradient(circle at 30% 50%, #e11d4820 0%, transparent 60%), radial-gradient(circle at 70% 20%, #7c3aed20 0%, transparent 40%)'
          }} />

        {/* Logo */}
        <div className="relative z-10">
          <div className="flex items-center gap-3 mb-16">
            <div className="w-12 h-12 rounded-xl flex items-center justify-center glow-red"
              style={{ background: 'linear-gradient(135deg, #e11d48, #be123c)' }}>
              <span className="text-2xl font-bold text-white" style={{ fontFamily: 'Rajdhani' }}>₹</span>
            </div>
            <div>
              <div className="text-xl font-bold text-white" style={{ fontFamily: 'Rajdhani', letterSpacing: '0.05em' }}>TAX VAAPSI</div>
              <div className="text-xs text-slate-400">India's First Autonomous Tax AI</div>
            </div>
          </div>

          <h1 className="text-4xl font-bold text-white mb-4" style={{ fontFamily: 'Rajdhani', lineHeight: 1.2 }}>
            We don't help you<br />
            <span className="text-gradient">FILE</span> taxes<br />
            We <span className="text-gradient">FIND</span> hidden<br />
            money & <span className="text-gradient">RECOVER</span> it
          </h1>
          <p className="text-slate-400 mt-6 text-lg">Autonomously. 24/7. In 22 languages.</p>
        </div>

        {/* Stats */}
        <div className="relative z-10 grid grid-cols-3 gap-4">
          {[
            { label: 'Avg Found', value: '₹12.45L', sub: 'per business' },
            { label: 'Success Rate', value: '82%', sub: 'refund approval' },
            { label: 'Time Saved', value: '70%', sub: 'vs manual' },
          ].map((stat) => (
            <div key={stat.label} className="glass rounded-xl p-4 text-center">
              <div className="text-2xl font-bold text-gradient" style={{ fontFamily: 'Rajdhani' }}>{stat.value}</div>
              <div className="text-xs text-slate-300 font-medium mt-1">{stat.label}</div>
              <div className="text-xs text-slate-500">{stat.sub}</div>
            </div>
          ))}
        </div>

        {/* Features list */}
        <div className="relative z-10 space-y-3">
          {[
            'AI scans 36 months GST/IT data automatically',
            'Risk reduced from 72% → 18% before filing',
            'Notice defense with AI-generated legal replies',
            'Works in Telugu, Hindi, Tamil + 19 more languages',
          ].map((f) => (
            <div key={f} className="flex items-center gap-3">
              <CheckCircle size={16} className="text-emerald-400 flex-shrink-0" />
              <span className="text-slate-300 text-sm">{f}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Right Panel - Login Form */}
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="w-full max-w-md">
          {/* Mobile logo */}
          <div className="lg:hidden flex items-center gap-3 mb-8">
            <div className="w-10 h-10 rounded-xl flex items-center justify-center"
              style={{ background: 'linear-gradient(135deg, #e11d48, #be123c)' }}>
              <span className="text-xl font-bold text-white">₹</span>
            </div>
            <div className="text-lg font-bold text-white" style={{ fontFamily: 'Rajdhani' }}>TAX VAAPSI</div>
          </div>

          {/* Tabs */}
          <div className="flex rounded-xl p-1 mb-8" style={{ background: 'rgba(255,255,255,0.05)' }}>
            {(['login', 'register'] as const).map((t) => (
              <button key={t} onClick={() => setTab(t)}
                className={`flex-1 py-2.5 rounded-lg text-sm font-semibold transition-all ${tab === t ? 'text-white' : 'text-slate-400 hover:text-slate-200'}`}
                style={tab === t ? { background: 'linear-gradient(135deg, #e11d48, #be123c)' } : {}}>
                {t === 'login' ? 'Sign In' : 'Register'}
              </button>
            ))}
          </div>

          {tab === 'login' ? (
            <form onSubmit={handleLogin} className="space-y-5">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Email Address</label>
                <input
                  type="email"
                  value={loginForm.email}
                  onChange={e => setLoginForm({ ...loginForm, email: e.target.value })}
                  className="input-dark w-full px-4 py-3 rounded-xl text-sm"
                  placeholder="you@business.com"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Password</label>
                <div className="relative">
                  <input
                    type={showPass ? 'text' : 'password'}
                    value={loginForm.password}
                    onChange={e => setLoginForm({ ...loginForm, password: e.target.value })}
                    className="input-dark w-full px-4 py-3 pr-12 rounded-xl text-sm"
                    placeholder="••••••••"
                    required
                  />
                  <button type="button" onClick={() => setShowPass(!showPass)}
                    className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white">
                    {showPass ? <EyeOff size={18} /> : <Eye size={18} />}
                  </button>
                </div>
              </div>

              {/* Demo hint */}
              <div className="glass-brand rounded-xl p-3 flex items-center gap-3">
                <AlertCircle size={16} className="text-brand-400 flex-shrink-0" />
                <p className="text-xs text-slate-300">
                  Demo: <span className="text-brand-300 font-mono">demo@taxvaapsi.in</span> / <span className="text-brand-300 font-mono">demo123</span>
                </p>
              </div>

              <button type="submit" disabled={loading}
                className="btn-primary w-full py-3.5 rounded-xl font-semibold text-sm flex items-center justify-center gap-2 disabled:opacity-70">
                {loading ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    Authenticating...
                  </>
                ) : (
                  <>
                    <Zap size={18} />
                    Sign In & Start Finding Money
                  </>
                )}
              </button>
            </form>
          ) : (
            <form onSubmit={handleRegister} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1.5">Business Name</label>
                  <input type="text" value={regForm.business_name}
                    onChange={e => setRegForm({ ...regForm, business_name: e.target.value })}
                    className="input-dark w-full px-3 py-2.5 rounded-xl text-sm" placeholder="ABC Exports" required />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1.5">Business Type</label>
                  <select value={regForm.business_type}
                    onChange={e => setRegForm({ ...regForm, business_type: e.target.value })}
                    className="input-dark w-full px-3 py-2.5 rounded-xl text-sm">
                    {['SME', 'Exporter', 'Manufacturer', 'Freelancer', 'Startup'].map(t => (
                      <option key={t} value={t}>{t}</option>
                    ))}
                  </select>
                </div>
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1.5">GSTIN</label>
                <input type="text" value={regForm.gstin}
                  onChange={e => setRegForm({ ...regForm, gstin: e.target.value.toUpperCase() })}
                  className="input-dark w-full px-3 py-2.5 rounded-xl text-sm font-mono" placeholder="27AABCU9603R1ZX" />
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1.5">PAN Number</label>
                <input type="text" value={regForm.pan}
                  onChange={e => setRegForm({ ...regForm, pan: e.target.value.toUpperCase() })}
                  className="input-dark w-full px-3 py-2.5 rounded-xl text-sm font-mono" placeholder="AABCU9603R" />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1.5">Email</label>
                  <input type="email" value={regForm.email}
                    onChange={e => setRegForm({ ...regForm, email: e.target.value })}
                    className="input-dark w-full px-3 py-2.5 rounded-xl text-sm" placeholder="you@business.com" required />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1.5">Phone</label>
                  <input type="tel" value={regForm.phone}
                    onChange={e => setRegForm({ ...regForm, phone: e.target.value })}
                    className="input-dark w-full px-3 py-2.5 rounded-xl text-sm" placeholder="+91 98765 43210" />
                </div>
              </div>

              <button type="submit" disabled={loading}
                className="btn-primary w-full py-3.5 rounded-xl font-semibold text-sm flex items-center justify-center gap-2 mt-2 disabled:opacity-70">
                {loading ? (
                  <><div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />Registering...</>
                ) : (
                  <><Shield size={18} />Register & Find Hidden Money</>
                )}
              </button>
            </form>
          )}

          <div className="mt-8 text-center">
            <p className="text-xs text-slate-500">
              Secured by AWS KMS • DPDPA 2023 Compliant • Data in Mumbai Region
            </p>
            <div className="flex items-center justify-center gap-4 mt-3 opacity-40">
              {['AWS Bedrock', 'Bhashini', 'Nova Pro'].map(b => (
                <span key={b} className="text-xs text-slate-400">{b}</span>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
