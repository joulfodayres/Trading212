import { useState, useEffect } from 'react'
import { Plus, ArrowLeft, Save, X, AlertCircle, CheckCircle, ChevronRight } from 'lucide-react'
import { Button } from '../components/ui/Button'
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card'
import { ToggleSwitch } from '../components/ui/ToggleSwitch'
import { apiClient } from '../api/client'

interface Strategy {
  id: string
  name: string
  description?: string
  initial_investment?: number
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

type ViewMode = 'list' | 'detail' | 'parameters'

export default function StrategiesPage() {
  const [strategies, setStrategies] = useState<Strategy[]>([])
  const [selectedStrategy, setSelectedStrategy] = useState<Strategy | null>(null)
  const [parameters, setParameters] = useState<StrategyParameter[]>([])
  const [loading, setLoading] = useState(false)
  const [viewMode, setViewMode] = useState<ViewMode>('list')

  // Modals
  const [showCreateStrategy, setShowCreateStrategy] = useState(false)
  const [showCreateParameter, setShowCreateParameter] = useState(false)

  // Form states
  const [strategyForm, setStrategyForm] = useState({
    name: '',
    description: '',
    initial_investment: 0,
  })

  const [strategyEditForm, setStrategyEditForm] = useState({
    name: '',
    description: '',
    initial_investment: 0,
    enabled: false,
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

  // Load parameters when strategy selected and viewing detail
  useEffect(() => {
    if (selectedStrategy && viewMode === 'parameters') {
      loadParameters(selectedStrategy.id)
    }
  }, [selectedStrategy, viewMode])

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
      loadStrategies()
    } catch (error) {
      console.error('Error creating strategy:', error)
    }
  }

  const handleStrategyClick = (strategy: Strategy) => {
    setSelectedStrategy(strategy)
    setStrategyEditForm({
      name: strategy.name || '',
      description: strategy.description || '',
      initial_investment: strategy.initial_investment || 0,
      enabled: strategy.enabled,
    })
    setViewMode('detail')
  }

  const handleSaveStrategyEdit = async () => {
    if (!selectedStrategy) return

    try {
      const response = await apiClient.put(`/v1/strategies/${selectedStrategy.id}`, {
        name: strategyEditForm.name,
        description: strategyEditForm.description,
        initial_investment: strategyEditForm.initial_investment,
        enabled: strategyEditForm.enabled,
      })

      setStrategies(strategies.map(s => s.id === selectedStrategy.id ? response.data : s))
      setSelectedStrategy(response.data)
      loadStrategies()
    } catch (error) {
      console.error('Error updating strategy:', error)
      alert('Error updating strategy')
    }
  }

  const handleToggleStrategy = async (enabled: boolean) => {
    setStrategyEditForm({ ...strategyEditForm, enabled })
  }

  const handleEditParameters = () => {
    loadParameters(selectedStrategy!.id)
    setViewMode('parameters')
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

  const formatDate = (dateStr?: string) => {
    if (!dateStr) return 'N/A'
    return new Date(dateStr).toLocaleString('en-US')
  }

  // ===== RENDER LIST VIEW =====
  if (viewMode === 'list') {
    return (
      <div className="space-y-6">
        <Card>
          <CardHeader className="flex items-center justify-between">
            <CardTitle>Strategies</CardTitle>
            <Button
              variant="primary"
              size="sm"
              icon={<Plus size={16} />}
              onClick={() => setShowCreateStrategy(true)}
            >
              New Strategy
            </Button>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="animate-pulse space-y-4">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="h-16 bg-t212-hover rounded" />
                ))}
              </div>
            ) : strategies.length > 0 ? (
              <div className="space-y-2">
                {strategies.map((strategy) => (
                  <button
                    key={strategy.id}
                    onClick={() => handleStrategyClick(strategy)}
                    className="w-full p-4 rounded-lg border border-t212-border hover:border-t212-primary hover:bg-t212-hover transition flex items-center justify-between"
                  >
                    <div className="flex-1 text-left">
                      <div className="flex items-center gap-2 mb-1">
                        <h3 className="font-semibold text-t212-primary">
                          {strategy.name && strategy.name.trim() ? strategy.name : `Strategy ${strategy.id.substring(0, 8)}`}
                        </h3>
                      </div>
                      {strategy.description && (
                        <p className="text-sm text-t212-secondary mb-1">{strategy.description}</p>
                      )}
                      <div className="flex items-center gap-2">
                        <span className={`text-xs font-semibold ${strategy.enabled ? 'text-t212-success' : 'text-t212-muted'}`}>
                          {strategy.enabled ? '🟢 Active' : '🔴 Inactive'}
                        </span>
                        {!strategy.is_valid && (
                          <span className="text-xs text-t212-warning flex items-center gap-1">
                            <AlertCircle size={12} /> Missing parameters
                          </span>
                        )}
                      </div>
                    </div>
                    <ChevronRight size={20} className="text-t212-secondary" />
                  </button>
                ))}
              </div>
            ) : (
              <p className="text-t212-secondary text-center py-8">No strategies created</p>
            )}
          </CardContent>
        </Card>

        {/* Create Strategy Modal */}
        {showCreateStrategy && (
          <>
            <div className="fixed inset-0 bg-black bg-opacity-60 z-40" onClick={() => setShowCreateStrategy(false)} />
            <div className="fixed inset-0 flex items-center justify-center z-50 p-4">
              <div className="bg-t212-bg-primary rounded-2xl shadow-2xl border border-t212-border w-full max-w-md">
                <div className="px-6 py-5 border-b border-t212-border">
                  <h3 className="text-lg font-bold text-t212-primary">New Strategy</h3>
                </div>
                <div className="px-6 py-5 space-y-4">
                  <input
                    type="text"
                    placeholder="Name"
                    value={strategyForm.name}
                    onChange={(e) => setStrategyForm({ ...strategyForm, name: e.target.value })}
                    className="w-full px-4 py-2 bg-t212-bg-secondary border border-t212-border rounded-lg text-t212-primary focus:outline-none focus:ring-2 focus:ring-t212-warning"
                  />
                  <textarea
                    placeholder="Description"
                    value={strategyForm.description}
                    onChange={(e) => setStrategyForm({ ...strategyForm, description: e.target.value })}
                    className="w-full px-4 py-2 bg-t212-bg-secondary border border-t212-border rounded-lg text-t212-primary focus:outline-none focus:ring-2 focus:ring-t212-warning"
                    rows={3}
                  />
                  <input
                    type="number"
                    placeholder="Initial Investment (EUR)"
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
                    Cancel
                  </Button>
                  <Button
                    variant="primary"
                    size="md"
                    onClick={handleCreateStrategy}
                    disabled={!strategyForm.name.trim()}
                    className="flex-1"
                  >
                    Create
                  </Button>
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    )
  }

  // ===== RENDER DETAIL VIEW =====
  if (viewMode === 'detail' && selectedStrategy) {
    return (
      <div className="space-y-6">
        <Button
          variant="secondary"
          size="sm"
          icon={<ArrowLeft size={16} />}
          onClick={() => setViewMode('list')}
        >
          Back
        </Button>

        <Card>
          <CardHeader>
            <CardTitle>Strategy Details</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Name */}
            <div>
              <label className="block text-sm font-semibold text-t212-primary mb-2">Name</label>
              <input
                type="text"
                value={strategyEditForm.name}
                onChange={(e) => setStrategyEditForm({ ...strategyEditForm, name: e.target.value })}
                className="w-full px-4 py-2 bg-t212-bg-secondary border border-t212-border rounded-lg text-t212-primary focus:outline-none focus:ring-2 focus:ring-t212-warning"
              />
            </div>

            {/* Description */}
            <div>
              <label className="block text-sm font-semibold text-t212-primary mb-2">Description</label>
              <textarea
                value={strategyEditForm.description}
                onChange={(e) => setStrategyEditForm({ ...strategyEditForm, description: e.target.value })}
                className="w-full px-4 py-2 bg-t212-bg-secondary border border-t212-border rounded-lg text-t212-primary focus:outline-none focus:ring-2 focus:ring-t212-warning"
                rows={3}
              />
            </div>

            {/* Initial Investment */}
            <div>
              <label className="block text-sm font-semibold text-t212-primary mb-2">Initial Investment (EUR)</label>
              <input
                type="number"
                value={strategyEditForm.initial_investment}
                onChange={(e) => setStrategyEditForm({ ...strategyEditForm, initial_investment: parseFloat(e.target.value) })}
                className="w-full px-4 py-2 bg-t212-bg-secondary border border-t212-border rounded-lg text-t212-primary focus:outline-none focus:ring-2 focus:ring-t212-warning"
              />
            </div>

            {/* Status Toggle */}
            <div>
              <label className="block text-sm font-semibold text-t212-primary mb-2">Status</label>
              <div className="flex items-center gap-3 p-3 rounded-lg bg-t212-bg-secondary border border-t212-border">
                <span className={`text-sm font-semibold ${strategyEditForm.enabled ? 'text-t212-success' : 'text-t212-muted'}`}>
                  {strategyEditForm.enabled ? '🟢 Active' : '🔴 Inactive'}
                </span>
                <ToggleSwitch
                  checked={strategyEditForm.enabled}
                  onChange={handleToggleStrategy}
                  disabled={!selectedStrategy.is_valid}
                />
                {!selectedStrategy.is_valid && (
                  <span className="text-xs text-t212-warning">Requires parameters -1, 0, 1</span>
                )}
              </div>
            </div>

            {/* Timestamps (read-only) */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-t212-muted mb-1">Created</label>
                <p className="text-sm text-t212-secondary">{formatDate(selectedStrategy.created_at)}</p>
              </div>
              <div>
                <label className="block text-xs font-semibold text-t212-muted mb-1">Last edited</label>
                <p className="text-sm text-t212-secondary">{formatDate(selectedStrategy.updated_at)}</p>
              </div>
            </div>

            {/* Validity Indicator */}
            <div className="flex items-center gap-2 p-3 rounded-lg bg-t212-bg-secondary border border-t212-border">
              {selectedStrategy.is_valid ? (
                <>
                  <CheckCircle size={16} className="text-t212-success" />
                  <span className="text-sm text-t212-success font-semibold">Valid strategy</span>
                </>
              ) : (
                <>
                  <AlertCircle size={16} className="text-t212-warning" />
                  <span className="text-sm text-t212-warning font-semibold">Missing parameters (-1, 0, 1)</span>
                </>
              )}
            </div>

            {/* Action Buttons */}
            <div className="flex gap-3 pt-4">
              <Button
                variant="secondary"
                size="md"
                icon={<X size={16} />}
                onClick={() => setViewMode('list')}
                className="flex-1"
              >
                Cancel
              </Button>
              <Button
                variant="primary"
                size="md"
                icon={<Save size={16} />}
                onClick={handleSaveStrategyEdit}
                className="flex-1"
              >
                Save Changes
              </Button>
            </div>

            {/* Edit Parameters Button */}
            <Button
              variant="secondary"
              size="md"
              onClick={handleEditParameters}
              className="w-full"
            >
              Edit Parameters
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  // ===== RENDER PARAMETERS VIEW =====
  if (viewMode === 'parameters' && selectedStrategy) {
    return (
      <div className="space-y-6">
        <Button
          variant="secondary"
          size="sm"
          icon={<ArrowLeft size={16} />}
          onClick={() => setViewMode('detail')}
        >
          Back
        </Button>

        <Card>
          <CardHeader className="flex items-center justify-between">
            <CardTitle>Parameters - {selectedStrategy.name || `Strategy ${selectedStrategy.id.substring(0, 8)}`}</CardTitle>
            <Button
              variant="primary"
              size="sm"
              icon={<Plus size={16} />}
              onClick={() => setShowCreateParameter(true)}
            >
              New Parameter
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
                      <th>Actions</th>
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
                            <X size={16} />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="text-t212-secondary text-center py-8">No parameters</p>
            )}
          </CardContent>
        </Card>

        {/* Create Parameter Modal */}
        {showCreateParameter && (
          <>
            <div className="fixed inset-0 bg-black bg-opacity-60 z-40" onClick={() => setShowCreateParameter(false)} />
            <div className="fixed inset-0 flex items-center justify-center z-50 p-4">
              <div className="bg-t212-bg-primary rounded-2xl shadow-2xl border border-t212-border w-full max-w-2xl max-h-[80vh] overflow-y-auto">
                <div className="px-6 py-5 border-b border-t212-border sticky top-0 bg-t212-bg-primary">
                  <h3 className="text-lg font-bold text-t212-primary">New Parameter</h3>
                </div>
                <div className="px-6 py-5 space-y-4">
                  <input
                    type="text"
                    placeholder="Position (ex: -1, 0, 1)"
                    value={parameterForm.pos}
                    onChange={(e) => setParameterForm({ ...parameterForm, pos: e.target.value })}
                    className="w-full px-4 py-2 bg-t212-bg-secondary border border-t212-border rounded-lg text-t212-primary focus:outline-none focus:ring-2 focus:ring-t212-warning"
                  />

                  {/* Parameters grid */}
                  <div className="grid grid-cols-2 gap-3">
                    {['param1', 'param2', 'param3', 'param4', 'param5', 'param6', 'param7', 'param8', 'param9', 'param10'].map((param) => (
                      <input
                        key={param}
                        type="number"
                        placeholder={param}
                        step="0.01"
                        value={parameterForm[param as keyof typeof parameterForm] ?? ''}
                        onChange={(e) => setParameterForm({
                          ...parameterForm,
                          [param]: e.target.value ? parseFloat(e.target.value) : undefined
                        })}
                        className="px-4 py-2 bg-t212-bg-secondary border border-t212-border rounded-lg text-t212-primary focus:outline-none focus:ring-2 focus:ring-t212-warning"
                      />
                    ))}
                  </div>
                </div>
                <div className="px-6 py-4 border-t border-t212-border bg-t212-bg-secondary flex gap-3 sticky bottom-0">
                  <Button
                    variant="secondary"
                    size="md"
                    onClick={() => setShowCreateParameter(false)}
                    className="flex-1"
                  >
                    Cancel
                  </Button>
                  <Button
                    variant="primary"
                    size="md"
                    onClick={handleCreateParameter}
                    disabled={!parameterForm.pos}
                    className="flex-1"
                  >
                    Create
                  </Button>
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    )
  }

  return null
}
