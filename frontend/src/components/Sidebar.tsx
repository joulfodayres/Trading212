import { useState, useEffect } from 'react'
import { LogOut, Settings, BarChart3, History, TrendingUp, Power, Sliders, FileText, Play } from 'lucide-react'
import { useAuthStore } from '../stores/authStore'
import { useGlobalAutomation } from '../hooks/useGlobalAutomation'
import { Button } from './ui/Button'
import { ToggleSwitch } from './ui/ToggleSwitch'

interface SidebarProps {
  activeView: string
  setActiveView: (view: string) => void
}

export default function Sidebar({ activeView, setActiveView }: SidebarProps) {
  const { logout } = useAuthStore()
  const { status, loading, fetchStatus, enable, disable, runOnce } = useGlobalAutomation()
  const [confirmDialog, setConfirmDialog] = useState(false)
  const [pendingAction, setPendingAction] = useState<'enable' | 'disable' | null>(null)

  useEffect(() => {
    fetchStatus()
    // Refresh status every 30 seconds
    const interval = setInterval(fetchStatus, 30000)
    return () => clearInterval(interval)
  }, [fetchStatus])

  const handleToggleGlobal = (checked: boolean) => {
    setPendingAction(checked ? 'enable' : 'disable')
    setConfirmDialog(true)
  }

  const handleConfirmToggle = async () => {
    if (pendingAction === 'enable') {
      await enable()
    } else if (pendingAction === 'disable') {
      await disable()
    }
    setConfirmDialog(false)
    setPendingAction(null)
  }

  const menuItems = [
    { id: 'isins', label: 'ISINs', icon: BarChart3 },
    { id: 'strategies', label: 'Strategies', icon: Sliders },
    { id: 'config', label: 'Configuration', icon: Settings },
    { id: 'reports', label: 'Reports', icon: FileText },
    { id: 'history', label: 'History', icon: History },
  ]

  return (
    <aside className="sidebar flex flex-col h-screen">
      {/* Logo */}
      <div className="p-6 border-b border-t212-border">
        <div className="flex items-center gap-3">
          <div className="flex items-center justify-center h-10 w-10 rounded-lg bg-gradient-to-br from-t212-primary to-t212-secondary">
            <TrendingUp size={20} className="text-gray-900" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-t212-primary">T212</h2>
            <p className="text-xs text-t212-muted">Bot Trader</p>
          </div>
        </div>
      </div>

      {/* Global Automation Toggle */}
      <div className="p-4 border-b border-t212-border">
        <div className="flex items-center justify-between gap-3 p-3 rounded-lg bg-gradient-to-r from-t212-bg-secondary to-t212-hover border border-t212-border">
          <div className="flex items-center gap-2">
            <div className={`p-2 rounded-lg ${status?.grid_trading_enabled ? 'bg-t212-success bg-opacity-20' : 'bg-t212-error bg-opacity-20'}`}>
              <Power size={16} className={status?.grid_trading_enabled ? 'text-t212-success' : 'text-t212-error'} />
            </div>
            <div className="flex-1">
              <p className="text-xs text-t212-muted">Automation</p>
              <p className="text-sm font-semibold text-t212-primary">
                {status?.grid_trading_enabled ? '🟢 Active' : '🔴 Inactive'}
              </p>
            </div>
          </div>
          <ToggleSwitch
            checked={status?.grid_trading_enabled || false}
            onChange={handleToggleGlobal}
            disabled={loading}
          />
        </div>
      </div>

      {/* Manual Cycle Button */}
      <div className="p-4 border-b border-t212-border">
        <button
          onClick={() => runOnce()}
          disabled={loading}
          className="w-full flex items-center justify-center gap-2 px-4 py-3 rounded-lg bg-gradient-to-r from-t212-primary to-t212-secondary text-gray-900 font-semibold text-sm hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed"
          title="Execute automation cycle once immediately"
        >
          <Play size={16} />
          <span>Run Cycle Once</span>
        </button>
      </div>

      {/* Navigation */}
      <nav className="sidebar-nav flex-1 p-4">
        <div className="space-y-2">
          {menuItems.map((item) => {
            const Icon = item.icon
            const isActive = activeView === item.id
            return (
              <button
                key={item.id}
                onClick={() => setActiveView(item.id)}
                className={`sidebar-item w-full rounded-lg ${isActive ? 'active' : ''}`}
              >
                <Icon size={18} />
                <span className="text-sm font-medium">{item.label}</span>
              </button>
            )
          })}
        </div>
      </nav>

      {/* User Info & Logout */}
      <div className="p-4 border-t border-t212-border">
        <div className="mb-4 p-3 rounded-lg bg-t212-hover border border-t212-border">
          <p className="text-xs text-t212-muted mb-1">Logged in as</p>
          <p className="text-sm text-t212-primary truncate">test@trading212.com</p>
        </div>

        <Button
          variant="danger"
          size="sm"
          onClick={logout}
          icon={<LogOut size={16} />}
          className="w-full"
        >
          Sign Out
        </Button>
      </div>

      {/* Confirmation Dialog */}
      {confirmDialog && (
        <>
          <div className="fixed inset-0 bg-black bg-opacity-60 backdrop-blur-sm z-40" onClick={() => setConfirmDialog(false)} />
          <div className="fixed inset-0 flex items-center justify-center z-50 p-4">
            <div className="bg-t212-bg-primary rounded-2xl shadow-2xl border border-t212-border w-full max-w-sm overflow-hidden">
              <div className="px-6 py-5 border-b border-t212-border">
                <h3 className="text-lg font-bold text-t212-primary">
                  {pendingAction === 'enable' ? 'Enable Automation' : 'Disable Automation'}
                </h3>
                <p className="text-sm text-t212-secondary mt-1">Global Action</p>
              </div>
              <div className="px-6 py-5">
                <p className="text-t212-primary font-semibold mb-2">
                  Are you sure you want to {pendingAction === 'enable' ? 'enable' : 'disable'} automation?
                </p>
                <p className="text-sm text-t212-secondary">
                  {pendingAction === 'enable'
                    ? 'This will start automatic processing of ISINs with automation enabled.'
                    : 'This will stop automatic processing of all ISINs.'}
                </p>
              </div>
              <div className="px-6 py-4 border-t border-t212-border bg-t212-bg-secondary flex gap-3">
                <Button
                  variant="secondary"
                  size="md"
                  onClick={() => setConfirmDialog(false)}
                  disabled={loading}
                  className="flex-1"
                >
                  Cancel
                </Button>
                <Button
                  variant={pendingAction === 'enable' ? 'primary' : 'danger'}
                  size="md"
                  onClick={handleConfirmToggle}
                  isLoading={loading}
                  disabled={loading}
                  className="flex-1"
                >
                  Confirm
                </Button>
              </div>
            </div>
          </div>
        </>
      )}
    </aside>
  )
}
