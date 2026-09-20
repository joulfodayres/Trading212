import { useState, useCallback } from 'react'
import { apiClient } from '../api/client'

interface GlobalAutomationStatus {
  grid_trading_enabled: boolean
  scheduler_running: boolean
  cycle_count: number
  last_cycle_duration?: number
}

export const useGlobalAutomation = () => {
  const [loading, setLoading] = useState(false)
  const [status, setStatus] = useState<GlobalAutomationStatus | null>(null)

  const fetchStatus = useCallback(async () => {
    try {
      const response = await apiClient.get('/v1/automation/global-status')
      setStatus(response.data)
      return response.data
    } catch (error: any) {
      console.error('Error fetching global status:', error)
      return null
    }
  }, [])

  const enable = useCallback(async () => {
    setLoading(true)
    try {
      const response = await apiClient.put('/v1/automation/enable')
      if (response.data.success) {
        await fetchStatus()
        return true
      }
      return false
    } catch (error: any) {
      console.error('Error enabling global automation:', error)
      return false
    } finally {
      setLoading(false)
    }
  }, [fetchStatus])

  const disable = useCallback(async () => {
    setLoading(true)
    try {
      const response = await apiClient.put('/v1/automation/disable')
      if (response.data.success) {
        await fetchStatus()
        return true
      }
      return false
    } catch (error: any) {
      console.error('Error disabling global automation:', error)
      return false
    } finally {
      setLoading(false)
    }
  }, [fetchStatus])

  return {
    status,
    loading,
    fetchStatus,
    enable,
    disable
  }
}
