import { useState } from 'react'
import { Settings } from 'lucide-react'
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card'
import { Input } from '../components/ui/Input'
import { Button } from '../components/ui/Button'
import { useToast } from '../components/ui/Toast'
import { apiClient } from '../api/client'
import { ConfigForm } from '../components/ConfigForm'

interface StrategyParams {
  buy_threshold_percent: number
  sell_threshold_percent: number
  buy_quantity_percent: number
  sell_quantity_percent: number
  check_interval_seconds: number
  max_position_size_percent: number
  stop_loss_percent: number
  max_drawdown_percent: number
}

export default function ConfigPage() {
  const [params, setParams] = useState<StrategyParams>({
    buy_threshold_percent: 1.0,
    sell_threshold_percent: 1.0,
    buy_quantity_percent: 50.0,
    sell_quantity_percent: 50.0,
    check_interval_seconds: 300,
    max_position_size_percent: 10.0,
    stop_loss_percent: 5.0,
    max_drawdown_percent: 10.0
  })
  const [loading, setLoading] = useState(false)
  const [activeTab, setActiveTab] = useState<'trading212' | 'strategy' | 'risk'>('trading212')
  const toast = useToast()

  const handleSaveStrategy = async () => {
    setLoading(true)
    try {
      const response = await apiClient.put('/config/strategy-params', params)
      toast.success('Parâmetros da estratégia guardados com sucesso!')
    } catch (error: any) {
      const message = error?.response?.data?.detail || 'Erro ao guardar parâmetros'
      toast.error(message)
    } finally {
      setLoading(false)
    }
  }

  const handleParamChange = (key: keyof StrategyParams, value: any) => {
    setParams({
      ...params,
      [key]: parseFloat(value) || 0
    })
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-2">
        <Settings size={24} className="text-t212-primary" />
        <h2 className="text-2xl font-bold text-t212-primary">Configuração</h2>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-t212-border">
        <button
          onClick={() => setActiveTab('trading212')}
          className={`px-4 py-3 font-medium transition-colors ${
            activeTab === 'trading212'
              ? 'border-b-2 border-t212-primary text-t212-primary'
              : 'text-t212-secondary hover:text-t212-primary'
          }`}
        >
          Trading 212
        </button>
        <button
          onClick={() => setActiveTab('strategy')}
          className={`px-4 py-3 font-medium transition-colors ${
            activeTab === 'strategy'
              ? 'border-b-2 border-t212-primary text-t212-primary'
              : 'text-t212-secondary hover:text-t212-primary'
          }`}
        >
          Estratégia
        </button>
        <button
          onClick={() => setActiveTab('risk')}
          className={`px-4 py-3 font-medium transition-colors ${
            activeTab === 'risk'
              ? 'border-b-2 border-t212-primary text-t212-primary'
              : 'text-t212-secondary hover:text-t212-primary'
          }`}
        >
          Gestão de Risco
        </button>
      </div>

      {/* Tab Content */}
      <div>
        {/* Trading 212 Config */}
        {activeTab === 'trading212' && (
          <ConfigForm />
        )}

        {/* Strategy Params */}
        {activeTab === 'strategy' && (
          <Card>
            <CardHeader>
              <CardTitle>Parâmetros da Estratégia Grid Trading</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Buy Configuration */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-t212-primary flex items-center gap-2">
                  📈 Compra (BUY)
                </h3>
                <Input
                  label="Limite de Compra (%)"
                  type="number"
                  step="0.1"
                  min="0.1"
                  value={params.buy_threshold_percent}
                  onChange={(e) => handleParamChange('buy_threshold_percent', e.target.value)}
                  hint="Percentagem de queda para dispara compra. Ex: 1.0 = -1%"
                />
                <Input
                  label="Quantidade de Compra (%)"
                  type="number"
                  step="1"
                  min="1"
                  max="100"
                  value={params.buy_quantity_percent}
                  onChange={(e) => handleParamChange('buy_quantity_percent', e.target.value)}
                  hint="Percentagem do capital a usar. Ex: 50 = 50% do saldo"
                />
              </div>

              {/* Sell Configuration */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-t212-primary flex items-center gap-2">
                  📉 Venda (SELL)
                </h3>
                <Input
                  label="Limite de Venda (%)"
                  type="number"
                  step="0.1"
                  min="0.1"
                  value={params.sell_threshold_percent}
                  onChange={(e) => handleParamChange('sell_threshold_percent', e.target.value)}
                  hint="Percentagem de subida para disparar venda. Ex: 1.0 = +1%"
                />
                <Input
                  label="Quantidade de Venda (%)"
                  type="number"
                  step="1"
                  min="1"
                  max="100"
                  value={params.sell_quantity_percent}
                  onChange={(e) => handleParamChange('sell_quantity_percent', e.target.value)}
                  hint="Percentagem da posição a vender. Ex: 50 = 50% da posição"
                />
              </div>

              {/* Check Interval */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-t212-primary flex items-center gap-2">
                  ⏱️ Frequência
                </h3>
                <Input
                  label="Intervalo de Verificação (segundos)"
                  type="number"
                  step="60"
                  min="60"
                  value={params.check_interval_seconds}
                  onChange={(e) => handleParamChange('check_interval_seconds', e.target.value)}
                  hint="Tempo entre verificações. Ex: 300 = 5 minutos"
                />
              </div>

              <Button
                variant="primary"
                onClick={handleSaveStrategy}
                isLoading={loading}
                className="w-full"
              >
                Guardar Parâmetros
              </Button>
            </CardContent>
          </Card>
        )}

        {/* Risk Management */}
        {activeTab === 'risk' && (
          <Card>
            <CardHeader>
              <CardTitle>Gestão de Risco</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="p-4 rounded-lg bg-t212-warning bg-opacity-10 border border-t212-warning text-t212-warning text-sm">
                ⚠️ Estes parâmetros protegem o seu capital limitando o risco por operação
              </div>

              <div className="space-y-4">
                <Input
                  label="Tamanho Máximo de Posição (%)"
                  type="number"
                  step="1"
                  min="1"
                  max="100"
                  value={params.max_position_size_percent}
                  onChange={(e) => handleParamChange('max_position_size_percent', e.target.value)}
                  hint="% máxima do capital em uma posição. Ex: 10 = máx 10% do saldo"
                />

                <Input
                  label="Stop Loss (%)"
                  type="number"
                  step="0.1"
                  min="0.1"
                  value={params.stop_loss_percent}
                  onChange={(e) => handleParamChange('stop_loss_percent', e.target.value)}
                  hint="Perda máxima aceitável. Ex: 5 = vende se perder 5%"
                />

                <Input
                  label="Drawdown Máximo (%)"
                  type="number"
                  step="1"
                  min="1"
                  value={params.max_drawdown_percent}
                  onChange={(e) => handleParamChange('max_drawdown_percent', e.target.value)}
                  hint="Queda máxima do capital. Ex: 10 = para se cair 10% total"
                />
              </div>

              <Button
                variant="primary"
                onClick={handleSaveStrategy}
                isLoading={loading}
                className="w-full"
              >
                Guardar Parâmetros de Risco
              </Button>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Info Card */}
      <Card className="border-t212-info border-opacity-30">
        <CardContent className="pt-6">
          <div className="space-y-3 text-sm text-t212-secondary">
            <p>💡 <strong>Dica:</strong> Comece com parâmetros conservadores e ajuste conforme ganhe experiência.</p>
            <p>🔒 <strong>Segurança:</strong> Suas credenciais são encriptadas e nunca são expostas.</p>
            <p>⚙️ <strong>Atualizações:</strong> Os parâmetros são aplicados na próxima verificação do scheduler.</p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
