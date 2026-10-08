import { useState, useEffect } from 'react'
import { ShieldCheck, ShieldOff, AlertTriangle } from 'lucide-react'
import { Button } from './ui/Button'
import { Input } from './ui/Input'
import { apiClient } from '../api/client'
import { useAuthStore } from '../stores/authStore'

export function SecuritySection() {
  const { user, checkAuth, logoutAll } = useAuthStore()

  const [settingUp, setSettingUp] = useState(false)
  const [qrCode, setQrCode] = useState<string | null>(null)
  const [secret, setSecret] = useState<string | null>(null)
  const [confirmCode, setConfirmCode] = useState('')
  const [disablePassword, setDisablePassword] = useState('')
  const [showDisable, setShowDisable] = useState(false)
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null)

  // Item #27: trusted device duration (dias), configurável por ambiente
  const [trustedDeviceDays, setTrustedDeviceDays] = useState<number>(7)
  const [trustedDeviceDaysInput, setTrustedDeviceDaysInput] = useState<string>('7')
  const [loadingTrustedDays, setLoadingTrustedDays] = useState(true)
  const [savingTrustedDays, setSavingTrustedDays] = useState(false)

  // Item #33: change password
  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [newPasswordConfirm, setNewPasswordConfirm] = useState('')
  const [changingPassword, setChangingPassword] = useState(false)
  const [passwordMessage, setPasswordMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null)

  useEffect(() => {
    checkAuth()
    fetchTrustedDeviceDays()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const fetchTrustedDeviceDays = async () => {
    try {
      setLoadingTrustedDays(true)
      const response = await apiClient.get('/v1/automation/config/trusted-device')
      const days = response.data.trusted_device_days ?? 7
      setTrustedDeviceDays(days)
      setTrustedDeviceDaysInput(String(days))
    } catch (error) {
      console.error('[SecuritySection] Error fetching trusted_device_days:', error)
    } finally {
      setLoadingTrustedDays(false)
    }
  }

  const handleSaveTrustedDeviceDays = async () => {
    const days = parseInt(trustedDeviceDaysInput, 10)
    if (isNaN(days) || days < 0 || days > 90) {
      console.warn('[SecuritySection] Invalid trusted_device_days:', days)
      return
    }
    setSavingTrustedDays(true)
    try {
      const response = await apiClient.put('/v1/automation/config/trusted-device', { trusted_device_days: days })
      setTrustedDeviceDays(response.data.trusted_device_days)
      console.log('[SecuritySection] trusted_device_days saved:', response.data.trusted_device_days)
    } catch (error) {
      console.error('[SecuritySection] Error saving trusted_device_days:', error)
      setTrustedDeviceDaysInput(String(trustedDeviceDays))
    } finally {
      setSavingTrustedDays(false)
    }
  }

  const handleChangePassword = async () => {
    setPasswordMessage(null)
    if (newPassword.length < 8) {
      setPasswordMessage({ type: 'error', text: 'Nova password deve ter mínimo 8 caracteres' })
      return
    }
    if (newPassword !== newPasswordConfirm) {
      setPasswordMessage({ type: 'error', text: 'Passwords não coincidem' })
      return
    }
    setChangingPassword(true)
    try {
      await apiClient.post('/auth/change-password', {
        current_password: currentPassword,
        new_password: newPassword,
        new_password_confirm: newPasswordConfirm,
      })
      setPasswordMessage({ type: 'success', text: 'Password alterada com sucesso' })
      setCurrentPassword('')
      setNewPassword('')
      setNewPasswordConfirm('')
    } catch (error: any) {
      setPasswordMessage({ type: 'error', text: error?.response?.data?.detail || 'Erro ao mudar password' })
    } finally {
      setChangingPassword(false)
    }
  }

  const startMfaSetup = async () => {
    setLoading(true)
    setMessage(null)
    try {
      const response = await apiClient.post('/auth/mfa/setup')
      setQrCode(response.data.qr_code_base64)
      setSecret(response.data.secret)
      setSettingUp(true)
    } catch (error: any) {
      setMessage({ type: 'error', text: error?.response?.data?.detail || 'Erro ao iniciar setup do MFA' })
    } finally {
      setLoading(false)
    }
  }

  const confirmMfaSetup = async () => {
    if (confirmCode.length < 6) return
    setLoading(true)
    setMessage(null)
    try {
      await apiClient.post('/auth/mfa/confirm', { code: confirmCode })
      setMessage({ type: 'success', text: 'MFA ativado com sucesso' })
      setSettingUp(false)
      setQrCode(null)
      setSecret(null)
      setConfirmCode('')
      await checkAuth()
    } catch (error: any) {
      setMessage({ type: 'error', text: error?.response?.data?.detail || 'Código inválido' })
    } finally {
      setLoading(false)
    }
  }

  const disableMfa = async () => {
    if (!disablePassword) return
    setLoading(true)
    setMessage(null)
    try {
      await apiClient.post('/auth/mfa/disable', { password: disablePassword })
      setMessage({ type: 'success', text: 'MFA desativado' })
      setShowDisable(false)
      setDisablePassword('')
      await checkAuth()
    } catch (error: any) {
      setMessage({ type: 'error', text: error?.response?.data?.detail || 'Password incorreta' })
    } finally {
      setLoading(false)
    }
  }

  const handleKillswitch = async () => {
    if (!window.confirm('Terminar todas as sessões ativas em todos os dispositivos? Vais ter de fazer login novamente.')) {
      return
    }
    setLoading(true)
    try {
      await logoutAll()
      window.location.href = '/login'
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="border-t border-t212-border pt-6 mt-6 space-y-6">
      <h3 className="text-lg font-semibold text-t212-primary mb-4">🔐 Security</h3>

      {message && (
        <div className={`p-3 rounded-lg text-sm border ${
          message.type === 'success'
            ? 'bg-green-500 bg-opacity-10 border-green-500 text-green-500'
            : 'bg-t212-error bg-opacity-20 border-t212-error text-t212-error'
        }`}>
          {message.text}
        </div>
      )}

      {/* MFA Status */}
      <div className="p-4 rounded-lg bg-t212-primary bg-opacity-5 border border-t212-primary border-opacity-20">
        <div className="flex items-center gap-2 mb-2">
          {user?.totp_enabled ? (
            <ShieldCheck size={18} className="text-green-500" />
          ) : (
            <AlertTriangle size={18} className="text-yellow-500" />
          )}
          <span className="text-sm font-medium text-t212-text-primary">
            Autenticação em dois fatores (MFA): {user?.totp_enabled ? 'Ativa' : 'Inativa'}
          </span>
        </div>
        {!user?.totp_enabled && (
          <p className="text-xs text-t212-secondary">
            Recomendado: ativa o MFA para proteger o acesso à tua conta T212.
          </p>
        )}
      </div>

      {/* Setup MFA flow */}
      {!user?.totp_enabled && !settingUp && (
        <Button variant="primary" onClick={startMfaSetup} isLoading={loading} className="w-full">
          Configurar MFA
        </Button>
      )}

      {settingUp && qrCode && (
        <div className="space-y-4 p-4 rounded-lg border border-t212-border">
          <p className="text-sm text-t212-secondary">
            1. Digitaliza o código com Google Authenticator, Authy ou equivalente
          </p>
          <img
            src={`data:image/png;base64,${qrCode}`}
            alt="MFA QR Code"
            className="mx-auto rounded-lg border border-t212-border"
            width={200}
            height={200}
          />
          {secret && (
            <p className="text-xs text-center text-t212-muted font-mono break-all">
              Ou introduz manualmente: {secret}
            </p>
          )}
          <p className="text-sm text-t212-secondary">2. Introduz o código gerado para confirmar</p>
          <Input
            label="Código de 6 dígitos"
            type="text"
            inputMode="numeric"
            value={confirmCode}
            onChange={(e) => setConfirmCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
            placeholder="123456"
          />
          <Button
            variant="primary"
            onClick={confirmMfaSetup}
            isLoading={loading}
            disabled={confirmCode.length < 6}
            className="w-full"
          >
            Confirmar e Ativar
          </Button>
        </div>
      )}

      {/* Disable MFA flow */}
      {user?.totp_enabled && !showDisable && (
        <button
          onClick={() => setShowDisable(true)}
          className="text-sm text-t212-secondary hover:text-t212-error transition"
        >
          Desativar MFA
        </button>
      )}

      {showDisable && (
        <div className="space-y-3 p-4 rounded-lg border border-t212-error border-opacity-30">
          <p className="text-sm text-t212-secondary">Confirma a tua password para desativar o MFA:</p>
          <Input
            label="Password"
            type="password"
            value={disablePassword}
            onChange={(e) => setDisablePassword(e.target.value)}
          />
          <div className="flex gap-2">
            <Button variant="secondary" onClick={() => setShowDisable(false)} className="flex-1">
              Cancelar
            </Button>
            <Button
              variant="primary"
              onClick={disableMfa}
              isLoading={loading}
              disabled={!disablePassword}
              className="flex-1"
              icon={<ShieldOff size={16} />}
            >
              Desativar
            </Button>
          </div>
        </div>
      )}

      {/* Trusted Device Duration (Item #27) */}
      <div className="border-t border-t212-border pt-6">
        <h4 className="text-sm font-semibold text-t212-primary mb-2">📱 Dispositivo confiável</h4>
        <p className="text-xs text-t212-secondary mb-3">
          Ao fazer login, podes marcar "Confiar neste dispositivo" para saltar o código MFA nas
          próximas vezes, durante o número de dias abaixo. A password continua sempre a ser pedida.
        </p>
        {loadingTrustedDays ? (
          <div className="flex items-center text-t212-secondary text-sm">
            <div className="animate-spin w-4 h-4 border-2 border-t212-primary border-t-transparent rounded-full mr-2" />
            A carregar...
          </div>
        ) : (
          <div className="flex items-end gap-3">
            <div className="flex-1 max-w-[180px]">
              <Input
                label="Dias a lembrar (0-90)"
                type="number"
                min="0"
                max="90"
                value={trustedDeviceDaysInput}
                onChange={(e) => setTrustedDeviceDaysInput(e.target.value)}
                hint="0 = pedir sempre MFA"
              />
            </div>
            <Button variant="primary" onClick={handleSaveTrustedDeviceDays} isLoading={savingTrustedDays}>
              Guardar
            </Button>
          </div>
        )}
      </div>

      {/* Change Password (Item #33) */}
      <div className="border-t border-t212-border pt-6 space-y-3">
        <h4 className="text-sm font-semibold text-t212-primary mb-2">🔑 Mudar Password</h4>

        {passwordMessage && (
          <div className={`p-3 rounded-lg text-sm border ${
            passwordMessage.type === 'success'
              ? 'bg-green-500 bg-opacity-10 border-green-500 text-green-500'
              : 'bg-t212-error bg-opacity-20 border-t212-error text-t212-error'
          }`}>
            {passwordMessage.text}
          </div>
        )}

        <Input
          label="Password atual"
          type="password"
          value={currentPassword}
          onChange={(e) => setCurrentPassword(e.target.value)}
        />
        <Input
          label="Nova password"
          type="password"
          value={newPassword}
          onChange={(e) => setNewPassword(e.target.value)}
          hint="Mínimo 8 caracteres"
        />
        <Input
          label="Confirmar nova password"
          type="password"
          value={newPasswordConfirm}
          onChange={(e) => setNewPasswordConfirm(e.target.value)}
        />
        <Button
          variant="primary"
          onClick={handleChangePassword}
          isLoading={changingPassword}
          disabled={!currentPassword || !newPassword || !newPasswordConfirm}
          className="w-full"
        >
          Mudar Password
        </Button>
      </div>

      {/* Killswitch */}
      <div className="border-t border-t212-border pt-4">
        <p className="text-xs text-t212-secondary mb-2">
          Suspeitas de acesso não autorizado? Termina todas as sessões ativas imediatamente.
        </p>
        <Button
          variant="danger"
          onClick={handleKillswitch}
          isLoading={loading}
          className="w-full"
        >
          🔴 Terminar Todas as Sessões
        </Button>
      </div>
    </div>
  )
}
