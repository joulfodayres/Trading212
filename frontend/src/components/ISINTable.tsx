import { useState } from 'react'
import { Plus, RefreshCw, TrendingUp, TrendingDown } from 'lucide-react'
import { Button } from './ui/Button'
import { Input } from './ui/Input'
import { Badge } from './ui/Badge'
import { ToggleSwitch } from './ui/ToggleSwitch'
import { useToast } from './ui/Toast'

interface ISIN {
  id: string
  isin: string
  ticker: string
  name: string
  automation_enabled: boolean
  currency: string
  price?: number
  pnl?: number
  pnl_percent?: number
}

export default function ISINTable() {
  const [isins, setIsins] = useState<ISIN[]>([
    {
      id: '1',
      isin: 'IE00BK5BQT80',
      ticker: 'VWCEd_EQ',
      name: 'Vanguard FTSE All-World (Acc)',
      automation_enabled: false,
      currency: 'EUR',
      price: 166.86,
      pnl: 24.50,
      pnl_percent: 2.1
    },
    {
      id: '2',
      isin: 'US9220427424',
      ticker: 'VOO',
      name: 'Vanguard S&P 500 ETF',
      automation_enabled: false,
      currency: 'EUR',
      price: 16.45,
      pnl: 12.30,
      pnl_percent: 0.8
    }
  ])
  const [showAddForm, setShowAddForm] = useState(false)
  const [newISIN, setNewISIN] = useState('')
  const [loadingSync, setLoadingSync] = useState(false)
  const toast = useToast()

  const handleSync = async () => {
    setLoadingSync(true)
    toast.info('Sincronizando carteira...')
    // TODO: Chamar API para sincronizar
    setTimeout(() => {
      setLoadingSync(false)
      toast.success('Carteira sincronizada com sucesso!')
    }, 2000)
  }

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
      toast.success('ISIN adicionado com sucesso!')
    }
  }

  const handleToggle = (id: string) => {
    setIsins(isins.map(i =>
      i.id === id ? { ...i, automation_enabled: !i.automation_enabled } : i
    ))
    const isin = isins.find(i => i.id === id)
    if (isin) {
      toast.success(`Automação ${!isin.automation_enabled ? 'ativada' : 'desativada'} para ${isin.ticker}`)
    }
  }

  return (
    <div className="space-y-4">
      {/* Action Bar */}
      <div className="flex gap-4">
        <Button
          variant="primary"
          size="md"
          icon={<Plus size={18} />}
          onClick={() => setShowAddForm(!showAddForm)}
        >
          Novo ISIN
        </Button>

        <Button
          variant="secondary"
          size="md"
          icon={<RefreshCw size={18} className={loadingSync ? 'animate-spin' : ''} />}
          onClick={handleSync}
          disabled={loadingSync}
        >
          Sincronizar Carteira
        </Button>
      </div>

      {/* Add Form */}
      {showAddForm && (
        <div className="card border-t212-primary border-opacity-20">
          <div className="flex gap-3">
            <Input
              type="text"
              value={newISIN}
              onChange={(e) => setNewISIN(e.target.value)}
              placeholder="Cole o ISIN ou Ticker..."
              className="flex-1"
            />
            <Button
              variant="primary"
              size="md"
              onClick={handleAdd}
            >
              Adicionar
            </Button>
            <Button
              variant="ghost"
              size="md"
              onClick={() => setShowAddForm(false)}
            >
              Cancelar
            </Button>
          </div>
        </div>
      )}

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="table w-full">
          <thead>
            <tr>
              <th>ISIN</th>
              <th>Ticker</th>
              <th>Nome</th>
              <th>Preço</th>
              <th>P&L</th>
              <th>Automação</th>
            </tr>
          </thead>
          <tbody>
            {isins.map((isin) => (
              <tr key={isin.id}>
                <td>
                  <span className="font-mono text-sm text-t212-primary">{isin.isin}</span>
                </td>
                <td>
                  <span className="font-semibold text-t212-primary">{isin.ticker}</span>
                </td>
                <td>
                  <span className="text-t212-primary">{isin.name || '-'}</span>
                </td>
                <td>
                  <span className="text-t212-primary">
                    {isin.price ? `€${isin.price.toFixed(2)}` : '-'}
                  </span>
                </td>
                <td>
                  {isin.pnl !== undefined ? (
                    <div className="flex items-center gap-2">
                      {isin.pnl >= 0 ? (
                        <>
                          <TrendingUp size={16} className="text-t212-success" />
                          <span className="price-positive">
                            +€{isin.pnl.toFixed(2)} ({isin.pnl_percent?.toFixed(1)}%)
                          </span>
                        </>
                      ) : (
                        <>
                          <TrendingDown size={16} className="text-t212-error" />
                          <span className="price-negative">
                            -€{Math.abs(isin.pnl).toFixed(2)} ({isin.pnl_percent?.toFixed(1)}%)
                          </span>
                        </>
                      )}
                    </div>
                  ) : (
                    <span className="text-t212-muted">-</span>
                  )}
                </td>
                <td>
                  <ToggleSwitch
                    checked={isin.automation_enabled}
                    onChange={() => handleToggle(isin.id)}
                  />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {isins.length === 0 && (
        <div className="text-center py-12">
          <p className="text-t212-secondary mb-4">Nenhum ISIN adicionado ainda</p>
          <Button
            variant="primary"
            onClick={() => setShowAddForm(true)}
          >
            Adicionar primeiro ISIN
          </Button>
        </div>
      )}
    </div>
  )
}
