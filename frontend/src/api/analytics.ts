import { apiClient } from './client';
import { AnalyticsData, APIAnalyticsData } from '../types/analytics';


export const analyticsAPI = {
  getProjectAnalytics: async (projectId: number, days: number = 7): Promise<AnalyticsData> => {
    const response = await apiClient.get<AnalyticsData>(
      `/api/logging/projects/${projectId}/analytics/?days=${days}`
    );
    return response.data;
  },

  getAPIAnalytics: async (projectId: number, apiSlug: string, days: number = 7): Promise<APIAnalyticsData> => {
    const response = await apiClient.get<APIAnalyticsData>(
      `/api/logging/projects/${projectId}/apis/${apiSlug}/analytics/?days=${days}`
    );
    return response.data;
  },
};