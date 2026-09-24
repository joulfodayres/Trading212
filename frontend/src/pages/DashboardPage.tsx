import { useState, useEffect } from 'react'
import Sidebar from '../components/Sidebar'
import ISINTable from '../components/ISINTable'
import StrategiesPage from './StrategiesPage'
import ConfigPage from './ConfigPage'
import ReportsPage from './ReportsPage'
import { TradingConsumptionPanel } from '../components/TradingConsumptionPanel'
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card'
import { useGlobalAutomation } from '../hooks/useGlobalAutomation'

export default function DashboardPage() {
  const [activeView, setActiveView] = useState('isins') // 'isins', 'strategies', 'config', 'history'
  const { status, fetchStatus } = useGlobalAutomation()

  useEffect(() => {
    fetchStatus()
  }, [fetchStatus])

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
              {activeView === 'isins' && '📊 My ISINs'}
              {activeView === 'strategies' && '⚙️ Strategies'}
              {activeView === 'config' && '⚙️ Configuration'}
              {activeView === 'reports' && '📄 Reports'}
              {activeView === 'history' && '📈 History'}
            </h1>
          </div>

          <TradingConsumptionPanel disabledReason={status?.automation_disabled_reason} />

          {activeView === 'isins' && (
            <div>
              {/* ISINs Table */}
              <Card>
                <CardHeader>
                  <CardTitle>ISINs Table</CardTitle>
                </CardHeader>
                <CardContent>
                  <ISINTable />
                </CardContent>
              </Card>
            </div>
          )}

          {activeView === 'strategies' && <StrategiesPage />}

          {activeView === 'config' && (
            <ConfigPage />
          )}

          {activeView === 'reports' && <ReportsPage />}

          {activeView === 'history' && (
            <div>
              <Card>
                <CardHeader>
                  <CardTitle>Trade History</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-t212-secondary">Under construction...</p>
                </CardContent>
              </Card>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
