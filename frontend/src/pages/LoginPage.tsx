import { useState, useEffect } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { Mail, Lock, LogIn } from 'lucide-react'
import { useAuthStore } from '../stores/authStore'
import { Button } from '../components/ui/Button'
import { Input } from '../components/ui/Input'
import { useToast } from '../components/ui/Toast'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [emailError, setEmailError] = useState('')
  const [passwordError, setPasswordError] = useState('')
  const navigate = useNavigate()
  const { login, isLoading, error, clearError } = useAuthStore()
  const toast = useToast()

  useEffect(() => {
    // Clear error when user starts typing
    if (error) {
      clearError()
      setEmailError('')
      setPasswordError('')
    }
  }, [email, password])

  const validateForm = () => {
    let isValid = true
    setEmailError('')
    setPasswordError('')

    if (!email || !email.includes('@')) {
      setEmailError('Invalid email')
      isValid = false
    }

    if (!password || password.length < 6) {
      setPasswordError('Password must be at least 6 characters')
      isValid = false
    }

    return isValid
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!validateForm()) {
      return
    }

    try {
      console.log('[LoginPage] Attempting login with email:', email)
      await login(email, password)
      console.log('[LoginPage] Login successful, navigating to dashboard')
      toast.success('Login successful!')
      navigate('/dashboard')
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Login error'
      console.error('[LoginPage] Login error:', {
        message,
        error: err,
        errorString: String(err)
      })
      toast.error(message)
      // Keep error visible for 5 seconds
      setTimeout(() => {
        clearError()
      }, 5000)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-t212-bg-dark via-t212-bg-darker to-t212-bg-dark flex items-center justify-center px-4">
      {/* Background decoration */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-t212-primary opacity-5 rounded-full blur-3xl"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-t212-secondary opacity-5 rounded-full blur-3xl"></div>
      </div>

      {/* Login Card */}
      <div className="relative z-10 w-full max-w-md">
        <div className="card border-t212-border shadow-xl backdrop-blur-sm">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center h-16 w-16 rounded-2xl bg-gradient-to-br from-t212-primary to-t212-secondary mb-4 shadow-lg">
              <span className="text-2xl">📈</span>
            </div>
            <h1 className="text-3xl font-bold text-t212-primary">
              Trading 212 Bot
            </h1>
            <p className="text-t212-secondary text-sm mt-1">
              Intelligent Trading Automation
            </p>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-5">
            <Input
              label="Email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="your@email.com"
              error={emailError}
              required
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

          {/* Footer */}
          <div className="mt-8 pt-6 border-t border-t212-border">
            <p className="text-center text-t212-secondary text-sm mb-4">
              Don't have an account?{' '}
              <Link to="/register" className="text-t212-primary hover:text-t212-primary-light font-medium transition">
                Create account
              </Link>
            </p>

            <div className="p-3 rounded-lg bg-t212-primary bg-opacity-10 border border-t212-primary border-opacity-20">
              <p className="text-t212-primary text-xs font-medium mb-2">Demo Account:</p>
              <p className="text-t212-secondary text-xs">
                Email: <span className="text-t212-text-primary font-mono">test@trading212.com</span>
              </p>
              <p className="text-t212-secondary text-xs">
                Password: <span className="text-t212-text-primary font-mono">test123</span>
              </p>
            </div>
          </div>
        </div>

        {/* Footer Text */}
        <p className="text-center text-t212-muted text-xs mt-6">
          © 2026 Trading 212 Bot. All rights reserved.
        </p>
      </div>
    </div>
  )
}

