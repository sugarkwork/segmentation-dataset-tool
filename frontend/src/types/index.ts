// API Response Types
export interface User {
  id: number;
  email: string;
  full_name: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Project {
  id: number;
  name: string;
  description?: string;
  owner_id: number;
  created_at: string;
  updated_at: string;
  image_count?: number;
  class_count?: number;
  annotation_count?: number;
}

export interface ProjectSummary {
  id: number;
  name: string;
  description?: string;
  created_at: string;
  updated_at: string;
  image_count: number;
  class_count: number;
  completion_percentage: number;
}

export interface Image {
  id: number;
  project_id: number;
  filename: string;
  original_filename: string;
  file_path: string;
  file_size: number;
  width: number;
  height: number;
  format: string;
  dataset_type: 'train' | 'val' | 'test';
  notes?: string;
  thumbnail_path?: string;
  created_at: string;
  updated_at: string;
}

export interface ClassDefinition {
  id: number;
  project_id: number;
  name: string;
  color: string;
  description?: string;
  created_at: string;
  updated_at: string;
}

// Form Types
export interface LoginForm {
  email: string;
  password: string;
}

export interface RegisterForm {
  email: string;
  full_name: string;
  password: string;
  confirmPassword: string;
}

export interface ProjectForm {
  name: string;
  description?: string;
}

export interface ClassForm {
  name: string;
  color: string;
  description?: string;
}