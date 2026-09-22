import { useState, useEffect } from 'react'
import { Plus, ArrowLeft, Save, X, AlertCircle, CheckCircle, Edit2, Trash2 } from 'lucide-react'
import { Button } from '../components/ui/Button'
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card'
import { ToggleSwitch } from '../components/ui/ToggleSwitch'
import { apiClient } from '../api/client'
import { useToast } from '../components/ui/Toast'

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
  const toast = useToast()

  // Edit mode state for parameters
  const [editingParamId, setEditingParamId] = useState<string | null>(null)
  const [editValues, setEditValues] = useState<{ [key: string]: number }>({})
  const [savingParamId, setSavingParamId] = useState<string | null>(null)

  // Modals
  const [showCreateStrategy, setShowCreateStrategy] = useState(false)
  const [showCreateParameter, setShowCreateParameter] = useState(false)

  // Error states
  const [createStrategyError, setCreateStrategyError] = useState<string>('')

  // Form states
  const [strategyForm, setStrategyForm] = useState({
    name: '',
    description: '',
    initial_investment: null as number | null,
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
      console.log('[StrategiesPage.loadStrategies] Full response:', response.data)
      response.data.forEach((s: Strategy) => {
        console.log(`[StrategiesPage] Strategy: ${s.name} | Description: "${s.description}" | Enabled: ${s.enabled} | Valid: ${s.is_valid}`)
      })
      setStrategies(response.data)
    } catch (error) {
      console.error('Error loading strategies:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadParameters = async (strategyId: string) => {
    try {
      const response = await apiClient.get(`/v1/strategies/${strategyId}`)
      const strategyData = response.data
      console.log(`[loadParameters] Full response for strategy ${strategyId}:`, strategyData)
      console.log(`[loadParameters] Parameters array:`, strategyData.parameters)

      // Set parameters
      setParameters(strategyData.parameters || [])

      // [NEW] Check if all required positions exist
      if (strategyData.parameters && Array.isArray(strategyData.parameters)) {
        const positions = strategyData.parameters.map((p: StrategyParameter) => p.pos)
        const hasNegativeOne = positions.includes("-1")
        const hasZero = positions.includes("0")
        const hasOne = positions.includes("1")

        const allRequiredPositionsExist = hasNegativeOne && hasZero && hasOne
        console.log(`[loadParameters] Positions check: -1=${hasNegativeOne}, 0=${hasZero}, 1=${hasOne}, valid=${allRequiredPositionsExist}`)

        // [NEW] Update strategy validation state based on actual parameters
        if (selectedStrategy) {
          setSelectedStrategy({
            ...selectedStrategy,
            is_valid: allRequiredPositionsExist
          })
        }
      } else {
        // No parameters at all - mark as invalid
        if (selectedStrategy) {
          setSelectedStrategy({
            ...selectedStrategy,
            is_valid: false
          })
        }
      }
    } catch (error) {
      console.error('[loadParameters] Error loading parameters:', error)
    }
  }

  const handleCreateStrategy = async () => {
    // Client-side validation only for format
    if (!strategyForm.name.trim()) {
      console.error('[handleCreateStrategy] Error: Name is required')
      return
    }

    if (!strategyForm.initial_investment || strategyForm.initial_investment <= 0) {
      console.error('[handleCreateStrategy] Error: Initial investment must be greater than 0')
      return
    }

    if (strategyForm.initial_investment < 0) {
      console.error('[handleCreateStrategy] Error: Initial investment cannot be negative')
      return
    }

    setLoading(true)
    try {
      console.log('[handleCreateStrategy] Creating strategy:', strategyForm)
      const response = await apiClient.post('/v1/strategies', {
        name: strategyForm.name.trim(),
        description: strategyForm.description.trim() || null,
        initial_investment: strategyForm.initial_investment,
      })
      console.log('[handleCreateStrategy] Success, response:', response.data)
      setStrategies([...strategies, response.data])
      setStrategyForm({ name: '', description: '', initial_investment: null })
      setCreateStrategyError('')
      setShowCreateStrategy(false)
      await loadStrategies()
    } catch (error: any) {
      const message = error?.response?.data?.detail || 'Failed to create strategy'
      console.error('[handleCreateStrategy] Backend Error:', message)

      // [NEW] Set error state for display
      setCreateStrategyError(message)
    } finally {
      setLoading(false)
    }
  }

  const handleStrategyClick = (strategy: Strategy) => {
    console.log('[StrategiesPage] Clicked strategy:', strategy)
    setSelectedStrategy(strategy)
    const formData = {
      name: strategy.name || '',
      description: strategy.description || '',
      initial_investment: strategy.initial_investment || 0,
      enabled: strategy.enabled || false,
    }
    console.log('[StrategiesPage] Setting form data:', formData)
    setStrategyEditForm(formData)
    setViewMode('detail')
  }

  const handleSaveStrategyEdit = async () => {
    if (!selectedStrategy) return

    // VALIDATION 1: Check for duplicate name
    const isDuplicate = strategies.some(
      s => s.id !== selectedStrategy.id &&
           s.name.toLowerCase().trim() === strategyEditForm.name.toLowerCase().trim()
    )
    if (isDuplicate) {
      console.error('[handleSaveStrategyEdit] Duplicate name error: A strategy with this name already exists')
      return
    }

    // VALIDATION 2: Check investment value
    if (!strategyEditForm.initial_investment || strategyEditForm.initial_investment <= 0) {
      console.error('[handleSaveStrategyEdit] Investment value error: Initial investment must be greater than 0')
      return
    }

    // VALIDATION 3: Check parameters if enabling
    if (strategyEditForm.enabled && !selectedStrategy.is_valid) {
      console.error('[handleSaveStrategyEdit] Parameters error: Cannot enable strategy. Must have parameters for positions -1, 0, and 1')
      return
    }

    try {
      const response = await apiClient.put(`/v1/strategies/${selectedStrategy.id}`, {
        name: strategyEditForm.name,
        description: strategyEditForm.description,
        initial_investment: strategyEditForm.initial_investment,
        enabled: strategyEditForm.enabled,
      })

      setStrategies(strategies.map(s => s.id === selectedStrategy.id ? response.data : s))
      setSelectedStrategy(response.data)
      console.log('[handleSaveStrategyEdit] Strategy updated successfully')
      setViewMode('list')
      loadStrategies()
    } catch (error: any) {
      const errorDetail = error?.response?.data?.detail || error?.message || 'Unknown error'
      console.error('[handleSaveStrategyEdit] API error:', errorDetail)
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
    if (!selectedStrategy || !parameterForm.pos) {
      console.error('[StrategiesPage] Position is required')
      return
    }

    // Validate Position is integer
    const posValue = parseInt(parameterForm.pos, 10)
    if (isNaN(posValue) || posValue.toString() !== parameterForm.pos.trim()) {
      console.error('[StrategiesPage] Position must be an integer (e.g., -1, 0, 1)')
      return
    }

    try {
      const response = await apiClient.post(
        `/v1/strategies/${selectedStrategy.id}/parameters`,
        { ...parameterForm, pos: posValue }  // Send as integer
      )
      console.log('[StrategiesPage] Parameter created successfully:', response.data)
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
    } catch (error: any) {
      const message = error?.response?.data?.detail || 'Failed to create parameter'
      console.error('[StrategiesPage] Create parameter error:', message)
    }
  }

  const handleDeleteParameter = async (paramId: string) => {
    if (!selectedStrategy) return

    try {
      await apiClient.delete(`/v1/strategies/${selectedStrategy.id}/parameters/${paramId}`)
      setParameters(parameters.filter(p => p.id !== paramId))
      toast.success('Parameter deleted', 3000)
    } catch (error) {
      const errorMsg = (error as any)?.response?.data?.detail || 'Failed to delete parameter'
      toast.error(errorMsg, 5000)
      console.error('Error deleting parameter:', error)
    }
  }

  const startEditParameter = (param: StrategyParameter) => {
    setEditingParamId(param.id)
    setEditValues({
      param1: param.param1 ?? 0,
      param2: param.param2 ?? 0,
      param3: param.param3 ?? 0,
      param4: param.param4 ?? 0,
      param5: param.param5 ?? 0,
      param6: param.param6 ?? 0,
      param7: param.param7 ?? 0,
      param8: param.param8 ?? 0,
      param9: param.param9 ?? 0,
      param10: param.param10 ?? 0,
    })
  }

  const cancelEditParameter = () => {
    setEditingParamId(null)
    setEditValues({})
  }

  const saveEditParameter = async (paramId: string) => {
    // Validation: ensure all values are numeric
    for (const [key, val] of Object.entries(editValues)) {
      const numVal = Number(val)
      if (isNaN(numVal)) {
        toast.error(`${key} must be a number`, 5000)
        return
      }
    }

    if (!selectedStrategy) return

    setSavingParamId(paramId)
    try {
      await apiClient.put(
        `/v1/strategies/${selectedStrategy.id}/parameters/${paramId}`,
        editValues
      )
      setParameters(parameters.map(p =>
        p.id === paramId ? { ...p, ...editValues } : p
      ))
      toast.success('Parameter updated successfully', 3000)
      setEditingParamId(null)
      setEditValues({})
    } catch (error) {
      const errorMsg = (error as any)?.response?.data?.detail || 'Failed to update parameter'
      toast.error(errorMsg, 5000)
    } finally {
      setSavingParamId(null)
    }
  }

  const [deleteStrategyId, setDeleteStrategyId] = useState<string | null>(null)
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)

  const handleDeleteStrategy = async (strategyId: string) => {
    setDeleteStrategyId(strategyId)
    setShowDeleteConfirm(true)
  }

  const handleConfirmDelete = async () => {
    if (!deleteStrategyId) return

    try {
      console.log('[handleConfirmDelete] Deleting strategy:', deleteStrategyId)
      await apiClient.delete(`/v1/strategies/${deleteStrategyId}`)
      setStrategies(strategies.filter(s => s.id !== deleteStrategyId))
      setShowDeleteConfirm(false)
      setDeleteStrategyId(null)
      console.log('[handleConfirmDelete] Strategy deleted successfully')
    } catch (error) {
      console.error('[handleConfirmDelete] Error deleting strategy:', error)
      setShowDeleteConfirm(false)
      setDeleteStrategyId(null)
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
              onClick={() => {
                setShowCreateStrategy(true)
                setCreateStrategyError('')
              }}
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
                {strategies.map((strategy) => {
                  const name = strategy.name && strategy.name.trim() ? strategy.name.trim() : null
                  const description = strategy.description && strategy.description.trim() && strategy.description !== 'None' ? strategy.description.trim() : null
                  const displayName = name || `Unnamed Strategy (${strategy.id.substring(0, 8)})`

                  console.log('[StrategiesPage] Rendering strategy:', {
                    id: strategy.id,
                    name,
                    description,
                    displayName,
                    enabled: strategy.enabled,
                    is_valid: strategy.is_valid
                  })

                  return (
                    <div
                      key={strategy.id}
                      className="w-full p-4 rounded-lg border border-t212-border hover:border-t212-primary hover:bg-t212-hover transition flex items-center justify-between"
                    >
                      <div className="flex-1 text-left">
                        <div className="flex items-center gap-2 mb-1">
                          <h3 className={`font-semibold ${name ? 'text-t212-primary' : 'text-t212-secondary'}`}>
                            {displayName}
                          </h3>
                        </div>
                        {description && (
                          <p className="text-sm text-t212-secondary mb-1">{description}</p>
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
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => handleStrategyClick(strategy)}
                          className="p-2 hover:bg-t212-hover rounded-lg transition text-t212-primary hover:text-t212-warning"
                          title="Edit strategy"
                        >
                          <Edit2 size={18} />
                        </button>
                        <button
                          onClick={() => handleDeleteStrategy(strategy.id)}
                          disabled={strategy.enabled}
                          className={`p-2 rounded-lg transition ${
                            strategy.enabled
                              ? 'text-t212-muted cursor-not-allowed'
                              : 'text-t212-error hover:bg-t212-hover hover:text-t212-warning'
                          }`}
                          title={strategy.enabled ? 'Cannot delete active strategy' : 'Delete strategy'}
                        >
                          <Trash2 size={18} />
                        </button>
                      </div>
                    </div>
                  )
                })}
              </div>
            ) : (
              <p className="text-t212-secondary text-center py-8">No strategies created</p>
            )}
          </CardContent>
        </Card>

        {/* Delete Confirmation Modal */}
        {showDeleteConfirm && deleteStrategyId && (
          <>
            <div className="fixed inset-0 bg-black bg-opacity-60 z-40" onClick={() => setShowDeleteConfirm(false)} />
            <div className="fixed inset-0 flex items-center justify-center z-50 p-4">
              <div className="bg-t212-bg-primary rounded-2xl shadow-2xl border border-t212-border w-full max-w-md">
                <div className="px-6 py-5 border-b border-t212-border">
                  <h3 className="text-lg font-bold text-t212-primary">Delete Strategy</h3>
                </div>
                <div className="px-6 py-5 space-y-4">
                  <p className="text-t212-primary font-semibold">
                    Delete strategy "{strategies.find(s => s.id === deleteStrategyId)?.name || 'Unnamed'}"?
                  </p>
                  <p className="text-sm text-t212-secondary">
                    This will permanently delete the strategy and all associated parameters. This action cannot be undone.
                  </p>
                </div>
                <div className="px-6 py-4 border-t border-t212-border bg-t212-bg-secondary flex gap-3">
                  <Button
                    variant="secondary"
                    size="md"
                    onClick={() => setShowDeleteConfirm(false)}
                    className="flex-1"
                  >
                    Cancel
                  </Button>
                  <Button
                    variant="danger"
                    size="md"
                    onClick={handleConfirmDelete}
                    className="flex-1"
                  >
                    Delete
                  </Button>
                </div>
              </div>
            </div>
          </>
        )}

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
                  {createStrategyError && (
                    <div className="p-3 rounded-lg bg-red-900 bg-opacity-20 border border-red-500 text-red-400 text-sm flex items-start gap-2">
                      <AlertCircle size={16} className="mt-0.5 flex-shrink-0" />
                      <span>{createStrategyError}</span>
                    </div>
                  )}
                  <input
                    type="text"
                    placeholder="Name"
                    value={strategyForm.name}
                    onChange={(e) => setStrategyForm({ ...strategyForm, name: e.target.value })}
                    className="w-full px-4 py-2 bg-t212-bg-secondary border border-t212-border rounded-lg placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-t212-warning"
                    style={{ color: '#000000' }}
                  />
                  <textarea
                    placeholder="Description"
                    value={strategyForm.description}
                    onChange={(e) => setStrategyForm({ ...strategyForm, description: e.target.value })}
                    className="w-full px-4 py-2 bg-t212-bg-secondary border border-t212-border rounded-lg placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-t212-warning"
                    style={{ color: '#000000' }}
                    rows={3}
                  />
                  <input
                    type="number"
                    placeholder="Initial Investment (EUR)"
                    value={strategyForm.initial_investment ?? ''}
                    onChange={(e) => setStrategyForm({ ...strategyForm, initial_investment: e.target.value ? parseFloat(e.target.value) : null })}
                    className="w-full px-4 py-2 bg-t212-bg-secondary border border-t212-border rounded-lg placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-t212-warning"
                    style={{ color: '#000000' }}
                    min="0"
                  />
                </div>
                <div className="px-6 py-4 border-t border-t212-border bg-t212-bg-secondary flex gap-3">
                  <Button
                    variant="secondary"
                    size="md"
                    onClick={() => {
                      setShowCreateStrategy(false)
                      setCreateStrategyError('')
                    }}
                    className="flex-1"
                  >
                    Cancel
                  </Button>
                  <Button
                    variant="primary"
                    size="md"
                    onClick={handleCreateStrategy}
                    disabled={!strategyForm.name.trim() || !strategyForm.initial_investment || strategyForm.initial_investment <= 0}
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
                className="w-full px-4 py-2 bg-t212-bg-secondary border border-t212-border rounded-lg placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-t212-warning"
                style={{ color: '#000000' }}
              />
            </div>

            {/* Description */}
            <div>
              <label className="block text-sm font-semibold text-t212-primary mb-2">Description</label>
              <textarea
                value={strategyEditForm.description}
                onChange={(e) => setStrategyEditForm({ ...strategyEditForm, description: e.target.value })}
                className="w-full px-4 py-2 bg-t212-bg-secondary border border-t212-border rounded-lg placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-t212-warning"
                style={{ color: '#000000' }}
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
                className="w-full px-4 py-2 bg-t212-bg-secondary border border-t212-border rounded-lg placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-t212-warning"
                style={{ color: '#000000' }}
                min="0"
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
                        {editingParamId === param.id ? (
                          // EDIT MODE
                          <>
                            <td className="font-semibold text-gray-500">{param.pos}</td>
                            {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((i) => (
                              <td key={`edit-${i}`} className="px-4 py-3">
                                <input
                                  type="number"
                                  value={editValues[`param${i}`] ?? ''}
                                  onChange={(e) =>
                                    setEditValues({
                                      ...editValues,
                                      [`param${i}`]: e.target.value === '' ? 0 : Number(e.target.value),
                                    })
                                  }
                                  className="w-full bg-gray-700 border border-gray-600 rounded px-2 py-1 text-white text-center text-sm"
                                  step="0.01"
                                  disabled={savingParamId === param.id}
                                />
                              </td>
                            ))}
                            <td className="px-4 py-3 text-center space-x-2">
                              <button
                                onClick={() => saveEditParameter(param.id)}
                                disabled={savingParamId === param.id}
                                className="text-green-500 hover:text-green-400 transition disabled:opacity-50"
                                title="Save"
                              >
                                {savingParamId === param.id ? '⏳' : '✓'}
                              </button>
                              <button
                                onClick={cancelEditParameter}
                                disabled={savingParamId === param.id}
                                className="text-yellow-500 hover:text-yellow-400 transition disabled:opacity-50"
                                title="Cancel"
                              >
                                ✕
                              </button>
                            </td>
                          </>
                        ) : (
                          // NORMAL MODE
                          <>
                            <td className="px-4 py-3 font-semibold text-white cursor-pointer hover:text-blue-400"
                                onClick={() => startEditParameter(param)}>
                              {param.pos}
                            </td>
                            {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((i) => (
                              <td
                                key={`cell-${i}`}
                                className="px-4 py-3 text-center text-gray-300 cursor-pointer hover:text-blue-400"
                                onClick={() => startEditParameter(param)}
                              >
                                {param[`param${i}`] ?? '-'}
                              </td>
                            ))}
                            <td className="px-4 py-3 text-center">
                              <button
                                onClick={() => handleDeleteParameter(param.id)}
                                className="text-red-500 hover:text-red-400 transition"
                                title="Delete"
                              >
                                <X size={16} />
                              </button>
                            </td>
                          </>
                        )}
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
                    type="number"
                    step="1"
                    placeholder="Position (ex: -1, 0, 1)"
                    value={parameterForm.pos}
                    onChange={(e) => {
                      const val = e.target.value
                      // Only allow empty, minus sign at start, or integers
                      if (val === '' || /^-?\d+$/.test(val)) {
                        setParameterForm({ ...parameterForm, pos: val })
                      }
                    }}
                    style={{ color: '#000000' }}
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
                        style={{ color: '#000000' }}
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
