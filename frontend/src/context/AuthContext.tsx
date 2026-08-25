import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../services/api';
import { User } from '../types';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (name: string, email: string, password: string) => Promise<void>;
  logout: () => void;
  updateGoals: (goals: {
    name?: string;
    calorie_goal?: number;
    protein_goal?: number;
    carbs_goal?: number;
    fat_goal?: number;
    fiber_goal?: number;
  }) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'));
  const [loading, setLoading] = useState<boolean>(true);

  // Initialize and check for existing token on mount
  useEffect(() => {
    const initAuth = async () => {
      const storedToken = localStorage.getItem('token');
      if (storedToken) {
        try {
          setToken(storedToken);
          const response = await api.get<User>('/api/auth/me');
          setUser(response.data);
        } catch (error) {
          console.error("Session token validation failed:", error);
          localStorage.removeItem('token');
          setToken(null);
          setUser(null);
        }
      }
      setLoading(false);
    };
    initAuth();
  }, [token]);

  // Login handler
  const login = async (email: string, password: string) => {
    setLoading(true);
    try {
      const response = await api.post<{ access_token: string; token_type: string }>('/api/auth/login', {
        email,
        password,
      });
      const jwtToken = response.data.access_token;
      localStorage.setItem('token', jwtToken);
      setToken(jwtToken);
      
      // Fetch user profile immediately
      const userResponse = await api.get<User>('/api/auth/me');
      setUser(userResponse.data);
    } catch (error) {
      localStorage.removeItem('token');
      setToken(null);
      setUser(null);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  // Register handler
  const register = async (name: string, email: string, password: string) => {
    setLoading(true);
    try {
      // Create user account
      await api.post<User>('/api/auth/register', {
        name,
        email,
        password,
      });
      
      // Log in immediately after successful sign up
      await login(email, password);
    } catch (error) {
      setLoading(false);
      throw error;
    }
  };

  // Logout handler
  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
  };

  // Profile goals update
  const updateGoals = async (goals: {
    name?: string;
    calorie_goal?: number;
    protein_goal?: number;
    carbs_goal?: number;
    fat_goal?: number;
    fiber_goal?: number;
  }) => {
    try {
      const response = await api.put<User>('/api/profile', goals);
      setUser(response.data);
    } catch (error) {
      console.error("Profile goal update failed:", error);
      throw error;
    }
  };

  return (
    <AuthContext.Provider value={{ user, loading, token, login, register, logout, updateGoals }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
