import axios from 'axios';

const getApiBaseUrl = () => {
  if (import.meta.env.VITE_API_BASE_URL) {
    return import.meta.env.VITE_API_BASE_URL;
  }
  const hostname = typeof window !== 'undefined' && window.location.hostname ? window.location.hostname : 'localhost';
  return `http://${hostname}:8000/api/v1`;
};

export const api = axios.create({
  baseURL: getApiBaseUrl(),
  timeout: 12000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor to inject JWT access token into request headers
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    if (config.data instanceof FormData) {
      delete config.headers['Content-Type'];
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Interceptor for 401 error response & token refresh logic
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      const url = originalRequest.url || '';
      if (url.includes('/auth/login') || url.includes('/auth/refresh') || url.includes('/auth/register')) {
        return Promise.reject(error);
      }
      originalRequest._retry = true;
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          const res = await axios.post(`${getApiBaseUrl()}/auth/refresh`, {
            refresh_token: refreshToken,
          });
          const newAccessToken = res.data.access_token;
          localStorage.setItem('access_token', newAccessToken);
          if (res.data.refresh_token) {
            localStorage.setItem('refresh_token', res.data.refresh_token);
          }
          originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
          return api(originalRequest);
        } catch (refreshErr) {
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          window.location.href = '/login';
        }
      }
    }
    return Promise.reject(error);
  }
);
