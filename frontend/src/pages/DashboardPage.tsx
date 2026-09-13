import { useState } from 'react'
import Sidebar from '../components/Sidebar'
import ISINTable from '../components/ISINTable'
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
              {/* KPI Cards */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                <Card>
                  <div className="kpi-card">
                    <div className="kpi-label">Saldo Total</div>
                    <div className="kpi-value">€5.889,99</div>
                    <div className="kpi-change kpi-positive">+2.3% hoje</div>
                  </div>
                </Card>

                <Card>
                  <div className="kpi-card">
                    <div className="kpi-label">P&L Geral</div>
                    <div className="kpi-value text-t212-success">+€124,50</div>
                    <div className="kpi-change kpi-positive">+2.1%</div>
                  </div>
                </Card>

                <Card>
                  <div className="kpi-card">
                    <div className="kpi-label">Posições Abertas</div>
                    <div className="kpi-value">12</div>
                    <div className="kpi-change text-t212-info">2 com automação</div>
                  </div>
                </Card>

                <Card>
                  <div className="kpi-card">
                    <div className="kpi-label">Trades Hoje</div>
                    <div className="kpi-value">5</div>
                    <div className="kpi-change kpi-positive">4 ganhos</div>
                  </div>
                </Card>
              </div>

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
            <div>
              <Card>
                <CardHeader>
                  <CardTitle>Configuração de Trading 212</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-t212-secondary">Em construção...</p>
                </CardContent>
              </Card>
            </div>
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
