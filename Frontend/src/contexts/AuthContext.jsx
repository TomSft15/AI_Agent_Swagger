/**
 * Authentication Context
 *
 * Provides authentication state and methods throughout the application
 */
import { createContext, useContext, useState, useEffect } from 'react';
import { authAPI } from '../services/api';

const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Check if user is already logged in on mount
  useEffect(() => {
    let isMounted = true;

    const initAuth = async () => {
      const token = localStorage.getItem('access_token');

      if (!token) {
        setLoading(false);
        return;
      }

      try {
        console.log('[AUTH] Checking authentication...');
        const userData = await authAPI.getCurrentUser();
        if (isMounted) {
          setUser(userData);
          console.log('[AUTH] User authenticated:', userData.email);
        }
      } catch (error) {
        console.error('[AUTH] Authentication check failed:', error);
        if (isMounted) {
          // Clear invalid token
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    initAuth();

    return () => {
      isMounted = false;
    };
  }, []);

  const checkAuth = async () => {
    const token = localStorage.getItem('access_token');

    if (!token) {
      setLoading(false);
      return;
    }

    try {
      console.log('[AUTH] Checking authentication...');
      const userData = await authAPI.getCurrentUser();
      setUser(userData);
      console.log('[AUTH] User authenticated:', userData.email);
    } catch (error) {
      console.error('[AUTH] Authentication check failed:', error);
      // Clear invalid token
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    try {
      setError(null);
      console.log('[AUTH] Logging in...');

      const response = await authAPI.login(email, password);

      // Get user info after login
      const userData = await authAPI.getCurrentUser();
      setUser(userData);

      console.log('[AUTH] Login successful:', userData.email);
      return { success: true };
    } catch (error) {
      console.error('[AUTH] Login failed:', error);
      setError(error.message || 'Login failed');
      return { success: false, error: error.message };
    }
  };

  const register = async (userData) => {
    try {
      setError(null);
      console.log('[AUTH] Registering new user...');

      await authAPI.register(userData);

      // Auto-login after registration
      const loginResult = await login(userData.email, userData.password);

      if (loginResult.success) {
        console.log('[AUTH] Registration and auto-login successful');
      }

      return loginResult;
    } catch (error) {
      console.error('[AUTH] Registration failed:', error);
      setError(error.message || 'Registration failed');
      return { success: false, error: error.message };
    }
  };

  const logout = () => {
    console.log('[AUTH] Logging out...');
    authAPI.logout();
    setUser(null);
    setError(null);
  };

  const value = {
    user,
    loading,
    error,
    login,
    register,
    logout,
    isAuthenticated: !!user,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
