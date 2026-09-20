import { useState } from 'react'
import Sidebar from '../components/Sidebar'
import ISINTable from '../components/ISINTable'
import ConfigPage from './ConfigPage'
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card'

export default function DashboardPage() {
  const [activeView, setActiveView] = useState('isins') // 'isins', 'config', 'history'

  return (
    <div className="flex h-screen bg-gradient-to-b from-t212-bg-dark to-t212-bg-darker">
      {/* Sidebar */}
      <Sidebar activeView={activeView} setActiveView={setActiveView} />

      {/* Main Content */}
      <div className="main-content flex-1 overflow-auto">
        <div className="page-container">
          {/* Header */}
          <div className="mb-8">
            <h1 className="page-header">
              {activeView === 'isins' && '📊 Meus ISINs'}
              {activeView === 'config' && '⚙️ Configuração'}
              {activeView === 'history' && '📈 Histórico'}
            </h1>
          </div>

          {activeView === 'isins' && (
            <div>
              {/* ISINs Table */}
              <Card>
                <CardHeader>
                  <CardTitle>Tabela de ISINs</CardTitle>
                </CardHeader>
                <CardContent>
                  <ISINTable />
                </CardContent>
              </Card>
            </div>
          )}

          {activeView === 'config' && (
            <ConfigPage />
          )}

          {activeView === 'history' && (
            <div>
              <Card>
                <CardHeader>
                  <CardTitle>Histórico de Trades</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-t212-secondary">Em construção...</p>
                </CardContent>
              </Card>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
