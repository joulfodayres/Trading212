import { useState, useCallback } from 'react'
import { apiClient } from '../api/client'
import { useToast } from '../components/ui/Toast'

interface AutomationConfig {
  isin_id: string
  automation_enabled: boolean
  strategy_id: string | null
  strategy_name: string | null
}

export const useAutomation = () => {
  const [loading, setLoading] = useState(false)
  const toast = useToast()

  const toggleAutomation = useCallback(
    async (isin: string, automationEnabled: boolean, strategyId?: string): Promise<AutomationConfig | null> => {
      setLoading(true)
      try {
        const response = await apiClient.put(`/isins/${isin}/automation`, {
          automation_enabled: automationEnabled,
          strategy_id: strategyId || null
        })

        const action = automationEnabled ? 'ativada' : 'desativada'
        toast.success(`Automação ${action} com sucesso`)

        return response.data
      } catch (error: any) {
        console.error('Erro ao alternar automação:', error)
        const message = error.response?.data?.detail || 'Erro ao alterar automação'
        toast.error(message)
        return null
      } finally {
        setLoading(false)
      }
    },
    [toast]
  )

  return {
    toggleAutomation,
    loading
  }
}
