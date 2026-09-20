import { useState, useEffect } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { Mail, Lock, UserPlus } from 'lucide-react'
import { useAuthStore } from '../stores/authStore'
import { Button } from '../components/ui/Button'
import { Input } from '../components/ui/Input'
import { useToast } from '../components/ui/Toast'

export default function RegisterPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [passwordConfirm, setPasswordConfirm] = useState('')
  const [emailError, setEmailError] = useState('')
  const [passwordError, setPasswordError] = useState('')
  const [passwordConfirmError, setPasswordConfirmError] = useState('')
  const navigate = useNavigate()
  const { register, isLoading, error, clearError } = useAuthStore()
  const toast = useToast()

  useEffect(() => {
    // Clear error when user starts typing
    if (error) {
      clearError()
      setEmailError('')
      setPasswordError('')
      setPasswordConfirmError('')
    }
  }, [email, password, passwordConfirm])

  const validateForm = () => {
    let isValid = true
    setEmailError('')
    setPasswordError('')
    setPasswordConfirmError('')

    if (!email || !email.includes('@')) {
      setEmailError('Invalid email')
      isValid = false
    }

    if (!password || password.length < 6) {
      setPasswordError('Password must be at least 6 characters')
      isValid = false
    }

    if (!passwordConfirm || passwordConfirm.length < 6) {
      setPasswordConfirmError('Password confirmation is invalid')
      isValid = false
    }

    if (password !== passwordConfirm) {
      setPasswordConfirmError('Passwords do not match')
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
      await register(email, password, passwordConfirm)
      toast.success('Account created successfully! Redirecting...')
      navigate('/dashboard')
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error creating account'
      toast.error(message)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-t212-bg-dark via-t212-bg-darker to-t212-bg-dark flex items-center justify-center px-4">
      {/* Background decoration */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-t212-primary opacity-5 rounded-full blur-3xl"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-t212-secondary opacity-5 rounded-full blur-3xl"></div>
      </div>

      {/* Register Card */}
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
              Create New Account
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

            <Input
              label="Confirm Password"
              type="password"
              value={passwordConfirm}
              onChange={(e) => setPasswordConfirm(e.target.value)}
              placeholder="••••••••"
              error={passwordConfirmError}
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
              icon={<UserPlus size={18} />}
              disabled={isLoading}
            >
              Create Account
            </Button>
          </form>

          {/* Footer */}
          <div className="mt-8 pt-6 border-t border-t212-border">
            <p className="text-center text-t212-secondary text-sm mb-4">
              Already have an account?{' '}
              <Link to="/login" className="text-t212-primary hover:text-t212-primary-light font-medium transition">
                Sign In
              </Link>
            </p>

            <div className="p-3 rounded-lg bg-t212-info bg-opacity-10 border border-t212-info border-opacity-20">
              <p className="text-t212-info text-xs font-medium mb-2">ℹ️ Requirements:</p>
              <ul className="text-t212-secondary text-xs space-y-1">
                <li>✓ Valid email</li>
                <li>✓ Password minimum 6 characters</li>
                <li>✓ Passwords must match</li>
              </ul>
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
