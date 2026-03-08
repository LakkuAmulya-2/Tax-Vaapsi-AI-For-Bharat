import type { Metadata } from 'next'
import './globals.css'
import { Toaster } from 'react-hot-toast'

export const metadata: Metadata = {
  title: 'Tax Vaapsi — India\'s First Autonomous Tax AI',
  description: 'We don\'t help you FILE taxes — We FIND hidden money and RECOVER it autonomously',
  icons: { icon: '/favicon.ico' },
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
      </head>
      <body>
        {children}
        <Toaster
          position="top-right"
          toastOptions={{
            style: {
              background: '#0d1527',
              color: '#e2e8f0',
              border: '1px solid rgba(225,29,72,0.3)',
              borderRadius: '10px',
              fontSize: '14px',
            },
            success: { iconTheme: { primary: '#4ade80', secondary: '#0d1527' } },
            error: { iconTheme: { primary: '#f43f6e', secondary: '#0d1527' } },
          }}
        />
      </body>
    </html>
  )
}
