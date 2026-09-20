import { useState } from 'react'
import { Eye, EyeOff, CheckCircle, AlertCircle } from 'lucide-react'
import { Button } from './ui/Button'
import { Input } from './ui/Input'
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from './ui/Card'
import { apiClient } from '../api/client'

export const ConfigForm = () => {
  const [apiKey, setApiKey] = useState('')
  const [apiSecret, setApiSecret] = useState('')
  const [environment, setEnvironment] = useState('demo')
  const [showKey, setShowKey] = useState(false)
  const [showSecret, setShowSecret] = useState(false)
  const [loading, setLoading] = useState(false)
  const [testing, setTesting] = useState(false)
  const [testResult, setTestResult] = useState<any>(null)

  const handleSave = async () => {
    if (!apiKey || !apiSecret) {
      console.warn('[ConfigForm] Missing API Key or API Secret')
      return
    }

    setLoading(true)
    try {
      const response = await apiClient.put('/config', {
        t212_api_key: apiKey,
        t212_api_secret: apiSecret,
        t212_environment: environment
      })

      console.log('[ConfigForm] Configuration saved successfully')
      // Clear fields (don't show credentials)
      setApiKey('')
      setApiSecret('')
    } catch (error: any) {
      const message = error?.response?.data?.detail || 'Error saving configuration'
      console.error('[ConfigForm] Error saving configuration:', message)
    } finally {
      setLoading(false)
    }
  }

  const handleTest = async () => {
    setTesting(true)
    setTestResult(null)
    try {
      const response = await apiClient.post('/config/test')
      setTestResult({ success: true, data: response.data })
      console.log('[ConfigForm] Connection test successful')
    } catch (error: any) {
      const message = error?.response?.data?.detail || 'Error testing connection'
      setTestResult({ success: false, error: message })
      console.error('[ConfigForm] Connection test failed:', message)
    } finally {
      setTesting(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Credentials */}
      <Card>
        <CardHeader>
          <CardTitle>Trading 212 Credentials</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="form-label">Environment</label>
            <select
              value={environment}
              onChange={(e) => setEnvironment(e.target.value)}
              className="input"
            >
              <option value="demo">🧪 Demo (Test)</option>
              <option value="live">🔴 Live (Real Money - CAUTION!)</option>
            </select>
            {environment === 'live' && (
              <div className="mt-2 p-3 rounded-lg bg-t212-error bg-opacity-20 border border-t212-error text-t212-error text-sm">
                ⚠️ WARNING: You are using REAL money! Only for experienced users.
              </div>
            )}
          </div>

          <div className="relative">
            <label className="form-label">API Key</label>
            <div className="flex gap-2">
              <input
                type={showKey ? 'text' : 'password'}
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                placeholder="Paste your API Key here"
                className="input flex-1"
              />
              <button
                onClick={() => setShowKey(!showKey)}
                className="btn btn-ghost btn-sm"
              >
                {showKey ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>
          </div>

          <div className="relative">
            <label className="form-label">API Secret</label>
            <div className="flex gap-2">
              <input
                type={showSecret ? 'text' : 'password'}
                value={apiSecret}
                onChange={(e) => setApiSecret(e.target.value)}
                placeholder="Paste your API Secret here"
                className="input flex-1"
              />
              <button
                onClick={() => setShowSecret(!showSecret)}
                className="btn btn-ghost btn-sm"
              >
                {showSecret ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>
          </div>

          <div className="p-3 rounded-lg bg-t212-info bg-opacity-10 border border-t212-info text-t212-info text-sm">
            💡 You can find your credentials at: Trading 212 → Settings → API
          </div>
        </CardContent>
        <CardFooter>
          <Button
            variant="secondary"
            onClick={handleTest}
            isLoading={testing}
            disabled={!apiKey || !apiSecret}
          >
            Test Connection
          </Button>
          <Button
            variant="primary"
            onClick={handleSave}
            isLoading={loading}
            disabled={!apiKey || !apiSecret}
          >
            Save Configuration
          </Button>
        </CardFooter>
      </Card>

      {/* Test Result */}
      {testResult && (
        <Card className={testResult.success ? 'border-t212-success' : 'border-t212-error'}>
          <CardContent className="pt-6">
            <div className="flex items-start gap-3">
              {testResult.success ? (
                <CheckCircle className="text-t212-success mt-1" size={24} />
              ) : (
                <AlertCircle className="text-t212-error mt-1" size={24} />
              )}
              <div className="flex-1">
                <h3 className={testResult.success ? 'text-t212-success font-semibold' : 'text-t212-error font-semibold'}>
                  {testResult.success ? 'Connection Successful!' : 'Connection Error'}
                </h3>
                {testResult.success && testResult.data?.account && (
                  <div className="mt-2 space-y-1 text-sm text-t212-secondary">
                    <p>📊 Balance: €{testResult.data.account.balance?.toFixed(2)}</p>
                    <p>📈 P&L: €{testResult.data.account.pnl?.toFixed(2)}</p>
                  </div>
                )}
                {testResult.error && (
                  <p className="mt-1 text-sm">{testResult.error}</p>
                )}
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
