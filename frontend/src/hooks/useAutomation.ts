import { useState, useCallback } from 'react'
import { apiClient } from '../api/client'

interface AutomationConfig {
  isin_id: string
  automation_enabled: boolean
  strategy_id: string | null
  strategy_name: string | null
  initial_investment?: number
}

interface Strategy {
  id: string
  strategy_name: string
}

export const useAutomation = () => {
  const [loading, setLoading] = useState(false)
  const [strategies, setStrategies] = useState<Strategy[]>([])

  const fetchStrategies = useCallback(async () => {
    try {
      const response = await apiClient.get('/isins/strategies')
      setStrategies(response.data)
      return response.data
    } catch (error: any) {
      console.error('Erro ao buscar estratégias:', error)
      return []
    }
  }, [])

  const toggleAutomation = useCallback(
    async (
      isin: string,
      automationEnabled: boolean,
      strategyId?: string
    ): Promise<AutomationConfig | null> => {
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
    fetchStrategies,
    strategies,
    loading
  }
}
