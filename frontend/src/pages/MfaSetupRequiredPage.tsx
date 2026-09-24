import { ShieldAlert } from 'lucide-react'
import { SecuritySection } from '../components/SecuritySection'
import { useAuthStore } from '../stores/authStore'

// Item #12 hard gate: o login por password sozinho não dá acesso ao resto da
// app enquanto o MFA não estiver ativo — só esta página (setup) fica
// acessível. App.tsx troca /dashboard por esta página sempre que
// `user.totp_enabled === false`.
export default function MfaSetupRequiredPage() {
  const { logout } = useAuthStore()

  return (
    <div className="min-h-screen bg-gradient-to-br from-t212-bg-dark via-t212-bg-darker to-t212-bg-dark flex items-center justify-center px-4">
      <div className="relative z-10 w-full max-w-md">
        <div className="card border-t212-border shadow-xl backdrop-blur-sm p-6">
          <div className="text-center mb-2">
            <div className="inline-flex items-center justify-center h-14 w-14 rounded-2xl bg-t212-primary bg-opacity-10 mb-3">
              <ShieldAlert size={28} className="text-t212-primary" />
            </div>
            <h1 className="text-xl font-bold text-t212-primary">Configuração de Segurança Obrigatória</h1>
            <p className="text-t212-secondary text-sm mt-2">
              Para proteger o acesso à tua conta T212, tens de ativar a autenticação em dois fatores (MFA)
              antes de poderes usar o resto da aplicação.
            </p>
          </div>

          <SecuritySection />

          <button
            onClick={() => logout()}
            className="w-full text-center text-t212-muted text-xs mt-6 hover:text-t212-secondary transition"
          >
            Sair sem configurar
          </button>
        </div>
      </div>
    </div>
  )
}
