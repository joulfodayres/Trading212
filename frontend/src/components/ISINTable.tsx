import { useState } from 'react'
import { Plus, Edit2, Trash2 } from 'lucide-react'

interface ISIN {
  id: string
  isin: string
  ticker: string
  name: string
  automation_enabled: boolean
  currency: string
}

export default function ISINTable() {
  const [isins, setIsins] = useState<ISIN[]>([
    {
      id: '1',
      isin: 'IE00BK5BQT80',
      ticker: 'VWCEd_EQ',
      name: 'Vanguard FTSE All-World (Acc)',
      automation_enabled: true,
      currency: 'EUR'
    }
  ])
  const [showAddForm, setShowAddForm] = useState(false)
  const [newISIN, setNewISIN] = useState('')

  const handleAdd = () => {
    if (newISIN) {
      // TODO: Chamar API para adicionar ISIN
      setIsins([...isins, {
        id: Date.now().toString(),
        isin: newISIN,
        ticker: '',
        name: '',
        automation_enabled: false,
        currency: 'EUR'
      }])
      setNewISIN('')
      setShowAddForm(false)
    }
  }

  const handleDelete = (id: string) => {
    // TODO: Chamar API para deletar ISIN
    setIsins(isins.filter(i => i.id !== id))
  }

  return (
    <div>
      <button
        onClick={() => setShowAddForm(!showAddForm)}
        className="mb-6 flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition"
      >
        <Plus size={20} />
        Novo ISIN
      </button>

      {showAddForm && (
        <div className="mb-6 bg-white p-4 rounded-lg shadow">
          <div className="flex gap-2">
            <input
              type="text"
              value={newISIN}
              onChange={(e) => setNewISIN(e.target.value)}
              placeholder="Cole o ISIN ou Ticker..."
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              onClick={handleAdd}
              className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition"
            >
              Adicionar
            </button>
          </div>
        </div>
      )}

      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-100 border-b">
            <tr>
              <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">ISIN</th>
              <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Ticker</th>
              <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Nome</th>
              <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Automação</th>
              <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Ações</th>
            </tr>
          </thead>
          <tbody>
            {isins.map((isin) => (
              <tr key={isin.id} className="border-b hover:bg-gray-50">
                <td className="px-6 py-3 font-mono text-sm">{isin.isin}</td>
                <td className="px-6 py-3 text-sm">{isin.ticker}</td>
                <td className="px-6 py-3 text-sm">{isin.name || '-'}</td>
                <td className="px-6 py-3 text-sm">
                  <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                    isin.automation_enabled
                      ? 'bg-green-100 text-green-800'
                      : 'bg-gray-100 text-gray-800'
                  }`}>
                    {isin.automation_enabled ? '✓ Ativo' : '✗ Inativo'}
                  </span>
                </td>
                <td className="px-6 py-3 text-sm">
                  <div className="flex gap-2">
                    <button className="text-blue-600 hover:text-blue-800">
                      <Edit2 size={18} />
                    </button>
                    <button
                      onClick={() => handleDelete(isin.id)}
                      className="text-red-600 hover:text-red-800"
                    >
                      <Trash2 size={18} />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
