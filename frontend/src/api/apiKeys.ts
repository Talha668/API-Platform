import { apiClient } from './client';
import { APIKey, APIKeyCreate, APIKeyUpdate } from '../types/apiKey';


export const apiKeysAPI = {
  list: async (projectId: number): Promise<APIKey[]> => {
    const response = await apiClient.get<APIKey[]>(`/api/api-keys/projects/${projectId}/keys/`);
    return response.data;
  },

  get: async (projectId: number, keyId: number): Promise<APIKey> => {
    const response = await apiClient.get<APIKey>(`/api/api-keys/projects/${projectId}/keys/${keyId}/`);
    return response.data;
  },

  create: async (projectId: number, data: APIKeyCreate): Promise<APIKey> => {
    const response = await apiClient.post<APIKey>(`/api/api-keys/projects/${projectId}/keys/`, data);
    return response.data;
  },

  update: async (projectId: number, keyId: number, data: APIKeyUpdate): Promise<APIKey> => {
    const response = await apiClient.patch<APIKey>(`/api/api-keys/projects/${projectId}/keys/${keyId}/`, data);
    return response.data;
  },

  delete: async (projectId: number, keyId: number): Promise<void> => {
    await apiClient.delete(`/api/api-keys/projects/${projectId}/keys/${keyId}/`);
  },

  regenerate: async (projectId: number, keyId: number): Promise<APIKey> => {
    const response = await apiClient.post<APIKey>(`/api/api-keys/projects/${projectId}/keys/${keyId}/regenerate/`);
    return response.data;
  },
};