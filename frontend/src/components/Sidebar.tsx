import { LogOut, Settings, BarChart3, History } from 'lucide-react'
import { useAuthStore } from '../stores/authStore'

interface SidebarProps {
  activeView: string
  setActiveView: (view: string) => void
}

export default function Sidebar({ activeView, setActiveView }: SidebarProps) {
  const { logout } = useAuthStore()

  const menuItems = [
    { id: 'isins', label: '📊 ISINs', icon: BarChart3 },
    { id: 'config', label: '⚙️ Configuração', icon: Settings },
    { id: 'history', label: '📈 Histórico', icon: History },
  ]

  return (
    <aside className="sidebar p-6">
      <div className="mb-8">
        <h2 className="text-xl font-bold text-gray-900">🤖 T212 Bot</h2>
      </div>

      <nav className="space-y-2 mb-8">
        {menuItems.map((item) => (
          <button
            key={item.id}
            onClick={() => setActiveView(item.id)}
            className={`w-full text-left px-4 py-3 rounded-lg transition ${
              activeView === item.id
                ? 'bg-blue-600 text-white'
                : 'text-gray-700 hover:bg-gray-100'
            }`}
          >
            {item.label}
          </button>
        ))}
      </nav>

      <button
        onClick={logout}
        className="w-full flex items-center justify-center gap-2 px-4 py-3 text-red-600 hover:bg-red-50 rounded-lg transition"
      >
        <LogOut size={20} />
        Sair
      </button>
    </aside>
  )
}
