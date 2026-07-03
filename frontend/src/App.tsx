import { useState } from 'react'
import './App.css'

function App() {
  return (
    <div className="min-h-screen flex items-center justify-center" style={{ background: 'var(--color-bg)' }}>
      <div className="text-center space-y-4 p-8">
        <div className="text-6xl">🔍</div>
        <h1 className="text-4xl font-bold" style={{ color: 'var(--color-text-heading)' }}>
          Multi-Agent Stock Research System
        </h1>
        <p style={{ color: 'var(--color-text-muted)' }} className="text-lg max-w-md mx-auto">
          AI-powered financial research platform — full UI coming in Phase 7
        </p>
        <div
          className="inline-flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium"
          style={{ background: 'rgba(99, 102, 241, 0.15)', color: 'var(--color-primary-light)', border: '1px solid rgba(99, 102, 241, 0.3)' }}
        >
          ⚡ Phase 1 — Project Setup Complete
        </div>
      </div>
    </div>
  )
}

export default App
