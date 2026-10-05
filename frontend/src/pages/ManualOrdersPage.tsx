import { useState, useEffect, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft } from 'lucide-react'
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card'
import { Button } from '../components/ui/Button'
import { manualOrdersAPI } from '../api'

// ===== Types =====

type Side = 'BUY' | 'SELL'

interface CurrentOrder {
  t212_order_id: number
  created_at: string
  side: Side
  price: number
  quantity: number
  variation_pct: number
}

interface CurrentOrderUiState {
  mode: 'idle' | 'editing' | 'edited' | 'deleted'
  newPrice: number
  newQuantity: number
}

interface ScreenData {
  isin: string
  ticker: string
  name: string
  current_price: number
  quantity: number
  portfolio_value: number
  pnl_percent: number
  current_orders: CurrentOrder[]
  quantity_precision: number
  price_precision: number
  validation_thresholds: Record<string, number>
  last_params?: { sell: Record<string, any>; buy: Record<string, any> } | null
}

interface SideParamsState {
  initialPrice: string
  priceIntervalBp: string
  accPrice: 'Y' | 'N'
  useAmount: boolean
  initialAmount: string
  amountIntervalPct: string
  accAmount: 'Y' | 'N'
  initialQuantity: string
  quantityIntervalPct: string
  accQuantity: 'Y' | 'N'
  step: string
  multiplier: string
  numberOfOrders: string
}

interface GeneratedOrder {
  side: Side
  price: number
  quantity: number
}

const defaultSideParams = (initialPrice: string): SideParamsState => ({
  initialPrice,
  priceIntervalBp: '50',
  accPrice: 'N',
  useAmount: false,
  initialAmount: '50',
  amountIntervalPct: '0',
  accAmount: 'N',
  initialQuantity: '1',
  quantityIntervalPct: '0',
  accQuantity: 'N',
  step: '0',
  multiplier: '1',
  numberOfOrders: '3'
})

// Builds a SideParamsState from a saved (snake_case, backend) params object,
// for pre-filling the form with the last-used generation params for this
// ISIN. `initialPrice` is ALWAYS the current market price, never restored
// from `saved` — see db/manual_orders_last_params.sql for why. Any field
// that's null in `saved` (e.g. the inactive Amount/Quantity zone) falls
// back to the hardcoded default for that specific field, so the inactive
// zone still has a sensible placeholder if the user later toggles to it.
const sideParamsFromSaved = (saved: Record<string, any>, initialPrice: string): SideParamsState => {
  const d = defaultSideParams(initialPrice)
  return {
    initialPrice,
    priceIntervalBp: saved.price_interval_bp != null ? String(saved.price_interval_bp) : d.priceIntervalBp,
    accPrice: saved.acc_price ?? d.accPrice,
    useAmount: saved.use_amount ?? d.useAmount,
    initialAmount: saved.initial_amount != null ? String(saved.initial_amount) : d.initialAmount,
    amountIntervalPct: saved.amount_interval_pct != null ? String(saved.amount_interval_pct) : d.amountIntervalPct,
    accAmount: saved.acc_amount ?? d.accAmount,
    initialQuantity: saved.initial_quantity != null ? String(saved.initial_quantity) : d.initialQuantity,
    quantityIntervalPct: saved.quantity_interval_pct != null ? String(saved.quantity_interval_pct) : d.quantityIntervalPct,
    accQuantity: saved.acc_quantity ?? d.accQuantity,
    step: saved.step != null ? String(saved.step) : d.step,
    multiplier: saved.multiplier != null ? String(saved.multiplier) : d.multiplier,
    numberOfOrders: saved.number_of_orders != null ? String(saved.number_of_orders) : d.numberOfOrders
  }
}

// ===== Component =====

export default function ManualOrdersPage() {
  const { isin } = useParams<{ isin: string }>()
  const navigate = useNavigate()

  const [screen, setScreen] = useState<ScreenData | null>(null)
  const [loading, setLoading] = useState(true)
  const [loadError, setLoadError] = useState<string | null>(null)

  const [mode, setMode] = useState<'existing' | 'new'>('new')

  // Current Orders state
  const [coState, setCoState] = useState<Record<number, CurrentOrderUiState>>({})
  const [executeResultMsg, setExecuteResultMsg] = useState<string | null>(null)
  const [executing, setExecuting] = useState(false)

  // Parameters state
  const [sellParams, setSellParams] = useState<SideParamsState>(defaultSideParams('0'))
  const [buyParams, setBuyParams] = useState<SideParamsState>(defaultSideParams('0'))

  // New Orders state
  const [newOrders, setNewOrders] = useState<GeneratedOrder[]>([])
  const [generating, setGenerating] = useState(false)
  const [applying, setApplying] = useState(false)
  const [applyResultMsg, setApplyResultMsg] = useState<string | null>(null)

  // Modal state (generic confirm/alert modal)
  const [modal, setModal] = useState<{
    title: string
    text?: string
    list?: string[]
    hideConfirm?: boolean
    cancelLabel?: string
    onConfirm?: () => void
    onCancel?: () => void
  } | null>(null)

  const loadScreen = useCallback(async () => {
    if (!isin) return
    setLoading(true)
    setLoadError(null)
    try {
      const res = await manualOrdersAPI.getScreen(isin)
      const data: ScreenData = res.data
      setScreen(data)
      const initial: Record<number, CurrentOrderUiState> = {}
      data.current_orders.forEach((o) => {
        initial[o.t212_order_id] = { mode: 'idle', newPrice: o.price, newQuantity: o.quantity }
      })
      setCoState(initial)
      const currentPriceStr = data.current_price.toFixed(data.price_precision)
      setSellParams(
        data.last_params?.sell ? sideParamsFromSaved(data.last_params.sell, currentPriceStr) : defaultSideParams(currentPriceStr)
      )
      setBuyParams(
        data.last_params?.buy ? sideParamsFromSaved(data.last_params.buy, currentPriceStr) : defaultSideParams(currentPriceStr)
      )
    } catch (err: any) {
      console.error('[ManualOrdersPage] Error loading screen:', err)
      setLoadError(err?.response?.data?.detail || 'Erro ao carregar dados do ecrã.')
    } finally {
      setLoading(false)
    }
  }, [isin])

  useEffect(() => {
    loadScreen()
  }, [loadScreen])

  if (!isin) return null

  // ===== Current Orders helpers =====

  const sortOrders = <T extends { side: Side; price: number }>(list: T[]): T[] =>
    [...list].sort((a, b) => {
      if (a.side !== b.side) return a.side === 'SELL' ? -1 : 1
      return b.price - a.price
    })

  const pendingCoCount = () =>
    Object.values(coState).filter((s) => s.mode === 'edited' || s.mode === 'deleted').length

  const updateCoState = (id: number, patch: Partial<CurrentOrderUiState>) => {
    setCoState((prev) => ({ ...prev, [id]: { ...prev[id], ...patch } }))
  }

  const handleDiscardCurrent = () => {
    if (!screen) return
    const reset: Record<number, CurrentOrderUiState> = {}
    screen.current_orders.forEach((o) => {
      reset[o.t212_order_id] = { mode: 'idle', newPrice: o.price, newQuantity: o.quantity }
    })
    setCoState(reset)
    setExecuteResultMsg(null)
  }

  const handleExecuteCurrent = async () => {
    if (!screen) return
    const edits = screen.current_orders
      .filter((o) => coState[o.t212_order_id]?.mode === 'edited')
      .map((o) => ({
        t212_order_id: o.t212_order_id,
        side: o.side,
        new_price: coState[o.t212_order_id].newPrice,
        new_quantity: coState[o.t212_order_id].newQuantity
      }))
    const cancels = screen.current_orders
      .filter((o) => coState[o.t212_order_id]?.mode === 'deleted')
      .map((o) => o.t212_order_id)

    if (edits.length === 0 && cancels.length === 0) return

    setExecuting(true)
    setExecuteResultMsg(null)
    try {
      const res = await manualOrdersAPI.executeCurrent(screen.isin, screen.ticker, { edits, cancels })
      const { created, deleted, errors } = res.data
      setExecuteResultMsg(`✅ ${created} ordem(ns) criada(s) · ${deleted} ordem(ns) apagada(s) · ${errors} erro(s)`)
      await loadScreen()
    } catch (err: any) {
      console.error('[ManualOrdersPage] Error executing current order changes:', err)
      setExecuteResultMsg('❌ Erro ao aplicar as alterações. Ver consola para detalhes.')
    } finally {
      setExecuting(false)
    }
  }

  // ===== Mode switch =====

  const requestModeChange = (requested: 'existing' | 'new') => {
    const pending = pendingCoCount()
    if (pending > 0 && requested !== mode) {
      setModal({
        title: 'Mudar de modo?',
        text: `Tens ${pending} alteração(ões) não aplicada(s) na lista de ordens atuais. Mudar de modo vai descartá-las.`,
        onConfirm: () => {
          handleDiscardCurrent()
          setMode(requested)
          setModal(null)
        },
        onCancel: () => setModal(null)
      })
    } else {
      setMode(requested)
    }
  }

  // ===== Parameters / generation =====

  const buildSideParamsPayload = (p: SideParamsState) => ({
    initial_price: parseFloat(p.initialPrice) || 0,
    price_interval_bp: parseFloat(p.priceIntervalBp) || 0,
    acc_price: p.accPrice,
    use_amount: p.useAmount,
    initial_amount: p.useAmount ? parseFloat(p.initialAmount) || 0 : null,
    amount_interval_pct: p.useAmount ? parseFloat(p.amountIntervalPct) || 0 : null,
    acc_amount: p.useAmount ? p.accAmount : null,
    initial_quantity: !p.useAmount ? parseFloat(p.initialQuantity) || 0 : null,
    quantity_interval_pct: !p.useAmount ? parseFloat(p.quantityIntervalPct) || 0 : null,
    acc_quantity: !p.useAmount ? p.accQuantity : null,
    step: parseInt(p.step) || 0,
    multiplier: parseFloat(p.multiplier) || 1,
    number_of_orders: parseInt(p.numberOfOrders) || 1
  })

  const doGenerate = async (confirmedSoftAlerts: boolean) => {
    if (!screen) return
    setGenerating(true)
    try {
      const res = await manualOrdersAPI.generate({
        isin: screen.isin,
        current_price: screen.current_price,
        quantity_precision: screen.quantity_precision,
        price_precision: screen.price_precision,
        sell: buildSideParamsPayload(sellParams),
        buy: buildSideParamsPayload(buyParams),
        confirmed_soft_alerts: confirmedSoftAlerts
      })
      const { hard_errors, soft_alerts, requires_confirmation, orders } = res.data

      if (hard_errors.length > 0) {
        setModal({
          title: '❌ Não é possível gerar',
          text: 'As seguintes condições bloqueiam a geração de ordens:',
          list: hard_errors,
          hideConfirm: true,
          cancelLabel: 'Fechar',
          onCancel: () => setModal(null)
        })
        return
      }

      if (requires_confirmation && soft_alerts.length > 0) {
        setModal({
          title: '⚠️ Confirmar parâmetros fora do habitual',
          text: 'As seguintes condições foram detetadas — confirma se pretendes continuar mesmo assim:',
          list: soft_alerts,
          onConfirm: () => {
            setModal(null)
            doGenerate(true)
          },
          onCancel: () => setModal(null)
        })
        return
      }

      setNewOrders(orders)
      setApplyResultMsg(null)
    } catch (err: any) {
      console.error('[ManualOrdersPage] Error generating new orders:', err)
      setModal({
        title: '❌ Erro ao gerar',
        text: err?.response?.data?.detail || 'Ocorreu um erro ao gerar as ordens.',
        hideConfirm: true,
        cancelLabel: 'Fechar',
        onCancel: () => setModal(null)
      })
    } finally {
      setGenerating(false)
    }
  }

  const handleApplyNew = async (confirmedEmpty: boolean) => {
    if (!screen) return
    setApplying(true)
    setApplyResultMsg(null)
    try {
      const res = await manualOrdersAPI.applyNew(screen.isin, {
        isin: screen.isin,
        ticker: screen.ticker,
        new_orders: newOrders,
        quantity_precision: screen.quantity_precision,
        price_precision: screen.price_precision,
        confirmed_empty_list: confirmedEmpty
      })
      const { requires_empty_confirmation, created, deleted, unchanged, errors } = res.data

      if (requires_empty_confirmation) {
        setModal({
          title: '⚠️ Lista de New Orders vazia',
          text: `Não há ordens geradas. Ao aplicar, TODAS as ordens pendentes atuais no T212 para este ISIN serão APAGADAS e nenhuma nova será criada. Confirmas?`,
          onConfirm: () => {
            setModal(null)
            handleApplyNew(true)
          },
          onCancel: () => setModal(null)
        })
        return
      }

      setApplyResultMsg(
        `✅ ${created} ordem(ns) criada(s) · ${deleted} ordem(ns) apagada(s) · ${unchanged} inalterada(s) · ${errors} erro(s)`
      )
      await loadScreen()
    } catch (err: any) {
      console.error('[ManualOrdersPage] Error applying new orders:', err)
      setApplyResultMsg('❌ Erro ao aplicar as novas ordens. Ver consola para detalhes.')
    } finally {
      setApplying(false)
    }
  }

  // ===== Render helpers =====

  const fmtPct = (v: number) => `${v >= 0 ? '+' : ''}${v.toFixed(2)}%`
  const pctClass = (v: number) => (v >= 0 ? 'text-t212-success' : 'text-t212-error')
  const computeVariationPct = (price: number, referencePrice: number) =>
    referencePrice ? ((price - referencePrice) / referencePrice) * 100 : 0

  if (loading) {
    return (
      <div className="page-container">
        <p className="text-t212-muted">A carregar...</p>
      </div>
    )
  }

  if (loadError || !screen) {
    return (
      <div className="page-container">
        <Button variant="secondary" onClick={() => navigate('/dashboard')} icon={<ArrowLeft size={16} />}>
          Voltar
        </Button>
        <p className="text-t212-error mt-4">{loadError || 'ISIN não encontrado.'}</p>
      </div>
    )
  }

  const sortedCurrentOrders = sortOrders(screen.current_orders)
  const sortedNewOrders = sortOrders(newOrders)

  return (
    <div className="page-container">
      <Button variant="secondary" onClick={() => navigate('/dashboard')} icon={<ArrowLeft size={16} />} className="mb-4">
        Voltar
      </Button>

      <h1 className="page-header mb-6">Gerir Ordens</h1>

      {/* 2.1 Header info */}
      <Card className="mb-6">
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-6 gap-4">
            <div>
              <div className="text-xs uppercase text-t212-muted mb-1">ISIN</div>
              <div className="font-semibold">{screen.isin}</div>
            </div>
            <div>
              <div className="text-xs uppercase text-t212-muted mb-1">Nome</div>
              <div className="font-semibold">{screen.name}</div>
            </div>
            <div>
              <div className="text-xs uppercase text-t212-muted mb-1">Preço atual</div>
              <div className="font-semibold">€{screen.current_price.toFixed(screen.price_precision)}</div>
            </div>
            <div>
              <div className="text-xs uppercase text-t212-muted mb-1">Qtd. em carteira</div>
              <div className="font-semibold">{screen.quantity}</div>
            </div>
            <div>
              <div className="text-xs uppercase text-t212-muted mb-1">Valor carteira</div>
              <div className="font-semibold">€{screen.portfolio_value.toFixed(2)}</div>
            </div>
            <div>
              <div className="text-xs uppercase text-t212-muted mb-1">Valorização</div>
              <div className={`font-semibold ${pctClass(screen.pnl_percent)}`}>{fmtPct(screen.pnl_percent)}</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Mode switch */}
      <Card className="mb-6">
        <CardContent>
          <div className="flex gap-6 items-center">
            <strong className="text-sm">Modo:</strong>
            <label className="flex items-center gap-2 text-sm cursor-pointer">
              <input
                type="radio"
                name="mode"
                checked={mode === 'existing'}
                onChange={() => requestModeChange('existing')}
              />
              Editar ordens existentes
            </label>
            <label className="flex items-center gap-2 text-sm cursor-pointer">
              <input type="radio" name="mode" checked={mode === 'new'} onChange={() => requestModeChange('new')} />
              Criar novas ordens via parâmetros
            </label>
          </div>
        </CardContent>
      </Card>

      {/* 2.3 Parameters */}
      <Card className={`mb-6 ${mode !== 'new' ? 'opacity-40 pointer-events-none' : ''}`}>
        <CardHeader>
          <CardTitle>Parâmetros — gerar novas ordens</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-2 gap-6">
            <SideParamsForm label="SELL" colorClass="text-t212-error" params={sellParams} setParams={setSellParams} pricePrecision={screen.price_precision} />
            <SideParamsForm label="BUY" colorClass="text-t212-success" params={buyParams} setParams={setBuyParams} pricePrecision={screen.price_precision} />
          </div>
          <div className="flex justify-center mt-4">
            <Button variant="primary" isLoading={generating} onClick={() => doGenerate(false)}>
              GERAR novas ordens
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* 2.4 New Orders */}
      <Card className={`mb-10 ${mode !== 'new' ? 'opacity-40 pointer-events-none' : ''}`}>
        <CardHeader>
          <CardTitle>New Orders ({sortedNewOrders.length})</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="table w-full">
              <thead>
                <tr>
                  <th>Tipo</th>
                  <th>Preço</th>
                  <th>Quantidade</th>
                  <th>Var. % vs Initial Price</th>
                </tr>
              </thead>
              <tbody>
                {sortedNewOrders.map((o, idx) => {
                  const refPrice = o.side === 'SELL' ? parseFloat(sellParams.initialPrice) || 0 : parseFloat(buyParams.initialPrice) || 0
                  const variation = refPrice ? ((o.price - refPrice) / refPrice) * 100 : 0
                  return (
                    <tr key={idx}>
                      <td>
                        <span className={o.side === 'SELL' ? 'text-t212-error font-bold text-xs' : 'text-t212-success font-bold text-xs'}>
                          {o.side}
                        </span>
                      </td>
                      <td>{o.price.toFixed(screen.price_precision)}</td>
                      <td>{o.quantity.toFixed(screen.quantity_precision)}</td>
                      <td className={pctClass(variation)}>{fmtPct(variation)}</td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
            {sortedNewOrders.length === 0 && (
              <p className="text-center text-t212-muted py-4 text-sm">
                Ainda sem ordens geradas. Define os parâmetros acima e clica "GERAR".
              </p>
            )}
          </div>
          <div className="flex justify-between items-center mt-3">
            <span className="text-xs text-t212-muted">{applyResultMsg}</span>
            <Button variant="primary" isLoading={applying} onClick={() => handleApplyNew(false)}>
              APLICAR (matching com T212)
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* 2.2 Current Orders (moved to the end, per layout change) */}
      <Card className={`mb-10 ${mode !== 'existing' ? 'opacity-40 pointer-events-none' : ''}`}>
        <CardHeader>
          <CardTitle>Current Orders ({sortedCurrentOrders.length})</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="table w-full">
              <thead>
                <tr>
                  <th>Data criação</th>
                  <th>Tipo</th>
                  <th>Preço</th>
                  <th>Quantidade</th>
                  <th>Var. % vs atual</th>
                  <th className="text-right">Ações</th>
                </tr>
              </thead>
              <tbody>
                {sortedCurrentOrders.map((o) => {
                  const s = coState[o.t212_order_id]
                  if (!s) return null
                  const rowClass =
                    s.mode === 'editing' ? 'bg-t212-bg-darker' : s.mode === 'edited' ? 'bg-yellow-900/20' : s.mode === 'deleted' ? 'bg-red-900/20' : ''
                  return (
                    <tr key={o.t212_order_id} className={rowClass}>
                      <td>{o.created_at?.slice(0, 10) || '-'}</td>
                      <td>
                        <span className={o.side === 'SELL' ? 'text-t212-error font-bold text-xs' : 'text-t212-success font-bold text-xs'}>
                          {o.side}
                        </span>
                      </td>
                      <td>
                        {s.mode === 'editing' ? (
                          <input
                            type="number"
                            step={Math.pow(10, -screen.price_precision)}
                            className="w-20 bg-t212-bg-darker border border-t212-primary rounded px-1 py-0.5 text-sm no-spinner"
                            value={s.newPrice}
                            onChange={(e) => updateCoState(o.t212_order_id, { newPrice: parseFloat(e.target.value) || 0 })}
                          />
                        ) : s.mode === 'deleted' ? (
                          <span className="line-through text-t212-muted">{o.price.toFixed(screen.price_precision)}</span>
                        ) : (
                          (s.mode === 'edited' ? s.newPrice : o.price).toFixed(screen.price_precision)
                        )}
                      </td>
                      <td>
                        {s.mode === 'editing' ? (
                          <input
                            type="number"
                            className="w-20 bg-t212-bg-darker border border-t212-primary rounded px-1 py-0.5 text-sm no-spinner"
                            value={s.newQuantity}
                            onChange={(e) => updateCoState(o.t212_order_id, { newQuantity: parseFloat(e.target.value) || 0 })}
                          />
                        ) : s.mode === 'deleted' ? (
                          <span className="line-through text-t212-muted">{o.quantity}</span>
                        ) : (
                          s.mode === 'edited' ? s.newQuantity : o.quantity
                        )}
                      </td>
                      <td className={pctClass(s.mode === 'editing' || s.mode === 'edited' ? computeVariationPct(s.newPrice, screen.current_price) : o.variation_pct)}>
                        {fmtPct(s.mode === 'editing' || s.mode === 'edited' ? computeVariationPct(s.newPrice, screen.current_price) : o.variation_pct)}
                      </td>
                      <td className="text-right whitespace-nowrap">
                        {s.mode === 'editing' ? (
                          <>
                            <button
                              className="text-t212-success border border-t212-success rounded px-2 py-0.5 text-xs ml-1"
                              onClick={() => updateCoState(o.t212_order_id, { mode: s.newPrice === o.price && s.newQuantity === o.quantity ? 'idle' : 'edited' })}
                            >
                              ✓
                            </button>
                            <button
                              className="text-t212-error border border-t212-error rounded px-2 py-0.5 text-xs ml-1"
                              onClick={() => updateCoState(o.t212_order_id, { mode: 'idle', newPrice: o.price, newQuantity: o.quantity })}
                            >
                              ✗
                            </button>
                          </>
                        ) : s.mode === 'deleted' ? (
                          <button
                            className="text-t212-primary border border-t212-primary rounded px-2 py-0.5 text-xs ml-1"
                            onClick={() => updateCoState(o.t212_order_id, { mode: 'idle' })}
                          >
                            ↶ Desfazer
                          </button>
                        ) : (
                          <>
                            {s.mode === 'edited' && (
                              <span className="text-xs bg-yellow-700 text-yellow-100 rounded-full px-2 py-0.5 mr-1">editado</span>
                            )}
                            <button
                              className="border border-t212-border rounded px-2 py-0.5 text-xs ml-1"
                              onClick={() => updateCoState(o.t212_order_id, { mode: 'editing' })}
                            >
                              ✏️
                            </button>
                            <button
                              className="border border-t212-border rounded px-2 py-0.5 text-xs ml-1"
                              onClick={() => updateCoState(o.t212_order_id, { mode: 'deleted' })}
                            >
                              🗑️
                            </button>
                          </>
                        )}
                      </td>
                    </tr>
                  )
                })}
                {sortedCurrentOrders.length === 0 && (
                  <tr>
                    <td colSpan={6} className="text-center text-t212-muted py-4">
                      Sem ordens pendentes para este ISIN.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
          <div className="flex justify-between items-center mt-3">
            <span className="text-xs text-t212-muted">
              {pendingCoCount() > 0 ? `${pendingCoCount()} alteração(ões) pendente(s) — nada enviado ainda` : ''}
              {executeResultMsg && <div className="mt-1">{executeResultMsg}</div>}
            </span>
            <div>
              <Button variant="secondary" disabled={pendingCoCount() === 0 || executing} onClick={handleDiscardCurrent}>
                Descartar tudo
              </Button>
              <Button
                variant="primary"
                className="ml-2"
                disabled={pendingCoCount() === 0 || executing}
                isLoading={executing}
                onClick={handleExecuteCurrent}
              >
                EXECUTAR ({pendingCoCount()})
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Modal */}
      {modal && (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-[200]">
          <div className="bg-t212-bg-dark border border-t212-border rounded-lg p-6 max-w-md w-[90%]">
            <h3 className="text-base font-semibold mb-3">{modal.title}</h3>
            {modal.text && <p className="text-sm mb-3">{modal.text}</p>}
            {modal.list && modal.list.length > 0 && (
              <ul className="text-sm text-yellow-200 list-disc pl-5 mb-4 space-y-1">
                {modal.list.map((l, i) => (
                  <li key={i}>{l}</li>
                ))}
              </ul>
            )}
            <div className="flex justify-end gap-2">
              <Button variant="secondary" onClick={modal.onCancel}>
                {modal.cancelLabel || 'Cancelar'}
              </Button>
              {!modal.hideConfirm && (
                <Button variant="primary" onClick={modal.onConfirm}>
                  Confirmar
                </Button>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

// ===== Side parameters sub-form =====

function SideParamsForm({
  label,
  colorClass,
  params,
  setParams,
  pricePrecision
}: {
  label: string
  colorClass: string
  params: SideParamsState
  setParams: (p: SideParamsState) => void
  pricePrecision: number
}) {
  const update = (patch: Partial<SideParamsState>) => setParams({ ...params, ...patch })

  return (
    <div className="border border-t212-border rounded-lg p-4 bg-t212-bg-darker">
      <h3 className={`text-sm font-semibold mb-3 ${colorClass}`}>{label}</h3>

      <div className="mb-3 pb-3 border-b border-dashed border-t212-border">
        <div className="text-[10px] uppercase text-t212-muted mb-2">Zona 1 — Preço</div>
        <FieldRow label="Initial Price">
          <input
            type="number"
            step={Math.pow(10, -pricePrecision)}
            className="no-spinner"
            value={params.initialPrice}
            onChange={(e) => update({ initialPrice: e.target.value })}
          />
        </FieldRow>
        <FieldRow label="Price Interval (bp)">
          <input type="number" className="no-spinner" value={params.priceIntervalBp} onChange={(e) => update({ priceIntervalBp: e.target.value })} />
        </FieldRow>
        <FieldRow label="Acc. Price (Y/N)">
          <select value={params.accPrice} onChange={(e) => update({ accPrice: e.target.value as 'Y' | 'N' })}>
            <option value="Y">Y</option>
            <option value="N">N</option>
          </select>
        </FieldRow>
      </div>

      <div className="flex gap-4 mb-3 text-xs">
        <label className="flex items-center gap-1 cursor-pointer">
          <input type="radio" checked={params.useAmount} onChange={() => update({ useAmount: true })} /> Usar Amount
        </label>
        <label className="flex items-center gap-1 cursor-pointer">
          <input type="radio" checked={!params.useAmount} onChange={() => update({ useAmount: false })} /> Usar Quantity
        </label>
      </div>

      <div className={`mb-3 pb-3 border-b border-dashed border-t212-border ${!params.useAmount ? 'opacity-30 pointer-events-none' : ''}`}>
        <div className="text-[10px] uppercase text-t212-muted mb-2">Zona 2 — Amount</div>
        <FieldRow label="Initial Amount">
          <input type="number" className="no-spinner" value={params.initialAmount} onChange={(e) => update({ initialAmount: e.target.value })} />
        </FieldRow>
        <FieldRow label="Amount Interval (%)">
          <input
            type="number"
            className="no-spinner"
            value={params.amountIntervalPct}
            onChange={(e) => update({ amountIntervalPct: e.target.value })}
          />
        </FieldRow>
        <FieldRow label="Acc. Amount (Y/N)">
          <select value={params.accAmount} onChange={(e) => update({ accAmount: e.target.value as 'Y' | 'N' })}>
            <option value="Y">Y</option>
            <option value="N">N</option>
          </select>
        </FieldRow>
      </div>

      <div className={`mb-3 pb-3 border-b border-dashed border-t212-border ${params.useAmount ? 'opacity-30 pointer-events-none' : ''}`}>
        <div className="text-[10px] uppercase text-t212-muted mb-2">Zona 3 — Quantity</div>
        <FieldRow label="Initial Quantity">
          <input type="number" className="no-spinner" value={params.initialQuantity} onChange={(e) => update({ initialQuantity: e.target.value })} />
        </FieldRow>
        <FieldRow label="Quantity Interval (%)">
          <input
            type="number"
            className="no-spinner"
            value={params.quantityIntervalPct}
            onChange={(e) => update({ quantityIntervalPct: e.target.value })}
          />
        </FieldRow>
        <FieldRow label="Acc. Quantity (Y/N)">
          <select value={params.accQuantity} onChange={(e) => update({ accQuantity: e.target.value as 'Y' | 'N' })}>
            <option value="Y">Y</option>
            <option value="N">N</option>
          </select>
        </FieldRow>
      </div>

      <div className="mb-3 pb-3 border-b border-dashed border-t212-border">
        <div className="text-[10px] uppercase text-t212-muted mb-2">Zona 4 — Multiplier</div>
        <FieldRow label="Step">
          <input type="number" className="no-spinner" value={params.step} onChange={(e) => update({ step: e.target.value })} />
        </FieldRow>
        <FieldRow label="Multiplier">
          <input
            type="number"
            step="0.01"
            className="no-spinner"
            value={params.multiplier}
            onChange={(e) => update({ multiplier: e.target.value })}
          />
        </FieldRow>
      </div>

      <div>
        <div className="text-[10px] uppercase text-t212-muted mb-2">Zona 5</div>
        <FieldRow label="Number of Orders">
          <input
            type="number"
            className="no-spinner"
            value={params.numberOfOrders}
            onChange={(e) => update({ numberOfOrders: e.target.value })}
          />
        </FieldRow>
      </div>
    </div>
  )
}

function FieldRow({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="flex items-center justify-between mb-2 gap-2 text-xs">
      <label>{label}</label>
      {children}
    </div>
  )
}
