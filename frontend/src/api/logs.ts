import { apiClient } from './client';
import { RequestLog, LogFilters } from '../types/log';


export const logsAPI = {
  list: async (projectId: number, filters?: LogFilters): Promise<RequestLog[]> => {
    const params = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          params.append(key, String(value));
        }
      });
    }
    const url = `/api/logging/projects/${projectId}/logs/?${params.toString()}`;
    const response = await apiClient.get<RequestLog[]>(url);
    return response.data;
  },
};