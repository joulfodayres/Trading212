import { useState } from 'react'
import Sidebar from '../components/Sidebar'
import ISINTable from '../components/ISINTable'

export default function DashboardPage() {
  const [activeView, setActiveView] = useState('isins') // 'isins', 'config', 'history'

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <Sidebar activeView={activeView} setActiveView={setActiveView} />

      {/* Main Content */}
      <div className="main-content p-8">
        <div className="max-w-7xl mx-auto">
          {activeView === 'isins' && (
            <div>
              <h1 className="text-3xl font-bold mb-6">📊 ISINs</h1>
              <ISINTable />
            </div>
          )}

          {activeView === 'config' && (
            <div>
              <h1 className="text-3xl font-bold mb-6">⚙️ Configuração</h1>
              <p className="text-gray-600">Em construção...</p>
            </div>
          )}

          {activeView === 'history' && (
            <div>
              <h1 className="text-3xl font-bold mb-6">📈 Histórico</h1>
              <p className="text-gray-600">Em construção...</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
