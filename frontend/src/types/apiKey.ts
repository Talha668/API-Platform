export interface APIKey {
  id: number;
  name: string;
  project: number;
  project_name: string;
  key: string | null;
  key_prefix: string;
  scope: 'read' | 'write' | 'admin';
  scope_display: string;
  is_active: boolean;
  is_expired: boolean;
  last_used_at: string | null;
  expires_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface APIKeyCreate {
  name: string;
  scope: 'read' | 'write' | 'admin';
  expires_at?: string;
}

export interface APIKeyUpdate {
  name?: string;
  scope?: 'read' | 'write' | 'admin';
  is_active?: boolean;
}