import { useState, useCallback } from 'react'
import { apiClient } from '../api/client'

interface AutomationConfig {
  isin_id: string
  automation_enabled: boolean
  strategy_id: string | null
  strategy_name: string | null
}

export const useAutomation = () => {
  const [loading, setLoading] = useState(false)

  const toggleAutomation = useCallback(
    async (isin: string, automationEnabled: boolean, strategyId?: string): Promise<AutomationConfig | null> => {
      setLoading(true)
      try {
        const response = await apiClient.put(`/isins/${isin}/automation`, {
          automation_enabled: automationEnabled,
          strategy_id: strategyId || null
        })

        return response.data
      } catch (error: any) {
        console.error('Erro ao alternar automação:', error)
        return null
      } finally {
        setLoading(false)
      }
    },
    []
  )

  return {
    toggleAutomation,
    loading
  }
}
