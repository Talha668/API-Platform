// src/types/auth.ts
export interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  company: string;
  bio: string;
  is_active: boolean;
  last_active_at: string;
  date_joined: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  password_confirm: string;   // required by backend
  first_name?: string;
  last_name?: string;
  company?: string;
}