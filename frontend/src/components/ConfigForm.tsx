import { useState } from 'react'
import { Eye, EyeOff, CheckCircle, AlertCircle } from 'lucide-react'
import { Button } from './ui/Button'
import { Input } from './ui/Input'
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from './ui/Card'
import { useToast } from './ui/Toast'
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
  const toast = useToast()

  const handleSave = async () => {
    if (!apiKey || !apiSecret) {
      toast.error('Por favor, preencha API Key e API Secret')
      return
    }

    setLoading(true)
    try {
      const response = await apiClient.put('/config', {
        t212_api_key: apiKey,
        t212_api_secret: apiSecret,
        t212_environment: environment
      })

      toast.success('Configuração guardada com sucesso!')
      // Limpar campos (não mostrar credenciais)
      setApiKey('')
      setApiSecret('')
    } catch (error: any) {
      const message = error?.response?.data?.detail || 'Erro ao guardar configuração'
      toast.error(message)
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
      toast.success('Conexão bem-sucedida!')
    } catch (error: any) {
      const message = error?.response?.data?.detail || 'Erro ao testar conexão'
      setTestResult({ success: false, error: message })
      toast.error(message)
    } finally {
      setTesting(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Credenciais */}
      <Card>
        <CardHeader>
          <CardTitle>Credenciais Trading 212</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="form-label">Environment</label>
            <select
              value={environment}
              onChange={(e) => setEnvironment(e.target.value)}
              className="input"
            >
              <option value="demo">🧪 Demo (Teste)</option>
              <option value="live">🔴 Live (Real Money - CUIDADO!)</option>
            </select>
            {environment === 'live' && (
              <div className="mt-2 p-3 rounded-lg bg-t212-error bg-opacity-20 border border-t212-error text-t212-error text-sm">
                ⚠️ ATENÇÃO: Estás a usar dinheiro REAL! Apenas para utilizadores experientes.
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
                placeholder="Cole aqui a sua API Key"
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
                placeholder="Cole aqui o seu API Secret"
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
            💡 Você pode encontrar suas credenciais em: Trading 212 → Settings → API
          </div>
        </CardContent>
        <CardFooter>
          <Button
            variant="secondary"
            onClick={handleTest}
            isLoading={testing}
            disabled={!apiKey || !apiSecret}
          >
            Testar Conexão
          </Button>
          <Button
            variant="primary"
            onClick={handleSave}
            isLoading={loading}
            disabled={!apiKey || !apiSecret}
          >
            Guardar Configuração
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
                  {testResult.success ? 'Conexão Bem-Sucedida!' : 'Erro na Conexão'}
                </h3>
                {testResult.success && testResult.data?.account && (
                  <div className="mt-2 space-y-1 text-sm text-t212-secondary">
                    <p>📊 Saldo: €{testResult.data.account.balance?.toFixed(2)}</p>
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
