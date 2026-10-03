import { useEffect, useState } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'
import MfaSetupRequiredPage from './pages/MfaSetupRequiredPage'
import ManualOrdersPage from './pages/ManualOrdersPage'
import { useAuthStore } from './stores/authStore'
import { ToastProvider } from './components/ui/Toast'
import { apiClient } from './api/client'

// Nota (Item #12): sem registo público — a rota /register foi removida do
// routing. A conta única é criada uma vez via POST /api/auth/register
// (bootstrap-only, bloqueado assim que exista 1 utilizador).

function App() {
  const { isAuthenticated, user, checkAuth } = useAuthStore()
  const [checkingAuth, setCheckingAuth] = useState(true)
  const [environment, setEnvironment] = useState<'live' | 'demo' | null>(null)

  useEffect(() => {
    // O token vive num cookie httpOnly (não em localStorage) — confirmamos
    // a sessão junto do backend ao arrancar a app.
    checkAuth().finally(() => setCheckingAuth(false))

    // Item #15: faixa permanente de aviso com o ambiente ligado a este backend
    // (LIVE = dinheiro real, DEMO = dinheiro fictício) — visível mesmo antes
    // do login, para nunca confundir os separadores DEMO/PROD abertos ao
    // mesmo tempo.
    apiClient
      .get('/config/status')
      .then((r) => setEnvironment(r.data?.environment === 'live' ? 'live' : 'demo'))
      .catch(() => setEnvironment(null))
  }, [])

  if (checkingAuth) {
    return null
  }

  // Item #12 hard gate: password sozinha entra na sessão (senão não há forma
  // de chegar ao ecrã de setup do MFA), mas o resto da app fica bloqueado —
  // só a página de configuração do MFA é acessível — até `totp_enabled`
  // ficar true.
  const mfaSetupPending = isAuthenticated && !!user && !user.totp_enabled

  return (
    <ToastProvider>
      {environment === 'live' && (
        <div className="fixed top-0 left-0 right-0 z-[100] bg-red-600 text-white text-center text-sm font-bold py-1.5 tracking-wide">
          🔴 PRODUÇÃO — DINHEIRO REAL
        </div>
      )}
      {environment === 'demo' && (
        <div className="fixed top-0 left-0 right-0 z-[100] bg-green-600 text-white text-center text-sm font-bold py-1.5 tracking-wide">
          🟢 DEMO — DINHEIRO FICTÍCIO
        </div>
      )}
      <div className={environment ? 'pt-7 h-screen box-border' : 'h-screen'}>
      <BrowserRouter>
        <Routes>
          <Route
            path="/login"
            element={!isAuthenticated ? <LoginPage /> : <Navigate to="/dashboard" />}
          />
          <Route
            path="/dashboard"
            element={
              !isAuthenticated ? (
                <Navigate to="/login" />
              ) : mfaSetupPending ? (
                <MfaSetupRequiredPage />
              ) : (
                <DashboardPage />
              )
            }
          />
          <Route
            path="/manual-orders/:isin"
            element={
              !isAuthenticated ? (
                <Navigate to="/login" />
              ) : mfaSetupPending ? (
                <MfaSetupRequiredPage />
              ) : (
                <ManualOrdersPage />
              )
            }
          />
          <Route path="/" element={<Navigate to={isAuthenticated ? "/dashboard" : "/login"} />} />
        </Routes>
      </BrowserRouter>
      </div>
    </ToastProvider>
  )
}

export default App
