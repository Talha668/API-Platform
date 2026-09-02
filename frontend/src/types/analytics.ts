export interface AnalyticsData {
  total_requests: number;
  successful_requests: number;
  failed_requests: number;
  error_rate: number;
  avg_response_time: number;
  min_response_time: number;
  max_response_time: number;
  status_distribution: Record<string, number>;
  top_endpoints: Array<{
    endpoint: string;
    count: number;
  }>;
  daily_requests: Array<{
    date: string;
    count: number;
  }>;
}

export interface APIAnalyticsData {
  total_requests: number;
  successful_requests: number;
  failed_requests: number;
  error_rate: number;
  avg_response_time: number;
  hourly_requests: Array<{
    hour: string;
    count: number;
  }>;
}