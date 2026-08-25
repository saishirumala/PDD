import axios from 'axios';

// Vite proxies /api to backend (http://localhost:8000/api) in dev mode.
// VITE_API_URL can be set in .env for custom deployments.
const baseURL = (import.meta.env.VITE_API_URL as string) || '';

const api = axios.create({
  baseURL: baseURL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Automatically inject JWT Bearer token if present in localStorage
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Global response error handler (e.g. automatic logout on 401)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Clear expired credentials
      localStorage.removeItem('token');
      // If we are not on the landing page or auth page, we might want to redirect.
      // The AuthContext will monitor token states and handle this reactively.
    }
    return Promise.reject(error);
  }
);

export default api;
