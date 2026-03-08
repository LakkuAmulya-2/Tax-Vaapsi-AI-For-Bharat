'use client'
import { useState, useRef } from 'react'
import DashboardLayout from '@/components/DashboardLayout'
import { Mic, MicOff, Volume2, Send, Globe } from 'lucide-react'
import toast from 'react-hot-toast'

const LANGUAGES = [
  { code: 'te', name: 'Telugu', native: 'తెలుగు' },
  { code: 'hi', name: 'Hindi', native: 'हिन्दी' },
  { code: 'ta', name: 'Tamil', native: 'தமிழ்' },
  { code: 'kn', name: 'Kannada', native: 'ಕನ್ನಡ' },
  { code: 'ml', name: 'Malayalam', native: 'മലയാളം' },
  { code: 'gu', name: 'Gujarati', native: 'ગુજરાતી' },
  { code: 'mr', name: 'Marathi', native: 'मराठी' },
  { code: 'bn', name: 'Bengali', native: 'বাংলা' },
  { code: 'en', name: 'English', native: 'English' },
]

const SAMPLE_COMMANDS = [
  { lang: 'te', cmd: 'Refund file karo', response: 'GST refund scan started. ₹6.84L found!' },
  { lang: 'hi', cmd: 'Mera refund kitna hai?', response: '₹12.45 lakh refund milega aapko!' },
  { lang: 'ta', cmd: 'GST return file pannu', response: 'GST return filing started automatically!' },
  { lang: 'en', cmd: 'Show my tax health', response: 'Your tax health score is 68/100. 3 improvements possible.' },
]

type ChatMsg = { type: 'user' | 'agent'; text: string; lang: string; time: string }

export default function VoicePage() {
  const [selectedLang, setSelectedLang] = useState('te')
  const [isListening, setIsListening] = useState(false)
  const [inputText, setInputText] = useState('')
  const [chat, setChat] = useState<ChatMsg[]>([
    { type: 'agent', text: 'Namaste! Tax Vaapsi voice assistant ready. Mee language lo matladandi! (Speak in your language)', lang: 'en', time: new Date().toLocaleTimeString() }
  ])

  const handleSend = async (text?: string) => {
    const cmd = text || inputText
    if (!cmd.trim()) return
    
    const userMsg: ChatMsg = { type: 'user', text: cmd, lang: selectedLang, time: new Date().toLocaleTimeString() }
    setChat(prev => [...prev, userMsg])
    setInputText('')

    // Simulate AI response
    setTimeout(() => {
      const sample = SAMPLE_COMMANDS.find(s => s.lang === selectedLang) || SAMPLE_COMMANDS[3]
      let response = sample.response
      if (cmd.toLowerCase().includes('refund') || cmd.toLowerCase().includes('రీఫండ్')) response = '₹12.45L total refund found! Filing GST claim autonomously... Done! ARN: GST-RFD-348921 ✅'
      else if (cmd.toLowerCase().includes('health') || cmd.toLowerCase().includes('score')) response = 'Tax health score: 68/100. 3 areas need improvement: Missing 80C deductions, GSTR reconciliation, advance tax.'
      else if (cmd.toLowerCase().includes('notice') || cmd.toLowerCase().includes('నోటీస్')) response = 'AI analyzing notice... 92% win probability. Legal reply generated with 3 case laws!'
      else response = `Understood! Processing your request via Bedrock AI agents. ${sample.response}`

      const agentMsg: ChatMsg = { type: 'agent', text: response, lang: 'en', time: new Date().toLocaleTimeString() }
      setChat(prev => [...prev, agentMsg])
      toast.success('Agent processed command!')
    }, 1500)
  }

  const toggleListening = () => {
    if (isListening) {
      setIsListening(false)
      // Simulate voice input
      const sample = SAMPLE_COMMANDS.find(s => s.lang === selectedLang)
      if (sample) {
        setInputText(sample.cmd)
        setTimeout(() => handleSend(sample.cmd), 500)
      }
      toast.success('Voice captured!')
    } else {
      setIsListening(true)
      toast('Listening... Speak now', { icon: '🎙️' })
      setTimeout(() => {
        setIsListening(false)
        const sample = SAMPLE_COMMANDS.find(s => s.lang === selectedLang)
        if (sample) {
          setInputText(sample.cmd)
          handleSend(sample.cmd)
        }
      }, 3000)
    }
  }

  return (
    <DashboardLayout>
      <div className="p-6 space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-white" style={{ fontFamily: 'Rajdhani' }}>Voice Assistant</h1>
          <p className="text-slate-400 text-sm mt-1">Bhashini AI4Bharat • 22 Indian languages • Voice-to-action • "Refund file karo" → Agent files</p>
        </div>

        {/* Language selector */}
        <div className="glass rounded-2xl p-5">
          <div className="flex items-center gap-2 mb-3">
            <Globe size={18} style={{ color: '#e11d48' }} />
            <h3 className="font-semibold text-white" style={{ fontFamily: 'Rajdhani' }}>Select Language</h3>
          </div>
          <div className="grid grid-cols-3 md:grid-cols-5 gap-2">
            {LANGUAGES.map(lang => (
              <button key={lang.code} onClick={() => setSelectedLang(lang.code)}
                className={`p-2.5 rounded-xl text-center transition-all ${selectedLang === lang.code ? 'text-white' : 'text-slate-400 hover:text-slate-200'}`}
                style={selectedLang === lang.code ? { background: 'linear-gradient(135deg, #e11d48, #be123c)' } : { background: 'rgba(255,255,255,0.04)' }}>
                <div className="text-base font-bold">{lang.native}</div>
                <div className="text-xs opacity-70 mt-0.5">{lang.name}</div>
              </button>
            ))}
            <div className="p-2.5 rounded-xl text-center" style={{ background: 'rgba(255,255,255,0.04)' }}>
              <div className="text-base font-bold text-slate-500">+13</div>
              <div className="text-xs text-slate-600 mt-0.5">more</div>
            </div>
          </div>
        </div>

        {/* Mic button */}
        <div className="flex flex-col items-center py-6">
          <button onClick={toggleListening}
            className="w-28 h-28 rounded-full flex items-center justify-center transition-all duration-300 relative"
            style={{
              background: isListening ? 'linear-gradient(135deg, #ef4444, #dc2626)' : 'linear-gradient(135deg, #e11d48, #be123c)',
              boxShadow: isListening ? '0 0 40px rgba(239,68,68,0.6)' : '0 0 30px rgba(225,29,72,0.4)',
              transform: isListening ? 'scale(1.05)' : 'scale(1)',
            }}>
            {isListening ? (
              <>
                <div className="absolute inset-0 rounded-full animate-pulse-ring"
                  style={{ background: 'rgba(239,68,68,0.3)' }} />
                <MicOff size={40} className="text-white relative z-10" />
              </>
            ) : (
              <Mic size={40} className="text-white" />
            )}
          </button>
          <p className="text-sm text-slate-400 mt-4">
            {isListening ? '🔴 Listening...' : 'Tap to speak'}
          </p>
          {isListening && (
            <div className="flex gap-1 mt-3">
              {Array.from({length: 5}, (_, i) => (
                <div key={i} className="w-1 rounded-full bg-red-400"
                  style={{ height: `${12 + Math.random() * 20}px`, animation: `pulse ${0.5 + i * 0.1}s ease-in-out infinite alternate` }} />
              ))}
            </div>
          )}
        </div>

        {/* Chat */}
        <div className="glass rounded-2xl overflow-hidden">
          <div className="p-4 border-b flex items-center justify-between" style={{ borderColor: 'var(--border)' }}>
            <h3 className="font-semibold text-white" style={{ fontFamily: 'Rajdhani' }}>Conversation</h3>
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-emerald-400 agent-active" />
              <span className="text-xs text-slate-400">Agent Active</span>
            </div>
          </div>

          <div className="h-72 overflow-y-auto p-4 space-y-3">
            {chat.map((msg, i) => (
              <div key={i} className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-xs rounded-2xl px-4 py-2.5 text-sm ${
                  msg.type === 'user' ? 'text-white' : 'text-slate-200'
                }`}
                  style={msg.type === 'user' ? { background: 'linear-gradient(135deg, #e11d48, #be123c)' } :
                    { background: 'rgba(255,255,255,0.08)', border: '1px solid var(--border)' }}>
                  {msg.type === 'agent' && <div className="text-xs text-slate-400 mb-1">🤖 Tax Vaapsi AI</div>}
                  <p>{msg.text}</p>
                  <div className="text-xs opacity-50 mt-1 text-right">{msg.time}</div>
                </div>
              </div>
            ))}
          </div>

          <div className="p-4 border-t" style={{ borderColor: 'var(--border)' }}>
            <div className="flex gap-2">
              <input value={inputText} onChange={e => setInputText(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && handleSend()}
                className="input-dark flex-1 px-4 py-2.5 rounded-xl text-sm"
                placeholder={`Type in ${LANGUAGES.find(l => l.code === selectedLang)?.name}...`} />
              <button onClick={() => handleSend()} className="btn-primary px-4 py-2.5 rounded-xl">
                <Send size={18} />
              </button>
            </div>
          </div>
        </div>

        {/* Quick commands */}
        <div className="glass rounded-2xl p-4">
          <h4 className="text-sm font-semibold text-slate-300 mb-3">Quick Commands</h4>
          <div className="grid grid-cols-2 gap-2">
            {SAMPLE_COMMANDS.map((cmd, i) => (
              <button key={i} onClick={() => handleSend(cmd.cmd)}
                className="text-left p-3 rounded-xl text-sm hover:bg-white/8 transition-colors"
                style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid var(--border)' }}>
                <div className="text-slate-200 font-medium">"{cmd.cmd}"</div>
                <div className="text-xs text-slate-500 mt-0.5">{LANGUAGES.find(l => l.code === cmd.lang)?.name}</div>
              </button>
            ))}
          </div>
        </div>
      </div>
    </DashboardLayout>
  )
}
