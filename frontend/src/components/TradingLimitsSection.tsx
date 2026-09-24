import { useEffect, useState } from 'react'
import { ShieldAlert } from 'lucide-react'
import { Input } from './ui/Input'
import { Button } from './ui/Button'
import { apiClient } from '../api/client'

interface Limits {
  max_buy_order_value: number | null
  max_sell_order_value: number | null
  max_daily_spend: number | null
}

interface AlertSettings {
  login_threshold: boolean
  security_events: boolean
  limit_reached: boolean
  order_rejected: boolean
  invalid_credentials: boolean
  cycle_errors: boolean
  deploy_disabled: boolean
}

const ALERT_LABELS: Record<keyof AlertSettings, string> = {
  login_threshold: 'Várias tentativas de login falhadas',
  security_events: 'MFA desativado / killswitch acionado',
  limit_reached: 'Limite de trading atingido (automação parada)',
  order_rejected: 'T212 rejeitou uma ordem',
  invalid_credentials: 'Credenciais T212 inválidas',
  cycle_errors: 'Vários ciclos seguidos com erro',
  deploy_disabled: 'Automação desligada após deploy',
}

// Empty string in the input == "sem limite" (null enviado ao backend).
function toInputValue(v: number | null): string {
  return v === null || v === undefined ? '' : String(v)
}

function toApiValue(s: string): number | null {
  const trimmed = s.trim()
  if (trimmed === '') return null
  const n = Number(trimmed)
  return Number.isFinite(n) ? n : null
}

// Item #15: limites de trading (proteção de dinheiro real) + interruptores
// de alerta — ambos guardados em app_parameters, valores independentes por
// ambiente (cada DEMO/PROD tem a sua própria base de dados).
export function TradingLimitsSection() {
  const [limits, setLimits] = useState<Limits>({
    max_buy_order_value: null,
    max_sell_order_value: null,
    max_daily_spend: null,
  })
  const [limitsInput, setLimitsInput] = useState({ buy: '', sell: '', daily: '' })
  const [alerts, setAlerts] = useState<AlertSettings | null>(null)
  const [loading, setLoading] = useState(true)
  const [savingLimits, setSavingLimits] = useState(false)

  useEffect(() => {
    Promise.all([
      apiClient.get('/v1/automation/config/limits'),
      apiClient.get('/v1/automation/config/alerts'),
    ])
      .then(([limitsRes, alertsRes]) => {
        setLimits(limitsRes.data)
        setLimitsInput({
          buy: toInputValue(limitsRes.data.max_buy_order_value),
          sell: toInputValue(limitsRes.data.max_sell_order_value),
          daily: toInputValue(limitsRes.data.max_daily_spend),
        })
        setAlerts(alertsRes.data)
      })
      .catch((e) => console.error('[TradingLimitsSection] Error loading:', e))
      .finally(() => setLoading(false))
  }, [])

  const handleSaveLimits = async () => {
    setSavingLimits(true)
    try {
      const payload = {
        max_buy_order_value: toApiValue(limitsInput.buy),
        max_sell_order_value: toApiValue(limitsInput.sell),
        max_daily_spend: toApiValue(limitsInput.daily),
      }
      const res = await apiClient.put('/v1/automation/config/limits', payload)
      setLimits(res.data)
      console.log('[TradingLimitsSection] Limits saved:', res.data)
    } catch (e) {
      console.error('[TradingLimitsSection] Error saving limits:', e)
    } finally {
      setSavingLimits(false)
    }
  }

  const handleToggleAlert = async (key: keyof AlertSettings, value: boolean) => {
    if (!alerts) return
    const previous = alerts
    setAlerts({ ...alerts, [key]: value }) // optimistic
    try {
      const res = await apiClient.put('/v1/automation/config/alerts', { [key]: value })
      setAlerts(res.data)
    } catch (e) {
      console.error('[TradingLimitsSection] Error updating alert:', e)
      setAlerts(previous) // revert on failure
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-4 text-t212-secondary">
        <div className="animate-spin w-4 h-4 border-2 border-t212-primary border-t-transparent rounded-full mr-2" />
        Loading trading limits...
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Trading Limits */}
      <div>
        <div className="flex items-center gap-2 mb-4">
          <ShieldAlert size={18} className="text-t212-primary" />
          <h3 className="text-lg font-semibold text-t212-primary">Trading Limits</h3>
        </div>
        <p className="text-xs text-t212-secondary mb-4">
          Atingir qualquer limite para a automação por completo. As ordens pendentes na T212 não
          são canceladas — a retoma é sempre manual. Deixa em branco para não aplicar limite.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Input
            label="Máximo por ordem de compra (€)"
            type="number"
            min="0"
            step="0.01"
            placeholder="Sem limite"
            value={limitsInput.buy}
            onChange={(e) => setLimitsInput({ ...limitsInput, buy: e.target.value })}
          />
          <Input
            label="Máximo por ordem de venda (€)"
            type="number"
            min="0"
            step="0.01"
            placeholder="Sem limite"
            value={limitsInput.sell}
            onChange={(e) => setLimitsInput({ ...limitsInput, sell: e.target.value })}
          />
          <Input
            label="Máximo de gasto diário (€)"
            type="number"
            min="0"
            step="0.01"
            placeholder="Sem limite"
            value={limitsInput.daily}
            onChange={(e) => setLimitsInput({ ...limitsInput, daily: e.target.value })}
            hint="Compras executadas − vendas executadas com lucro, desde as 00:00"
          />
        </div>

        <Button variant="primary" onClick={handleSaveLimits} isLoading={savingLimits} className="mt-4">
          Save Limits
        </Button>
      </div>

      {/* Alert toggles */}
      {alerts && (
        <div className="border-t border-t212-border pt-6">
          <h3 className="text-lg font-semibold text-t212-primary mb-4">🔔 Alerts</h3>
          <div className="space-y-3">
            {(Object.keys(ALERT_LABELS) as Array<keyof AlertSettings>).map((key) => (
              <label key={key} className="flex items-center gap-3 text-sm text-t212-secondary cursor-pointer">
                <input
                  type="checkbox"
                  checked={alerts[key]}
                  onChange={(e) => handleToggleAlert(key, e.target.checked)}
                  className="rounded border-t212-border"
                />
                {ALERT_LABELS[key]}
              </label>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
