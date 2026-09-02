export interface RequestLog {
  id: number;
  project: number;
  project_name: string;
  api_key: number | null;
  api_key_name: string | null;
  api_definition: number | null;
  api_name: string | null;
  api_slug: string | null;
  method: string;
  path: string;
  full_url: string;
  status_code: number;
  response_time: number;
  ip_address: string;
  user_agent: string;
  is_error: boolean;
  is_authenticated: boolean;
  error_message: string | null;
  created_at: string;
  processed_at: string | null;
}

export interface LogFilters {
  status_code?: number;
  api?: string;
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE';
  start_date?: string;
  end_date?: string;
}