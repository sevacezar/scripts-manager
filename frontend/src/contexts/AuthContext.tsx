import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { apiClient } from '../api/client';
import type { LoginRequest, RegisterRequest, UserResponse } from '../types/api';

interface AuthContextType {
  isAuthenticated: boolean;
  isLoading: boolean;
  user: UserResponse | null;
  needsOnboarding: boolean;
  login: (data: LoginRequest) => Promise<void>;
  register: (data: RegisterRequest) => Promise<void>;
  logout: () => void;
  updateOnboardingStatus: (needsOnboarding: boolean) => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider = ({ children }: AuthProviderProps) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [user, setUser] = useState<UserResponse | null>(null);

  const loadUser = async () => {
    try {
      const userData = await apiClient.getCurrentUser();
      setUser(userData);
      setIsAuthenticated(true);
    } catch (error) {
      // Token might be invalid or expired
      localStorage.removeItem('access_token');
      setUser(null);
      setIsAuthenticated(false);
    }
  };

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      loadUser().finally(() => setIsLoading(false));
    } else {
      setIsLoading(false);
    }
  }, []);

  const handleLogin = async (data: LoginRequest) => {
    const response = await apiClient.login(data);
    localStorage.setItem('access_token', response.access_token);
    await loadUser();
  };

  const handleRegister = async (data: RegisterRequest) => {
    // Registration doesn't return a token - user needs to login separately
    await apiClient.register(data);
    // Don't set token or authentication state - user should login after registration
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    setUser(null);
    setIsAuthenticated(false);
  };

  const handleUpdateOnboardingStatus = async (needsOnboarding: boolean) => {
    const updatedUser = await apiClient.updateOnboardingStatus(needsOnboarding);
    setUser(updatedUser);
  };

  const handleRefreshUser = async () => {
    await loadUser();
  };

  return (
    <AuthContext.Provider
      value={{
        isAuthenticated,
        isLoading,
        user,
        needsOnboarding: user?.needs_onboarding ?? false,
        login: handleLogin,
        register: handleRegister,
        logout: handleLogout,
        updateOnboardingStatus: handleUpdateOnboardingStatus,
        refreshUser: handleRefreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};


