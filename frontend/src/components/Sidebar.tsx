import { LogOut, Settings, BarChart3, History, TrendingUp } from 'lucide-react'
import { useAuthStore } from '../stores/authStore'
import { Button } from './ui/Button'

interface SidebarProps {
  activeView: string
  setActiveView: (view: string) => void
}

export default function Sidebar({ activeView, setActiveView }: SidebarProps) {
  const { logout } = useAuthStore()

  const menuItems = [
    { id: 'isins', label: 'ISINs', icon: BarChart3 },
    { id: 'config', label: 'Configuração', icon: Settings },
    { id: 'history', label: 'Histórico', icon: History },
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
          <p className="text-xs text-t212-muted mb-1">Logado como</p>
          <p className="text-sm text-t212-primary truncate">teste@trading212.com</p>
        </div>

        <Button
          variant="danger"
          size="sm"
          onClick={logout}
          icon={<LogOut size={16} />}
          className="w-full"
        >
          Sair
        </Button>
      </div>
    </aside>
  )
}
