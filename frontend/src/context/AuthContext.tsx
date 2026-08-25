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

  // Helper to create mock user
  const getMockUser = (emailVal: string, nameVal?: string): User => {
    const savedUser = localStorage.getItem('mock_user_data');
    if (savedUser) {
      try {
        return JSON.parse(savedUser);
      } catch (e) {}
    }
    const defaultUser: User = {
      id: 1,
      name: nameVal || emailVal.split('@')[0] || "Healthy Eater",
      email: emailVal,
      calorie_goal: 2000,
      protein_goal: 150,
      carbs_goal: 225,
      fat_goal: 65,
      fiber_goal: 30,
      created_at: new Date().toISOString()
    };
    localStorage.setItem('mock_user_data', JSON.stringify(defaultUser));
    return defaultUser;
  };

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
          // If backend isn't running or network error, fallback to stored local user
          console.warn("Backend unavailable, using local session fallback.");
          const mockUser = getMockUser("user@example.com");
          setUser(mockUser);
        }
      }
      setLoading(false);
    };
    initAuth();
  }, []);

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
      
      const userResponse = await api.get<User>('/api/auth/me');
      setUser(userResponse.data);
    } catch (error: any) {
      // Fallback for demo/offline mode on static hosts like GitHub Pages (where API returns 404)
      if (!error.response || error.response.status === 404 || error.code === 'ERR_NETWORK') {
        console.log("Using local offline/demo login fallback.");
        const fakeToken = "demo_token_" + Date.now();
        localStorage.setItem('token', fakeToken);
        setToken(fakeToken);
        const mockUser = getMockUser(email);
        setUser(mockUser);
        setLoading(false);
        return;
      }
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
      await api.post<User>('/api/auth/register', {
        name,
        email,
        password,
      });
      await login(email, password);
    } catch (error: any) {
      if (!error.response || error.response.status === 404 || error.code === 'ERR_NETWORK') {
        console.log("Using local offline/demo registration fallback.");
        const mockUser: User = {
          id: 1,
          name: name.trim(),
          email: email.trim(),
          calorie_goal: 2000,
          protein_goal: 150,
          carbs_goal: 225,
          fat_goal: 65,
          fiber_goal: 30,
          created_at: new Date().toISOString()
        };
        localStorage.setItem('mock_user_data', JSON.stringify(mockUser));
        const fakeToken = "demo_token_" + Date.now();
        localStorage.setItem('token', fakeToken);
        setToken(fakeToken);
        setUser(mockUser);
        setLoading(false);
        return;
      }
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
