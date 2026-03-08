import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export interface User {
  user_id: string
  gstin: string
  pan: string
  business_name: string
  email: string
  phone: string
  business_type: string
}

export interface AgentActivity {
  agent: string
  action: string
  status: 'running' | 'success' | 'error'
  timestamp: string
  result?: string
}

export interface MoneyFound {
  gst: number
  it: number
  tds: number
  tax_savings: number
  penalties_avoided: number
  total: number
}

interface AppState {
  user: User | null
  isAuthenticated: boolean
  moneyFound: MoneyFound
  agentActivities: AgentActivity[]
  taxHealthScore: number
  isScanning: boolean
  scanProgress: number
  activeAgents: string[]
  riskScore: number

  setUser: (user: User) => void
  logout: () => void
  setMoneyFound: (money: MoneyFound) => void
  addAgentActivity: (activity: AgentActivity) => void
  setTaxHealthScore: (score: number) => void
  setIsScanning: (scanning: boolean) => void
  setScanProgress: (progress: number) => void
  setActiveAgents: (agents: string[]) => void
  setRiskScore: (score: number) => void
}

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      user: null,
      isAuthenticated: false,
      moneyFound: { gst: 684000, it: 176000, tds: 92000, tax_savings: 185000, penalties_avoided: 45000, total: 1245000 },
      agentActivities: [
        { agent: 'GST Bedrock Agent', action: 'Scanning 36 months GSTR-3B data', status: 'success', timestamp: new Date().toISOString(), result: '₹6.84L found' },
        { agent: 'IT Bedrock Agent', action: 'Analyzing 40+ deductions under 80C/80D/80G', status: 'success', timestamp: new Date().toISOString(), result: '₹1.76L found' },
        { agent: 'TDS Commando', action: 'Parsing Form 26AS for TDS credits', status: 'running', timestamp: new Date().toISOString() },
        { agent: 'Notice Defense AI', action: 'Monitoring GST portal for deficiency notices', status: 'success', timestamp: new Date().toISOString(), result: 'All clear' },
      ],
      taxHealthScore: 68,
      isScanning: false,
      scanProgress: 0,
      activeAgents: ['GST Agent', 'IT Agent', 'TDS Agent', 'Notice Defense'],
      riskScore: 18,

      setUser: (user) => set({ user, isAuthenticated: true }),
      logout: () => set({ user: null, isAuthenticated: false }),
      setMoneyFound: (moneyFound) => set({ moneyFound }),
      addAgentActivity: (activity) =>
        set((state) => ({ agentActivities: [activity, ...state.agentActivities].slice(0, 20) })),
      setTaxHealthScore: (taxHealthScore) => set({ taxHealthScore }),
      setIsScanning: (isScanning) => set({ isScanning }),
      setScanProgress: (scanProgress) => set({ scanProgress }),
      setActiveAgents: (activeAgents) => set({ activeAgents }),
      setRiskScore: (riskScore) => set({ riskScore }),
    }),
    {
      name: 'taxvaapsi-store',
      partialize: (state) => ({ user: state.user, isAuthenticated: state.isAuthenticated }),
    }
  )
)
