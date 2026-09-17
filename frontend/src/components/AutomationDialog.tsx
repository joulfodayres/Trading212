import { useState, useEffect } from 'react'
import { AlertCircle, Check, X } from 'lucide-react'
import { Button } from './ui/Button'
import { useToast } from './ui/Toast'
import { apiClient } from '../api/client'

interface Strategy {
  id: string
  strategy_name: string
}

interface AutomationDialogProps {
  isOpen: boolean
  type: 'enable' | 'disable'
  isin: string
  onConfirm: (strategyId?: string) => Promise<void>
  onCancel: () => void
}

export const AutomationDialog: React.FC<AutomationDialogProps> = ({
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

  // Load enabled strategies when dialog opens for enable
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
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-t212-bg-secondary rounded-lg shadow-lg max-w-md w-full mx-4 border border-t212-border">
        {/* Header */}
        <div className="p-6 border-b border-t212-border">
          <div className="flex items-start gap-3">
            <AlertCircle className="text-t212-warning flex-shrink-0 mt-1" size={24} />
            <div>
              <h3 className="text-lg font-semibold text-t212-primary">
                {type === 'enable' ? 'Ativar Automação' : 'Desativar Automação'}
              </h3>
              <p className="text-sm text-t212-secondary mt-1">ISIN: {isin}</p>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 space-y-4">
          {type === 'enable' ? (
            <>
              <p className="text-t212-primary text-sm">
                Escolhe a estratégia que queres associar a este ISIN:
              </p>

              {loadingStrategies ? (
                <div className="h-10 bg-t212-hover rounded animate-pulse"></div>
              ) : strategies.length > 0 ? (
                <select
                  value={selectedStrategy}
                  onChange={(e) => setSelectedStrategy(e.target.value)}
                  disabled={confirming}
                  className="w-full px-3 py-2 bg-t212-bg-primary border border-t212-border rounded text-t212-primary focus:outline-none focus:border-t212-primary transition"
                >
                  {strategies.map((strategy) => (
                    <option key={strategy.id} value={strategy.id}>
                      {strategy.strategy_name}
                    </option>
                  ))}
                </select>
              ) : (
                <div className="p-3 bg-t212-hover rounded text-t212-secondary text-sm">
                  Nenhuma estratégia ativada disponível
                </div>
              )}
            </>
          ) : (
            <p className="text-t212-primary text-sm">
              Tens a certeza que queres <strong>desativar a automação</strong> para este ISIN?
            </p>
          )}
        </div>

        {/* Footer */}
        <div className="p-6 border-t border-t212-border flex gap-3 justify-end">
          <Button
            variant="secondary"
            size="md"
            icon={<X size={18} />}
            onClick={onCancel}
            disabled={confirming}
          >
            Cancelar
          </Button>
          <Button
            variant="primary"
            size="md"
            icon={<Check size={18} />}
            onClick={handleConfirm}
            isLoading={confirming}
            disabled={
              confirming ||
              loadingStrategies ||
              (type === 'enable' && strategies.length === 0)
            }
          >
            Confirmar
          </Button>
        </div>
      </div>
    </div>
  )
}
