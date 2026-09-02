import { apiClient } from './client';
import type { User, LoginCredentials, RegisterData, AuthResponse } from '../types/auth';


export const authAPI = {
  register: async (data: RegisterData): Promise<User> => {
    const response = await apiClient.post<AuthResponse>('/api/auth/register/', data);
    return response.data.user;
  },

  login: async (credentials: LoginCredentials): Promise<User> => {
    const response = await apiClient.post<AuthResponse>('/api/auth/login/', credentials);
    return response.data.user;
  },

  logout: async (): Promise<void> => {
    await apiClient.post('/api/auth/logout/');
  },

  refresh: async (): Promise<void> => {
    await apiClient.post('/api/auth/refresh/');
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await apiClient.get<User>('/api/auth/me/');
    return response.data;
  },

  updateProfile: async (data: Partial<User>): Promise<User> => {
    const response = await apiClient.patch<User>('/api/auth/me/', data);
    return response.data;
  },
};