# 🔗 Frontend Integration Guide - JWT Authentication

**Para:** Frontend React  
**Endpoints:** `POST /api/auth/login`, `POST /api/auth/register`, `GET /api/auth/me`  
**Padrão:** Bearer token em Authorization header

---

## 1️⃣ Setup no Frontend (React + Axios)

### Instalar axios (se não tiver):
```bash
npm install axios
```

### Criar arquivo `src/api/authClient.ts`:

```typescript
import axios, { AxiosInstance } from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Criar instância axios
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor: adicionar token a todas as requisições
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Interceptor: handle 401 (token expirado)
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expirado, fazer logout
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default apiClient;
```

### Criar `src/api/authService.ts`:

```typescript
import apiClient from './authClient';

interface LoginRequest {
  email: string;
  password: string;
}

interface RegisterRequest {
  email: string;
  password: string;
  password_confirm: string;
}

interface TokenResponse {
  access_token: string;
  token_type: string;
  user_id: string;
  email: string;
  message: string;
}

interface User {
  id: string;
  email: string;
  is_admin: boolean;
}

export const authService = {
  // Login
  async login(email: string, password: string): Promise<TokenResponse> {
    const response = await apiClient.post<TokenResponse>('/api/auth/login', {
      email,
      password,
    });
    
    // Guardar token em localStorage
    localStorage.setItem('auth_token', response.data.access_token);
    localStorage.setItem('user_id', response.data.user_id);
    localStorage.setItem('user_email', response.data.email);
    
    return response.data;
  },

  // Register
  async register(
    email: string,
    password: string,
    passwordConfirm: string
  ): Promise<TokenResponse> {
    const response = await apiClient.post<TokenResponse>('/api/auth/register', {
      email,
      password,
      password_confirm: passwordConfirm,
    });
    
    // Guardar token
    localStorage.setItem('auth_token', response.data.access_token);
    localStorage.setItem('user_id', response.data.user_id);
    localStorage.setItem('user_email', response.data.email);
    
    return response.data;
  },

  // Logout
  async logout(): Promise<void> {
    await apiClient.post('/api/auth/logout');
    
    // Remover token
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_id');
    localStorage.removeItem('user_email');
  },

  // Get current user
  async getCurrentUser(): Promise<User> {
    const response = await apiClient.get<{ user: User; message: string }>(
      '/api/auth/me'
    );
    return response.data.user;
  },

  // Verify token
  async verifyToken(): Promise<boolean> {
    try {
      await apiClient.post('/api/auth/verify-token');
      return true;
    } catch {
      return false;
    }
  },

  // Get token from localStorage
  getToken(): string | null {
    return localStorage.getItem('auth_token');
  },

  // Check if user is authenticated
  isAuthenticated(): boolean {
    return !!this.getToken();
  },
};

export default authService;
```

---

## 2️⃣ Login Page Component

### `src/pages/LoginPage.tsx`:

```typescript
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import authService from '../api/authService';

export const LoginPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await authService.login(email, password);
      console.log('✅ Login bem-sucedido:', response);
      
      // Redirecionar para dashboard
      navigate('/dashboard');
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || 'Erro ao fazer login';
      setError(errorMsg);
      console.error('❌ Erro de login:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-900">
      <div className="w-full max-w-md p-8 bg-gray-800 rounded-lg shadow-lg">
        <h1 className="text-3xl font-bold text-white mb-8 text-center">
          Trading 212 Bot
        </h1>

        <form onSubmit={handleLogin} className="space-y-6">
          {error && (
            <div className="p-4 bg-red-500/20 text-red-200 rounded-lg">
              {error}
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Email
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full px-4 py-2 bg-gray-700 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="seu@email.com"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full px-4 py-2 bg-gray-700 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="••••••••"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition disabled:opacity-50"
          >
            {loading ? 'Carregando...' : 'Entrar'}
          </button>
        </form>

        <p className="text-center text-gray-400 mt-6">
          Sem conta?{' '}
          <a href="/register" className="text-blue-400 hover:underline">
            Criar conta
          </a>
        </p>
      </div>
    </div>
  );
};

export default LoginPage;
```

---

## 3️⃣ Register Page Component

### `src/pages/RegisterPage.tsx`:

```typescript
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import authService from '../api/authService';

export const RegisterPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [passwordConfirm, setPasswordConfirm] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    // Validações simples
    if (password.length < 8) {
      setError('Password deve ter mínimo 8 caracteres');
      setLoading(false);
      return;
    }

    if (password !== passwordConfirm) {
      setError('Passwords não coincidem');
      setLoading(false);
      return;
    }

    try {
      const response = await authService.register(email, password, passwordConfirm);
      console.log('✅ Registo bem-sucedido:', response);
      
      // Redirecionar para dashboard
      navigate('/dashboard');
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || 'Erro ao registar';
      setError(errorMsg);
      console.error('❌ Erro de registo:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-900">
      <div className="w-full max-w-md p-8 bg-gray-800 rounded-lg shadow-lg">
        <h1 className="text-3xl font-bold text-white mb-8 text-center">
          Criar Conta
        </h1>

        <form onSubmit={handleRegister} className="space-y-6">
          {error && (
            <div className="p-4 bg-red-500/20 text-red-200 rounded-lg">
              {error}
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Email
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full px-4 py-2 bg-gray-700 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="seu@email.com"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Password (mínimo 8 caracteres)
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full px-4 py-2 bg-gray-700 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="••••••••"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Confirmar Password
            </label>
            <input
              type="password"
              value={passwordConfirm}
              onChange={(e) => setPasswordConfirm(e.target.value)}
              required
              className="w-full px-4 py-2 bg-gray-700 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="••••••••"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition disabled:opacity-50"
          >
            {loading ? 'Criando...' : 'Criar Conta'}
          </button>
        </form>

        <p className="text-center text-gray-400 mt-6">
          Já tem conta?{' '}
          <a href="/login" className="text-blue-400 hover:underline">
            Fazer login
          </a>
        </p>
      </div>
    </div>
  );
};

export default RegisterPage;
```

---

## 4️⃣ Auth Context (Zustand Store)

### `src/stores/authStore.ts`:

```typescript
import { create } from 'zustand';
import authService from '../api/authService';

interface User {
  id: string;
  email: string;
  is_admin: boolean;
}

interface AuthStore {
  user: User | null;
  loading: boolean;
  error: string | null;
  isAuthenticated: boolean;

  // Actions
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, passwordConfirm: string) => Promise<void>;
  logout: () => Promise<void>;
  checkAuth: () => Promise<void>;
}

export const useAuthStore = create<AuthStore>((set) => ({
  user: null,
  loading: false,
  error: null,
  isAuthenticated: false,

  login: async (email: string, password: string) => {
    set({ loading: true, error: null });
    try {
      const response = await authService.login(email, password);
      set({
        user: {
          id: response.user_id,
          email: response.email,
          is_admin: false,
        },
        isAuthenticated: true,
        loading: false,
      });
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Erro ao fazer login',
        loading: false,
      });
      throw error;
    }
  },

  register: async (email: string, password: string, passwordConfirm: string) => {
    set({ loading: true, error: null });
    try {
      const response = await authService.register(email, password, passwordConfirm);
      set({
        user: {
          id: response.user_id,
          email: response.email,
          is_admin: false,
        },
        isAuthenticated: true,
        loading: false,
      });
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Erro ao registar',
        loading: false,
      });
      throw error;
    }
  },

  logout: async () => {
    set({ loading: true });
    try {
      await authService.logout();
      set({
        user: null,
        isAuthenticated: false,
        loading: false,
      });
    } catch (error: any) {
      set({
        error: 'Erro ao fazer logout',
        loading: false,
      });
    }
  },

  checkAuth: async () => {
    set({ loading: true });
    try {
      if (authService.isAuthenticated()) {
        const user = await authService.getCurrentUser();
        set({
          user,
          isAuthenticated: true,
          loading: false,
        });
      } else {
        set({
          isAuthenticated: false,
          loading: false,
        });
      }
    } catch (error) {
      set({
        isAuthenticated: false,
        loading: false,
      });
    }
  },
}));
```

---

## 5️⃣ Protected Route Component

### `src/components/ProtectedRoute.tsx`:

```typescript
import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const { isAuthenticated, loading } = useAuthStore();

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-white">Carregando...</div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};

export default ProtectedRoute;
```

---

## 6️⃣ App Routing Setup

### `src/App.tsx`:

```typescript
import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from './stores/authStore';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import DashboardPage from './pages/DashboardPage';
import ProtectedRoute from './components/ProtectedRoute';

function App() {
  const { checkAuth, loading } = useAuthStore();

  useEffect(() => {
    // Verificar se user já está autenticado ao carregar app
    checkAuth();
  }, [checkAuth]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-900">
        <div className="text-white text-xl">Carregando...</div>
      </div>
    );
  }

  return (
    <Router>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />

        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <DashboardPage />
            </ProtectedRoute>
          }
        />

        <Route path="/" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </Router>
  );
}

export default App;
```

---

## 7️⃣ Environment Variables

### `.env`:

```env
REACT_APP_API_URL=http://localhost:8000
# Em produção: https://trading212-4ojx.onrender.com
```

---

## ✅ Checklist de Integração

- [ ] Criar `src/api/authClient.ts` (axios instance + interceptors)
- [ ] Criar `src/api/authService.ts` (login, register, logout)
- [ ] Criar `src/stores/authStore.ts` (Zustand store)
- [ ] Criar `src/pages/LoginPage.tsx`
- [ ] Criar `src/pages/RegisterPage.tsx`
- [ ] Criar `src/components/ProtectedRoute.tsx`
- [ ] Atualizar `src/App.tsx` com routing
- [ ] Configurar `.env` com API_URL
- [ ] Testar login/register com backend

---

## 🧪 Testes

### Test 1: Registar e fazer login

```bash
# Frontend: Ir para http://localhost:3000/register
# Preencher: email=novo@example.com, password=SenhaForte123
# Clicar "Criar Conta"
# Esperar redirect para /dashboard
```

### Test 2: Token armazenado

```typescript
// Console do browser
localStorage.getItem('auth_token')
// Deve retornar: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Test 3: Requisição autenticada

```typescript
// Usar authService.getCurrentUser()
// Deve retornar: { id: "...", email: "novo@example.com", is_admin: false }
```

---

## 📞 Support

Para dúvidas, consultar:
- Backend: `backend/routes/auth.py`
- Docs: `AUTH_JWT_IMPLEMENTATION.md`
- FastAPI Swagger: `http://localhost:8000/docs`
