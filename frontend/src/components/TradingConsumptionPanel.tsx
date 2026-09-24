import { useEffect, useState } from 'react'
import { AlertTriangle } from 'lucide-react'
import { Card, CardContent } from './ui/Card'
import { apiClient } from '../api/client'

interface Consumption {
  daily_spend: number
  max_daily_spend: number | null
}

// Item #15: mostra o consumo do gasto diário face ao limite configurado, e
// destaca (se aplicável) porque é que a automação está parada. Visível no
// topo do dashboard, independentemente da view ativa.
export function TradingConsumptionPanel({ disabledReason }: { disabledReason?: string | null }) {
  const [consumption, setConsumption] = useState<Consumption | null>(null)

  useEffect(() => {
    const fetchConsumption = () => {
      apiClient
        .get('/v1/automation/consumption')
        .then((r) => setConsumption(r.data))
        .catch((e) => console.error('[TradingConsumptionPanel] Error:', e))
    }
    fetchConsumption()
    const interval = setInterval(fetchConsumption, 30000)
    return () => clearInterval(interval)
  }, [])

  if (!consumption && !disabledReason) return null

  const hasLimit = consumption?.max_daily_spend !== null && consumption?.max_daily_spend !== undefined
  const pct = hasLimit && consumption!.max_daily_spend
    ? Math.min(100, (consumption!.daily_spend / consumption!.max_daily_spend) * 100)
    : 0
  const isNearLimit = pct >= 80

  return (
    <div className="space-y-3 mb-6">
      {disabledReason && (
        <Card className="border-t212-error border-opacity-50">
          <CardContent className="py-3">
            <div className="flex items-center gap-2 text-t212-error text-sm">
              <AlertTriangle size={18} />
              <span>
                <strong>Automação parada:</strong> {disabledReason}
              </span>
            </div>
          </CardContent>
        </Card>
      )}

      {consumption && hasLimit && (
        <Card>
          <CardContent className="py-3">
            <div className="flex items-center justify-between text-sm mb-2">
              <span className="text-t212-secondary">Gasto diário</span>
              <span className={isNearLimit ? 'text-t212-error font-semibold' : 'text-t212-primary font-semibold'}>
                €{consumption.daily_spend.toFixed(2)} / €{consumption.max_daily_spend!.toFixed(2)}
              </span>
            </div>
            <div className="w-full h-2 rounded-full bg-t212-hover overflow-hidden">
              <div
                className={`h-full rounded-full transition-all ${isNearLimit ? 'bg-t212-error' : 'bg-t212-primary'}`}
                style={{ width: `${pct}%` }}
              />
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
