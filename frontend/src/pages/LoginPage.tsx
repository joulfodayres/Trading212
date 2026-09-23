import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Mail, Lock, LogIn, ShieldCheck } from 'lucide-react'
import { useAuthStore } from '../stores/authStore'
import { Button } from '../components/ui/Button'
import { Input } from '../components/ui/Input'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [mfaCode, setMfaCode] = useState('')
  const [trustDevice, setTrustDevice] = useState(false)
  const [emailError, setEmailError] = useState('')
  const [passwordError, setPasswordError] = useState('')

  const navigate = useNavigate()
  const {
    login, verifyMfa, isLoading, error, clearError,
    mfaRequired, mfaSetupRequired, clearMfaFlow, isAuthenticated
  } = useAuthStore()

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard')
    }
  }, [isAuthenticated])

  useEffect(() => {
    if (error) {
      clearError()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [email, password, mfaCode])

  const validateStep1 = () => {
    let isValid = true
    setEmailError('')
    setPasswordError('')

    if (!email || !email.includes('@')) {
      setEmailError('Email inválido')
      isValid = false
    }
    if (!password || password.length < 6) {
      setPasswordError('Password deve ter pelo menos 6 caracteres')
      isValid = false
    }
    return isValid
  }

  const handleSubmitStep1 = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!validateStep1()) return

    try {
      await login(email, password)
      // Se mfa_required ficou true, o formulário muda para o passo 2 automaticamente
    } catch (err) {
      // Erro já fica visível via `error` no store
    }
  }

  const handleSubmitStep2 = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!mfaCode || mfaCode.length < 6) return

    try {
      await verifyMfa(mfaCode, trustDevice)
    } catch (err) {
      setMfaCode('')
    }
  }

  const handleBackToStep1 = () => {
    clearMfaFlow()
    setMfaCode('')
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-t212-bg-dark via-t212-bg-darker to-t212-bg-dark flex items-center justify-center px-4">
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-t212-primary opacity-5 rounded-full blur-3xl"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-t212-secondary opacity-5 rounded-full blur-3xl"></div>
      </div>

      <div className="relative z-10 w-full max-w-md">
        <div className="card border-t212-border shadow-xl backdrop-blur-sm">
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center h-16 w-16 rounded-2xl bg-gradient-to-br from-t212-primary to-t212-secondary mb-4 shadow-lg">
              <span className="text-2xl">📈</span>
            </div>
            <h1 className="text-3xl font-bold text-t212-primary">Trading 212 Bot</h1>
            <p className="text-t212-secondary text-sm mt-1">Intelligent Trading Automation</p>
          </div>

          {!mfaRequired ? (
            <form onSubmit={handleSubmitStep1} className="space-y-5">
              <Input
                label="Email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="your@email.com"
                error={emailError}
                required
                autoFocus
              />
              <Input
                label="Password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                error={passwordError}
                required
              />

              {error && (
                <div className="p-3 rounded-lg bg-t212-error bg-opacity-20 border border-t212-error text-t212-error text-sm">
                  {error}
                </div>
              )}

              <Button
                type="submit"
                variant="primary"
                size="lg"
                isLoading={isLoading}
                className="w-full mt-6"
                icon={<LogIn size={18} />}
                disabled={isLoading}
              >
                Sign In
              </Button>
            </form>
          ) : (
            <form onSubmit={handleSubmitStep2} className="space-y-5">
              <div className="flex items-center gap-2 text-t212-secondary text-sm mb-2">
                <ShieldCheck size={18} className="text-t212-primary" />
                <span>Introduz o código da tua app de autenticação</span>
              </div>

              <Input
                label="Código de 6 dígitos"
                type="text"
                inputMode="numeric"
                value={mfaCode}
                onChange={(e) => setMfaCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
                placeholder="123456"
                required
                autoFocus
              />

              <label className="flex items-center gap-2 text-sm text-t212-secondary cursor-pointer">
                <input
                  type="checkbox"
                  checked={trustDevice}
                  onChange={(e) => setTrustDevice(e.target.checked)}
                  className="rounded border-t212-border"
                />
                Confiar neste dispositivo
              </label>

              {error && (
                <div className="p-3 rounded-lg bg-t212-error bg-opacity-20 border border-t212-error text-t212-error text-sm">
                  {error}
                </div>
              )}

              <Button
                type="submit"
                variant="primary"
                size="lg"
                isLoading={isLoading}
                className="w-full mt-2"
                icon={<Lock size={18} />}
                disabled={isLoading || mfaCode.length < 6}
              >
                Verificar
              </Button>

              <button
                type="button"
                onClick={handleBackToStep1}
                className="w-full text-center text-t212-secondary text-sm hover:text-t212-primary transition"
              >
                ← Voltar
              </button>
            </form>
          )}

          {mfaSetupRequired && !mfaRequired && (
            <div className="mt-6 p-3 rounded-lg bg-t212-primary bg-opacity-10 border border-t212-primary border-opacity-20 text-t212-primary text-xs">
              ⚠️ Configura o MFA em Config → Security antes de continuares a usar a app.
            </div>
          )}
        </div>

        <p className="text-center text-t212-muted text-xs mt-6">
          © 2026 Trading 212 Bot. All rights reserved.
        </p>
      </div>
    </div>
  )
}
