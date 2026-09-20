import { useState, useEffect } from 'react'
import { Settings } from 'lucide-react'
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card'
import { Input } from '../components/ui/Input'
import { Button } from '../components/ui/Button'
import { useToast } from '../components/ui/Toast'
import { apiClient } from '../api/client'
import { ConfigForm } from '../components/ConfigForm'

export default function ConfigPage() {
  const [schedulerInterval, setSchedulerInterval] = useState<number>(15)
  const [intervalInput, setIntervalInput] = useState<string>('15')
  const [loading, setLoading] = useState(false)
  const [loadingInterval, setLoadingInterval] = useState(true)
  const toast = useToast()

  // Fetch current scheduler interval on mount
  useEffect(() => {
    fetchSchedulerInterval()
  }, [])

  const fetchSchedulerInterval = async () => {
    try {
      setLoadingInterval(true)
      const response = await apiClient.get('/automation/config/interval')
      const interval = response.data.scheduler_interval_seconds || 15
      setSchedulerInterval(interval)
      setIntervalInput(String(interval))
    } catch (error: any) {
      const message = error?.response?.data?.detail || 'Erro ao carregar intervalo do scheduler'
      toast.error(message)
      // Keep current values on error
    } finally {
      setLoadingInterval(false)
    }
  }

  const handleSaveInterval = async () => {
    const interval = parseInt(intervalInput)

    if (isNaN(interval) || interval < 5 || interval > 300) {
      toast.error('Intervalo deve estar entre 5 e 300 segundos')
      return
    }

    setLoading(true)
    try {
      await apiClient.put('/automation/config/interval', {
        scheduler_interval_seconds: interval
      })
      setSchedulerInterval(interval)
      toast.success('Intervalo do scheduler atualizado com sucesso!')
    } catch (error: any) {
      const message = error?.response?.data?.detail || 'Erro ao guardar intervalo'
      toast.error(message)
      // Reset input on error
      setIntervalInput(String(schedulerInterval))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-2">
        <Settings size={24} className="text-t212-primary" />
        <h2 className="text-2xl font-bold text-t212-primary">Configuração</h2>
      </div>

      {/* Geral Section */}
      <Card>
        <CardHeader>
          <CardTitle>Geral</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Trading 212 Config */}
          <div>
            <h3 className="text-lg font-semibold text-t212-primary mb-4">Trading 212</h3>
            <ConfigForm />
          </div>

          {/* Scheduler Interval */}
          <div className="border-t border-t212-border pt-6 mt-6">
            <h3 className="text-lg font-semibold text-t212-primary mb-4">⏱️ Scheduler</h3>

            {loadingInterval ? (
              <div className="flex items-center justify-center py-4 text-t212-secondary">
                <div className="animate-spin w-4 h-4 border-2 border-t212-primary border-t-transparent rounded-full mr-2" />
                Carregando intervalo...
              </div>
            ) : (
              <div className="space-y-4">
                {/* Current Interval Display */}
                <div className="p-4 rounded-lg bg-t212-primary bg-opacity-5 border border-t212-primary border-opacity-20">
                  <div className="text-sm text-t212-secondary mb-1">Intervalo Atual</div>
                  <div className="text-2xl font-bold text-t212-primary">
                    {schedulerInterval}s
                  </div>
                  <div className="text-xs text-t212-secondary mt-1">
                    (~{Math.round(schedulerInterval / 60 * 10) / 10} minuto{schedulerInterval >= 60 ? 's' : ''})
                  </div>
                </div>

                {/* Interval Input */}
                <Input
                  label="Novo Intervalo (segundos)"
                  type="number"
                  step="5"
                  min="5"
                  max="300"
                  value={intervalInput}
                  onChange={(e) => setIntervalInput(e.target.value)}
                  hint="Intervalo entre ciclos de automação. Mín: 5s, Máx: 300s"
                />

                {/* Info Messages */}
                <div className="space-y-2 text-xs text-t212-secondary">
                  <p>📌 <strong>Intervalo recomendado:</strong> 15 segundos (padrão)</p>
                  <p>⚡ <strong>Menor intervalo:</strong> Mais responsivo, mais requisições à API</p>
                  <p>🔋 <strong>Maior intervalo:</strong> Menos requisições, resposta mais lenta</p>
                </div>

                {/* Save Button */}
                <Button
                  variant="primary"
                  onClick={handleSaveInterval}
                  isLoading={loading}
                  className="w-full"
                >
                  {loading ? 'Guardando...' : 'Guardar Intervalo'}
                </Button>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Info Card */}
      <Card className="border-t212-info border-opacity-30">
        <CardContent className="pt-6">
          <div className="space-y-3 text-sm text-t212-secondary">
            <p>💡 <strong>Dica:</strong> Utilize o intervalo do scheduler para controlar a frequência de execução da automação.</p>
            <p>🔒 <strong>Segurança:</strong> Suas credenciais são encriptadas e nunca são expostas.</p>
            <p>⚙️ <strong>Atualizações:</strong> As alterações ao intervalo entram em vigor imediatamente.</p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
