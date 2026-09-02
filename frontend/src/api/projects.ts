import { apiClient } from './client';
import { Project, ProjectCreate, ProjectUpdate, ProjectUsage } from '../types/project';

export const projectsAPI = {
  list: async (): Promise<Project[]> => {
    const response = await apiClient.get<Project[]>('/api/projects/');
    return response.data;
  },

  get: async (id: number): Promise<Project> => {
    const response = await apiClient.get<Project>(`/api/projects/${id}/`);
    return response.data;
  },

  create: async (data: ProjectCreate): Promise<Project> => {
    const response = await apiClient.post<Project>('/api/projects/', data);
    return response.data;
  },

  update: async (id: number, data: ProjectUpdate): Promise<Project> => {
    const response = await apiClient.patch<Project>(`/api/projects/${id}/`, data);
    return response.data;
  },

  delete: async (id: number): Promise<void> => {
    await apiClient.delete(`/api/projects/${id}/`);
  },

  getUsage: async (id: number, days: number = 7): Promise<ProjectUsage> => {
    const response = await apiClient.get<ProjectUsage>(`/api/projects/${id}/usage/?days=${days}`);
    return response.data;
  },

  getRateLimit: async (id: number): Promise<any> => {
    const response = await apiClient.get(`/api/projects/${id}/rate-limit/`);
    return response.data;
  },
};