import { useState, useEffect } from 'react'
import { Plus, Edit2, Trash2, AlertCircle, CheckCircle } from 'lucide-react'
import { Button } from '../components/ui/Button'
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card'
import { apiClient } from '../api/client'

interface Strategy {
  id: string
  name: string
  description?: string
  initial_investment: number
  enabled: boolean
  is_valid: boolean
  created_at?: string
  updated_at?: string
}

interface StrategyParameter {
  id: string
  strategy_id: string
  pos: string
  param1: number
  param2: number
  param3?: number
  param4?: number
  param5?: number
  param6?: number
  param7?: number
  param8?: number
  param9?: number
  param10?: number
}

export default function StrategiesPage() {
  const [strategies, setStrategies] = useState<Strategy[]>([])
  const [selectedStrategy, setSelectedStrategy] = useState<Strategy | null>(null)
  const [parameters, setParameters] = useState<StrategyParameter[]>([])
  const [loading, setLoading] = useState(false)
  const [showCreateStrategy, setShowCreateStrategy] = useState(false)
  const [showCreateParameter, setShowCreateParameter] = useState(false)

  // Form states
  const [strategyForm, setStrategyForm] = useState({
    name: '',
    description: '',
    initial_investment: 0,
  })

  const [parameterForm, setParameterForm] = useState({
    pos: '',
    param1: 0,
    param2: 0,
    param3: undefined,
    param4: undefined,
    param5: undefined,
    param6: undefined,
    param7: undefined,
    param8: undefined,
    param9: undefined,
    param10: undefined,
  })

  // Load strategies on mount
  useEffect(() => {
    loadStrategies()
  }, [])

  // Load parameters when strategy selected
  useEffect(() => {
    if (selectedStrategy) {
      loadParameters(selectedStrategy.id)
    }
  }, [selectedStrategy])

  const loadStrategies = async () => {
    setLoading(true)
    try {
      const response = await apiClient.get('/v1/strategies')
      setStrategies(response.data)
      console.log('Strategies loaded:', response.data)
    } catch (error) {
      console.error('Error loading strategies:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadParameters = async (strategyId: string) => {
    try {
      const response = await apiClient.get(`/v1/strategies/${strategyId}`)
      setParameters(response.data.parameters || [])
    } catch (error) {
      console.error('Error loading parameters:', error)
    }
  }

  const handleCreateStrategy = async () => {
    if (!strategyForm.name.trim()) return

    try {
      const response = await apiClient.post('/v1/strategies', strategyForm)
      setStrategies([...strategies, response.data])
      setStrategyForm({ name: '', description: '', initial_investment: 0 })
      setShowCreateStrategy(false)
    } catch (error) {
      console.error('Error creating strategy:', error)
    }
  }

  const handleToggleStrategy = async (strategy: Strategy) => {
    try {
      const response = await apiClient.put(`/v1/strategies/${strategy.id}`, {
        enabled: !strategy.enabled
      })

      setStrategies(strategies.map(s => s.id === strategy.id ? response.data : s))
      if (selectedStrategy?.id === strategy.id) {
        setSelectedStrategy(response.data)
      }
    } catch (error) {
      console.error('Error toggling strategy:', error)
      alert('Não podes ativar. Strategy precisa dos parâmetros -1, 0, 1')
    }
  }

  const handleCreateParameter = async () => {
    if (!selectedStrategy || !parameterForm.pos) return

    try {
      const response = await apiClient.post(
        `/v1/strategies/${selectedStrategy.id}/parameters`,
        parameterForm
      )
      setParameters([...parameters, response.data])
      setParameterForm({
        pos: '',
        param1: 0,
        param2: 0,
        param3: undefined,
        param4: undefined,
        param5: undefined,
        param6: undefined,
        param7: undefined,
        param8: undefined,
        param9: undefined,
        param10: undefined,
      })
      setShowCreateParameter(false)
    } catch (error) {
      console.error('Error creating parameter:', error)
    }
  }

  const handleDeleteParameter = async (paramId: string) => {
    if (!selectedStrategy) return

    try {
      await apiClient.delete(`/v1/strategies/${selectedStrategy.id}/parameters/${paramId}`)
      setParameters(parameters.filter(p => p.id !== paramId))
    } catch (error) {
      console.error('Error deleting parameter:', error)
    }
  }

  return (
    <div className="space-y-6">
      {/* Strategies Section */}
      <Card>
        <CardHeader className="flex items-center justify-between">
          <CardTitle>Estratégias</CardTitle>
          <Button
            variant="primary"
            size="sm"
            icon={<Plus size={16} />}
            onClick={() => setShowCreateStrategy(true)}
          >
            Nova Estratégia
          </Button>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="animate-pulse space-y-4">
              {[1, 2, 3].map((i) => (
                <div key={i} className="h-10 bg-t212-hover rounded" />
              ))}
            </div>
          ) : strategies.length > 0 ? (
            <div className="space-y-3">
              {strategies.map((strategy) => (
                <div
                  key={strategy.id}
                  onClick={() => setSelectedStrategy(strategy)}
                  className={`p-4 rounded-lg border-2 cursor-pointer transition ${
                    selectedStrategy?.id === strategy.id
                      ? 'border-t212-primary bg-t212-bg-secondary'
                      : 'border-t212-border hover:border-t212-primary'
                  }`}
                >
                  <div className="flex items-center justify-between gap-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <h3 className="font-semibold text-t212-primary">{strategy.name}</h3>
                        {strategy.is_valid ? (
                          <CheckCircle size={16} className="text-t212-success" title="Válida" />
                        ) : (
                          <AlertCircle size={16} className="text-t212-warning" title="Faltam parâmetros" />
                        )}
                      </div>
                      {strategy.description && (
                        <p className="text-sm text-t212-secondary mb-1">{strategy.description}</p>
                      )}
                      <p className="text-xs text-t212-muted">
                        Investimento: €{strategy.initial_investment.toFixed(2)}
                      </p>
                    </div>

                    <div className="flex items-center gap-2">
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          handleToggleStrategy(strategy)
                        }}
                        disabled={!strategy.is_valid}
                        className={`px-3 py-1 rounded text-sm font-medium transition ${
                          strategy.enabled
                            ? 'bg-t212-success bg-opacity-20 text-t212-success'
                            : strategy.is_valid
                            ? 'bg-t212-hover text-t212-secondary hover:text-t212-primary'
                            : 'bg-t212-hover text-t212-muted cursor-not-allowed opacity-50'
                        }`}
                      >
                        {strategy.enabled ? '✓ Ativa' : 'Inativa'}
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-t212-secondary text-center py-8">Nenhuma estratégia criada</p>
          )}
        </CardContent>
      </Card>

      {/* Parameters Section */}
      {selectedStrategy && (
        <Card>
          <CardHeader className="flex items-center justify-between">
            <CardTitle>Parâmetros - {selectedStrategy.name}</CardTitle>
            <Button
              variant="primary"
              size="sm"
              icon={<Plus size={16} />}
              onClick={() => setShowCreateParameter(true)}
            >
              Novo Parâmetro
            </Button>
          </CardHeader>
          <CardContent>
            {parameters.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="table w-full">
                  <thead>
                    <tr>
                      <th>Pos</th>
                      <th>Param1</th>
                      <th>Param2</th>
                      <th>Param3</th>
                      <th>Param4</th>
                      <th>Param5</th>
                      <th>Param6</th>
                      <th>Param7</th>
                      <th>Param8</th>
                      <th>Param9</th>
                      <th>Param10</th>
                      <th>Ações</th>
                    </tr>
                  </thead>
                  <tbody>
                    {parameters.map((param) => (
                      <tr key={param.id}>
                        <td className="font-semibold">{param.pos}</td>
                        <td>{param.param1}</td>
                        <td>{param.param2}</td>
                        <td>{param.param3 ?? '-'}</td>
                        <td>{param.param4 ?? '-'}</td>
                        <td>{param.param5 ?? '-'}</td>
                        <td>{param.param6 ?? '-'}</td>
                        <td>{param.param7 ?? '-'}</td>
                        <td>{param.param8 ?? '-'}</td>
                        <td>{param.param9 ?? '-'}</td>
                        <td>{param.param10 ?? '-'}</td>
                        <td>
                          <button
                            onClick={() => handleDeleteParameter(param.id)}
                            className="text-t212-error hover:text-t212-warning transition"
                          >
                            <Trash2 size={16} />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="text-t212-secondary text-center py-8">Nenhum parâmetro</p>
            )}
          </CardContent>
        </Card>
      )}

      {/* Create Strategy Modal */}
      {showCreateStrategy && (
        <>
          <div className="fixed inset-0 bg-black bg-opacity-60 z-40" onClick={() => setShowCreateStrategy(false)} />
          <div className="fixed inset-0 flex items-center justify-center z-50 p-4">
            <div className="bg-t212-bg-primary rounded-2xl shadow-2xl border border-t212-border w-full max-w-md">
              <div className="px-6 py-5 border-b border-t212-border">
                <h3 className="text-lg font-bold text-t212-primary">Nova Estratégia</h3>
              </div>
              <div className="px-6 py-5 space-y-4">
                <input
                  type="text"
                  placeholder="Nome"
                  value={strategyForm.name}
                  onChange={(e) => setStrategyForm({ ...strategyForm, name: e.target.value })}
                  className="w-full px-4 py-2 bg-t212-bg-secondary border border-t212-border rounded-lg text-t212-primary focus:outline-none focus:ring-2 focus:ring-t212-warning"
                />
                <textarea
                  placeholder="Descrição"
                  value={strategyForm.description}
                  onChange={(e) => setStrategyForm({ ...strategyForm, description: e.target.value })}
                  className="w-full px-4 py-2 bg-t212-bg-secondary border border-t212-border rounded-lg text-t212-primary focus:outline-none focus:ring-2 focus:ring-t212-warning"
                  rows={3}
                />
                <input
                  type="number"
                  placeholder="Investimento Inicial (EUR)"
                  value={strategyForm.initial_investment}
                  onChange={(e) => setStrategyForm({ ...strategyForm, initial_investment: parseFloat(e.target.value) })}
                  className="w-full px-4 py-2 bg-t212-bg-secondary border border-t212-border rounded-lg text-t212-primary focus:outline-none focus:ring-2 focus:ring-t212-warning"
                />
              </div>
              <div className="px-6 py-4 border-t border-t212-border bg-t212-bg-secondary flex gap-3">
                <Button
                  variant="secondary"
                  size="md"
                  onClick={() => setShowCreateStrategy(false)}
                  className="flex-1"
                >
                  Cancelar
                </Button>
                <Button
                  variant="primary"
                  size="md"
                  onClick={handleCreateStrategy}
                  disabled={!strategyForm.name.trim()}
                  className="flex-1"
                >
                  Criar
                </Button>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
