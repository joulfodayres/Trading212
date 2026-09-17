import { useState, useEffect } from 'react'
import { AlertCircle, Check, X, ChevronUp } from 'lucide-react'
import { Button } from './ui/Button'
import { useToast } from './ui/Toast'
import { apiClient } from '../api/client'

interface Strategy {
  id: string
  strategy_name: string
}

interface AutomationBottomSheetProps {
  isOpen: boolean
  type: 'enable' | 'disable'
  isin: string
  onConfirm: (strategyId?: string) => Promise<void>
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
  const [loadingStrategies, setLoadingStrategies] = useState(false)
  const [confirming, setConfirming] = useState(false)
  const toast = useToast()

  // Load enabled strategies when sheet opens for enable
  useEffect(() => {
    if (isOpen && type === 'enable') {
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
      toast.error('Erro ao carregar estratégias')
    } finally {
      setLoadingStrategies(false)
    }
  }

  const handleConfirm = async () => {
    if (type === 'enable' && !selectedStrategy) {
      toast.error('Seleciona uma estratégia')
      return
    }

    setConfirming(true)
    try {
      await onConfirm(type === 'enable' ? selectedStrategy : undefined)
    } finally {
      setConfirming(false)
    }
  }

  if (!isOpen) return null

  return (
    <>
      {/* Overlay semi-transparente (apenas para desfoque de background) */}
      <div
        className="fixed inset-0 bg-black bg-opacity-40 transition-opacity z-40"
        onClick={onCancel}
      />

      {/* Bottom Sheet */}
      <div className="fixed bottom-0 left-0 right-0 bg-t212-bg-primary rounded-t-2xl shadow-2xl z-50 max-h-[80vh] overflow-y-auto">
        {/* Handle bar (visual indicator) */}
        <div className="flex justify-center pt-3 pb-2">
          <div className="w-12 h-1 bg-t212-border rounded-full" />
        </div>

        {/* Header */}
        <div className="px-6 py-4 border-b border-t212-border sticky top-0 bg-t212-bg-primary rounded-t-2xl">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <AlertCircle className="text-t212-warning flex-shrink-0" size={24} />
              <div>
                <h3 className="text-lg font-bold text-t212-primary">
                  {type === 'enable' ? 'Ativar Automação' : 'Desativar Automação'}
                </h3>
                <p className="text-sm text-t212-primary font-semibold mt-1">
                  ISIN: {isin}
                </p>
              </div>
            </div>
            <button
              onClick={onCancel}
              disabled={confirming}
              className="p-2 hover:bg-t212-hover rounded-lg transition text-t212-secondary hover:text-t212-primary"
            >
              <X size={20} />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="px-6 py-6 space-y-6">
          {type === 'enable' ? (
            <>
              <div>
                <label className="block text-sm font-semibold text-t212-primary mb-3">
                  Escolhe a estratégia que queres associar a este ISIN:
                </label>

                {loadingStrategies ? (
                  <div className="h-10 bg-t212-hover rounded animate-pulse" />
                ) : strategies.length > 0 ? (
                  <select
                    value={selectedStrategy}
                    onChange={(e) => setSelectedStrategy(e.target.value)}
                    disabled={confirming}
                    className="w-full px-4 py-3 bg-t212-bg-secondary border-2 border-t212-primary rounded-lg text-t212-primary focus:outline-none focus:border-t212-warning transition font-medium"
                  >
                    {strategies.map((strategy) => (
                      <option key={strategy.id} value={strategy.id}>
                        {strategy.strategy_name}
                      </option>
                    ))}
                  </select>
                ) : (
                  <div className="p-4 bg-t212-bg-secondary border-2 border-t212-warning rounded-lg text-t212-warning font-medium">
                    Nenhuma estratégia ativada disponível
                  </div>
                )}
              </div>
            </>
          ) : (
            <div>
              <p className="text-t212-primary font-medium text-base leading-relaxed">
                Tens a certeza que queres{' '}
                <span className="text-t212-warning font-bold">desativar a automação</span> para este ISIN?
              </p>
              <p className="text-t212-secondary text-sm mt-2">
                Esta ação será registada no histórico de automação.
              </p>
            </div>
          )}
        </div>

        {/* Footer / Actions */}
        <div className="px-6 py-6 border-t border-t212-border bg-t212-bg-secondary sticky bottom-0 rounded-b-2xl flex gap-3">
          <Button
            variant="secondary"
            size="lg"
            icon={<X size={18} />}
            onClick={onCancel}
            disabled={confirming}
            className="flex-1"
          >
            Cancelar
          </Button>
          <Button
            variant="primary"
            size="lg"
            icon={<Check size={18} />}
            onClick={handleConfirm}
            isLoading={confirming}
            disabled={
              confirming ||
              loadingStrategies ||
              (type === 'enable' && strategies.length === 0)
            }
            className="flex-1"
          >
            Confirmar
          </Button>
        </div>
      </div>
    </>
  )
}
