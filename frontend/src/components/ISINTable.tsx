import { useState, useEffect } from 'react'
import { Plus, RefreshCw, TrendingUp, TrendingDown } from 'lucide-react'
import { Button } from './ui/Button'
import { Input } from './ui/Input'
import { ToggleSwitch } from './ui/ToggleSwitch'
import { useToast } from './ui/Toast'
import { apiClient } from '../api/client'

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
  const [isins, setIsins] = useState<ISIN[]>([])
  const [showAddForm, setShowAddForm] = useState(false)
  const [newISIN, setNewISIN] = useState('')
  const [loadingSync, setLoadingSync] = useState(false)
  const [loadingList, setLoadingList] = useState(true)
  const toast = useToast()

  // Fetch ISINs na primeira carga
  useEffect(() => {
    loadISINs()
  }, [])

  // Carregar ISINs da API
  const loadISINs = async () => {
    setLoadingList(true)
    try {
      const response = await apiClient.get('/api/isins')
      setIsins(response.data)
    } catch (error) {
      console.error('Erro ao carregar ISINs:', error)
      toast.error('Erro ao carregar ISINs')
      // Se erro, começar com lista vazia
      setIsins([])
    } finally {
      setLoadingList(false)
    }
  }

  // Sincronizar carteira com T212
  const handleSync = async () => {
    setLoadingSync(true)
    toast.info('Sincronizando carteira...')
    try {
      const response = await apiClient.get('/api/isins/sync-from-trading212')
      const { isins: syncedISINs, message } = response.data

      // Atualizar lista com ISINs sincronizados
      setIsins(syncedISINs)
      toast.success(message || 'Carteira sincronizada com sucesso!')

      // Guardar timestamp em localStorage
      localStorage.setItem('last_sync_date', new Date().toISOString())
    } catch (error: any) {
      const message = error?.response?.data?.detail || 'Erro ao sincronizar carteira'
      toast.error(message)
      console.error('Erro ao sincronizar:', error)
    } finally {
      setLoadingSync(false)
    }
  }

  // Adicionar novo ISIN
  const handleAdd = async () => {
    if (!newISIN) {
      toast.error('Por favor, insira um ISIN ou Ticker')
      return
    }

    try {
      // TODO: Chamar API POST /api/isins
      const newISINObj: ISIN = {
        id: Date.now().toString(),
        isin: newISIN,
        ticker: '',
        name: '',
        automation_enabled: false,
        currency: 'EUR'
      }

      setIsins([...isins, newISINObj])
      setNewISIN('')
      setShowAddForm(false)
      toast.success('ISIN adicionado com sucesso!')
    } catch (error) {
      toast.error('Erro ao adicionar ISIN')
      console.error('Erro:', error)
    }
  }

  // Toggle automação
  const handleToggle = async (id: string) => {
    try {
      // TODO: Chamar API PUT /api/isins/{id}/automation/toggle
      setIsins(isins.map(i =>
        i.id === id ? { ...i, automation_enabled: !i.automation_enabled } : i
      ))

      const isin = isins.find(i => i.id === id)
      if (isin) {
        const action = !isin.automation_enabled ? 'ativada' : 'desativada'
        toast.success(`Automação ${action} para ${isin.ticker}`)
      }
    } catch (error) {
      toast.error('Erro ao toggle automação')
      console.error('Erro:', error)
    }
  }

  // Loading skeleton
  if (loadingList) {
    return (
      <div className="space-y-4">
        <div className="h-10 bg-t212-hover rounded-lg animate-pulse"></div>
        <div className="h-64 bg-t212-hover rounded-lg animate-pulse"></div>
      </div>
    )
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
          isLoading={loadingSync}
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
      {isins.length > 0 ? (
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
      ) : (
        <div className="text-center py-12">
          <p className="text-t212-secondary mb-4">Nenhum ISIN adicionado ainda</p>
          <p className="text-t212-muted text-sm mb-6">
            Clique em "Sincronizar Carteira" para importar suas posições do Trading 212
          </p>
          <Button
            variant="primary"
            onClick={handleSync}
            isLoading={loadingSync}
          >
            Sincronizar Carteira
          </Button>
        </div>
      )}
    </div>
  )
}
