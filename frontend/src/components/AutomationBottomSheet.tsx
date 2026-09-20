import { useState, useEffect } from 'react'
import { Zap, X } from 'lucide-react'
import { Button } from './ui/Button'
import { apiClient } from '../api/client'

interface Strategy {
  id: string
  strategy_name: string
}

interface AutomationBottomSheetProps {
  isOpen: boolean
  type: 'enable' | 'disable' | 'edit'
  isin: string
  onConfirm: (strategyId?: string, initialInvestment?: number) => Promise<void>
  onCancel: () => void
}

export const AutomationBottomSheet: React.FC<AutomationBottomSheetProps> = ({
  isOpen,
  type,
  isin,
  onConfirm,
  onCancel
}) => {
  const [strategies, setStrategies] = useState<Strategy[]>([])
  const [selectedStrategy, setSelectedStrategy] = useState<string>('')
  const [initialInvestment, setInitialInvestment] = useState<string>('')
  const [loadingStrategies, setLoadingStrategies] = useState(false)
  const [confirming, setConfirming] = useState(false)

  // Load enabled strategies when sheet opens for enable or edit
  useEffect(() => {
    if (isOpen && (type === 'enable' || type === 'edit')) {
      loadStrategies()
    }
  }, [isOpen, type])

  const loadStrategies = async () => {
    setLoadingStrategies(true)
    try {
      const response = await apiClient.get('/isins/strategies')
      setStrategies(response.data)
      if (response.data.length > 0) {
        setSelectedStrategy(response.data[0].id)
      }
    } catch (error) {
      console.error('Erro ao carregar estratégias:', error)
    } finally {
      setLoadingStrategies(false)
    }
  }

  const handleConfirm = async () => {
    if ((type === 'enable' || type === 'edit') && !selectedStrategy) {
      return
    }

    setConfirming(true)
    try {
      const investment = type === 'edit' || type === 'enable' ? parseFloat(initialInvestment) || undefined : undefined
      await onConfirm(
        (type === 'enable' || type === 'edit') ? selectedStrategy : undefined,
        investment
      )
    } finally {
      setConfirming(false)
    }
  }

  if (!isOpen) return null

  return (
    <>
      {/* Overlay escuro (full coverage) */}
      <div
        className="fixed inset-0 bg-black bg-opacity-60 backdrop-blur-sm transition-opacity z-40"
        onClick={onCancel}
      />

      {/* Modal Centered (Trading 212 Style) */}
      <div className="fixed inset-0 flex items-center justify-center z-50 p-4">
        <div className="bg-t212-bg-primary rounded-2xl shadow-2xl border border-t212-border w-full max-w-md overflow-hidden">

          {/* Header com ícone e fechar */}
          <div className="px-6 py-5 border-b border-t212-border bg-gradient-to-r from-t212-bg-primary to-t212-bg-secondary flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-t212-warning bg-opacity-20 rounded-lg">
                <Zap className="text-t212-warning" size={20} />
              </div>
              <div>
                <h3 className="text-lg font-bold text-t212-primary">
                  {type === 'enable' ? 'Ativar Automação' : type === 'edit' ? 'Editar Automação' : 'Desativar Automação'}
                </h3>
                <p className="text-xs text-t212-secondary font-medium mt-0.5">
                  {isin}
                </p>
              </div>
            </div>
            <button
              onClick={onCancel}
              disabled={confirming}
              className="p-1.5 hover:bg-t212-hover rounded-lg transition text-t212-secondary hover:text-t212-primary"
            >
              <X size={20} />
            </button>
          </div>

          {/* Content */}
          <div className="px-6 py-6">
            {type === 'enable' || type === 'edit' ? (
              <div className="space-y-5">
                {/* Strategy Selection */}
                <div>
                  <label className="block text-sm font-semibold text-t212-primary mb-3">
                    Escolhe a estratégia:
                  </label>

                  {loadingStrategies ? (
                    <div className="h-11 bg-t212-hover rounded-lg animate-pulse" />
                  ) : strategies.length > 0 ? (
                    <select
                      value={selectedStrategy}
                      onChange={(e) => setSelectedStrategy(e.target.value)}
                      disabled={confirming}
                      className="w-full px-4 py-3 bg-t212-bg-secondary border-2 border-t212-primary rounded-lg text-t212-primary focus:outline-none focus:ring-2 focus:ring-t212-warning focus:border-transparent transition font-medium placeholder-t212-secondary"
                    >
                      {strategies.map((strategy) => (
                        <option key={strategy.id} value={strategy.id}>
                          {strategy.strategy_name}
                        </option>
                      ))}
                    </select>
                  ) : (
                    <div className="p-4 bg-t212-bg-secondary border-2 border-t212-warning rounded-lg text-t212-warning font-medium text-center">
                      Nenhuma estratégia disponível
                    </div>
                  )}
                </div>

                {/* Initial Investment */}
                <div>
                  <label className="block text-sm font-semibold text-t212-primary mb-3">
                    Investimento Inicial (EUR):
                  </label>

                  <input
                    type="number"
                    step="0.01"
                    min="0"
                    placeholder="Ex: 10.00"
                    value={initialInvestment}
                    onChange={(e) => setInitialInvestment(e.target.value)}
                    disabled={confirming}
                    className="w-full px-4 py-3 bg-t212-bg-secondary border-2 border-t212-primary rounded-lg text-t212-primary focus:outline-none focus:ring-2 focus:ring-t212-warning focus:border-transparent transition font-medium placeholder-t212-secondary"
                  />
                </div>
              </div>
            ) : (
              <div className="space-y-3">
                <p className="text-t212-primary font-semibold text-base leading-relaxed">
                  Tens a certeza que queres{' '}
                  <span className="text-t212-warning">desativar a automação</span>?
                </p>
                <p className="text-t212-secondary text-sm">
                  Esta ação será registada no histórico de automação e nenhum trade automático será realizado.
                </p>
              </div>
            )}
          </div>

          {/* Footer com botões */}
          <div className="px-6 py-4 border-t border-t212-border bg-t212-bg-secondary flex gap-3">
            <Button
              variant="secondary"
              size="md"
              onClick={onCancel}
              disabled={confirming}
              className="flex-1"
            >
              Cancelar
            </Button>
            <Button
              variant="primary"
              size="md"
              onClick={handleConfirm}
              isLoading={confirming}
              disabled={
                confirming ||
                loadingStrategies ||
                ((type === 'enable' || type === 'edit') && strategies.length === 0)
              }
              className="flex-1"
            >
              {type === 'edit' ? 'Guardar Mudanças' : 'Confirmar'}
            </Button>
          </div>
        </div>
      </div>
    </>
  )
}
