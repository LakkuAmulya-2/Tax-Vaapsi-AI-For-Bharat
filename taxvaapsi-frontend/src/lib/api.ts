import axios from 'axios'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8081'

const api = axios.create({
  baseURL: API_BASE,
  timeout: 60000,
  headers: { 'Content-Type': 'application/json' },
})

// Add auth token
api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('tv_token')
    if (token) config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// ────────────────────────────────────────────────────
// AUTH
// ────────────────────────────────────────────────────
export const authApi = {
  register: (data: {
    gstin: string; pan: string; business_name: string;
    email: string; phone: string; business_type: string;
  }) => api.post('/api/onboard/register', data),

  login: (email: string, password: string) =>
    api.post('/api/user/login', { email, password }),
}

// ────────────────────────────────────────────────────
// ONBOARDING / SCAN
// ────────────────────────────────────────────────────
export const scanApi = {
  fullScan: (user_id: string, gstin: string, pan: string) =>
    api.post('/api/onboard/full-scan', { user_id, gstin, pan }),

  quickDemo: () => api.get('/demo/quick-start'),
}

// ────────────────────────────────────────────────────
// GST
// ────────────────────────────────────────────────────
export const gstApi = {
  scan: (user_id: string, gstin: string) =>
    api.post('/api/gst/scan', { user_id, gstin }),

  riskAnalysis: (user_id: string, gstin: string, refund_type: string, amount: number) =>
    api.post('/api/gst/risk-analysis', { user_id, gstin, refund_type, amount }),

  file: (user_id: string, gstin: string, refund_type: string, amount: number) =>
    api.post('/api/gst/file', { user_id, scan_id: 'auto', gstin, refund_type, amount }),

  replyDeficiency: (user_id: string, gstin: string, arn: string, deficiency_details: string) =>
    api.post('/api/gst/deficiency-reply', { user_id, gstin, arn, deficiency_details }),
}

// ────────────────────────────────────────────────────
// INCOME TAX
// ────────────────────────────────────────────────────
export const itApi = {
  scan: (user_id: string, pan: string) =>
    api.post('/api/it/scan', { user_id, pan }),

  optimize: (user_id: string, pan: string, gross_income: number, existing_deductions: Record<string, number>) =>
    api.post('/api/it/optimize', { user_id, pan, gross_income, existing_deductions }),

  compareRegime: (user_id: string, pan: string, gross_income: number, deductions: Record<string, number>) =>
    api.post('/api/it/regime-compare', { user_id, pan, gross_income, deductions }),

  fileITR: (user_id: string, pan: string, itr_type: string, income_data: Record<string, number>) =>
    api.post('/api/it/file-itr', { user_id, pan, itr_type, income_data }),
}

// ────────────────────────────────────────────────────
// TDS
// ────────────────────────────────────────────────────
export const tdsApi = {
  scan: (user_id: string, pan: string, financial_year: string = '2023-24') =>
    api.post('/api/tds/scan', { user_id, pan, financial_year }),
}

// ────────────────────────────────────────────────────
// NOTICE DEFENSE
// ────────────────────────────────────────────────────
export const noticeApi = {
  defend: (user_id: string, notice_content: string, notice_meta: Record<string, string> = {}) =>
    api.post('/api/notice/defend', { user_id, notice_content, notice_meta }),
}

// ────────────────────────────────────────────────────
// DASHBOARD
// ────────────────────────────────────────────────────
export const dashboardApi = {
  getSummary: (user_id: string) =>
    api.get(`/api/dashboard/summary/${user_id}`),

  getAgentActivity: (user_id: string) =>
    api.get(`/api/dashboard/agent-activity/${user_id}`),

  getTaxHealth: (user_id: string) =>
    api.get(`/api/dashboard/tax-health/${user_id}`),
}

// ────────────────────────────────────────────────────
// COMPLIANCE
// ────────────────────────────────────────────────────
export const complianceApi = {
  getCalendar: (user_id: string) =>
    api.get(`/api/compliance/calendar/${user_id}`),

  getUpcoming: (user_id: string) =>
    api.get(`/api/compliance/upcoming/${user_id}`),
}

// ────────────────────────────────────────────────────
// VOICE
// ────────────────────────────────────────────────────
export const voiceApi = {
  processCommand: (user_id: string, command: string, language: string = 'en') =>
    api.post('/api/voice/process', { user_id, command, language }),
}

// ────────────────────────────────────────────────────
// MCP / AGENTS
// ────────────────────────────────────────────────────
export const mcpApi = {
  getTools: (server: string) =>
    api.get(`/api/mcp/tools/${server}`),

  executeTool: (server: string, tool_name: string, input: Record<string, unknown>) =>
    api.post('/api/mcp/execute', { server, tool_name, input }),
}

export const a2aApi = {
  listAgents: () => api.get('/api/a2a/agents'),
  sendTask: (agent_id: string, task: string, metadata: Record<string, string> = {}) =>
    api.post('/api/a2a/send-task', { agent_id, task, metadata }),
}

// ────────────────────────────────────────────────────
// HEALTH
// ────────────────────────────────────────────────────
export const healthApi = {
  check: () => api.get('/health'),
  root: () => api.get('/'),
}

export default api

// ────────────────────────────────────────────────────
// ADVANCED AI v3.1 (Reasoning + HITL + Streaming + RAG)
// ────────────────────────────────────────────────────
export const advancedApi = {
  // 1. Reasoning loop
  startReasoning: (user_id: string, task: string, context: Record<string, unknown>) =>
    api.post('/api/advanced/reasoning/start', { user_id, task, context }),

  // 2. Human-in-the-loop
  getPending:      (user_id: string) =>    api.get(`/api/advanced/hitl/pending/${user_id}`),
  approvePlan:     (session_id: string, user_id: string, approved: boolean, modifications: Record<string, unknown>) =>
    api.post('/api/advanced/hitl/approve', { session_id, user_id, approved, modifications }),
  getHITLStatus:   (session_id: string) => api.get(`/api/advanced/hitl/status/${session_id}`),

  // 3. Streaming — use native fetch for SSE (not axios)
  streamChatUrl: () => `${API_BASE}/api/advanced/stream/chat`,

  // 4. RAG Knowledge Base
  ragQuery:        (user_id: string, query: string, domain: string) =>
    api.post('/api/advanced/rag/query', { user_id, query, domain }),
  ragDocs:         (domain: string) => api.get(`/api/advanced/rag/documents/${domain}`),
  ragStats:        ()                => api.get('/api/advanced/rag/stats'),

  // Combined full flow
  fullAutonomousFlow: (user_id: string, task: string, context: Record<string, unknown>) =>
    api.post('/api/advanced/autonomous/full-flow', { user_id, task, context }),
}
