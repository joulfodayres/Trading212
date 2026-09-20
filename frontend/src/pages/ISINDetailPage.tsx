import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, TrendingUp, TrendingDown } from 'lucide-react'
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card'
import { Button } from '../components/ui/Button'
import { apiClient } from '../api/client'

interface ISINDetail {
  id: string
  isin: string
  ticker: string
  name: string
  price: number
  quantity: number
  average_price: number
  pnl: number
  pnl_percent: number
  currency: string
  automation_enabled: boolean
}

interface Trade {
  id: string
  type: 'BUY' | 'SELL'
  quantity: number
  price: number
  date: string
  status: string
  pnl?: number
}

export default function ISINDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [isin, setIsin] = useState<ISINDetail | null>(null)
  const [trades, setTrades] = useState<Trade[]>([])

  useEffect(() => {
    loadISINDetail()
  }, [id])

  const loadISINDetail = async () => {
    if (!id) return

    setLoading(true)
    try {
      // Chamar GET /api/isins/{id}
      const isinResponse = await apiClient.get(`/isins/${id}`)
      setIsin(isinResponse.data)

      // Chamar GET /api/isins/{id}/trades
      try {
        const tradesResponse = await apiClient.get(`/isins/${id}/trades`)
        setTrades(tradesResponse.data || [])
      } catch (error) {
        // Se endpoint não existe ainda, manter array vazio
        console.log('Endpoint /trades não disponível ainda')
        setTrades([])
      }
    } catch (error: any) {
      const message = error?.response?.data?.detail || 'Erro ao carregar detalhes do ISIN'
      console.error('Erro:', message, error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="h-10 bg-t212-hover rounded-lg animate-pulse"></div>
        <div className="h-96 bg-t212-hover rounded-lg animate-pulse"></div>
      </div>
    )
  }

  if (!isin) {
    return (
      <div className="text-center py-12">
        <p className="text-t212-secondary mb-4">ISIN não encontrado</p>
        <Button variant="primary" onClick={() => navigate(-1)}>
          Voltar
        </Button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header com Voltar */}
      <div className="flex items-center gap-4 mb-6">
        <button
          onClick={() => navigate(-1)}
          className="p-2 hover:bg-t212-hover rounded-lg transition"
        >
          <ArrowLeft size={24} className="text-t212-primary" />
        </button>
        <div>
          <h1 className="text-3xl font-bold text-t212-primary">{isin.ticker}</h1>
          <p className="text-t212-secondary">{isin.name}</p>
        </div>
      </div>

      {/* Main Info Card */}
      <Card>
        <CardContent className="pt-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Preço */}
            <div>
              <div className="text-t212-secondary text-sm mb-1">Preço Atual</div>
              <div className="text-3xl font-bold text-t212-primary">
                €{isin.price.toFixed(2)}
              </div>
            </div>

            {/* P&L */}
            <div>
              <div className="text-t212-secondary text-sm mb-1">P&L Total</div>
              <div className={`text-3xl font-bold flex items-center gap-2 ${
                isin.pnl >= 0 ? 'text-t212-success' : 'text-t212-error'
              }`}>
                {isin.pnl >= 0 ? (
                  <TrendingUp size={28} />
                ) : (
                  <TrendingDown size={28} />
                )}
                €{Math.abs(isin.pnl).toFixed(2)}
              </div>
              <div className={`text-sm ${isin.pnl_percent >= 0 ? 'text-t212-success' : 'text-t212-error'}`}>
                {isin.pnl_percent >= 0 ? '+' : ''}{isin.pnl_percent.toFixed(2)}%
              </div>
            </div>

            {/* Quantidade */}
            <div>
              <div className="text-t212-secondary text-sm mb-1">Quantidade</div>
              <div className="text-3xl font-bold text-t212-primary">
                {isin.quantity.toFixed(2)}
              </div>
              <div className="text-t212-secondary text-sm">
                Preço médio: €{isin.average_price.toFixed(2)}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Informações</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex justify-between">
              <span className="text-t212-secondary">ISIN:</span>
              <span className="text-t212-primary font-mono">{isin.isin}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-t212-secondary">Moeda:</span>
              <span className="text-t212-primary">{isin.currency}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-t212-secondary">Automação:</span>
              <span className={isin.automation_enabled ? 'text-t212-success font-semibold' : 'text-t212-muted'}>
                {isin.automation_enabled ? '✓ Ativa' : '✗ Inativa'}
              </span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Estatísticas</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex justify-between">
              <span className="text-t212-secondary">Valor Total:</span>
              <span className="text-t212-primary font-semibold">
                €{(isin.price * isin.quantity).toFixed(2)}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-t212-secondary">Custo Total:</span>
              <span className="text-t212-primary font-semibold">
                €{(isin.average_price * isin.quantity).toFixed(2)}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-t212-secondary">Número de Trades:</span>
              <span className="text-t212-primary font-semibold">{trades.length}</span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Histórico de Trades */}
      <Card>
        <CardHeader>
          <CardTitle>Histórico de Trades</CardTitle>
        </CardHeader>
        <CardContent>
          {trades.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="table w-full">
                <thead>
                  <tr>
                    <th>Data</th>
                    <th>Tipo</th>
                    <th>Quantidade</th>
                    <th>Preço</th>
                    <th>Total</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {trades.map((trade) => (
                    <tr key={trade.id}>
                      <td className="text-t212-primary">{trade.date}</td>
                      <td>
                        <span className={`font-semibold ${
                          trade.type === 'BUY' ? 'text-t212-success' : 'text-t212-error'
                        }`}>
                          {trade.type === 'BUY' ? '📈 BUY' : '📉 SELL'}
                        </span>
                      </td>
                      <td className="text-t212-primary">{trade.quantity.toFixed(2)}</td>
                      <td className="text-t212-primary">€{trade.price.toFixed(2)}</td>
                      <td className="text-t212-primary font-semibold">
                        €{(trade.quantity * trade.price).toFixed(2)}
                      </td>
                      <td>
                        <span className="text-t212-success text-sm">✓ {trade.status}</span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="text-t212-secondary text-center py-8">
              Nenhum trade realizado neste ISIN
            </p>
          )}
        </CardContent>
      </Card>

      {/* Chart Placeholder */}
      <Card>
        <CardHeader>
          <CardTitle>Gráfico de Preço</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-64 bg-t212-hover rounded-lg flex items-center justify-center">
            <p className="text-t212-secondary">
              Gráfico de preço em breve (Recharts)
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
