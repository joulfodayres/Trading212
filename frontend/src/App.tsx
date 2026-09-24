import { useEffect, useState } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'
import MfaSetupRequiredPage from './pages/MfaSetupRequiredPage'
import { useAuthStore } from './stores/authStore'
import { ToastProvider } from './components/ui/Toast'

// Nota (Item #12): sem registo público — a rota /register foi removida do
// routing. A conta única é criada uma vez via POST /api/auth/register
// (bootstrap-only, bloqueado assim que exista 1 utilizador).

function App() {
  const { isAuthenticated, user, checkAuth } = useAuthStore()
  const [checkingAuth, setCheckingAuth] = useState(true)

  useEffect(() => {
    // O token vive num cookie httpOnly (não em localStorage) — confirmamos
    // a sessão junto do backend ao arrancar a app.
    checkAuth().finally(() => setCheckingAuth(false))
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
          <Route path="/" element={<Navigate to={isAuthenticated ? "/dashboard" : "/login"} />} />
        </Routes>
      </BrowserRouter>
    </ToastProvider>
  )
}

export default App
