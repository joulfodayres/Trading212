import { useEffect, useState } from 'react'
import { CheckCircle, XCircle } from 'lucide-react'
import { Card, CardHeader, CardTitle, CardContent } from './ui/Card'
import { apiClient } from '../api/client'

interface T212Status {
  environment: string
  connected: boolean
}

// Item #15: substitui o antigo formulário de credenciais (nunca funcionou —
// não guardava nada). As credenciais T212 são geridas só por variáveis de
// ambiente no Render; isto é apenas um painel de leitura do estado real.
export function T212StatusPanel() {
  const [status, setStatus] = useState<T212Status | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    apiClient
      .get('/config/status')
      .then((r) => setStatus(r.data))
      .catch(() => setStatus(null))
      .finally(() => setLoading(false))
  }, [])

  return (
    <Card>
      <CardHeader>
        <CardTitle>Trading 212</CardTitle>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="flex items-center gap-2 text-t212-secondary text-sm">
            <div className="animate-spin w-4 h-4 border-2 border-t212-primary border-t-transparent rounded-full" />
            A verificar ligação...
          </div>
        ) : status ? (
          <div className="flex items-center gap-3">
            <span
              className={`px-2 py-1 rounded text-xs font-bold ${
                status.environment === 'live' ? 'bg-red-600 text-white' : 'bg-blue-500 text-white'
              }`}
            >
              {status.environment === 'live' ? 'LIVE' : 'DEMO'}
            </span>
            {status.connected ? (
              <span className="flex items-center gap-1 text-t212-success text-sm">
                <CheckCircle size={16} /> Ligado
              </span>
            ) : (
              <span className="flex items-center gap-1 text-t212-error text-sm">
                <XCircle size={16} /> Sem ligação
              </span>
            )}
          </div>
        ) : (
          <p className="text-t212-error text-sm">Não foi possível verificar o estado.</p>
        )}
        <p className="text-xs text-t212-muted mt-3">
          As credenciais T212 são geridas nas variáveis de ambiente do Render (T212_API_KEY,
          T212_API_SECRET, T212_ENVIRONMENT) — não são configuráveis aqui.
        </p>
      </CardContent>
    </Card>
  )
}
