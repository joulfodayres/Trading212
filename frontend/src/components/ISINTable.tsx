import { useState, useEffect } from 'react'
import { RefreshCw, TrendingUp, TrendingDown } from 'lucide-react'
import { Button } from './ui/Button'
import { ToggleSwitch } from './ui/ToggleSwitch'
import { AutomationBottomSheet } from './AutomationBottomSheet'
import { useAutomation } from '../hooks/useAutomation'
import { apiClient } from '../api/client'

interface ISIN {
  isin: string
  ticker: string
  name: string
  currency: string
  quantity: number
  currentPrice: number
  averagePricePaid: number
  automation_enabled: boolean
  strategy_name?: string
  pnl: number
  pnl_percent: number
}

export default function ISINTable() {
  const [isins, setIsins] = useState<ISIN[]>([])
  const [loadingSync, setLoadingSync] = useState(false)
  const [loadingList, setLoadingList] = useState(true)
  const [dialogOpen, setDialogOpen] = useState(false)
  const [dialogType, setDialogType] = useState<'enable' | 'disable'>('enable')
  const [selectedISIN, setSelectedISIN] = useState<ISIN | null>(null)
  const { toggleAutomation, loading: automationLoading } = useAutomation()

  // Fetch ISINs na primeira carga
  useEffect(() => {
    // Auto-load ISINs on component mount
    loadISINs()
  }, [])

  // Carregar ISINs da API (dados frescos da T212)
  const loadISINs = async () => {
    setLoadingList(true)
    setLoadingSync(true)
    try {
      console.log('[ISINTable] Fetching ISINs from backend...')
      const response = await apiClient.get('/isins')
      console.log('[ISINTable] ISINs received:', response.data)
      setIsins(response.data)
    } catch (error) {
      console.error('Erro ao carregar ISINs:', error)
      setIsins([])
    } finally {
      setLoadingList(false)
      setLoadingSync(false)
    }
  }

  // Sincronizar carteira com T212
  const handleSync = async () => {
    setLoadingSync(true)
    try {
      console.log('[ISINTable] Syncing with T212 API...')
      const response = await apiClient.post('/isins/sync')
      console.log('[ISINTable] Sync response:', response.data)

      if (response.data.success) {
        // Após sync bem-sucedido, recarregar ISINs
        await loadISINs()
      }
    } catch (error) {
      console.error('Erro ao sincronizar carteira:', error)
    } finally {
      setLoadingSync(false)
    }
  }

  // Handler para toggle automação
  function handleToggleAutomation(isin: ISIN, currentState: boolean) {
    setSelectedISIN(isin)
    if (currentState) {
      // Desativar - pedir confirmação
      setDialogType('disable')
      setDialogOpen(true)
    } else {
      // Ativar - mostrar dialog de escolha de estratégia
      setDialogType('enable')
      setDialogOpen(true)
    }
  }

  async function handleDialogConfirm(strategyId?: string) {
    if (!selectedISIN) return

    const result = await toggleAutomation(
      selectedISIN.isin,
      dialogType === 'enable',
      strategyId
    )

    if (result) {
      // Atualizar o ISIN na lista local
      setIsins((prev) =>
        prev.map((item) =>
          item.isin === selectedISIN.isin
            ? {
                ...item,
                automation_enabled: result.automation_enabled,
                strategy_name: result.strategy_name || undefined
              }
            : item
        )
      )
      setDialogOpen(false)
      setSelectedISIN(null)
    }
  }

  function handleDialogCancel() {
    setDialogOpen(false)
    setSelectedISIN(null)
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

      {/* Automation Bottom Sheet */}
      {selectedISIN && (
        <AutomationBottomSheet
          isOpen={dialogOpen}
          type={dialogType}
          isin={selectedISIN.isin}
          onConfirm={handleDialogConfirm}
          onCancel={handleDialogCancel}
        />
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
                <th>Quantidade</th>
                <th>Preço Atual</th>
                <th>Preço Médio</th>
                <th>P&L</th>
                <th>Automação</th>
                <th>Estratégia</th>
              </tr>
            </thead>
            <tbody>
              {isins.map((isin) => (
                <tr key={isin.isin}>
                  <td>
                    <span className="font-mono text-sm text-t212-primary">{isin.isin}</span>
                  </td>
                  <td>
                    <span className="font-semibold text-t212-primary">{isin.ticker}</span>
                  </td>
                  <td>
                    <span className="text-t212-primary">{isin.name}</span>
                  </td>
                  <td>
                    <span className="text-t212-primary">{isin.quantity.toFixed(2)}</span>
                  </td>
                  <td>
                    <span className="text-t212-primary">
                      €{isin.currentPrice.toFixed(2)}
                    </span>
                  </td>
                  <td>
                    <span className="text-t212-primary">
                      €{isin.averagePricePaid.toFixed(2)}
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
                      onChange={() => handleToggleAutomation(isin, isin.automation_enabled)}
                      disabled={automationLoading}
                    />
                  </td>
                  <td>
                    {isin.automation_enabled && isin.strategy_name ? (
                      <span className="px-2 py-1 bg-t212-success bg-opacity-20 text-t212-success rounded text-sm">
                        {isin.strategy_name}
                      </span>
                    ) : (
                      <span className="text-t212-muted text-sm">-</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="text-center py-12">
          <p className="text-t212-secondary mb-4">Nenhuma posição aberta</p>
          <p className="text-t212-muted text-sm">
            Clique em "Sincronizar Carteira" acima para carregares as tuas posições do Trading 212
          </p>
        </div>
      )}
    </div>
  )
}
