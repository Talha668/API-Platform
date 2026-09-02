export interface Project {
  id: number;
  name: string;
  description: string | null;
  owner: number;
  owner_email: string;
  is_active: boolean;
  tier: 'free' | 'pro' | 'enterprise';
  custom_rate_limit: number | null;
  api_keys_count: number;
  enabled_apis_count: number;
  total_requests: number;
  successful_requests: number;
  failed_requests: number;
  error_rate: number;
  avg_response_time: number;
  rate_limit: number;
  rate_limit_daily: number;
  rate_limit_remaining: number;
  total_requests_today: number;
  total_requests_this_week: number;
  created_at: string;
  updated_at: string;
}

export interface ProjectCreate {
  name: string;
  description?: string;
  tier?: 'free' | 'pro' | 'enterprise';
  custom_rate_limit?: number;
}

export interface ProjectUpdate {
  name?: string;
  description?: string;
  is_active?: boolean;
  tier?: 'free' | 'pro' | 'enterprise';
  custom_rate_limit?: number;
}

export interface ProjectUsage {
  daily_stats: Array<{
    day: string;
    total: number;
    successful: number;
    failed: number;
    avg_response: number;
  }>;
  top_endpoints: Array<{
    path: string;
    total: number;
    avg_response: number;
  }>;
  status_distribution: Record<string, number>;
  summary: {
    total: number;
    successful: number;
    failed: number;
    error_rate: number;
    avg_response_time: number;
  };
}