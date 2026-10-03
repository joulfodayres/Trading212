import { useEffect, useState } from 'react'
import { ListOrdered } from 'lucide-react'
import { Input } from './ui/Input'
import { Button } from './ui/Button'
import { manualOrdersAPI } from '../api'

interface Thresholds {
  mo_price_max_variation_pct: number
  mo_price_alert_variation_pct: number
  mo_price_max_interval_bp: number
  mo_amount_max: number
  mo_amount_max_interval_pct: number
  mo_quantity_max: number
  mo_quantity_max_interval_pct: number
}

const DEFAULTS: Thresholds = {
  mo_price_max_variation_pct: 10,
  mo_price_alert_variation_pct: 1,
  mo_price_max_interval_bp: 100,
  mo_amount_max: 100,
  mo_amount_max_interval_pct: 10,
  mo_quantity_max: 10,
  mo_quantity_max_interval_pct: 10,
}

function toInputValues(t: Thresholds): Record<keyof Thresholds, string> {
  return Object.fromEntries(
    Object.entries(t).map(([k, v]) => [k, String(v)])
  ) as Record<keyof Thresholds, string>
}

// Item #22 ("Gerir Ordens") — thresholds de validação para a geração manual
// de ordens a partir de parâmetros. Independentes do Item #15/#19 (não são
// limites de trading automático) e independentes por ambiente (cada
// DEMO/PROD tem a sua própria base de dados), mesma convenção da
// TradingLimitsSection.
export function ManualOrdersConfigSection() {
  const [thresholds, setThresholds] = useState<Thresholds>(DEFAULTS)
  const [inputs, setInputs] = useState<Record<keyof Thresholds, string>>(toInputValues(DEFAULTS))
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    manualOrdersAPI
      .getValidationThresholds()
      .then((res) => {
        setThresholds(res.data)
        setInputs(toInputValues(res.data))
      })
      .catch((e) => console.error('[ManualOrdersConfigSection] Error loading:', e))
      .finally(() => setLoading(false))
  }, [])

  const update = (key: keyof Thresholds, value: string) => {
    setInputs((prev) => ({ ...prev, [key]: value }))
  }

  const handleSave = async () => {
    setSaving(true)
    try {
      const payload = Object.fromEntries(
        Object.entries(inputs).map(([k, v]) => [k, Number(v)])
      ) as unknown as Thresholds
      const res = await manualOrdersAPI.updateValidationThresholds(payload)
      setThresholds(res.data)
      setInputs(toInputValues(res.data))
      console.log('[ManualOrdersConfigSection] Thresholds saved:', res.data)
    } catch (e) {
      console.error('[ManualOrdersConfigSection] Error saving thresholds:', e)
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-4 text-t212-secondary">
        <div className="animate-spin w-4 h-4 border-2 border-t212-primary border-t-transparent rounded-full mr-2" />
        Loading manual orders validation thresholds...
      </div>
    )
  }

  return (
    <div>
      <div className="flex items-center gap-2 mb-4">
        <ListOrdered size={18} className="text-t212-primary" />
        <h3 className="text-lg font-semibold text-t212-primary">Gerir Ordens — Validação</h3>
      </div>
      <p className="text-xs text-t212-secondary mb-4">
        Thresholds usados ao gerar novas ordens manualmente no ecrã "Gerir Ordens" (Item #22).
        Só a "Variação Máxima de Preço" bloqueia a geração — as restantes pedem apenas confirmação.
        Este caminho manual NÃO está sujeito aos limites de trading automático (Trading Limits acima).
      </p>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Input
          label="Variação Máxima de Preço (%)"
          type="number"
          min="0"
          step="0.1"
          value={inputs.mo_price_max_variation_pct}
          onChange={(e) => update('mo_price_max_variation_pct', e.target.value)}
          hint="Bloqueia a geração se excedido"
        />
        <Input
          label="Variação de Alerta de Preço (%)"
          type="number"
          min="0"
          step="0.1"
          value={inputs.mo_price_alert_variation_pct}
          onChange={(e) => update('mo_price_alert_variation_pct', e.target.value)}
        />
        <Input
          label="Intervalo Máximo de Preço (bp)"
          type="number"
          min="0"
          step="1"
          value={inputs.mo_price_max_interval_bp}
          onChange={(e) => update('mo_price_max_interval_bp', e.target.value)}
        />
        <Input
          label="Amount Máximo"
          type="number"
          min="0"
          step="1"
          value={inputs.mo_amount_max}
          onChange={(e) => update('mo_amount_max', e.target.value)}
        />
        <Input
          label="Intervalo Máximo de Amount (%)"
          type="number"
          min="0"
          step="0.1"
          value={inputs.mo_amount_max_interval_pct}
          onChange={(e) => update('mo_amount_max_interval_pct', e.target.value)}
        />
        <Input
          label="Quantity Máximo"
          type="number"
          min="0"
          step="1"
          value={inputs.mo_quantity_max}
          onChange={(e) => update('mo_quantity_max', e.target.value)}
        />
        <Input
          label="Intervalo Máximo de Quantity (%)"
          type="number"
          min="0"
          step="0.1"
          value={inputs.mo_quantity_max_interval_pct}
          onChange={(e) => update('mo_quantity_max_interval_pct', e.target.value)}
        />
      </div>

      <Button variant="primary" onClick={handleSave} isLoading={saving} className="mt-4">
        Save Thresholds
      </Button>
    </div>
  )
}
