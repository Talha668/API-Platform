import axios, { AxiosError } from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: API_URL,
  withCredentials: true, // Important for cookies
  headers: {
    'Content-Type': 'application/json',
  },
});

// Separate instance WITHOUT interceptors — used only for refreshing,
// so a failed refresh can never re-trigger the interceptor.
const refreshClient = axios.create({
  baseURL: API_URL,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Lock so only ONE refresh happens at a time;
// concurrent 401s wait for it and then retry.
let isRefreshing = false;
let failedQueue: Array<{
  resolve: (value?: unknown) => void;
  reject: (reason?: unknown) => void;
}> = [];

const processQueue = (error: unknown) => {
  failedQueue.forEach(({ resolve, reject }) =>
    error ? reject(error) : resolve()
  );
  failedQueue = [];
};

const forceLogout = () => {
  // Guard against redirect loops: only navigate if not already on /login
  if (!window.location.pathname.startsWith('/login')) {
    window.location.href = '/login';
  }
};

apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as (typeof error.config & { _retry?: boolean }) | undefined;

    if (!originalRequest) return Promise.reject(error);

    // RULE 1: never refresh for auth endpoints themselves
    if (originalRequest.url?.includes('/api/auth/refresh')) {
      return Promise.reject(error);
    }

    if (error.response?.status === 401 && !originalRequest._retry) {
      // Another refresh is already in flight — queue this request
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        }).then(() => apiClient(originalRequest));
      }

      originalRequest._retry = true; // RULE 2: retry each request only once
      isRefreshing = true;

      try {
        // RULE 3: use the interceptor-free instance
        await refreshClient.post('/api/auth/refresh/');
        processQueue(null);
        return apiClient(originalRequest);
      } catch (refreshError) {
        processQueue(refreshError);
        forceLogout();
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);